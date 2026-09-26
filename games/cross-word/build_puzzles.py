#!/usr/bin/env python3
"""
Reads cw.xlsx (sheets: 'puzzles' and 'words') from this folder and writes
a single self-contained cross-word.html to the PARENT folder.
"""

import json
from pathlib import Path
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent     # cross-word/
PARENT_DIR = SCRIPT_DIR.parent                   # parent/
XLSX_PATH  = SCRIPT_DIR / "cw.xlsx"
HTML_PATH  = PARENT_DIR / "cross-word.html"

print(f"📖 Reading : {XLSX_PATH}")
print(f"📤 Writing : {HTML_PATH}")

if not XLSX_PATH.exists():
    raise SystemExit(f"❌ File not found: {XLSX_PATH}")

# ------------------------------------------------------------------
# Load workbook
# ------------------------------------------------------------------
puzzles_df = pd.read_excel(XLSX_PATH, sheet_name="puzzles")
words_df   = pd.read_excel(XLSX_PATH, sheet_name="words")

puzzles_df.columns = [c.strip().lower() for c in puzzles_df.columns]
words_df.columns   = [c.strip().lower() for c in words_df.columns]

puzzles_df["name"] = puzzles_df["name"].astype(str).str.strip()
if "difficulty" in puzzles_df.columns:
    puzzles_df["difficulty"] = puzzles_df["difficulty"].astype(str).str.strip()
else:
    puzzles_df["difficulty"] = "medium"

for col in ["answer", "dir", "clue"]:
    words_df[col] = words_df[col].astype(str).str.strip()
words_df["dir"] = words_df["dir"].str.lower()

# ------------------------------------------------------------------
# Build nested puzzle list
# ------------------------------------------------------------------
puzzles = []
for _, p in puzzles_df.iterrows():
    pid = int(p["puzzle_id"])
    words = [
        {
            "answer": w["answer"].upper(),
            "row":    int(w["row"]),
            "col":    int(w["col"]),
            "dir":    w["dir"],
            "clue":   w["clue"],
        }
        for _, w in words_df[words_df["puzzle_id"] == pid].iterrows()
    ]
    puzzles.append({
        "name":       p["name"],
        "difficulty": p["difficulty"],
        "words":      words,
    })

# ------------------------------------------------------------------
# Validate crossings
# ------------------------------------------------------------------
errors = 0
for pz in puzzles:
    cell_map = {}
    for w in pz["words"]:
        for i, ch in enumerate(w["answer"]):
            r = w["row"] + (i if w["dir"] == "down" else 0)
            c = w["col"] + (i if w["dir"] == "across" else 0)
            key = (r, c)
            if key in cell_map and cell_map[key] != ch:
                print(f"❌ [{pz['name']}] conflict at {key}: "
                      f"{cell_map[key]} vs {ch} (from '{w['answer']}')")
                errors += 1
            cell_map[key] = ch

if errors == 0:
    print("✅ Validation passed — all crossings match.")
else:
    print(f"⚠ {errors} conflict(s) — fix the spreadsheet and re-run.")

