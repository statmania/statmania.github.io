#!/usr/bin/env python3
"""
Parses question/bank/stat1_mcq_bank.tex and stat2_mcq_bank.tex and generates
question/stat-prob.html: a self-contained, dark-theme quiz app.

Run: python3 build_quiz.py
Re-run any time the .tex source files change to regenerate the HTML.
"""
import json
import re
from html import escape as _esc
from pathlib import Path

HERE = Path(__file__).parent
SOURCES = [
    ("Statistics I", HERE / "bank" / "stat1_mcq_bank.tex"),
    ("Statistics II", HERE / "bank" / "stat2_mcq_bank.tex"),
]
OUT_HTML = HERE / "stat-prob.html"

LETTER_TO_IDX = {"a": 0, "b": 1, "c": 2, "d": 3}


def extract_braced(s, brace_start):
    """s[brace_start] must be '{'. Returns (inner_content, index_after_closing_brace)."""
    assert s[brace_start] == "{"
    depth = 0
    i = brace_start
    n = len(s)
    while i < n:
        ch = s[i]
        if ch == "\\" and i + 1 < n:
            i += 2
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return s[brace_start + 1:i], i + 1
        i += 1
    raise ValueError("Unbalanced braces starting at %d" % brace_start)


def strip_comments_with_markers(text):
    """Strip LaTeX '%' comments line by line, but turn our four semantic
    marker comments into sentinel tokens so downstream parsing can see them
    inline in the token stream."""
    markers = [
        (re.compile(r"^\s*%\s*Situation Set Starts"), "@@SITSTART@@"),
        (re.compile(r"^\s*%\s*Situation Set Ends"), "@@SITEND@@"),
        (re.compile(r"^\s*%\s*Multiple Completion Starts"), "@@MCSTART@@"),
        (re.compile(r"^\s*%\s*Multiple Completion Ends"), "@@MCEND@@"),
    ]
    out_lines = []
    for line in text.split("\n"):
        matched = False
        for pat, sentinel in markers:
            if pat.match(line):
                out_lines.append(sentinel)
                matched = True
                break
        if matched:
            continue
        # strip trailing comment at first unescaped '%'
        cut = len(line)
        i = 0
        while i < len(line):
            if line[i] == "\\" and i + 1 < len(line):
                i += 2
                continue
            if line[i] == "%":
                cut = i
                break
            i += 1
        out_lines.append(line[:cut])
    return "\n".join(out_lines)


def cell_to_html(cell):
    """Convert one table cell: unwrap \\textbf{...} -> <strong>, escape the rest."""
    cell = cell.strip()
    cell = cell.replace(r"\%", "%").replace(r"\&", "&").replace(r"\#", "#")
    out = []
    i = 0
    n = len(cell)
    while i < n:
        m = re.search(r"\\textbf\s*\{", cell[i:])
        if not m:
            out.append(_esc(cell[i:]))
            break
        start = i + m.start()
        out.append(_esc(cell[i:start]))
        brace_pos = i + m.end() - 1
        inner, after = extract_braced(cell, brace_pos)
        out.append("<strong>%s</strong>" % _esc(inner.strip()))
        i = after
    return "".join(out).strip()


def convert_table(tabular_body):
    """Convert the inner body of a \\begin{tabular}{..}...\\end{tabular} into an HTML table."""
    body = tabular_body.replace(r"\hline", "")
    rows = [r for r in re.split(r"\\\\", body) if r.strip()]
    html_rows = []
    for row in rows:
        cells = [c.strip() for c in row.split("&")]
        tds = "".join("<td>%s</td>" % cell_to_html(c) for c in cells)
        html_rows.append("<tr>%s</tr>" % tds)
    return '<table class="q-table">%s</table>' % "".join(html_rows)


def strip_table_wrappers(text):
    """Remove no-op wrapper commands (\\begin{table}, \\centering, \\begin{center}, ...)
    that surround a tabular but carry no content of their own."""
    text = re.sub(r"\\begin\{table\}(\[[^\]]*\])?", "", text)
    text = re.sub(r"\\end\{table\}", "", text)
    text = re.sub(r"\\centering", "", text)
    text = re.sub(r"\\begin\{center\}", "", text)
    text = re.sub(r"\\end\{center\}", "", text)
    return text


