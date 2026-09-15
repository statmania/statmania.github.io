#!/usr/bin/env python3
"""
Reads puzzles.json (built by build_sudoku.py) from this folder and
writes a single self-contained games/sudoku.html to the parent folder.
"""
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent      # sudoku/
PARENT_DIR = SCRIPT_DIR.parent                    # games/
PUZZLES_PATH = SCRIPT_DIR / "puzzles.json"
HTML_PATH = PARENT_DIR / "sudoku.html"

print(f"📖 Reading : {PUZZLES_PATH}")
print(f"📤 Writing : {HTML_PATH}")

if not PUZZLES_PATH.exists():
    raise SystemExit(f"❌ File not found: {PUZZLES_PATH} — run build_sudoku.py first")

puzzles = json.loads(PUZZLES_PATH.read_text())
puzzles_json = json.dumps(puzzles, separators=(",", ":"))
print(f"   {len(puzzles)} puzzles embedded")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Stat Mania - Mini Sudoku</title>
<!-- Tailwind CSS CDN -->
<script src="https://cdn.tailwindcss.com"></script>
<!-- Google Fonts - Inter -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/dark-theme.css">
<style>
  :root {
    --card: rgba(255,255,255,0.045); --ink: #e8ecf7; --muted: #9aa4c2;
    --line: rgba(255,255,255,0.14); --accent: #00e5ff; --accent-dark: #0e7490;
    --good: #4ade80; --bad: #ff6b6b;
  }
  body { font-family: 'Inter', sans-serif; }
  ::-webkit-scrollbar { width: 8px; height: 8px; }
  ::-webkit-scrollbar-track { background: #0a0f1e; border-radius: 10px; }
  ::-webkit-scrollbar-thumb { background: #3a4a6b; border-radius: 10px; }
  ::-webkit-scrollbar-thumb:hover { background: #54688f; }

  .toolbar { display: flex; flex-wrap: wrap; gap: 12px; align-items: center;
             justify-content: space-between; margin-bottom: 20px; }
  .toolbar-left { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
  .toolbar-right { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
  select { background: rgba(255,255,255,0.04); color: var(--ink);
           border: 1px solid rgba(255,255,255,0.18); border-radius: 999px;
           padding: 6px 14px; font-size: 0.85rem; font-weight: 600;
           font-family: inherit; cursor: pointer; }
  select:hover { border-color: var(--accent); }
  select option { background: #0a0f1e; color: var(--ink); }
  button.action { border: none; background: linear-gradient(90deg, var(--accent), #38bdf8);
           color: #04101c; padding: 8px 14px; border-radius: 999px; font-size: 0.85rem;
           font-weight: 700; cursor: pointer; transition: transform 0.15s, box-shadow 0.15s;
           font-family: inherit; box-shadow: 0 0 20px rgba(0,229,255,0.3); }
  button.action:hover { transform: translateY(-2px); box-shadow: 0 0 30px rgba(0,229,255,0.5); }
  button.action:active { transform: scale(0.97); }
  button.action.ghost { background: rgba(255,255,255,0.04); color: var(--ink);
           border: 1px solid rgba(255,255,255,0.18); box-shadow: none; }
  button.action.ghost:hover { border-color: var(--accent); box-shadow: 0 0 20px rgba(0,229,255,0.25); }

  .meta-row { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center;
              align-items: center; margin-bottom: 18px; }
  .badge { display: inline-block; font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
           letter-spacing: 0.06em; padding: 3px 10px; border-radius: 999px; border: 1px solid; }
  .badge.easy { color: #4ade80; border-color: rgba(74,222,128,0.4); background: rgba(74,222,128,0.12); }
  .badge.medium { color: #fbbf24; border-color: rgba(251,191,36,0.4); background: rgba(251,191,36,0.12); }
  .badge.hard { color: #ff6b6b; border-color: rgba(255,107,107,0.4); background: rgba(255,107,107,0.12); }
  .badge.size { color: var(--accent); border-color: rgba(0,229,255,0.4); background: rgba(0,229,255,0.12); }
  #puzzle-name { font-size: 1.2rem; font-weight: 800;
                 background: linear-gradient(90deg, var(--sm-cyan,#00e5ff), var(--sm-purple,#a855f7), var(--sm-pink,#ff2fb4));
                 -webkit-background-clip: text; background-clip: text; color: transparent; }
  #timer { font-family: 'Courier New', monospace; color: var(--muted); font-size: 0.9rem; }

  .game-layout { display: grid; grid-template-columns: auto 1fr; gap: 24px;
                 align-items: start; margin-bottom: 20px; }
  @media (max-width: 800px) { .game-layout { grid-template-columns: 1fr; } }

  .board-wrap { background: var(--card); border: 1px solid rgba(255,255,255,0.08);
                border-radius: 14px; padding: 16px; display: flex;
                justify-content: center; overflow: auto; }
  .sboard { display: grid; gap: 1px; background: rgba(255,255,255,0.14); border-radius: 6px;
            padding: 1px; width: max-content; }
  .scell { width: 46px; height: 46px; background: rgba(255,255,255,0.04); position: relative; }
  .scell input { width: 100%; height: 100%; border: none; background: transparent;
                 text-align: center; font-size: 1.2rem; font-weight: 700;
                 color: var(--ink); font-family: 'Courier New', monospace; outline: none;
                 padding: 0; caret-color: transparent; }
  .scell.given { background: rgba(255,255,255,0.09); }
  .scell.given input { color: var(--accent); font-weight: 800; }
  .scell.correct input { color: var(--good); }
  .scell.wrong input { color: var(--bad); }
  .scell.wrong { background: rgba(255,107,107,0.18); }
  .scell.box-right { border-right: 2px solid rgba(255,255,255,0.5); }
  .scell.box-bottom { border-bottom: 2px solid rgba(255,255,255,0.5); }

  #win-banner { max-width: 1100px; margin: 0 auto 20px; padding: 14px 24px; border-radius: 12px;
                text-align: center; font-weight: 700; font-size: 1.05rem; display: none;
                background: linear-gradient(135deg, #22c55e, #16a34a); color: white;
                box-shadow: 0 6px 20px rgba(34,197,94,0.35); animation: pop 0.4s ease; }
  @keyframes pop { 0% { transform: scale(0.9); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }

  .rules-panel { background: var(--card); border: 1px solid rgba(255,255,255,0.08);
                 border-radius: 14px; padding: 20px 22px; }
  .rules-panel h3 { font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.06em;
                     color: var(--accent); margin: 0 0 14px; }
  .rules-panel ul { margin: 0; padding-left: 1.3em; display: flex; flex-direction: column; gap: 12px; }
  .rules-panel li { font-size: 1.05rem; line-height: 1.5; color: var(--ink); }
  .rules-panel em { color: var(--accent); font-style: normal; font-weight: 700; }
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
                    <li><a href="index.html" class="text-slate-600 hover:text-indigo-600 transition duration-300">All Games</a></li>
                    <li><a href="#cta" class="text-slate-600 hover:text-indigo-600 transition duration-300">Contact</a></li>
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
            <a href="index.html" class="block px-3 py-2 rounded-md text-base font-medium text-slate-700 hover:bg-slate-100 hover:text-indigo-600">All Games</a>
            <a href="#cta" class="block px-3 py-2 rounded-md text-base font-medium text-slate-700 hover:bg-slate-100 hover:text-indigo-600">Contact</a>
        </div>
    </header>

    <main class="flex-grow">
        <!-- Hero Section -->
        <section class="sm-hero-wrap">
            <canvas class="sm-canvas" aria-hidden="true"></canvas>
            <div class="sm-hero-inner">
                <span class="sm-eyebrow">Stat Mania &middot; Games</span>
                <h1 class="text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-tight mb-4 flex items-center justify-center gap-4 sm-gradient-text">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-12 h-12 sm-hero-icon">
                        <path fill-rule="evenodd" d="M3.375 3C2.339 3 1.5 3.84 1.5 4.875v14.25C1.5 20.16 2.34 21 3.375 21h17.25c1.035 0 1.875-.84 1.875-1.875V4.875C22.5 3.839 21.66 3 20.625 3H3.375ZM6 6.75A.75.75 0 0 1 6.75 6h1.5a.75.75 0 0 1 0 1.5h-1.5A.75.75 0 0 1 6 6.75Zm5.25 0a.75.75 0 0 1 .75-.75h1.5a.75.75 0 0 1 0 1.5h-1.5a.75.75 0 0 1-.75-.75ZM17.25 6a.75.75 0 0 0 0 1.5h.75a.75.75 0 0 0 0-1.5h-.75ZM6 11.25a.75.75 0 0 1 .75-.75h1.5a.75.75 0 0 1 0 1.5h-1.5a.75.75 0 0 1-.75-.75Zm6-.75a.75.75 0 0 0 0 1.5h.75a.75.75 0 0 0 0-1.5h-.75Zm4.5.75a.75.75 0 0 1 .75-.75h.75a.75.75 0 0 1 0 1.5H17.25a.75.75 0 0 1-.75-.75ZM6.75 15a.75.75 0 0 0 0 1.5h.75a.75.75 0 0 0 0-1.5h-.75ZM11.25 15.75a.75.75 0 0 1 .75-.75h1.5a.75.75 0 0 1 0 1.5h-1.5a.75.75 0 0 1-.75-.75ZM17.25 15a.75.75 0 0 0 0 1.5h.75a.75.75 0 0 0 0-1.5h-.75Z" clip-rule="evenodd" />
                    </svg>
                    Mini Sudoku
                </h1>
                <p class="text-lg sm:text-xl sm-subtitle-sm">4&times;4, 6&times;6, and 6&times;4 logic puzzles &mdash; no two of a kind in any row, column, or box</p>
            </div>
        </section>

        <!-- Game Section -->
        <section class="py-12 px-4 sm:px-6 lg:px-8 bg-slate-50">
            <div class="container mx-auto max-w-3xl">
                <div class="sm-card p-8">
                    <div class="toolbar">
                        <div class="toolbar-left">
                            <select id="puzzle-select" aria-label="Choose a puzzle"></select>
                        </div>
                        <div class="toolbar-right">
                            <button id="check-btn" class="action ghost">✓ Check</button>
                            <button id="reveal-btn" class="action ghost">💡 Reveal</button>
                            <button id="clear-btn" class="action ghost">↺ Clear</button>
                        </div>
                    </div>

                    <div class="meta-row">
                        <span id="puzzle-name"></span>
                        <span class="badge size" id="badge-size"></span>
                        <span class="badge" id="badge-difficulty"></span>
                        <span id="timer">0:00</span>
                    </div>

                    <div id="win-banner">🎉 Solved! Nice work.</div>

                    <div class="game-layout">
                        <div class="board-wrap">
                            <div class="sboard" id="board"></div>
                        </div>
                        <div class="rules-panel">
                            <h3>Rules</h3>
                            <ul>
                                <li>Every <em>row</em> uses each number exactly once.</li>
                                <li>Every <em>box</em> uses each number exactly once.</li>
                                <li>A <em>column</em> never repeats a number either.</li>
                                <li>On rectangular boards, a column just won't contain <em>every</em> number &mdash; it's shorter than the digit range.</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Call to Action Section -->
        <section id="cta" class="sm-section-dark py-16 px-4 sm:px-6 lg:px-8 text-center">
            <div class="container mx-auto max-w-3xl">
                <h2 class="text-3xl sm:text-4xl font-bold mb-6" style="color:#fff">Explore Other Games</h2>
                <p class="text-lg sm:text-xl mb-8 sm-subtitle-sm">Check out all available games</p>
                <div class="flex flex-col sm:flex-row justify-center gap-4">
                    <a href="index.html" class="sm-btn sm-btn-primary">All Games</a>
                    <a href="#" class="sm-btn sm-btn-ghost">Back to Top</a>
                </div>
            </div>
        </section>
    </main>

    <!-- Footer -->
    <footer class="bg-slate-800 text-white py-8 px-4 sm:px-6 lg:px-8 text-center mt-auto" style="border-top:1px solid rgba(255,255,255,0.08)">
        <div class="container mx-auto">
            <p class="mb-4">&copy; <span id="copyright-year">2026</span> Stat Mania. All rights reserved.</p>
            <div class="flex justify-center space-x-6">
                <a href="#" class="text-slate-300 hover:text-white transition duration-300">Privacy Policy</a>
                <a href="#" class="text-slate-300 hover:text-white transition duration-300">Terms of Service</a>
                <a href="#" class="text-slate-300 hover:text-white transition duration-300">Sitemap</a>
            </div>
        </div>
    </footer>

    <script>document.getElementById("copyright-year").textContent = new Date().getFullYear();</script>

    <script>
        const mobileMenuButton = document.getElementById('mobile-menu-button');
        const mobileMenu = document.getElementById('mobile-menu');
        mobileMenuButton.addEventListener('click', () => mobileMenu.classList.toggle('hidden'));
        mobileMenu.querySelectorAll('a').forEach(link => link.addEventListener('click', () => mobileMenu.classList.add('hidden')));
    </script>
    <script src="js/starfield.js"></script>

<script>
/* ============================================================
   PUZZLE DATA (embedded)
   ============================================================ */
const PUZZLES = __PUZZLES__;

/* ============================================================
   STATE
   ============================================================ */
let state = null;
let timerInterval = null;

function loadPuzzle(p) {
  clearInterval(timerInterval);
  state = {
    puzzle: p,
    grid: p.puzzle.map(row => row.slice()),
    startedAt: Date.now(),
    solved: false,
  };
  document.getElementById("puzzle-select").value = String(PUZZLES.indexOf(p));
  document.getElementById("puzzle-name").textContent = p.name;
  document.getElementById("badge-size").textContent = p.label;
  const diffBadge = document.getElementById("badge-difficulty");
  diffBadge.textContent = p.difficulty;
  diffBadge.className = "badge " + p.difficulty;
  document.getElementById("win-banner").style.display = "none";
  renderBoard();
  timerInterval = setInterval(updateTimer, 1000);
  updateTimer();
}

function updateTimer() {
  if (!state || state.solved) return;
  const secs = Math.floor((Date.now() - state.startedAt) / 1000);
  const m = Math.floor(secs / 60), s = secs % 60;
  document.getElementById("timer").textContent = `${m}:${String(s).padStart(2, "0")}`;
}

function renderBoard() {
  const { rows, cols, boxH, boxW } = state.puzzle;
  const el = document.getElementById("board");
  el.style.gridTemplateColumns = `repeat(${cols}, 46px)`;
  el.innerHTML = "";
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const div = document.createElement("div");
      div.className = "scell";
      if ((c + 1) % boxW === 0 && c !== cols - 1) div.classList.add("box-right");
      if ((r + 1) % boxH === 0 && r !== rows - 1) div.classList.add("box-bottom");

      const given = state.puzzle.puzzle[r][c] !== 0;
      const input = document.createElement("input");
      input.maxLength = 1;
      input.inputMode = "numeric";
      input.autocomplete = "off";
      input.spellcheck = false;

      if (given) {
        div.classList.add("given");
        input.value = state.puzzle.puzzle[r][c];
        input.readOnly = true;
        input.tabIndex = -1;
      } else {
        const v = state.grid[r][c];
        input.value = v ? v : "";
        // With maxLength=1, once a cell already holds a digit the browser
        // won't insert a new keystroke unless the existing text is
        // selected first - select on focus so typing always overwrites
        // instead of silently doing nothing.
        input.addEventListener("focus", () => input.select());
        input.addEventListener("keydown", (e) => onKeyDown(e, r, c));
        input.addEventListener("input", (e) => onInput(e, r, c));
      }
      div.dataset.r = r;
      div.dataset.c = c;
      div.appendChild(input);
      el.appendChild(div);
    }
  }
}

function setCell(r, c, val) {
  const digits = state.puzzle.digits;
  if (val !== 0 && (val < 1 || val > digits)) return;
  state.grid[r][c] = val;
  const div = document.querySelector(`.scell[data-r="${r}"][data-c="${c}"]`);
  div.classList.remove("correct", "wrong");
  const input = div.querySelector("input");
  input.value = val ? val : "";
}

function onInput(e, r, c) {
  const raw = e.target.value.replace(/[^0-9]/g, "").slice(-1);
  const val = raw ? parseInt(raw, 10) : 0;
  setCell(r, c, val);
  if (val) focusNext(r, c);
  maybeCheckWin();
}

function onKeyDown(e, r, c) {
  if (e.key === "Backspace" || e.key === "Delete") {
    e.preventDefault();
    setCell(r, c, 0);
    return;
  }
  const { rows, cols } = state.puzzle;
  const deltas = { ArrowLeft: [0, -1], ArrowRight: [0, 1], ArrowUp: [-1, 0], ArrowDown: [1, 0] };
  if (deltas[e.key]) {
    e.preventDefault();
    let [dr, dc] = deltas[e.key];
    let nr = r + dr, nc = c + dc;
    if (nr >= 0 && nr < rows && nc >= 0 && nc < cols) focusCell(nr, nc);
  }
}

function focusCell(r, c) {
  const input = document.querySelector(`.scell[data-r="${r}"][data-c="${c}"] input`);
  if (input && !input.readOnly) input.focus();
}

function focusNext(r, c) {
  const { rows, cols } = state.puzzle;
  let nr = r, nc = c + 1;
  if (nc >= cols) { nc = 0; nr++; }
  while (nr < rows) {
    if (state.puzzle.puzzle[nr][nc] === 0) { focusCell(nr, nc); return; }
    nc++;
    if (nc >= cols) { nc = 0; nr++; }
  }
}

function checkAnswers() {
  const { rows, cols } = state.puzzle;
  const sol = state.puzzle.solution;
  let allCorrect = true;
  let allFilled = true;
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (state.puzzle.puzzle[r][c] !== 0) continue;
      const div = document.querySelector(`.scell[data-r="${r}"][data-c="${c}"]`);
      div.classList.remove("correct", "wrong");
      const v = state.grid[r][c];
      if (!v) { allFilled = false; continue; }
      if (v === sol[r][c]) div.classList.add("correct");
      else { div.classList.add("wrong"); allCorrect = false; }
    }
  }
  if (allFilled && allCorrect) showWin();
  return allFilled && allCorrect;
}

function maybeCheckWin() {
  const { rows, cols } = state.puzzle;
  const sol = state.puzzle.solution;
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (state.grid[r][c] !== sol[r][c]) return;
    }
  }
  showWin();
}

function showWin() {
  if (state.solved) return;
  state.solved = true;
  clearInterval(timerInterval);
  document.getElementById("win-banner").style.display = "block";
}

function revealSolution() {
  const { rows, cols } = state.puzzle;
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      setCell(r, c, state.puzzle.solution[r][c]);
    }
  }
  showWin();
}

function clearBoard() {
  const { rows, cols } = state.puzzle;
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (state.puzzle.puzzle[r][c] === 0) setCell(r, c, 0);
    }
  }
  document.getElementById("win-banner").style.display = "none";
}

/* ============================================================
   WIRE UP
   ============================================================ */
function populatePuzzleSelect() {
  const select = document.getElementById("puzzle-select");
  select.innerHTML = PUZZLES.map((p, i) =>
    `<option value="${i}">${p.label} · ${p.difficulty} · ${p.name}</option>`).join("");
}

document.getElementById("puzzle-select").addEventListener("change", (e) => {
  loadPuzzle(PUZZLES[parseInt(e.target.value, 10)]);
});
document.getElementById("check-btn").addEventListener("click", checkAnswers);
document.getElementById("reveal-btn").addEventListener("click", revealSolution);
document.getElementById("clear-btn").addEventListener("click", clearBoard);

populatePuzzleSelect();
loadPuzzle(PUZZLES[0]);
</script>
</body>
</html>
"""

html = HTML_TEMPLATE.replace("__PUZZLES__", puzzles_json)
HTML_PATH.write_text(html, encoding="utf-8")
print(f"✅ Wrote self-contained HTML → {HTML_PATH}")