# ------------------------------------------------------------------
# Build the self-contained HTML
# ------------------------------------------------------------------
data_json = json.dumps(puzzles, ensure_ascii=False, indent=2)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Stat Mania - Crossword</title>
<!-- Tailwind CSS CDN -->
<script src="https://cdn.tailwindcss.com"></script>
<!-- Google Fonts - Inter -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/dark-theme.css">
<style>
  :root {
    --card: rgba(255,255,255,0.045); --ink: #e8ecf7; --muted: #9aa4c2;
    --line: rgba(255,255,255,0.14); --active-cell: rgba(0,229,255,0.22);
    --active-word: rgba(168,85,247,0.2); --correct: rgba(34,197,94,0.3);
    --wrong: rgba(255,45,57,0.3); --accent: #00e5ff; --accent-dark: #0e7490;
  }
  body { font-family: 'Inter', sans-serif; }
  ::-webkit-scrollbar { width: 8px; height: 8px; }
  ::-webkit-scrollbar-track { background: #0a0f1e; border-radius: 10px; }
  ::-webkit-scrollbar-thumb { background: #3a4a6b; border-radius: 10px; }
  ::-webkit-scrollbar-thumb:hover { background: #54688f; }

  .toolbar { display: flex; flex-wrap: wrap; gap: 12px; align-items: center;
             justify-content: space-between; margin-bottom: 24px; }
  .puzzle-picker { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; }
  .puzzle-name { font-size: 1.4rem; font-weight: 700; margin: 0;
                 background: linear-gradient(90deg, var(--sm-cyan, #00e5ff), var(--sm-purple, #a855f7), var(--sm-pink, #ff2fb4));
                 -webkit-background-clip: text; background-clip: text; color: transparent; }
  .difficulty-badge { display: inline-block; font-size: 0.7rem; font-weight: 700;
           text-transform: uppercase; letter-spacing: 0.06em; padding: 3px 10px;
           border-radius: 999px; border: 1px solid; }
  .difficulty-badge.easy { color: #4ade80; border-color: rgba(74,222,128,0.4); background: rgba(74,222,128,0.12); }
  .difficulty-badge.medium { color: #fbbf24; border-color: rgba(251,191,36,0.4); background: rgba(251,191,36,0.12); }
  .difficulty-badge.hard { color: #ff6b6b; border-color: rgba(255,107,107,0.4); background: rgba(255,107,107,0.12); }
  #puzzle-select { background: rgba(255,255,255,0.04); color: var(--ink);
           border: 1px solid rgba(255,255,255,0.18); border-radius: 999px;
           padding: 6px 14px; font-size: 0.85rem; font-weight: 600;
           font-family: inherit; cursor: pointer; }
  #puzzle-select:hover { border-color: var(--accent); }
  #puzzle-select:focus { outline: none; border-color: var(--accent);
           box-shadow: 0 0 0 3px rgba(0,229,255,0.25); }
  #puzzle-select option { background: #0a0f1e; color: var(--ink); }
  .controls { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }
  .controls button { border: none; background: linear-gradient(90deg, var(--accent), #38bdf8);
           color: #04101c; padding: 8px 14px; border-radius: 999px; font-size: 0.85rem;
           font-weight: 700; cursor: pointer; transition: transform 0.15s, box-shadow 0.15s;
           font-family: inherit; box-shadow: 0 0 20px rgba(0,229,255,0.3); }
  .controls button:hover { transform: translateY(-2px); box-shadow: 0 0 30px rgba(0,229,255,0.5); }
  .controls button:active { transform: scale(0.97); }
  .controls button.ghost { background: rgba(255,255,255,0.04); color: var(--ink);
           border: 1px solid rgba(255,255,255,0.18); box-shadow: none; }
  .controls button.ghost:hover { border-color: var(--accent); box-shadow: 0 0 20px rgba(0,229,255,0.25); }
  .cw-main { display: grid; grid-template-columns: auto 1fr; gap: 24px; align-items: start; }
  @media (max-width: 800px) { .cw-main { grid-template-columns: 1fr; } }
  .grid-wrap { background: var(--card); padding: 16px; border-radius: 14px;
               border: 1px solid rgba(255,255,255,0.08); display: flex; justify-content: center; }
  #grid { display: grid; gap: 2px; background: var(--line); padding: 2px; border-radius: 6px; }
  .cw-cell { width: 40px; height: 40px; background: rgba(255,255,255,0.06); position: relative; border-radius: 2px; }
  .cw-cell.blank { background: #05070d; border-radius: 0; }
  .cw-cell input { width: 100%; height: 100%; border: none; background: transparent;
                text-align: center; font-size: 1.25rem; font-weight: 700;
                text-transform: uppercase; color: var(--ink);
                font-family: 'Courier New', monospace; outline: none; padding: 0;
                caret-color: transparent; }
  .cw-cell .num { position: absolute; top: 1px; left: 3px; font-size: 0.6rem;
               color: var(--muted); font-weight: 600; pointer-events: none; }
  .cw-cell.in-word { background: var(--active-word); }
  .cw-cell.active {
    background: var(--active-cell);
    outline: 2px solid var(--accent);
    outline-offset: -2px;
    box-shadow: 0 0 12px rgba(0,229,255,0.65);
    z-index: 1;
  }
  .cw-cell.active input { color: var(--accent); }
  .cw-cell.correct input { color: #4ade80; }
  .cw-cell.wrong input { color: #ff6b6b; }
  .cw-cell.wrong { background: var(--wrong); }
  .cw-cell.correct { background: var(--correct); }
  #clues { background: var(--card); padding: 20px; border-radius: 14px;
           border: 1px solid rgba(255,255,255,0.08); }
  .clue-group { margin-bottom: 20px; }
  .clue-group h2 { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em;
                   color: var(--muted); margin: 0 0 10px; border-bottom: 2px solid var(--line);
                   padding-bottom: 6px; }
  .clue { display: flex; gap: 8px; padding: 7px 9px; border-radius: 6px;
          cursor: pointer; font-size: 0.92rem; line-height: 1.4; transition: background 0.12s; color: var(--ink); }
  .clue:hover { background: rgba(255,255,255,0.06); }
  .clue.active { background: var(--active-word); font-weight: 600; }
  .clue.done { color: var(--muted); text-decoration: line-through; }
  .clue .cnum { font-weight: 700; color: var(--accent); min-width: 18px; }
  #win-banner { max-width: 1100px; margin: 20px auto 0;
                background: linear-gradient(135deg, #22c55e, #16a34a);
                color: white; padding: 16px 24px; border-radius: 12px; text-align: center;
                font-weight: 700; font-size: 1.1rem; display: none;
                box-shadow: 0 6px 20px rgba(34,197,94,0.35); animation: pop 0.4s ease; }
  @keyframes pop { 0% { transform: scale(0.9); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
  .hint { max-width: 1100px; margin: 16px auto 0; text-align: center;
          font-size: 0.82rem; color: var(--muted); }
  kbd { background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.18);
        border-bottom-width: 2px; border-radius: 4px; padding: 1px 5px;
        font-size: 0.75rem; font-family: monospace; color: var(--ink); }
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
                        <path fill-rule="evenodd" d="M3.375 3C2.339 3 1.5 3.84 1.5 4.875v.75c0 1.036.84 1.875 1.875 1.875h17.25c1.035 0 1.875-.84 1.875-1.875v-.75C22.5 3.839 21.66 3 20.625 3H3.375Zm0 12.75c-1.036 0-1.875.84-1.875 1.875v.75C1.5 19.41 2.34 20.25 3.375 20.25h6.75c1.035 0 1.875-.84 1.875-1.875v-.75c0-1.036-.84-1.875-1.875-1.875h-6.75Zm10.5 0c-1.035 0-1.875.84-1.875 1.875v.75c0 1.035.84 1.875 1.875 1.875h6.75c1.035 0 1.875-.84 1.875-1.875v-.75c0-1.036-.84-1.875-1.875-1.875h-6.75Z" clip-rule="evenodd" />
                    </svg>
                    Crossword
                </h1>
                <p class="text-lg sm:text-xl sm-subtitle-sm">Fill in the grid, one clue at a time</p>
            </div>
        </section>

        <!-- Game Section -->
        <section class="py-12 px-4 sm:px-6 lg:px-8 bg-slate-50">
            <div class="container mx-auto max-w-5xl">
                <div class="sm-card p-8">
                    <div class="toolbar">
                        <div class="puzzle-picker">
                          <h2 class="puzzle-name" id="puzzle-name"></h2>
                          <span class="difficulty-badge" id="puzzle-difficulty"></span>
                          <select id="puzzle-select" aria-label="Choose a puzzle"></select>
                        </div>
                        <div class="controls">
                            <button id="new-btn">🎲 New Puzzle</button>
                            <button id="check-btn" class="ghost">✓ Check</button>
                            <button id="reveal-letter-btn" class="ghost">💡 Letter</button>
                            <button id="reveal-word-btn" class="ghost">🔓 Word</button>
                            <button id="clear-btn" class="ghost">↺ Clear</button>
                        </div>
                    </div>

                    <div class="cw-main">
                      <div class="grid-wrap"><div id="grid"></div></div>
                      <div id="clues"></div>
                    </div>

                    <div id="win-banner">🎉 Puzzle solved! Well done.</div>

                    <p class="hint">
                      <kbd>←</kbd> <kbd>↑</kbd> <kbd>→</kbd> <kbd>↓</kbd> navigate ·
                      <kbd>Space</kbd> toggle direction ·
                      <kbd>Backspace</kbd> delete · Click a clue to jump to that word
                    </p>
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
    <script src="../starfield.js"></script>

<script>
/* ============================================================
   PUZZLE DATA (embedded)
   ============================================================ */
const PUZZLES = __PUZZLES__;

/* ============================================================
   STATE
   ============================================================ */
let state = {
  puzzle: null, grid: [], rows: 0, cols: 0, words: [],
  current: null, dir: "across", inputs: new Map()
};

/* ============================================================
   GRID BUILDER
   ============================================================ */
function buildGrid(puzzle) {
  let rows = 0, cols = 0;
  puzzle.words.forEach(w => {
    if (w.dir === "across") {
      rows = Math.max(rows, w.row + 1);
      cols = Math.max(cols, w.col + w.answer.length);
    } else {
      rows = Math.max(rows, w.row + w.answer.length);
      cols = Math.max(cols, w.col + 1);
    }
  });

  const grid = Array.from({ length: rows }, () =>
    Array.from({ length: cols }, () => null));

  puzzle.words.forEach((w, wi) => {
    for (let i = 0; i < w.answer.length; i++) {
      const r = w.dir === "across" ? w.row : w.row + i;
      const c = w.dir === "across" ? w.col + i : w.col;
      const letter = w.answer[i].toUpperCase();
      if (!grid[r][c]) grid[r][c] = { letter, words: [] };
      else if (grid[r][c].letter !== letter)
        console.warn(`⚠ Conflict at (${r},${c}) in "${puzzle.name}"`);
      grid[r][c].words.push(wi);
    }
  });

  let num = 1;
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (!grid[r][c]) continue;
      const startsAcross = puzzle.words.some(w => w.dir === "across" && w.row === r && w.col === c);
      const startsDown   = puzzle.words.some(w => w.dir === "down"   && w.row === r && w.col === c);
      if (startsAcross || startsDown) grid[r][c].number = num++;
    }
  }

  const words = puzzle.words.map((w, wi) => {
    const cells = [];
    for (let i = 0; i < w.answer.length; i++) {
      const r = w.dir === "across" ? w.row : w.row + i;
      const c = w.dir === "across" ? w.col + i : w.col;
      cells.push({ r, c });
    }
    return { ...w, id: wi, number: grid[w.row][w.col].number,
             solution: w.answer.toUpperCase(), cells };
  });

  return { grid, rows, cols, words };
}

/* ============================================================
   RENDERING
   ============================================================ */
function renderGrid() {
  const gridEl = document.getElementById("grid");
  gridEl.innerHTML = "";
  gridEl.style.gridTemplateColumns = `repeat(${state.cols}, 40px)`;
  state.inputs.clear();

  for (let r = 0; r < state.rows; r++) {
    for (let c = 0; c < state.cols; c++) {
      const cellData = state.grid[r][c];
      const cell = document.createElement("div");
      cell.className = "cw-cell";
      cell.dataset.r = r; cell.dataset.c = c;

      if (!cellData) { cell.classList.add("blank"); gridEl.appendChild(cell); continue; }

      if (cellData.number) {
        const n = document.createElement("span");
        n.className = "num"; n.textContent = cellData.number;
        cell.appendChild(n);
      }

      const input = document.createElement("input");
      input.type = "text"; input.maxLength = 1;
      input.autocomplete = "off"; input.autocapitalize = "characters";
      input.spellcheck = false;
      input.dataset.r = r; input.dataset.c = c;
      input.addEventListener("focus", () => onCellFocus(r, c));
      input.addEventListener("keydown", onKeyDown);
      input.addEventListener("input", onInput);
      cell.appendChild(input);
      state.inputs.set(`${r},${c}`, input);

      cell.addEventListener("mousedown", e => { e.preventDefault(); onCellClick(r, c); });
      gridEl.appendChild(cell);
    }
  }
}

function renderClues() {
  const cluesEl = document.getElementById("clues");
  const across = state.words.filter(w => w.dir === "across").sort((a, b) => a.number - b.number);
  const down   = state.words.filter(w => w.dir === "down").sort((a, b) => a.number - b.number);

  const makeClues = list => list.map(w =>
    `<div class="clue" data-wid="${w.id}">
       <span class="cnum">${w.number}.</span>
       <span>${w.clue}</span>
     </div>`).join("");

  cluesEl.innerHTML = `
    <div class="clue-group"><h2>Across</h2>${makeClues(across)}</div>
    <div class="clue-group"><h2>Down</h2>${makeClues(down)}</div>
  `;

  cluesEl.querySelectorAll(".clue").forEach(el => {
    el.addEventListener("click", () => selectWord(parseInt(el.dataset.wid)));
  });
}

/* ============================================================
   SELECTION
   ============================================================ */
function wordAt(r, c, dir) {
  const cellData = state.grid[r]?.[c];
  if (!cellData) return null;
  const wid = cellData.words.find(i => state.words[i].dir === dir);
  return wid !== undefined ? state.words[wid] : null;
}

function selectWord(wid) {
  const w = state.words[wid];
  state.dir = w.dir;
  state.current = { r: w.row, c: w.col };
  focusCurrent();
  updateHighlights();
}

function onCellClick(r, c) {
  const cellData = state.grid[r]?.[c];
  if (!cellData) return;
  const sameCell = state.current && state.current.r === r && state.current.c === c;
  const hasAcross = cellData.words.some(i => state.words[i].dir === "across");
  const hasDown   = cellData.words.some(i => state.words[i].dir === "down");

  if (sameCell && hasAcross && hasDown) state.dir = state.dir === "across" ? "down" : "across";
  else if (!hasAcross && hasDown) state.dir = "down";
  else if (hasAcross && !hasDown) state.dir = "across";

  state.current = { r, c };
  focusCurrent();
  updateHighlights();
}

function onCellFocus(r, c) {
  if (!state.current || state.current.r !== r || state.current.c !== c) onCellClick(r, c);
}

function focusCurrent() {
  if (!state.current) return;
  const input = state.inputs.get(`${state.current.r},${state.current.c}`);
  if (input && document.activeElement !== input) input.focus();
}

function updateHighlights() {
  document.querySelectorAll(".cw-cell").forEach(el => el.classList.remove("active", "in-word"));
  document.querySelectorAll(".clue").forEach(el => el.classList.remove("active"));
  if (!state.current) return;

  const w = wordAt(state.current.r, state.current.c, state.dir);
  if (w) {
    w.cells.forEach(({ r, c }) => {
      const el = document.querySelector(`.cw-cell[data-r="${r}"][data-c="${c}"]`);
      if (el) el.classList.add("in-word");
    });
    const clueEl = document.querySelector(`.clue[data-wid="${w.id}"]`);
    if (clueEl) clueEl.classList.add("active");
    updateClueDone();
  }
  const activeEl = document.querySelector(
    `.cw-cell[data-r="${state.current.r}"][data-c="${state.current.c}"]`);
  if (activeEl) activeEl.classList.add("active");
}

function updateClueDone() {
  document.querySelectorAll(".clue").forEach(el => {
    const w = state.words[parseInt(el.dataset.wid)];
    const done = w.cells.every(({ r, c }) => {
      const input = state.inputs.get(`${r},${c}`);
      return input && input.value.toUpperCase() === state.grid[r][c].letter;
    });
    el.classList.toggle("done", done);
  });
}

/* ============================================================
   INPUT
   ============================================================ */
function onInput(e) {
  const input = e.target;
  const r = parseInt(input.dataset.r), c = parseInt(input.dataset.c);
  let val = input.value.slice(-1).toUpperCase();
  if (!/[A-Z]/.test(val)) val = "";
  input.value = val;
  input.parentElement.classList.remove("correct", "wrong");
  if (val) advance(r, c, +1);
  updateClueDone();
  checkWin();
}

function onKeyDown(e) {
  const input = e.target;
  const r = parseInt(input.dataset.r), c = parseInt(input.dataset.c);
  const key = e.key;

  if (key === "Backspace") {
    e.preventDefault();
    if (input.value) {
      input.value = "";
      input.parentElement.classList.remove("correct", "wrong");
      updateClueDone();
    } else {
      const prev = neighbor(r, c, -1);
      if (prev) {
        state.current = prev; focusCurrent();
        const pIn = state.inputs.get(`${prev.r},${prev.c}`);
        pIn.value = ""; pIn.parentElement.classList.remove("correct", "wrong");
        updateHighlights(); updateClueDone();
      }
    }
    return;
  }
  if (key === " ") { e.preventDefault(); toggleDirection(r, c); return; }

  if (key.startsWith("Arrow")) {
    e.preventDefault();
    const deltas = {
      ArrowLeft:  { dr: 0, dc: -1, dir: "across" },
      ArrowRight: { dr: 0, dc: 1,  dir: "across" },
      ArrowUp:    { dr: -1, dc: 0, dir: "down" },
      ArrowDown:  { dr: 1, dc: 0,  dir: "down" }
    };
    const d = deltas[key];
    if (d.dir !== state.dir && wordAt(r, c, d.dir)) state.dir = d.dir;
    moveByDelta(r, c, d.dr, d.dc);
    return;
  }
  if (key === "Tab") { e.preventDefault(); gotoNextWord(); return; }
}

function toggleDirection(r, c) {
  const cellData = state.grid[r][c];
  const hasAcross = cellData.words.some(i => state.words[i].dir === "across");
  const hasDown   = cellData.words.some(i => state.words[i].dir === "down");
  if (hasAcross && hasDown) {
    state.dir = state.dir === "across" ? "down" : "across";
    updateHighlights();
  }
}

function neighbor(r, c, step) {
  const w = wordAt(r, c, state.dir);
  if (!w) return null;
  const idx = w.cells.findIndex(p => p.r === r && p.c === c);
  return w.cells[idx + step] || null;
}

function advance(r, c, step) {
  const next = neighbor(r, c, step);
  if (next) { state.current = next; focusCurrent(); updateHighlights(); }
}

function moveByDelta(r, c, dr, dc) {
  let nr = r + dr, nc = c + dc;
  while (nr >= 0 && nr < state.rows && nc >= 0 && nc < state.cols) {
    if (state.grid[nr][nc]) {
      state.current = { r: nr, c: nc };
      focusCurrent(); updateHighlights();
      return;
    }
    nr += dr; nc += dc;
  }
}

function gotoNextWord() {
  if (!state.current) return;
  const cur = wordAt(state.current.r, state.current.c, state.dir);
  const sameDir = state.words.filter(w => w.dir === state.dir).sort((a, b) => a.number - b.number);
  const idx = sameDir.findIndex(w => w.id === cur.id);
  selectWord(sameDir[(idx + 1) % sameDir.length].id);
}

/* ============================================================
   ACTIONS
   ============================================================ */
function checkAnswers() {
  let allCorrect = true;
  for (let r = 0; r < state.rows; r++) {
    for (let c = 0; c < state.cols; c++) {
      const cellData = state.grid[r][c];
      if (!cellData) continue;
      const input = state.inputs.get(`${r},${c}`);
      const cell = input.parentElement;
      cell.classList.remove("correct", "wrong");
      if (!input.value) { allCorrect = false; continue; }
      if (input.value.toUpperCase() === cellData.letter) cell.classList.add("correct");
      else { cell.classList.add("wrong"); allCorrect = false; }
    }
  }
  updateClueDone();
  if (allCorrect) showWin();
}

function revealLetter() {
  if (!state.current) return;
  const { r, c } = state.current;
  const input = state.inputs.get(`${r},${c}`);
  input.value = state.grid[r][c].letter;
  input.parentElement.classList.remove("wrong");
  input.parentElement.classList.add("correct");
  advance(r, c, +1);
  updateClueDone(); checkWin();
}

function revealWord() {
  const w = wordAt(state.current.r, state.current.c, state.dir);
  if (!w) return;
  w.cells.forEach(({ r, c }, i) => {
    const input = state.inputs.get(`${r},${c}`);
    input.value = w.solution[i];
    input.parentElement.classList.remove("wrong");
    input.parentElement.classList.add("correct");
  });
  updateClueDone(); checkWin();
}

function clearAll() {
  state.inputs.forEach(input => {
    input.value = "";
    input.parentElement.classList.remove("correct", "wrong");
  });
  updateClueDone(); hideWin();
}

function checkWin() {
  for (let r = 0; r < state.rows; r++) {
    for (let c = 0; c < state.cols; c++) {
      const cellData = state.grid[r][c];
      if (!cellData) continue;
      const input = state.inputs.get(`${r},${c}`);
      if (input.value.toUpperCase() !== cellData.letter) return;
    }
  }
  showWin();
}

function showWin() { document.getElementById("win-banner").style.display = "block"; }
function hideWin() { document.getElementById("win-banner").style.display = "none"; }

/* ============================================================
   LOAD
   ============================================================ */
function loadPuzzle(puzzle) {
  state.puzzle = puzzle;
  const built = buildGrid(puzzle);
  state.grid = built.grid; state.rows = built.rows;
  state.cols = built.cols; state.words = built.words;
  state.current = null; state.dir = "across";

  document.getElementById("puzzle-name").textContent = puzzle.name;
  const diffEl = document.getElementById("puzzle-difficulty");
  diffEl.textContent = puzzle.difficulty;
  diffEl.className = "difficulty-badge " + puzzle.difficulty;
  document.getElementById("puzzle-select").value = String(PUZZLES.indexOf(puzzle));
  hideWin(); renderGrid(); renderClues();

  const first = state.words.filter(w => w.dir === "across")
                            .sort((a, b) => a.number - b.number)[0] || state.words[0];
  if (first) selectWord(first.id);
}

function loadRandomPuzzle() {
  if (!PUZZLES || PUZZLES.length === 0) {
    alert("No puzzles loaded.");
    return;
  }
  loadPuzzle(PUZZLES[Math.floor(Math.random() * PUZZLES.length)]);
}

function populatePuzzleSelect() {
  const select = document.getElementById("puzzle-select");
  select.innerHTML = PUZZLES.map((p, i) =>
    `<option value="${i}">${p.name}</option>`).join("");
}

document.getElementById("new-btn").addEventListener("click", loadRandomPuzzle);
document.getElementById("check-btn").addEventListener("click", checkAnswers);
document.getElementById("reveal-letter-btn").addEventListener("click", revealLetter);
document.getElementById("reveal-word-btn").addEventListener("click", revealWord);
document.getElementById("clear-btn").addEventListener("click", clearAll);
document.getElementById("puzzle-select").addEventListener("change", e => {
  loadPuzzle(PUZZLES[parseInt(e.target.value)]);
});

populatePuzzleSelect();
loadRandomPuzzle();
</script>
</body>
</html>
"""

html = HTML_TEMPLATE.replace("__PUZZLES__", data_json)
HTML_PATH.write_text(html, encoding="utf-8")
print(f"✅ Wrote self-contained HTML → {HTML_PATH}")