def latexify_inline(text):
    """Escape HTML, convert \\textbf{...} -> <strong>, and line breaks -> <br>.
    Leaves $...$ math delimiters intact for client-side KaTeX rendering."""
    text = text.strip()
    # escaped punctuation with no special meaning outside LaTeX -- drop the backslash
    text = text.replace(r"\%", "%").replace(r"\&", "&").replace(r"\#", "#")

    # Convert \textbf{...} (brace-aware) before escaping, capturing plain inner text.
    out = []
    i = 0
    n = len(text)
    while i < n:
        m = re.match(r"\\textbf\s*\{", text[i:])
        if m:
            brace_pos = i + m.end() - 1
            inner, after = extract_braced(text, brace_pos)
            out.append(("STRONG", inner))
            i = after
            continue
        # find next occurrence of \textbf from here
        nxt = text.find("\\textbf", i)
        if nxt == -1:
            out.append(("TEXT", text[i:]))
            break
        out.append(("TEXT", text[i:nxt]))
        i = nxt

    html_parts = []
    for kind, val in out:
        if kind == "TEXT":
            esc = _esc(val)
            esc = esc.replace("\\\\", "<br>")
            esc = re.sub(r"\\begin\{center\}", "", esc)
            esc = re.sub(r"\\end\{center\}", "", esc)
            html_parts.append(esc)
        else:  # STRONG (recurse in case of nested content, though rare)
            inner_esc = _esc(val)
            inner_esc = inner_esc.replace("\\\\", "<br>")
            html_parts.append("<strong>%s</strong>" % inner_esc)
    html = "".join(html_parts)
    # a blank line is a real LaTeX paragraph break (e.g. between the question
    # stem and a roman-numeral list, or between the list and "Which one is
    # correct?") -- preserve it as a line break before collapsing the rest.
    html = re.sub(r"[ \t]*\n[ \t]*\n[ \t]*", "<br>", html)
    html = re.sub(r"[ \t]*\n[ \t]*", " ", html).strip()
    html = re.sub(r"[ \t]{2,}", " ", html)
    html = re.sub(r"(?:<br>\s*){2,}", "<br>", html)
    html = re.sub(r"^(?:<br>\s*)+|(?:<br>\s*)+$", "", html)
    return html


def latexify_block(text):
    """Like latexify_inline but also converts any embedded LaTeX table to HTML.
    Used for both Situation Set context paragraphs and question stems, since
    either can carry a \\begin{table}/\\begin{center} wrapped tabular."""
    text = text.strip()
    text = strip_table_wrappers(text)
    table_htmls = []

    def _stash(m):
        table_htmls.append(convert_table(m.group(1)))
        return " @@TABLE%d@@ " % (len(table_htmls) - 1)

    text = re.sub(r"\\begin\{tabular\}\{[^}]*\}(.*?)\\end\{tabular\}", _stash, text, flags=re.S)

    image_htmls = []

    def _stash_img(m):
        # Paths in the .tex are relative to question/bank/; stat-prob.html
        # lives one directory up, in question/, so drop exactly one leading
        # "../" to re-base them (e.g. "../img/x.png" -> "img/x.png",
        # "../../slide/img/x.jpg" -> "../slide/img/x.jpg").
        path = re.sub(r"^\.\./", "", m.group(1).strip(), count=1)
        image_htmls.append('<img src="%s" alt="" class="q-image">' % _esc(path))
        return " @@IMG%d@@ " % (len(image_htmls) - 1)

    text = re.sub(r"\\includegraphics(?:\[[^\]]*\])?\{([^{}]*)\}", _stash_img, text)

    html = latexify_inline(text)
    for idx, th in enumerate(table_htmls):
        html = html.replace("@@TABLE%d@@" % idx, th)
    for idx, ih in enumerate(image_htmls):
        html = html.replace("@@IMG%d@@" % idx, ih)
    return html


