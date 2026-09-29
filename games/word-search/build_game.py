#!/usr/bin/env python3
"""
Reads wordlist.json (built by wordweave/build_wordlist.py) from the
sibling wordweave/ folder and writes a single self-contained
games/word-search.html (a Boggle-style word search) to the parent
folder. Same pattern as wordweave/build_game.py and
word-ladder/build_game.py - one HTML_TEMPLATE string with the word
list spliced in at __WORDS__.
"""
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent          # word-search/
PARENT_DIR = SCRIPT_DIR.parent                        # games/
WORDLIST_PATH = PARENT_DIR / "wordweave" / "wordlist.json"
HTML_PATH = PARENT_DIR / "word-search.html"

print(f"📖 Reading : {WORDLIST_PATH}")
print(f"📤 Writing : {HTML_PATH}")

if not WORDLIST_PATH.exists():
    raise SystemExit(f"❌ File not found: {WORDLIST_PATH}")

words = json.loads(WORDLIST_PATH.read_text())
words_json = json.dumps(words, separators=(",", ":"))
print(f"   {len(words)} words embedded")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Stat Mania - Word Search</title>
    <meta name="description" content="Play Word Search (Boggle-style): find as many words as you can on a random letter grid before time runs out.">
    <link rel="canonical" href="https://www.statmania.info/games/word-search.html">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://www.statmania.info/games/word-search.html">
    <meta property="og:site_name" content="Stat Mania">
    <meta property="og:title" content="Stat Mania - Word Search">
    <meta property="og:description" content="Play Word Search (Boggle-style): find as many words as you can on a random letter grid before time runs out.">
    <meta property="og:image" content="https://www.statmania.info/assets/images/logo.png">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="Stat Mania - Word Search">
    <meta name="twitter:description" content="Play Word Search (Boggle-style): find as many words as you can on a random letter grid before time runs out.">
    <meta name="twitter:image" content="https://www.statmania.info/assets/images/logo.png">
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
  .toolbar-left { display: flex; flex-wrap: wrap; gap: 14px; align-items: center; }
  .toolbar-right { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
  .select-group { display: flex; flex-direction: column; gap: 2px; cursor: pointer; }
  .select-label { font-size: 0.65rem; font-weight: 700; text-transform: uppercase;
                  letter-spacing: 0.06em; color: var(--muted); padding-left: 2px; }
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
  button.action:disabled { opacity: 0.4; cursor: not-allowed; transform: none; box-shadow: none; }

  .scoreboard { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-bottom: 20px; }
  .score-tile { background: var(--card); border: 1px solid rgba(255,255,255,0.08);
                border-radius: 14px; padding: 14px 16px; text-align: center; }
  .score-tile .label { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em;
                        color: var(--muted); margin-bottom: 4px; }
  .score-tile .num { font-size: 1.8rem; font-weight: 800; color: var(--ink); font-family: 'Courier New', monospace; }
  .score-tile.timer .num { color: var(--accent); }
  .score-tile.timer.low .num { color: var(--bad); }
  .score-tile.score .num { color: var(--good); }

  .game-layout { display: grid; grid-template-columns: auto 1fr; gap: 24px;
                 align-items: start; margin-bottom: 8px; }
  @media (max-width: 760px) { .game-layout { grid-template-columns: 1fr; } }

  .board-wrap { background: var(--card); border: 1px solid rgba(255,255,255,0.08);
                border-radius: 14px; padding: 16px; display: flex; justify-content: center; }
  .bg-grid { display: grid; gap: 4px; width: max-content; touch-action: none; user-select: none; }
  .bg-cell { width: 56px; height: 56px; border-radius: 10px; background: rgba(255,255,255,0.05);
             border: 1px solid rgba(255,255,255,0.12); display: flex; align-items: center;
             justify-content: center; font-family: 'Courier New', monospace; font-weight: 800;
             font-size: 1.4rem; text-transform: uppercase; color: var(--ink); cursor: pointer;
             transition: background 0.1s, border-color 0.1s, transform 0.1s; position: relative; }
  .bg-cell.selected { background: rgba(0,229,255,0.22); border-color: var(--accent);
                       color: var(--accent); transform: scale(0.95);
                       box-shadow: 0 0 14px rgba(0,229,255,0.4); }
  .bg-cell.selected .bg-order { display: flex; }
  .bg-order { display: none; position: absolute; top: -6px; right: -6px; width: 18px; height: 18px;
              border-radius: 999px; background: var(--accent); color: #04101c; font-size: 0.62rem;
              font-weight: 800; align-items: center; justify-content: center; font-family: 'Inter', sans-serif; }
  .bg-cell.locked { pointer-events: none; opacity: 0.6; }

  .current-word { text-align: center; min-height: 2rem; font-size: 1.3rem; font-weight: 800;
                   letter-spacing: 0.1em; text-transform: uppercase; color: var(--accent);
                   font-family: 'Courier New', monospace; margin: 14px 0; }
  #ws-feedback { text-align: center; min-height: 1.3em; font-size: 0.85rem; margin-bottom: 8px; }
  #ws-feedback.good { color: var(--good); }
  #ws-feedback.bad { color: var(--bad); }

  .found-panel { background: var(--card); border: 1px solid rgba(255,255,255,0.08);
                 border-radius: 14px; padding: 16px 18px; max-height: 420px; overflow-y: auto; }
  .found-panel h3 { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em;
                     color: var(--muted); margin: 0 0 10px; border-bottom: 2px solid var(--line);
                     padding-bottom: 6px; }
  .found-list { display: flex; flex-wrap: wrap; gap: 6px; }
  .found-chip { background: rgba(74,222,128,0.14); border: 1px solid rgba(74,222,128,0.35);
                color: var(--good); border-radius: 999px; padding: 3px 11px; font-size: 0.82rem;
                font-weight: 700; text-transform: uppercase; font-family: 'Courier New', monospace; }
  .missed-chip { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.14);
                color: var(--muted); border-radius: 999px; padding: 3px 11px; font-size: 0.82rem;
                font-weight: 700; text-transform: uppercase; font-family: 'Courier New', monospace; }

  #end-banner { display: none; flex-wrap: wrap; gap: 12px; justify-content: center;
                align-items: stretch; margin: 20px 0; animation: pop 0.4s ease; }
  @keyframes pop { 0% { transform: scale(0.9); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
  .win-box { padding: 14px 24px; border-radius: 12px; font-weight: 700; font-size: 1.05rem;
             display: flex; align-items: center; color: white;
             box-shadow: 0 6px 20px rgba(34,197,94,0.35); }
  .win-box.message { background: linear-gradient(135deg, #22c55e, #16a34a); }
  .win-box.info { background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.18);
                   color: var(--ink); box-shadow: none; }

  .rules-panel { background: var(--card); border: 1px solid rgba(255,255,255,0.08);
                 border-radius: 14px; padding: 20px 22px; margin-top: 24px; }
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
                <img src="../img/statmania_logo.svg" alt="Stat Mania Logo" class="w-10 h-10 rounded-full" onerror="this.onerror=null;this.src='https://placehold.co/40x40/4f46e5/ffffff?text=Logo';">
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
        <canvas class="sm-canvas" aria-hidden="true"></canvas>
        <section class="sm-hero-wrap">
            <div class="sm-hero-inner">
                <span class="sm-eyebrow">Stat Mania &middot; Games</span>
                <h1 class="text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-tight mb-4 flex items-center justify-center gap-4 sm-gradient-text">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-12 h-12 sm-hero-icon">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 3.75h4.5v4.5h-4.5v-4.5ZM9.75 3.75h4.5v4.5h-4.5v-4.5ZM15.75 3.75h4.5v4.5h-4.5v-4.5ZM3.75 9.75h4.5v4.5h-4.5v-4.5ZM9.75 9.75h4.5v4.5h-4.5v-4.5ZM15.75 9.75h4.5v4.5h-4.5v-4.5ZM3.75 15.75h4.5v4.5h-4.5v-4.5ZM9.75 15.75h4.5v4.5h-4.5v-4.5ZM15.75 15.75h4.5v4.5h-4.5v-4.5Z" />
                    </svg>
                    Word Search
                </h1>
                <p class="text-lg sm:text-xl sm-subtitle-sm">Drag across adjacent letters to find every word you can before time runs out</p>
            </div>
        </section>

        <!-- Game Section -->
        <section class="py-12 px-4 sm:px-6 lg:px-8 bg-slate-50">
            <div class="container mx-auto max-w-4xl">
                <div class="sm-card p-8">
                    <div class="toolbar">
                        <div class="toolbar-left">
                            <div class="select-group">
                                <span class="select-label">Board size</span>
                                <select id="size-select" aria-label="Board size">
                                    <option value="4" selected>4&times;4 (Classic)</option>
                                    <option value="5">5&times;5 (Big)</option>
                                </select>
                            </div>
                            <div class="select-group">
                                <span class="select-label">Time</span>
                                <select id="time-select" aria-label="Time limit">
                                    <option value="60">60s</option>
                                    <option value="90" selected>90s</option>
                                    <option value="120">120s</option>
                                    <option value="180">180s</option>
                                </select>
                            </div>
                        </div>
                        <div class="toolbar-right">
                            <button id="new-board-btn" class="action">🎲 New Board</button>
                        </div>
                    </div>

                    <div class="scoreboard">
                        <div class="score-tile timer" id="timer-tile">
                            <div class="label">Time Left</div>
                            <div class="num" id="timer-value">90</div>
                        </div>
                        <div class="score-tile score">
                            <div class="label">Score</div>
                            <div class="num" id="score-value">0</div>
                        </div>
                        <div class="score-tile">
                            <div class="label">Words Found</div>
                            <div class="num" id="count-value">0</div>
                        </div>
                    </div>

                    <div id="end-banner"></div>

                    <div class="game-layout">
                        <div class="board-wrap">
                            <div class="bg-grid" id="bg-grid"></div>
                        </div>
                        <div class="found-panel">
                            <h3 id="found-panel-title">Words Found</h3>
                            <div class="found-list" id="found-list"></div>
                        </div>
                    </div>

                    <div class="current-word" id="current-word">&nbsp;</div>
                    <div id="ws-feedback"></div>

                    <div class="rules-panel">
                        <h3>How to Play</h3>
                        <ul>
                            <li>Click or drag across <em>adjacent</em> letters (including diagonals) to spell a word &mdash; each cell can only be used once per word.</li>
                            <li>Words must be at least <em>3 letters</em> long and appear in the dictionary.</li>
                            <li>Longer words score more: 3&ndash;4 letters = 1pt, 5 = 2pts, 6 = 3pts, 7 = 5pts, 8+ = 11pts (classic Boggle scoring).</li>
                            <li>The <em>Qu</em> tile counts as both letters at once, just like in real Boggle dice.</li>
                            <li>When time runs out, the computer reveals every word that could have been found on that exact board.</li>
                        </ul>
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
    <script src="../starfield.js"></script>

<script>
/* ============================================================
   WORD LIST + TRIE (trie built once, used only for the end-of-round
   exhaustive board solver)
   ============================================================ */
const WORDS = __WORDS__;
const WORD_SET = new Set(WORDS);
const MIN_WORD_LEN = 3;

function buildTrie(words) {
  const root = { children: Object.create(null), end: false };
  for (const w of words) {
    if (w.length < MIN_WORD_LEN) continue;
    let node = root;
    for (const ch of w) {
      node = node.children[ch] || (node.children[ch] = { children: Object.create(null), end: false });
    }
    node.end = true;
  }
  return root;
}
const TRIE = buildTrie(WORDS);

/* ============================================================
   DICE SETS (standard Boggle / Big Boggle letter dice)
   ============================================================ */
const DICE_4 = [
  "AAEEGN", "ELRTTY", "AOOTTW", "ABBJOO", "EHRTVW", "CIMOTU",
  "DISTTY", "EIOSST", "DELRVY", "ACHOPS", "HIMNQU", "EEINSU",
  "EEGHNW", "AFFKPS", "HLNNRZ", "DEILRX",
];
const DICE_5 = [
  "AAAFRS", "AAEEEE", "AAFIRS", "ADENNN", "AEEEEM", "AEEGMU",
  "AEGMNN", "AFIRSY", "BJKQXZ", "CCNSTW", "CEIILT", "CEILPT",
  "CEIPST", "DDLNOR", "DHHLOR", "DHHNOT", "DHLNOR", "EIIITT",
  "EMOTTT", "ENSSSU", "FIPRSY", "GORRVW", "HIPRRY", "NOOTUW", "OOOTTU",
];

function shuffled(arr) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function tileFor(letter) {
  return letter === "Q" ? "qu" : letter.toLowerCase();
}

function rollBoard(size) {
  const dice = shuffled(size === 5 ? DICE_5 : DICE_4);
  const tiles = [];
  let idx = 0;
  for (let r = 0; r < size; r++) {
    const row = [];
    for (let c = 0; c < size; c++) {
      const die = dice[idx++];
      const face = die[Math.floor(Math.random() * die.length)];
      row.push(tileFor(face));
    }
    tiles.push(row);
  }
  return tiles;
}

/* ============================================================
   SCORING + SOLVER
   ============================================================ */
function scoreFor(word) {
  const n = word.length;
  if (n < 3) return 0;
  if (n <= 4) return 1;
  if (n === 5) return 2;
  if (n === 6) return 3;
  if (n === 7) return 5;
  return 11;
}

const DIRS = [[-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]];

function solveBoard(tiles) {
  const rows = tiles.length, cols = tiles[0].length;
  const found = new Set();

  function dfs(r, c, mask, node, prefix) {
    let curNode = node;
    let curPrefix = prefix;
    for (const ch of tiles[r][c]) {
      curNode = curNode.children[ch];
      if (!curNode) return;
      curPrefix += ch;
    }
    if (curNode.end && curPrefix.length >= MIN_WORD_LEN) found.add(curPrefix);
    const newMask = mask | (1 << (r * cols + c));
    for (const [dr, dc] of DIRS) {
      const nr = r + dr, nc = c + dc;
      if (nr < 0 || nr >= rows || nc < 0 || nc >= cols) continue;
      if (newMask & (1 << (nr * cols + nc))) continue;
      dfs(nr, nc, newMask, curNode, curPrefix);
    }
  }

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) dfs(r, c, 0, TRIE, "");
  }
  return found;
}

/* ============================================================
   GAME STATE
   ============================================================ */
const state = {
  size: 4, tiles: null, found: new Map(), score: 0,
  running: false, timeLeft: 90, timerId: null,
  path: [], dragging: false,
};

const sizeSelect = document.getElementById("size-select");
const timeSelect = document.getElementById("time-select");
const gridEl = document.getElementById("bg-grid");
const timerTileEl = document.getElementById("timer-tile");
const timerValueEl = document.getElementById("timer-value");
const scoreValueEl = document.getElementById("score-value");
const countValueEl = document.getElementById("count-value");
const currentWordEl = document.getElementById("current-word");
const feedbackEl = document.getElementById("ws-feedback");
const foundListEl = document.getElementById("found-list");
const foundPanelTitleEl = document.getElementById("found-panel-title");
const endBannerEl = document.getElementById("end-banner");

function cellsAdjacent(a, b) {
  return Math.abs(a.r - b.r) <= 1 && Math.abs(a.c - b.c) <= 1 && !(a.r === b.r && a.c === b.c);
}

function pathWord() {
  return state.path.map(p => state.tiles[p.r][p.c]).join("");
}

function renderGrid() {
  gridEl.style.gridTemplateColumns = `repeat(${state.size}, 56px)`;
  gridEl.innerHTML = "";
  for (let r = 0; r < state.size; r++) {
    for (let c = 0; c < state.size; c++) {
      const div = document.createElement("div");
      div.className = "bg-cell";
      div.dataset.r = r;
      div.dataset.c = c;
      div.innerHTML = `${state.tiles[r][c]}<span class="bg-order"></span>`;
      gridEl.appendChild(div);
    }
  }
}

function updateSelectionUI() {
  const cells = gridEl.querySelectorAll(".bg-cell");
  cells.forEach(cell => {
    const r = parseInt(cell.dataset.r, 10), c = parseInt(cell.dataset.c, 10);
    const idx = state.path.findIndex(p => p.r === r && p.c === c);
    cell.classList.toggle("selected", idx !== -1);
    const orderEl = cell.querySelector(".bg-order");
    orderEl.textContent = idx !== -1 ? String(idx + 1) : "";
  });
  currentWordEl.textContent = state.path.length ? pathWord() : "\\u00a0";
}

function renderFound() {
  countValueEl.textContent = String(state.found.size);
  scoreValueEl.textContent = String(state.score);
  const words = [...state.found.keys()].sort((a, b) => b.length - a.length || a.localeCompare(b));
  foundListEl.innerHTML = words.map(w => `<span class="found-chip">${w} (${state.found.get(w)})</span>`).join("");
}

function flashFeedback(msg, good) {
  feedbackEl.textContent = msg;
  feedbackEl.className = good ? "good" : "bad";
  clearTimeout(flashFeedback._t);
  flashFeedback._t = setTimeout(() => { feedbackEl.textContent = ""; feedbackEl.className = ""; }, 1400);
}

function submitPath() {
  const path = state.path;
  state.path = [];
  updateSelectionUI();
  if (path.length < 1) return;
  const word = path.map(p => state.tiles[p.r][p.c]).join("");
  if (word.length < MIN_WORD_LEN) return;
  if (state.found.has(word)) {
    flashFeedback(`Already found "${word}"`, false);
    return;
  }
  if (!WORD_SET.has(word)) {
    flashFeedback(`"${word}" is not a valid word`, false);
    return;
  }
  const pts = scoreFor(word);
  state.found.set(word, pts);
  state.score += pts;
  flashFeedback(`+${pts} for "${word}"`, true);
  renderFound();
}

function cellFromEvent(e) {
  const el = document.elementFromPoint(e.clientX, e.clientY);
  const cell = el && el.closest(".bg-cell");
  if (!cell) return null;
  return { r: parseInt(cell.dataset.r, 10), c: parseInt(cell.dataset.c, 10) };
}

function startDragAt(pos) {
  if (!state.running) return;
  state.dragging = true;
  state.path = [pos];
  updateSelectionUI();
}

function extendDragTo(pos) {
  if (!state.dragging || !pos) return;
  const path = state.path;
  const last = path[path.length - 1];
  if (last.r === pos.r && last.c === pos.c) return;
  if (path.length > 1) {
    const prev = path[path.length - 2];
    if (prev.r === pos.r && prev.c === pos.c) {
      path.pop();
      updateSelectionUI();
      return;
    }
  }
  if (!cellsAdjacent(last, pos)) return;
  if (path.some(p => p.r === pos.r && p.c === pos.c)) return;
  path.push(pos);
  updateSelectionUI();
}

function endDrag() {
  if (!state.dragging) return;
  state.dragging = false;
  submitPath();
}

gridEl.addEventListener("pointerdown", (e) => {
  const pos = cellFromEvent(e);
  if (pos) startDragAt(pos);
});
document.addEventListener("pointermove", (e) => {
  if (state.dragging) extendDragTo(cellFromEvent(e));
});
document.addEventListener("pointerup", endDrag);
document.addEventListener("pointercancel", endDrag);

/* ============================================================
   ROUND LIFECYCLE
   ============================================================ */
function tick() {
  state.timeLeft--;
  timerValueEl.textContent = String(state.timeLeft);
  timerTileEl.classList.toggle("low", state.timeLeft <= 10);
  if (state.timeLeft <= 0) endRound();
}

function newBoard() {
  clearInterval(state.timerId);
  state.size = parseInt(sizeSelect.value, 10);
  state.tiles = rollBoard(state.size);
  state.found = new Map();
  state.score = 0;
  state.path = [];
  state.dragging = false;
  state.running = true;
  state.timeLeft = parseInt(timeSelect.value, 10);
  timerTileEl.classList.remove("low");
  timerValueEl.textContent = String(state.timeLeft);
  endBannerEl.style.display = "none";
  endBannerEl.innerHTML = "";
  foundPanelTitleEl.textContent = "Words Found";
  feedbackEl.textContent = "";
  gridEl.classList.remove("board-locked");
  renderGrid();
  updateSelectionUI();
  renderFound();
  state.timerId = setInterval(tick, 1000);
}

function endRound() {
  clearInterval(state.timerId);
  state.running = false;
  state.path = [];
  state.dragging = false;
  gridEl.querySelectorAll(".bg-cell").forEach(c => c.classList.add("locked"));
  updateSelectionUI();

  const all = solveBoard(state.tiles);
  let maxScore = 0;
  for (const w of all) maxScore += scoreFor(w);
  const missed = [...all].filter(w => !state.found.has(w))
    .sort((a, b) => b.length - a.length || a.localeCompare(b));

  foundPanelTitleEl.textContent = `Words Found (missed ${missed.length})`;
  foundListEl.innerHTML =
    [...state.found.keys()].sort((a, b) => b.length - a.length || a.localeCompare(b))
      .map(w => `<span class="found-chip">${w} (${state.found.get(w)})</span>`).join("") +
    missed.map(w => `<span class="missed-chip">${w} (${scoreFor(w)})</span>`).join("");

  endBannerEl.style.display = "flex";
  endBannerEl.innerHTML = `
    <div class="win-box message">You found ${state.found.size} word${state.found.size === 1 ? "" : "s"} for ${state.score} pt${state.score === 1 ? "" : "s"}</div>
    <div class="win-box info">This board had ${all.size} possible words worth ${maxScore} pts</div>
  `;
}

document.getElementById("new-board-btn").addEventListener("click", newBoard);
sizeSelect.addEventListener("change", newBoard);
timeSelect.addEventListener("change", newBoard);

newBoard();
</script>
</body>
</html>
"""

html = HTML_TEMPLATE.replace("__WORDS__", words_json)
HTML_PATH.write_text(html, encoding="utf-8")
print(f"✅ Wrote {len(html):,} bytes to {HTML_PATH}")
