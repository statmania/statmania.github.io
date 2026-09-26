#!/usr/bin/env python3
"""
Parses quiz/gk.csv and generates quiz/quiz.html: a self-contained, dark-theme
General Knowledge quiz app matching the look of question/stat-prob.html.

Run: python3 build_quiz.py
Re-run any time gk.csv changes to regenerate the HTML.
"""
import csv
import json
from html import escape as _esc
from pathlib import Path

HERE = Path(__file__).parent
SRC_CSV = HERE / "gk.csv"
OUT_HTML = HERE / "quiz.html"


def load_questions():
    questions = []
    with SRC_CSV.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            question = (row.get("Question") or "").strip()
            answer = (row.get("Answer") or "").strip()
            topic = (row.get("Topic") or "").strip()
            subtopic = (row.get("Subtopic") or "").strip()
            if not question or not answer or not topic:
                continue
            questions.append({
                "id": row.get("SL", "").strip(),
                "question_html": _esc(question),
                "answer_html": _esc(answer),
                "topic": topic,
                "subtopic": subtopic or None,
            })
    return questions


def build_outline(questions):
    outline = {}
    for q in questions:
        topics = outline.setdefault(q["topic"], {})
        if q["subtopic"]:
            topics[q["subtopic"]] = topics.get(q["subtopic"], 0) + 1
    return outline


HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>General Knowledge Quiz | Stat Mania</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<script src="https://cdn.tailwindcss.com"></script>
<link rel="stylesheet" href="../games/css/dark-theme.css">
<style>
  body { font-family: 'Inter', sans-serif; }
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
  input.sm-input {
    background-color: #0a0f1e;
    border: 1px solid rgba(0,229,255,0.3);
    color: #e5e9f5;
  }
  input.sm-input:focus { outline: none; border-color: #00e5ff; }
  input.sm-input::placeholder { color: rgba(229,233,245,0.35); }
  .mark-btn { transition: all .15s ease; }
  .mark-btn.chosen-correct { border-color: #22c55e !important; background: rgba(34,197,94,0.15) !important; color: #86efac !important; }
  .mark-btn.chosen-wrong { border-color: #ef4444 !important; background: rgba(239,68,68,0.15) !important; color: #fca5a5 !important; }
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
                <li><a href="../question/stat-prob.html" class="text-slate-600 hover:text-indigo-600 transition duration-300">Stat &amp; Prob Quiz</a></li>
                <li><a href="quiz.html" class="text-slate-600 hover:text-indigo-600 transition duration-300">GK Quiz</a></li>
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
        <a href="../question/stat-prob.html" class="block px-3 py-2 rounded-md text-base font-medium text-slate-700 hover:bg-slate-100 hover:text-indigo-600">Stat &amp; Prob Quiz</a>
        <a href="quiz.html" class="block px-3 py-2 rounded-md text-base font-medium text-slate-700 hover:bg-slate-100 hover:text-indigo-600">GK Quiz</a>
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
                    <path fill-rule="evenodd" d="M11.25 4.533A9.707 9.707 0 0 0 6 3a9.735 9.735 0 0 0-3.25.555.75.75 0 0 0-.5.707v14.25a.75.75 0 0 0 1 .707A8.237 8.237 0 0 1 6 18.75c1.995 0 3.823.707 5.25 1.886V4.533ZM12.75 20.636A8.214 8.214 0 0 1 18 18.75c.966 0 1.89.166 2.75.47a.75.75 0 0 0 1-.708V4.262a.75.75 0 0 0-.5-.707A9.735 9.735 0 0 0 18 3a9.707 9.707 0 0 0-5.25 1.533v16.103Z" />
                </svg>
                General Knowledge Quiz
            </h1>
            <p class="text-lg sm:text-xl sm-subtitle-sm">__QCOUNT__ GK questions &mdash; pick a topic, a subtopic, and how many questions you want.</p>
        </div>
    </section>

    <!-- Quiz Section -->
    <section class="py-12 px-4 sm:px-6 lg:px-8 bg-slate-50">
        <div class="container mx-auto max-w-3xl">

            <div id="setup-view" class="sm-card p-8 space-y-5">
                <div>
                    <label class="block text-sm text-slate-400 mb-1">Topic</label>
                    <select id="topic-select" class="sm-select w-full rounded-lg px-3 py-2"></select>
                </div>
                <div>
                    <label class="block text-sm text-slate-400 mb-1">Subtopic</label>
                    <select id="subtopic-select" class="sm-select w-full rounded-lg px-3 py-2"></select>
                </div>
                <div>
                    <label class="block text-sm text-slate-400 mb-1">Number of questions</label>
                    <select id="count-select" class="sm-select w-full rounded-lg px-3 py-2"></select>
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
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm text-slate-400 mb-1">Overall time limit (minutes)</label>
                        <input type="number" min="0" id="overall-limit-input" class="sm-input w-full rounded-lg px-3 py-2" placeholder="No limit">
                    </div>
                    <div>
                        <label class="block text-sm text-slate-400 mb-1">Per-question time limit (seconds)</label>
                        <input type="number" min="0" id="perq-limit-input" class="sm-input w-full rounded-lg px-3 py-2" placeholder="No limit">
                    </div>
                </div>
                <button id="start-btn" class="sm-btn sm-btn-primary w-full justify-center">Start Quiz</button>
            </div>

            <div id="quiz-view" class="hidden">
                <div class="flex items-center justify-between text-sm mb-1" style="color:var(--sm-muted)">
                    <span id="progress-label">Question 1 / 10</span>
                    <span class="flex items-center gap-4">
                        <span id="score-label">Score: 0</span>
                        <button id="end-quiz-btn" class="text-xs underline" style="color:var(--sm-muted)">End Quiz</button>
                    </span>
                </div>
                <div class="flex items-center justify-between text-xs mb-2" style="color:var(--sm-muted)">
                    <span id="overall-timer-label"></span>
                    <span id="perq-timer-label"></span>
                </div>
                <div class="h-1.5 rounded-full bg-white/10 overflow-hidden mb-6">
                    <div id="progress-bar" class="progress-bar-fill h-full bg-gradient-to-r from-[#00e5ff] via-[#a855f7] to-[#ff2fb4]" style="width:0%"></div>
                </div>
                <div class="sm-card p-8">
                    <div id="q-meta" class="text-xs uppercase tracking-wide mb-3" style="color:var(--sm-cyan)"></div>
                    <div id="q-text" class="text-lg font-semibold mb-5 leading-relaxed"></div>

                    <div id="q-reveal-row" class="mb-2 flex gap-3">
                        <button id="reveal-btn" class="sm-btn sm-btn-ghost">Show Answer</button>
                        <button id="skip-btn-immediate" class="sm-btn sm-btn-ghost">Skip</button>
                    </div>

                    <div id="q-answer-box" class="hidden mt-2 mb-4 rounded-lg p-4" style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08)">
                        <div class="text-xs uppercase tracking-wide mb-1" style="color:var(--sm-muted)">Answer</div>
                        <div id="q-answer-text" class="font-medium"></div>
                    </div>

                    <div id="q-selfmark-row" class="hidden flex gap-3 mb-2">
                        <button data-verdict="correct" class="mark-btn sm-btn sm-btn-ghost">I got it right</button>
                        <button data-verdict="wrong" class="mark-btn sm-btn sm-btn-ghost">I missed it</button>
                    </div>

                    <div class="mt-6 flex justify-between items-center">
                        <button id="skip-btn-end" class="hidden sm-btn sm-btn-ghost">Skip</button>
                        <button id="next-btn" class="hidden sm-btn sm-btn-primary ml-auto">Next</button>
                    </div>
                </div>
            </div>

            <div id="summary-view" class="hidden sm-card p-8 text-center">
                <div class="text-4xl mb-2">\U0001F389</div>
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
<script src="../starfield.js"></script>

<script>
const QUESTIONS = __QUESTIONS_JSON__;
const OUTLINE = __OUTLINE_JSON__;

const topicSelect = document.getElementById('topic-select');
const subtopicSelect = document.getElementById('subtopic-select');
const countSelect = document.getElementById('count-select');

function populateTopics() {
  const allOpt = document.createElement('option');
  allOpt.value = '__ALL__';
  allOpt.textContent = 'All Topics';
  topicSelect.appendChild(allOpt);
  Object.keys(OUTLINE).sort().forEach(t => {
    const opt = document.createElement('option');
    opt.value = t;
    opt.textContent = t;
    topicSelect.appendChild(opt);
  });
}

function populateSubtopics() {
  subtopicSelect.innerHTML = '';
  const allOpt = document.createElement('option');
  allOpt.value = '__ALL__';
  allOpt.textContent = 'All Subtopics';
  subtopicSelect.appendChild(allOpt);
  const tp = topicSelect.value;
  let subtopics = new Set();
  if (tp === '__ALL__') {
    Object.values(OUTLINE).forEach(s => Object.keys(s).forEach(x => subtopics.add(x)));
  } else if (OUTLINE[tp]) {
    Object.keys(OUTLINE[tp]).forEach(x => subtopics.add(x));
  }
  [...subtopics].sort().forEach(s => {
    const opt = document.createElement('option');
    opt.value = s;
    opt.textContent = s;
    subtopicSelect.appendChild(opt);
  });
  subtopicSelect.disabled = subtopics.size === 0;
}

function filteredQuestions() {
  const tp = topicSelect.value;
  const sub = subtopicSelect.value;
  return QUESTIONS.filter(q => (tp === '__ALL__' || q.topic === tp) && (sub === '__ALL__' || q.subtopic === sub));
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

topicSelect.addEventListener('change', () => { populateSubtopics(); populateCounts(); });
subtopicSelect.addEventListener('change', populateCounts);

populateTopics();
populateSubtopics();
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
let tickHandle = null;

function fmtTime(sec) {
  sec = Math.max(0, Math.round(sec));
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${m}:${String(s).padStart(2, '0')}`;
}

function startTicker() {
  stopTicker();
  tickHandle = setInterval(tick, 250);
  tick();
}

function stopTicker() {
  if (tickHandle) { clearInterval(tickHandle); tickHandle = null; }
}

function tick() {
  if (!state || !state.current) return;
  const overallElapsed = (Date.now() - state.startTs) / 1000;
  const qElapsed = (Date.now() - state.qStartTs) / 1000;

  document.getElementById('overall-timer-label').textContent = state.overallLimitSec
    ? `Overall: ${fmtTime(overallElapsed)} / ${fmtTime(state.overallLimitSec)}`
    : `Overall: ${fmtTime(overallElapsed)}`;
  document.getElementById('perq-timer-label').textContent = state.perqLimitSec
    ? `This question: ${fmtTime(qElapsed)} / ${fmtTime(state.perqLimitSec)}`
    : `This question: ${fmtTime(qElapsed)}`;

  if (state.overallLimitSec && overallElapsed >= state.overallLimitSec) {
    endQuizNow();
    return;
  }
  if (state.perqLimitSec && qElapsed >= state.perqLimitSec) {
    // Hard timeout: unlike a manual Skip, this is final -- scored 0, no requeue.
    const item = state.current;
    state.current = null;
    state.finalized.push({ q: item.q, correct: false });
    nextQuestion();
  }
}

document.getElementById('start-btn').addEventListener('click', () => {
  const n = parseInt(countSelect.value, 10);
  if (!n) return;
  const pool = filteredQuestions();
  const picked = shuffle(pool).slice(0, n);
  const revealMode = document.querySelector('input[name="reveal-mode"]:checked').value;
  const overallLimitMin = parseFloat(document.getElementById('overall-limit-input').value);
  const perqLimitSecVal = parseFloat(document.getElementById('perq-limit-input').value);
  state = {
    total: picked.length,
    queue: picked.map(q => ({ q, skippedOnce: false })),
    finalized: [],
    revealMode,
    score: 0,
    current: null,
    overallLimitSec: overallLimitMin > 0 ? overallLimitMin * 60 : 0,
    perqLimitSec: perqLimitSecVal > 0 ? perqLimitSecVal : 0,
    startTs: Date.now(),
    qStartTs: null,
  };
  document.getElementById('setup-view').classList.add('hidden');
  document.getElementById('summary-view').classList.add('hidden');
  document.getElementById('quiz-view').classList.remove('hidden');
  startTicker();
  nextQuestion();
});

function nextQuestion() {
  if (state.queue.length === 0) {
    showSummary();
    return;
  }
  state.current = state.queue.shift();
  state.qStartTs = Date.now();
  renderQuestion();
}

// A voluntary Skip requeues the question once so it can come back later in
// the same run; skipping that same question a second time finalizes it as
// missed instead of requeuing forever.
function doSkip() {
  const item = state.current;
  state.current = null;
  if (item.skippedOnce) {
    state.finalized.push({ q: item.q, correct: false });
  } else {
    item.skippedOnce = true;
    state.queue.push(item);
  }
  nextQuestion();
}

function renderQuestion() {
  const q = state.current.q;
  document.getElementById('progress-label').textContent = `Question ${state.finalized.length + 1} / ${state.total}`;
  document.getElementById('score-label').textContent = `Score: ${state.score}`;
  document.getElementById('progress-bar').style.width = `${(state.finalized.length / state.total) * 100}%`;

  const metaBits = [q.topic];
  if (q.subtopic) metaBits.push(q.subtopic);
  document.getElementById('q-meta').textContent = metaBits.join(' • ');
  document.getElementById('q-text').innerHTML = q.question_html;

  const answerBox = document.getElementById('q-answer-box');
  const answerText = document.getElementById('q-answer-text');
  const revealRow = document.getElementById('q-reveal-row');
  const selfMarkRow = document.getElementById('q-selfmark-row');
  const nextBtn = document.getElementById('next-btn');
  const skipBtnEnd = document.getElementById('skip-btn-end');

  answerBox.classList.add('hidden');
  answerText.innerHTML = '';
  selfMarkRow.classList.add('hidden');
  [...selfMarkRow.children].forEach(b => b.classList.remove('chosen-correct', 'chosen-wrong'));
  nextBtn.classList.add('hidden');

  let marked = false;

  if (state.revealMode === 'end') {
    revealRow.classList.add('hidden');
    skipBtnEnd.classList.remove('hidden');
    nextBtn.classList.remove('hidden');
  } else {
    revealRow.classList.remove('hidden');
    skipBtnEnd.classList.add('hidden');
    document.getElementById('reveal-btn').onclick = () => {
      answerText.innerHTML = q.answer_html;
      answerBox.classList.remove('hidden');
      revealRow.classList.add('hidden');
      selfMarkRow.classList.remove('hidden');
    };
    document.getElementById('skip-btn-immediate').onclick = doSkip;
  }

  skipBtnEnd.onclick = doSkip;

  [...selfMarkRow.children].forEach(btn => {
    btn.onclick = () => {
      if (marked) return;
      marked = true;
      const correct = btn.dataset.verdict === 'correct';
      if (correct) state.score++;
      state.finalized.push({ q, correct });
      btn.classList.add(correct ? 'chosen-correct' : 'chosen-wrong');
      document.getElementById('score-label').textContent = `Score: ${state.score}`;
      nextBtn.classList.remove('hidden');
    };
  });

  nextBtn.onclick = () => {
    if (state.revealMode === 'end') {
      state.finalized.push({ q, correct: null });
    }
    state.current = null;
    nextQuestion();
  };
}

function showSummary() {
  stopTicker();
  document.getElementById('quiz-view').classList.add('hidden');
  document.getElementById('summary-view').classList.remove('hidden');

  const listEl = document.getElementById('summary-list');
  listEl.innerHTML = '';

  if (state.revealMode === 'end') {
    document.getElementById('summary-score').textContent =
      `Here are all ${state.finalized.length} questions and answers -- mark yourself below.`;
    state.finalized.forEach((a, i) => {
      const div = document.createElement('div');
      div.className = 'rounded-lg p-4';
      div.style.background = 'rgba(255,255,255,0.02)';
      div.style.border = '1px solid rgba(255,255,255,0.08)';
      div.innerHTML = `
        <div class="text-sm mb-1" style="color:var(--sm-muted)">Q${i + 1} &middot; ${a.q.topic}${a.q.subtopic ? ' &middot; ' + a.q.subtopic : ''}</div>
        <div class="font-medium mb-2">${a.q.question_html}</div>
        <div class="text-sm text-green-300 mb-3">Answer: ${a.q.answer_html}</div>
        <div class="flex gap-3">
          <button data-verdict="correct" class="mark-btn sm-btn sm-btn-ghost text-sm">I got it right</button>
          <button data-verdict="wrong" class="mark-btn sm-btn sm-btn-ghost text-sm">I missed it</button>
        </div>
      `;
      const btns = div.querySelectorAll('.mark-btn');
      btns.forEach(btn => {
        btn.addEventListener('click', () => {
          if (a.correct !== null) { state.score--; }
          a.correct = btn.dataset.verdict === 'correct';
          if (a.correct) state.score++;
          btns.forEach(b => b.classList.remove('chosen-correct', 'chosen-wrong'));
          btn.classList.add(a.correct ? 'chosen-correct' : 'chosen-wrong');
          updateEndScore();
        });
      });
      listEl.appendChild(div);
    });
    updateEndScore();
  } else {
    updateImmediateScore();
    state.finalized.forEach((a, i) => {
      const div = document.createElement('div');
      div.className = 'rounded-lg p-4';
      div.style.background = 'rgba(255,255,255,0.02)';
      div.style.border = '1px solid rgba(255,255,255,0.08)';
      div.innerHTML = `
        <div class="text-sm mb-1" style="color:var(--sm-muted)">Q${i + 1} &middot; ${a.correct ? '<span class="text-green-400">Correct</span>' : '<span class="text-red-400">Missed</span>'}</div>
        <div class="font-medium mb-2">${a.q.question_html}</div>
        <div class="text-sm text-green-300">Answer: ${a.q.answer_html}</div>
      `;
      listEl.appendChild(div);
    });
  }
}

function updateEndScore() {
  const marked = state.finalized.filter(a => a.correct !== null);
  const score = marked.filter(a => a.correct).length;
  document.getElementById('summary-score').textContent =
    marked.length === state.finalized.length
      ? `You scored ${score} / ${state.finalized.length}.`
      : `Scored so far: ${score} / ${marked.length} marked (${state.finalized.length} total).`;
}

function updateImmediateScore() {
  document.getElementById('summary-score').textContent =
    `You scored ${state.score} / ${state.finalized.length}.`;
}

document.getElementById('restart-btn').addEventListener('click', () => {
  stopTicker();
  document.getElementById('summary-view').classList.add('hidden');
  document.getElementById('setup-view').classList.remove('hidden');
});

function endQuizNow() {
  if (!state) return;
  stopTicker();
  if (state.revealMode === 'end' && state.current) {
    state.finalized.push({ q: state.current.q, correct: null });
    state.current = null;
  }
  if (state.finalized.length === 0) {
    document.getElementById('quiz-view').classList.add('hidden');
    document.getElementById('setup-view').classList.remove('hidden');
    state = null;
    return;
  }
  showSummary();
}

document.getElementById('end-quiz-btn').addEventListener('click', endQuizNow);
</script>
</body>
</html>
"""


def main():
    questions = load_questions()
    print(f"{SRC_CSV.name}: parsed {len(questions)} questions")

    outline = build_outline(questions)
    for topic, subtopics in sorted(outline.items()):
        extra = f" ({len(subtopics)} subtopics)" if subtopics else ""
        print(f"  {topic}{extra}")

    html = HTML_TEMPLATE
    html = html.replace("__QCOUNT__", str(len(questions)))
    html = html.replace("__QUESTIONS_JSON__", json.dumps(questions, ensure_ascii=False))
    html = html.replace("__OUTLINE_JSON__", json.dumps(outline, ensure_ascii=False))

    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT_HTML} ({OUT_HTML.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