def parse_bank(path, subject_label):
    raw = path.read_text(encoding="utf-8")
    doc_m = re.search(r"\\begin\{document\}", raw)
    end_m = re.search(r"\\end\{document\}", raw)
    if not doc_m:
        raise ValueError("No \\begin{document} found in %s" % path)
    body = raw[doc_m.end():end_m.start() if end_m else len(raw)]
    stream = strip_comments_with_markers(body)

    token_re = re.compile(
        r"\\subsubsection\*?\s*\{|\\subsection\*?\s*\{|\\section\*?\s*\{|\\question\b"
        r"|@@SITSTART@@|@@SITEND@@|@@MCSTART@@|@@MCEND@@"
    )

    current = {"section": None, "subsection": None, "subsubsection": None}
    in_situation = False
    context_captured = True
    situation_counter = 0
    current_situation_id = None
    pending_text = []
    in_mc = False

    questions = []
    situations = {}  # situation_id -> context_html

    pos = 0
    n = len(stream)
    while True:
        m2 = token_re.search(stream, pos)
        if not m2:
            break
        # text between pos and m2.start() is plain body text
        plain = stream[pos:m2.start()]
        pending_text.append(plain)
        tok = m2.group(0)

        if tok in ("@@SITSTART@@",):
            in_situation = True
            context_captured = False
            situation_counter += 1
            current_situation_id = situation_counter
            pending_text = []
            pos = m2.end()
            continue
        if tok in ("@@SITEND@@",):
            in_situation = False
            current_situation_id = None
            pending_text = []
            pos = m2.end()
            continue
        if tok in ("@@MCSTART@@",):
            in_mc = True
            pos = m2.end()
            continue
        if tok in ("@@MCEND@@",):
            in_mc = False
            pos = m2.end()
            continue

        if tok.startswith("\\section"):
            brace_pos = m2.end() - 1
            content, after = extract_braced(stream, brace_pos)
            current["section"] = latexify_inline(content)
            current["subsection"] = None
            current["subsubsection"] = None
            pending_text = []
            pos = after
            continue
        if tok.startswith("\\subsubsection"):
            brace_pos = m2.end() - 1
            content, after = extract_braced(stream, brace_pos)
            current["subsubsection"] = latexify_inline(content)
            pending_text = []
            pos = after
            continue
        if tok.startswith("\\subsection"):
            brace_pos = m2.end() - 1
            content, after = extract_braced(stream, brace_pos)
            current["subsection"] = latexify_inline(content)
            current["subsubsection"] = None
            pending_text = []
            pos = after
            continue

        if tok == "\\question":
            # a malformed source question has no \choice before the next \question
            # (or end of stream) -- skip just that one question rather than
            # merging its text with the next question's choices.
            next_q_m = token_re.search(stream, m2.end())
            boundary = next_q_m.start() if next_q_m else len(stream)
            choice_m = re.search(r"\\choice\s*\{", stream[m2.end():boundary])
            if not choice_m:
                pending_text = []
                pos = m2.end()
                continue
            q_text_raw = stream[m2.end():m2.end() + choice_m.start()]
            choice_brace_pos = m2.end() + choice_m.end() - 1
            args = []
            bp = choice_brace_pos
            for _ in range(5):
                content, after = extract_braced(stream, bp)
                args.append(content)
                # advance bp to the next '{'
                nb = stream.find("{", after)
                bp = nb
            options_raw, answer_letter = args[:4], args[4].strip().lower()
            answer_idx = LETTER_TO_IDX.get(answer_letter, 0)

            q_type = "multiple_completion" if in_mc else ("situation" if in_situation else "simple")

            if in_situation and not context_captured:
                ctx_text = "".join(pending_text)
                situations[current_situation_id] = latexify_block(ctx_text)
                context_captured = True

            topic = current["subsection"] or current["section"] or "General"
            subtopic = current["subsubsection"]

            questions.append({
                "subject": subject_label,
                "chapter": current["section"] or "General",
                "topic": topic,
                "subtopic": subtopic,
                "type": q_type,
                "situation_id": ("%s-%s" % (subject_label, current_situation_id)) if in_situation else None,
                "question_html": latexify_block(q_text_raw),
                "options_html": [latexify_block(o) for o in options_raw],
                "answer": answer_idx,
            })
            pending_text = []
            pos = args and bp  # bp currently points at leftover '{' search result; recompute properly below

            # recompute pos precisely: end of 5th brace group
            # (re-extract to know exact end index)
            bp2 = choice_brace_pos
            end_after = choice_brace_pos
            for _ in range(5):
                content, after = extract_braced(stream, bp2)
                end_after = after
                nb = stream.find("{", after)
                bp2 = nb if nb != -1 else after
            pos = end_after
            continue

    # attach situation context to each question
    for q in questions:
        if q["situation_id"] is not None:
            q["context_html"] = situations.get(int(q["situation_id"].split("-")[-1]), "")
        else:
            q["context_html"] = None
    return questions


def build_outline(all_questions):
    """chapter -> topic -> count, for the dropdown UI."""
    outline = {}
    for q in all_questions:
        ch = outline.setdefault(q["chapter"], {})
        ch[q["topic"]] = ch.get(q["topic"], 0) + 1
    return outline


HTML_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Stat &amp; Prob Quiz | Stat Mania</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<script src="https://cdn.tailwindcss.com"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/contrib/auto-render.min.js"></script>
<link rel="stylesheet" href="../games/css/dark-theme.css">
<style>
  body { font-family: 'Inter', sans-serif; }
  .q-table { border-collapse: collapse; margin: 0.75rem 0; font-size: 0.9rem; }
  .q-table td { border: 1px solid rgba(255,255,255,0.15); padding: 4px 10px; }
  .q-image { max-width: 100%; border-radius: 0.6rem; margin: 0.75rem 0; display: block; }
  select.sm-select {
    background-color: #0a0f1e;
    border: 1px solid rgba(0,229,255,0.3);
    color: #e5e9f5;
    background-image: url("data:image/svg+xml;charset=UTF-8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20' fill='none' stroke='%2300e5ff' stroke-width='2'%3E%3Cpath d='M6 8l4 4 4-4' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 0.75rem center;
    background-size: 1.1rem;
    padding-right: 2.25rem;
    -webkit-appearance: none;
    appearance: none;
  }
  select.sm-select:focus { outline: none; border-color: #00e5ff; }
  /* Native <option> popups don't inherit page theming and can render
     light-on-light in some browsers -- force explicit contrast. */
  select.sm-select option {
    background-color: #0a0f1e;
    color: #e5e9f5;
  }
  .opt-btn { transition: all .15s ease; }
  .opt-btn.correct { border-color: #22c55e !important; background: rgba(34,197,94,0.12) !important; }
  .opt-btn.wrong { border-color: #ef4444 !important; background: rgba(239,68,68,0.12) !important; }
  .opt-btn.picked:not(.correct):not(.wrong) { border-color: #00e5ff !important; }
  .progress-bar-fill { transition: width .25s ease; }
  #quiz-note { color: var(--sm-muted, #9aa4c2); }
</style>
</head>
<body class="antialiased flex flex-col min-h-screen">

<!-- Header/Navbar -->
<header class="bg-white shadow-sm py-4">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8 flex justify-between items-center">
        <a href="../index.html" class="flex items-center space-x-3 no-underline hover:opacity-80 transition-opacity">
            <img src="../img/statmania_logo.png" alt="Stat Mania Logo" class="w-10 h-10 rounded-full" onerror="this.onerror=null;this.src='https://placehold.co/40x40/4f46e5/ffffff?text=Logo';">
            <div>
                <div class="text-2xl font-bold text-indigo-600">Stat Mania</div>
                <p class="text-sm text-slate-500">Making sense of statistics</p>
            </div>
        </a>
        <nav class="hidden md:block">
            <ul class="flex space-x-6">
                <li><a href="../index.html" class="text-slate-600 hover:text-indigo-600 transition duration-300">Home</a></li>
                <li><a href="../games/index.html" class="text-slate-600 hover:text-indigo-600 transition duration-300">Games</a></li>
                <li><a href="stat-prob.html" class="text-slate-600 hover:text-indigo-600 transition duration-300">Quiz</a></li>
            </ul>
        </nav>
        <button id="mobile-menu-button" class="md:hidden p-2 rounded-md text-slate-600 hover:text-indigo-600 focus:outline-none focus:ring-2 focus:ring-indigo-500">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7"></path>
            </svg>
        </button>
    </div>
    <div id="mobile-menu" class="hidden md:hidden px-2 pt-2 pb-3 space-y-1 sm:px-3">
        <a href="../index.html" class="block px-3 py-2 rounded-md text-base font-medium text-slate-700 hover:bg-slate-100 hover:text-indigo-600">Home</a>
        <a href="../games/index.html" class="block px-3 py-2 rounded-md text-base font-medium text-slate-700 hover:bg-slate-100 hover:text-indigo-600">Games</a>
        <a href="stat-prob.html" class="block px-3 py-2 rounded-md text-base font-medium text-slate-700 hover:bg-slate-100 hover:text-indigo-600">Quiz</a>
    </div>
</header>

<main class="flex-grow">
    <!-- Hero Section -->
    <section class="sm-hero-wrap">
        <canvas class="sm-canvas" aria-hidden="true"></canvas>
        <div class="sm-hero-inner">
            <span class="sm-eyebrow">Stat Mania &middot; Practice</span>
            <h1 class="text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-tight mb-4 flex items-center justify-center gap-4 sm-gradient-text">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-12 h-12 sm-hero-icon">
                    <path fill-rule="evenodd" d="M4.5 2.25a.75.75 0 0 0 0 1.5v16.5h-.75a.75.75 0 0 0 0 1.5h16.5a.75.75 0 0 0 0-1.5h-.75V3.75a.75.75 0 0 0 0-1.5h-15Zm4.5 15a.75.75 0 0 1 .75-.75h1.5a.75.75 0 0 1 .75.75v3h-3v-3Zm6-6a.75.75 0 0 1 .75-.75h1.5a.75.75 0 0 1 .75.75v9h-3v-9Zm-9-3a.75.75 0 0 1 .75-.75h1.5a.75.75 0 0 1 .75.75v12h-3v-12Z" clip-rule="evenodd" />
                </svg>
                Statistics &amp; Probability Quiz
            </h1>
            <p class="text-lg sm:text-xl sm-subtitle-sm">__QCOUNT__ questions across both Statistics I and Statistics II question banks &mdash; pick a chapter, a topic, and how many questions you want.</p>
        </div>
    </section>

    <!-- Quiz Section -->
    <section class="py-12 px-4 sm:px-6 lg:px-8 bg-slate-50">
        <div class="container mx-auto max-w-3xl">

            <div id="setup-view" class="sm-card p-8 space-y-5">
                <div>
                    <label class="block text-sm text-slate-400 mb-1">Chapter</label>
                    <select id="chapter-select" class="sm-select w-full rounded-lg px-3 py-2"></select>
                </div>
                <div>
                    <label class="block text-sm text-slate-400 mb-1">Topic</label>
                    <select id="topic-select" class="sm-select w-full rounded-lg px-3 py-2"></select>
                </div>
                <div>
                    <label class="block text-sm text-slate-400 mb-1">Number of questions</label>
                    <select id="count-select" class="sm-select w-full rounded-lg px-3 py-2"></select>
                    <p class="text-xs mt-1.5" id="quiz-note">Situation Set questions are always kept together, so the actual count may land a little under what you pick.</p>
                </div>
                <div>
                    <label class="block text-sm text-slate-400 mb-1">Answer reveal</label>
                    <div class="flex gap-3">
                        <label class="flex items-center gap-2 text-sm text-slate-300">
                            <input type="radio" name="reveal-mode" value="immediate" checked> After each question
                        </label>
                        <label class="flex items-center gap-2 text-sm text-slate-300">
                            <input type="radio" name="reveal-mode" value="end"> After all questions
                        </label>
                    </div>
                </div>
                <button id="start-btn" class="sm-btn sm-btn-primary w-full justify-center">Start Quiz</button>
            </div>

            <div id="quiz-view" class="hidden">
                <div class="flex items-center justify-between text-sm mb-2" style="color:var(--sm-muted)">
                    <span id="progress-label">Question 1 / 10</span>
                    <span id="score-label">Score: 0</span>
                </div>
                <div class="h-1.5 rounded-full bg-white/10 overflow-hidden mb-6">
                    <div id="progress-bar" class="progress-bar-fill h-full bg-gradient-to-r from-[#00e5ff] via-[#a855f7] to-[#ff2fb4]" style="width:0%"></div>
                </div>
                <div class="sm-card p-8">
                    <div id="q-meta" class="text-xs uppercase tracking-wide mb-3" style="color:var(--sm-cyan)"></div>
                    <div id="q-context" class="mb-4 text-sm leading-relaxed hidden rounded-lg p-4" style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08)"></div>
                    <div id="q-text" class="text-lg font-semibold mb-5 leading-relaxed"></div>
                    <div id="q-options" class="space-y-3"></div>
                    <div id="q-feedback" class="mt-4 text-sm hidden"></div>
                    <div class="mt-6 flex justify-end">
                        <button id="next-btn" class="hidden sm-btn sm-btn-primary">Next</button>
                        <button id="submit-end-btn" class="hidden sm-btn sm-btn-primary">Submit Answer</button>
                    </div>
                </div>
            </div>

            <div id="summary-view" class="hidden sm-card p-8 text-center">
                <div class="text-4xl mb-2">🎉</div>
                <h2 class="text-2xl font-bold mb-1">Quiz Complete!</h2>
                <p id="summary-score" class="mb-6" style="color:var(--sm-muted)"></p>
                <div id="summary-list" class="text-left space-y-4 max-h-[50vh] overflow-y-auto pr-1"></div>
                <button id="restart-btn" class="sm-btn sm-btn-primary mt-6">New Quiz</button>
            </div>

        </div>
    </section>
</main>

<!-- Footer -->
<footer class="bg-slate-800 text-white py-8 px-4 sm:px-6 lg:px-8 text-center mt-auto" style="border-top:1px solid rgba(255,255,255,0.08)">
    <div class="container mx-auto">
        <p class="mb-4">&copy; <span id="copyright-year">2026</span> Stat Mania. All rights reserved.</p>
    </div>
</footer>

<script>document.getElementById("copyright-year").textContent = new Date().getFullYear();</script>

<script>
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    mobileMenuButton.addEventListener('click', () => mobileMenu.classList.toggle('hidden'));
    mobileMenu.querySelectorAll('a').forEach(link => link.addEventListener('click', () => mobileMenu.classList.add('hidden')));
</script>
<script src="../games/js/starfield.js"></script>

<script>
const QUESTIONS = __QUESTIONS_JSON__;
const OUTLINE = __OUTLINE_JSON__;

const chapterSelect = document.getElementById('chapter-select');
const topicSelect = document.getElementById('topic-select');
const countSelect = document.getElementById('count-select');

function populateChapters() {
  const chapters = Object.keys(OUTLINE);
  const allOpt = document.createElement('option');
  allOpt.value = '__ALL__';
  allOpt.textContent = 'All Chapters';
  chapterSelect.appendChild(allOpt);
  chapters.forEach(ch => {
    const opt = document.createElement('option');
    opt.value = ch;
    opt.textContent = ch;
    chapterSelect.appendChild(opt);
  });
}

function populateTopics() {
  topicSelect.innerHTML = '';
  const allOpt = document.createElement('option');
  allOpt.value = '__ALL__';
  allOpt.textContent = 'All Topics';
  topicSelect.appendChild(allOpt);
  const ch = chapterSelect.value;
  let topics = new Set();
  if (ch === '__ALL__') {
    Object.values(OUTLINE).forEach(t => Object.keys(t).forEach(x => topics.add(x)));
  } else if (OUTLINE[ch]) {
    Object.keys(OUTLINE[ch]).forEach(x => topics.add(x));
  }
  [...topics].forEach(t => {
    const opt = document.createElement('option');
    opt.value = t;
    opt.textContent = t;
    topicSelect.appendChild(opt);
  });
}

function filteredQuestions() {
  const ch = chapterSelect.value;
  const tp = topicSelect.value;
  return QUESTIONS.filter(q => (ch === '__ALL__' || q.chapter === ch) && (tp === '__ALL__' || q.topic === tp));
}

// Situation Set questions must always be kept together in the quiz. Group the
// filtered pool into "units": a unit is either a single simple/multiple-completion
// question, or the full ordered list of questions that share one situation_id.
function buildUnits(pool) {
  const groups = {};
  const units = [];
  pool.forEach(q => {
    if (q.situation_id) {
      if (!groups[q.situation_id]) {
        groups[q.situation_id] = [];
        units.push(groups[q.situation_id]);
      }
      groups[q.situation_id].push(q);
    } else {
      units.push([q]);
    }
  });
  return units;
}

// Picks units at random, greedily filling toward the requested count without
// ever splitting a unit, and without exceeding n. Because situation-set units
// are size 2-4, an exact match on n isn't always achievable -- try a handful of
// random orderings and keep the closest (highest) fill under n.
function pickQuestions(pool, n) {
  const units = buildUnits(pool);
  const totalAvail = pool.length;
  if (n >= totalAvail) return { questions: shuffle(units).flat(), requested: n };

  let best = null;
  for (let attempt = 0; attempt < 60; attempt++) {
    const order = shuffle(units);
    let remaining = n;
    const chosen = [];
    for (const u of order) {
      if (u.length <= remaining) {
        chosen.push(u);
        remaining -= u.length;
      }
      if (remaining === 0) break;
    }
    const got = n - remaining;
    if (best === null || got > best.got) best = { chosen, got };
    if (remaining === 0) break;
  }
  return { questions: shuffle(best.chosen).flat(), requested: n };
}

function populateCounts() {
  countSelect.innerHTML = '';
  const avail = filteredQuestions().length;
  const options = [5, 10, 15, 20, 30].filter(n => n <= avail);
  if (avail > 0) options.push(avail);
  const uniq = [...new Set(options)].sort((a,b)=>a-b);
  if (uniq.length === 0) uniq.push(0);
  uniq.forEach(n => {
    const opt = document.createElement('option');
    opt.value = n;
    opt.textContent = n + ' question' + (n === 1 ? '' : 's');
    countSelect.appendChild(opt);
  });
  countSelect.value = uniq[uniq.length - 1];
}

chapterSelect.addEventListener('change', () => { populateTopics(); populateCounts(); });
topicSelect.addEventListener('change', populateCounts);

populateChapters();
populateTopics();
populateCounts();

function shuffle(arr) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

let state = null;

function renderMath(el) {
  if (window.renderMathInElement) {
    renderMathInElement(el, {
      delimiters: [
        {left: '$', right: '$', display: false},
        {left: '\\(', right: '\\)', display: false}
      ],
      throwOnError: false
    });
  }
}

document.getElementById('start-btn').addEventListener('click', () => {
  const n = parseInt(countSelect.value, 10);
  if (!n) return;
  const pool = filteredQuestions();
  const { questions: picked, requested } = pickQuestions(pool, n);
  const revealMode = document.querySelector('input[name="reveal-mode"]:checked').value;
  state = { questions: picked, idx: 0, score: 0, revealMode, answers: [], requested };
  document.getElementById('setup-view').classList.add('hidden');
  document.getElementById('summary-view').classList.add('hidden');
  document.getElementById('quiz-view').classList.remove('hidden');
  renderQuestion();
});

function renderQuestion() {
  const q = state.questions[state.idx];
  const shortLabel = state.questions.length < state.requested
    ? ` (closest fit to ${state.requested} keeping Situation Sets together)`
    : '';
  document.getElementById('progress-label').textContent = `Question ${state.idx + 1} / ${state.questions.length}${shortLabel}`;
  document.getElementById('score-label').textContent = `Score: ${state.score}`;
  document.getElementById('progress-bar').style.width = `${(state.idx / state.questions.length) * 100}%`;

  const metaBits = [q.subject, q.chapter];
  if (q.topic && q.topic !== q.chapter) metaBits.push(q.topic);
  if (q.type === 'multiple_completion') metaBits.push('Multiple Completion');
  if (q.type === 'situation') metaBits.push('Situation Set');
  document.getElementById('q-meta').textContent = metaBits.join(' • ');

  const ctxEl = document.getElementById('q-context');
  if (q.context_html) {
    ctxEl.innerHTML = q.context_html;
    ctxEl.classList.remove('hidden');
  } else {
    ctxEl.classList.add('hidden');
  }

  document.getElementById('q-text').innerHTML = q.question_html;

  const optsEl = document.getElementById('q-options');
  optsEl.innerHTML = '';
  const feedbackEl = document.getElementById('q-feedback');
  feedbackEl.classList.add('hidden');
  feedbackEl.innerHTML = '';
  document.getElementById('next-btn').classList.add('hidden');
  document.getElementById('submit-end-btn').classList.add('hidden');

  let picked = null;

  q.options_html.forEach((opt, i) => {
    const btn = document.createElement('button');
    btn.className = 'opt-btn w-full text-left rounded-lg border border-white/15 bg-white/[0.02] px-4 py-3 hover:border-cyan-400/60';
    btn.innerHTML = opt;
    btn.addEventListener('click', () => {
      if (state.locked) return;
      picked = i;
      [...optsEl.children].forEach(b => b.classList.remove('picked'));
      btn.classList.add('picked');
      if (state.revealMode === 'immediate') {
        lockAndReveal(i);
      } else {
        document.getElementById('submit-end-btn').classList.remove('hidden');
      }
    });
    optsEl.appendChild(btn);
  });

  state.locked = false;

  function lockAndReveal(pickedIdx) {
    state.locked = true;
    const correct = pickedIdx === q.answer;
    if (correct) state.score++;
    state.answers.push({ q, pickedIdx, correct });
    [...optsEl.children].forEach((b, i) => {
      if (i === q.answer) b.classList.add('correct');
      else if (i === pickedIdx) b.classList.add('wrong');
    });
    feedbackEl.classList.remove('hidden');
    feedbackEl.innerHTML = correct
      ? '<span class="text-green-400 font-semibold">Correct!</span>'
      : `<span class="text-red-400 font-semibold">Not quite.</span> The correct answer is highlighted above.`;
    document.getElementById('submit-end-btn').classList.add('hidden');
    document.getElementById('next-btn').classList.remove('hidden');
    document.getElementById('score-label').textContent = `Score: ${state.score}`;
    renderMath(feedbackEl);
  }

  document.getElementById('submit-end-btn').onclick = () => {
    if (picked === null) return;
    if (state.revealMode === 'end') {
      state.locked = true;
      const correct = picked === q.answer;
      if (correct) state.score++;
      state.answers.push({ q, pickedIdx: picked, correct });
      document.getElementById('score-label').textContent = `Score: ${state.score}`;
      document.getElementById('submit-end-btn').classList.add('hidden');
      document.getElementById('next-btn').classList.remove('hidden');
    } else {
      lockAndReveal(picked);
    }
  };

  document.getElementById('next-btn').onclick = () => {
    state.idx++;
    if (state.idx >= state.questions.length) {
      showSummary();
    } else {
      renderQuestion();
    }
  };

  renderMath(document.getElementById('quiz-view'));
}

function showSummary() {
  document.getElementById('quiz-view').classList.add('hidden');
  document.getElementById('summary-view').classList.remove('hidden');
  document.getElementById('summary-score').textContent =
    `You scored ${state.score} / ${state.questions.length}.`;
  const listEl = document.getElementById('summary-list');
  listEl.innerHTML = '';
  state.answers.forEach((a, i) => {
    const div = document.createElement('div');
    div.className = 'rounded-lg p-4';
    div.style.background = 'rgba(255,255,255,0.02)';
    div.style.border = '1px solid rgba(255,255,255,0.08)';
    const correctText = a.q.options_html[a.q.answer];
    const pickedText = a.q.options_html[a.pickedIdx];
    div.innerHTML = `
      <div class="text-sm mb-1" style="color:var(--sm-muted)">Q${i + 1} · ${a.correct ? '<span class="text-green-400">Correct</span>' : '<span class="text-red-400">Incorrect</span>'}</div>
      <div class="font-medium mb-2">${a.q.question_html}</div>
      ${a.correct ? '' : `<div class="text-sm text-red-300 mb-1">Your answer: ${pickedText}</div>`}
      <div class="text-sm text-green-300">Correct answer: ${correctText}</div>
    `;
    listEl.appendChild(div);
  });
  renderMath(listEl);
}

document.getElementById('restart-btn').addEventListener('click', () => {
  document.getElementById('summary-view').classList.add('hidden');
  document.getElementById('setup-view').classList.remove('hidden');
});
</script>
</body>
</html>
"""


def main():
    all_questions = []
    for subject_label, path in SOURCES:
        qs = parse_bank(path, subject_label)
        print(f"{path.name}: parsed {len(qs)} questions")
        all_questions.extend(qs)

    type_counts = {}
    for q in all_questions:
        type_counts[q["type"]] = type_counts.get(q["type"], 0) + 1
    print("By type:", type_counts)

    outline = build_outline(all_questions)
    for ch, topics in outline.items():
        print(f"  {ch}: {sum(topics.values())} q  ({len(topics)} topics)")

    html = HTML_TEMPLATE
    html = html.replace("__QCOUNT__", str(len(all_questions)))
    html = html.replace("__QUESTIONS_JSON__", json.dumps(all_questions, ensure_ascii=False))
    html = html.replace("__OUTLINE_JSON__", json.dumps(outline, ensure_ascii=False))

    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT_HTML} ({OUT_HTML.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
