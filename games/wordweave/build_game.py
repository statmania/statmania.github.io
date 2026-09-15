#!/usr/bin/env python3
"""
Reads wordlist.json (built by build_wordlist.py) from this folder and
writes a single self-contained games/wordweave.html to the parent folder.
"""
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent      # wordweave/
PARENT_DIR = SCRIPT_DIR.parent                    # games/
WORDLIST_PATH = SCRIPT_DIR / "wordlist.json"
HTML_PATH = PARENT_DIR / "wordweave.html"

print(f"📖 Reading : {WORDLIST_PATH}")
print(f"📤 Writing : {HTML_PATH}")

if not WORDLIST_PATH.exists():
    raise SystemExit(f"❌ File not found: {WORDLIST_PATH} — run build_wordlist.py first")

words = json.loads(WORDLIST_PATH.read_text())
words_json = json.dumps(words, separators=(",", ":"))
print(f"   {len(words)} words embedded")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Stat Mania - WordWeave</title>
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
  select, .num-input { background: rgba(255,255,255,0.04); color: var(--ink);
           border: 1px solid rgba(255,255,255,0.18); border-radius: 999px;
           padding: 6px 14px; font-size: 0.85rem; font-weight: 600;
           font-family: inherit; cursor: pointer; }
  select:hover, .num-input:hover { border-color: var(--accent); }
  select option { background: #0a0f1e; color: var(--ink); }
  .num-field { display: flex; align-items: center; gap: 6px; font-size: 0.8rem; color: var(--muted); }
  .num-field input { width: 56px; background: rgba(255,255,255,0.04); color: var(--ink);
           border: 1px solid rgba(255,255,255,0.18); border-radius: 8px; padding: 5px 8px;
           font-size: 0.85rem; font-weight: 600; font-family: inherit; cursor: text; }
  .num-field input:hover, .num-field input:focus { border-color: var(--accent); outline: none; }
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

  .scoreboard { display: grid; grid-template-columns: 1fr 1fr auto; gap: 16px; margin-bottom: 24px; align-items: stretch; }
  .score-tile { background: var(--card); border: 1px solid rgba(255,255,255,0.08);
                border-radius: 14px; padding: 16px 20px; text-align: center;
                transition: border-color 0.2s, box-shadow 0.2s; }
  .score-tile.active { border-color: var(--accent); box-shadow: 0 0 20px rgba(0,229,255,0.25); }
  .score-tile .label { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.08em;
                        color: var(--muted); margin-bottom: 6px; }
  .score-tile .num { font-size: 2.2rem; font-weight: 800; color: var(--ink); }
  .score-tile.you .num { color: var(--accent); }
  .score-tile.cpu .num { color: #a855f7; }
  .winner-tile { min-width: 120px; display: flex; flex-direction: column; align-items: center;
                 justify-content: center; gap: 4px; padding: 16px 18px; border-radius: 14px;
                 border: 1px solid rgba(255,255,255,0.08); background: var(--card); }
  .winner-tile .label { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.08em;
                         color: var(--muted); }
  .winner-tile .value { font-size: 1rem; font-weight: 800; color: var(--muted); text-align: center; }
  .winner-tile.win { border-color: var(--good); box-shadow: 0 0 20px rgba(74,222,128,0.3); }
  .winner-tile.win .value { color: var(--good); }
  .winner-tile.lose { border-color: var(--bad); box-shadow: 0 0 20px rgba(255,107,107,0.25); }
  .winner-tile.lose .value { color: var(--bad); }
  .winner-tile.tie { border-color: #a855f7; box-shadow: 0 0 20px rgba(168,85,247,0.25); }
  .winner-tile.tie .value { color: #c084fc; }
  @media (max-width: 640px) { .scoreboard { grid-template-columns: 1fr 1fr; } .winner-tile { grid-column: span 2; } }

  .board-wrap { background: var(--card); border: 1px solid rgba(255,255,255,0.08);
                border-radius: 14px; padding: 16px; margin-bottom: 20px; overflow: auto; }
  .board-grid { display: grid; gap: 2px; background: var(--line); padding: 2px;
                border-radius: 6px; width: max-content; margin: 0 auto; }
  .gcell { width: 26px; height: 26px; background: rgba(255,255,255,0.04); position: relative;
           border-radius: 2px; }
  .gcell input { width: 100%; height: 100%; border: none; background: transparent;
                 text-align: center; font-size: 0.85rem; font-weight: 700; text-transform: uppercase;
                 color: var(--ink); font-family: 'Courier New', monospace; outline: none;
                 padding: 0; caret-color: transparent; cursor: default; }
  .gcell.legal { background: rgba(0,229,255,0.14); cursor: pointer; }
  .gcell.legal:hover { background: rgba(0,229,255,0.26); }
  .gcell.selected { background: rgba(0,229,255,0.35); box-shadow: 0 0 10px rgba(0,229,255,0.6); z-index: 1; }
  .gcell.filled.you input { color: var(--accent); }
  .gcell.filled.cpu input { color: #c084fc; }
  .gcell.scored input { color: var(--good); text-shadow: 0 0 8px rgba(74,222,128,0.6); }

  .turn-indicator { text-align: center; margin-bottom: 16px; font-size: 0.9rem; color: var(--muted); }
  .turn-indicator .pill { display: inline-block; padding: 4px 14px; border-radius: 999px;
                           font-weight: 700; border: 1px solid rgba(255,255,255,0.18); }
  .turn-indicator .pill.you { color: var(--accent); border-color: rgba(0,229,255,0.4); }
  .turn-indicator .pill.cpu { color: #a855f7; border-color: rgba(168,85,247,0.4); }
  .board-hint { text-align: center; font-size: 0.8rem; color: var(--muted); margin: -10px 0 16px; }

  #history { background: var(--card); border: 1px solid rgba(255,255,255,0.08);
             border-radius: 14px; padding: 16px 20px; max-height: 260px; overflow-y: auto; }
  #history h3 { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em;
                color: var(--muted); margin: 0 0 10px; border-bottom: 2px solid var(--line);
                padding-bottom: 6px; }
  .hist-row { display: flex; justify-content: space-between; gap: 10px; padding: 5px 0;
              font-size: 0.88rem; border-bottom: 1px solid rgba(255,255,255,0.05); color: var(--ink); }
  .hist-row:last-child { border-bottom: none; }
  .hist-row .who { color: var(--muted); min-width: 64px; }
  .hist-row .who.you { color: var(--accent); }
  .hist-row .who.cpu { color: #a855f7; }
  .hist-row .pts { font-weight: 700; color: var(--good); }
  .hist-row .pts.zero { color: var(--muted); font-weight: 400; }

  #end-banner { max-width: 1100px; margin: 20px auto 0; padding: 16px 24px; border-radius: 12px;
                text-align: center; font-weight: 700; font-size: 1.1rem; display: none;
                animation: pop 0.4s ease; }
  #end-banner.win { background: linear-gradient(135deg, #22c55e, #16a34a); color: white;
                     box-shadow: 0 6px 20px rgba(34,197,94,0.35); }
  #end-banner.lose { background: linear-gradient(135deg, #ef4444, #b91c1c); color: white;
                      box-shadow: 0 6px 20px rgba(239,68,68,0.35); }
  #end-banner.tie { background: linear-gradient(135deg, #a855f7, #7e22ce); color: white;
                     box-shadow: 0 6px 20px rgba(168,85,247,0.35); }
  @keyframes pop { 0% { transform: scale(0.9); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
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
                        <path d="M12 2.25a.75.75 0 0 1 .75.75v1.5a.75.75 0 0 1-1.5 0V3a.75.75 0 0 1 .75-.75ZM7.5 12a4.5 4.5 0 1 1 9 0 4.5 4.5 0 0 1-9 0ZM18.894 6.166a.75.75 0 0 0-1.06-1.06l-1.06 1.06a.75.75 0 0 0 1.06 1.06l1.06-1.06ZM21.75 12a.75.75 0 0 1-.75.75h-1.5a.75.75 0 0 1 0-1.5H21a.75.75 0 0 1 .75.75ZM17.834 18.894a.75.75 0 0 0 1.06-1.06l-1.06-1.06a.75.75 0 1 0-1.06 1.06l1.06 1.06ZM12 18.75a.75.75 0 0 1 .75.75V21a.75.75 0 0 1-1.5 0v-1.5a.75.75 0 0 1 .75-.75ZM7.758 17.834a.75.75 0 0 0-1.061-1.06l-1.06 1.06a.75.75 0 0 0 1.06 1.06l1.06-1.06ZM6 12a.75.75 0 0 1-.75.75h-1.5a.75.75 0 0 1 0-1.5h1.5A.75.75 0 0 1 6 12ZM6.697 7.757a.75.75 0 0 0 1.06-1.06l-1.06-1.061a.75.75 0 0 0-1.06 1.06l1.06 1.06Z" />
                    </svg>
                    WordWeave
                </h1>
                <p class="text-lg sm:text-xl sm-subtitle-sm">Build a crossword one letter at a time and outscore the computer</p>
            </div>
        </section>

        <!-- Game Section -->
        <section class="py-12 px-4 sm:px-6 lg:px-8 bg-slate-50">
            <div class="container mx-auto max-w-5xl">
                <div class="sm-card p-8">
                    <div class="toolbar">
                        <div class="toolbar-left">
                            <select id="difficulty-select" aria-label="Computer difficulty">
                                <option value="easy">Easy</option>
                                <option value="medium" selected>Medium</option>
                                <option value="hard">Hard</option>
                            </select>
                            <select id="starter-select" aria-label="Who starts">
                                <option value="you">You start</option>
                                <option value="cpu">Computer starts</option>
                                <option value="toss" selected>Coin toss</option>
                            </select>
                            <label class="num-field">Rows <input type="number" id="rows-input" min="5" max="40" value="20"></label>
                            <label class="num-field">Cols <input type="number" id="cols-input" min="5" max="40" value="20"></label>
                            <select id="end-mode-select" aria-label="How the game ends">
                                <option value="turns" selected>End: fixed turns</option>
                                <option value="points">End: first to points</option>
                            </select>
                            <label class="num-field" id="turns-field">Turns <input type="number" id="turns-input" min="4" max="200" value="40"></label>
                            <label class="num-field" id="target-field" hidden>Target <input type="number" id="target-input" min="1" max="500" value="30"></label>
                        </div>
                        <div class="toolbar-right">
                            <button id="new-game-btn" class="action">🔄 New Game</button>
                            <button id="end-game-btn" class="action ghost">🏁 End Game</button>
                        </div>
                    </div>

                    <div class="scoreboard">
                        <div class="score-tile you" id="score-tile-you">
                            <div class="label">You</div>
                            <div class="num" id="score-you">0</div>
                        </div>
                        <div class="score-tile cpu" id="score-tile-cpu">
                            <div class="label">Computer</div>
                            <div class="num" id="score-cpu">0</div>
                        </div>
                        <div class="winner-tile" id="winner-tile">
                            <div class="label">Winner</div>
                            <div class="value" id="winner-value">—</div>
                        </div>
                    </div>

                    <div class="turn-indicator" id="turn-indicator"></div>
                    <p class="board-hint">Type a letter into any highlighted cell</p>

                    <div class="board-wrap">
                        <div class="board-grid" id="board-grid"></div>
                    </div>

                    <div id="history">
                        <h3>Move History</h3>
                        <div id="history-rows"></div>
                    </div>

                    <div id="end-banner"></div>
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
   WORD LIST (embedded)
   ============================================================ */
const WORDS = __WORDS__;
const WORD_SET = new Set(WORDS);
const LETTERS = "abcdefghijklmnopqrstuvwxyz".split("");

/* ============================================================
   CORE RULES (2D grid)
   Each turn, place one letter in one legal cell (first move: any
   cell; after that: orthogonally adjacent to a filled cell). Check
   the maximal contiguous run through that cell across (row) and down
   (column); each run of length >= 2 that is a valid word scores
   points = its length, for whoever just placed the letter. A move
   can score twice (once across, once down).
   ============================================================ */
function isLegalCell(grid, rows, cols, r, c, hasAnyMove) {
  if (grid[r][c]) return false;
  if (!hasAnyMove) return true;
  return (
    (r > 0 && grid[r - 1][c]) ||
    (r < rows - 1 && grid[r + 1][c]) ||
    (c > 0 && grid[r][c - 1]) ||
    (c < cols - 1 && grid[r][c + 1])
  );
}

function legalMoves(grid, rows, cols, hasAnyMove) {
  const moves = [];
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (isLegalCell(grid, rows, cols, r, c, hasAnyMove)) moves.push([r, c]);
    }
  }
  return moves;
}

function runBounds(grid, rows, cols, r, c, letter, dir) {
  // dir: "across" walks columns, "down" walks rows. Treats (r,c) as if
  // it already holds `letter` without mutating the real grid.
  const get = (rr, cc) => (rr === r && cc === c) ? letter : (grid[rr][cc] ? grid[rr][cc].letter : null);
  if (dir === "across") {
    let start = c, end = c;
    while (start > 0 && get(r, start - 1)) start--;
    while (end < cols - 1 && get(r, end + 1)) end++;
    let word = "";
    for (let cc = start; cc <= end; cc++) word += get(r, cc);
    return { word, start: [r, start], end: [r, end] };
  } else {
    let start = r, end = r;
    while (start > 0 && get(start - 1, c)) start--;
    while (end < rows - 1 && get(end + 1, c)) end++;
    let word = "";
    for (let rr = start; rr <= end; rr++) word += get(rr, c);
    return { word, start: [start, c], end: [end, c] };
  }
}

function scoreMove(grid, rows, cols, r, c, letter) {
  const across = runBounds(grid, rows, cols, r, c, letter, "across");
  const down = runBounds(grid, rows, cols, r, c, letter, "down");
  const hits = [];
  if (across.word.length >= 2 && WORD_SET.has(across.word)) hits.push({ ...across, dir: "across", points: across.word.length });
  if (down.word.length >= 2 && WORD_SET.has(down.word)) hits.push({ ...down, dir: "down", points: down.word.length });
  return { hits, points: hits.reduce((s, h) => s + h.points, 0) };
}

/* ============================================================
   COMPUTER AI
   Easy: random legal cell + random letter.
   Medium: greedy - picks the (cell, letter) scoring the most now.
   Hard: also looks at the best reply the opponent could score next
   turn from the resulting board, and avoids handing them a big one.
   ============================================================ */
function aiPickMove(state, difficulty) {
  const { grid, rows, cols } = state;
  const moves = legalMoves(grid, rows, cols, state.history.length > 0);
  if (moves.length === 0) return null;

  if (difficulty === "easy") {
    const [r, c] = moves[Math.floor(Math.random() * moves.length)];
    const letter = LETTERS[Math.floor(Math.random() * LETTERS.length)];
    return { r, c, letter };
  }

  // Score every (cell, letter) candidate once - reused by medium & hard.
  const candidates = [];
  for (const [r, c] of moves) {
    for (const letter of LETTERS) {
      const { points } = scoreMove(grid, rows, cols, r, c, letter);
      candidates.push({ r, c, letter, points });
    }
  }

  if (difficulty === "medium") {
    const bestPts = Math.max(...candidates.map(m => m.points));
    const best = candidates.filter(m => m.points === bestPts);
    return best[Math.floor(Math.random() * best.length)];
  }

  // hard: 2-ply over the top-scoring candidates only, for speed.
  candidates.sort((a, b) => b.points - a.points);
  const topN = candidates.slice(0, 20);
  let best = [];
  let bestValue = -Infinity;
  for (const cand of topN) {
    const trialGrid = grid.map(row => row.slice());
    trialGrid[cand.r][cand.c] = { letter: cand.letter, player: "cpu" };
    const oppMoves = legalMoves(trialGrid, rows, cols, true);
    let oppBest = 0;
    for (const [r2, c2] of oppMoves) {
      for (const letter2 of LETTERS) {
        const { points } = scoreMove(trialGrid, rows, cols, r2, c2, letter2);
        if (points > oppBest) oppBest = points;
      }
    }
    const value = cand.points - oppBest;
    if (value > bestValue) { bestValue = value; best = [cand]; }
    else if (value === bestValue) { best.push(cand); }
  }
  return best[Math.floor(Math.random() * best.length)];
}

/* ============================================================
   STATE
   ============================================================ */
let state = null;

function newGame() {
  const rows = clampInt("rows-input", 5, 40);
  const cols = clampInt("cols-input", 5, 40);
  const maxTurns = clampInt("turns-input", 4, 200);
  const targetPoints = clampInt("target-input", 1, 500);
  const endMode = document.getElementById("end-mode-select").value;
  const starterChoice = document.getElementById("starter-select").value;
  const starter = starterChoice === "toss"
    ? (Math.random() < 0.5 ? "you" : "cpu")
    : starterChoice;

  state = {
    rows, cols, maxTurns, endMode, targetPoints,
    grid: Array.from({ length: rows }, () => Array.from({ length: cols }, () => null)),
    turn: starter,
    scores: { you: 0, cpu: 0 },
    history: [],
    selected: null,
    difficulty: document.getElementById("difficulty-select").value,
    over: false,
  };
  document.getElementById("end-banner").style.display = "none";
  const winnerTile = document.getElementById("winner-tile");
  winnerTile.classList.remove("win", "lose", "tie");
  document.getElementById("winner-value").textContent = "—";
  render();

  const tossEl = document.getElementById("turn-indicator");
  if (starterChoice === "toss") {
    tossEl.innerHTML = `🪙 Coin toss: <span class="pill ${starter === "you" ? "you" : "cpu"}">${starter === "you" ? "you" : "computer"} go${starter === "you" ? "" : "es"} first</span>`;
    setTimeout(() => { if (state && state.history.length === 0) render(); }, 1400);
  }

  if (state.turn === "cpu" && !state.over) {
    setTimeout(() => {
      if (!state || state.over || state.history.length > 0) return;
      const move = aiPickMove(state, state.difficulty);
      if (move) playMove(move.r, move.c, move.letter);
    }, starterChoice === "toss" ? 1500 : 550);
  }
}

function clampInt(id, min, max) {
  const el = document.getElementById(id);
  let v = parseInt(el.value, 10);
  if (isNaN(v)) v = min;
  v = Math.max(min, Math.min(max, v));
  el.value = v;
  return v;
}

/* ============================================================
   MOVES
   ============================================================ */
function playMove(r, c, letter) {
  if (!state || state.over) return;
  const player = state.turn;
  const { hits, points } = scoreMove(state.grid, state.rows, state.cols, r, c, letter);
  state.grid[r][c] = { letter, player };
  state.scores[player] += points;
  state.selected = null;
  state.history.push({ player, r, c, letter, hits, points });

  const reachedTarget = state.endMode === "points" &&
    (state.scores.you >= state.targetPoints || state.scores.cpu >= state.targetPoints);
  if (reachedTarget || state.history.length >= state.maxTurns) {
    endGame();
    return;
  }

  state.turn = player === "you" ? "cpu" : "you";
  render();

  if (state.turn === "cpu" && !state.over) {
    setTimeout(() => {
      if (!state || state.over) return;
      const move = aiPickMove(state, state.difficulty);
      if (!move) { endGame(); return; }
      playMove(move.r, move.c, move.letter);
    }, 550);
  }
}

function selectCell(r, c) {
  if (!state || state.over || state.turn !== "you") return;
  if (!isLegalCell(state.grid, state.rows, state.cols, r, c, state.history.length > 0)) return;
  state.selected = [r, c];
  render();
  const input = document.querySelector(`.gcell[data-r="${r}"][data-c="${c}"] input`);
  if (input) input.focus();
}

function endGame() {
  if (!state) return;
  state.over = true;
  render();
  const banner = document.getElementById("end-banner");
  const winnerTile = document.getElementById("winner-tile");
  const winnerValue = document.getElementById("winner-value");
  const { you, cpu } = state.scores;
  banner.style.display = "block";
  winnerTile.classList.remove("win", "lose", "tie");
  if (you > cpu) {
    banner.className = "win";
    banner.textContent = `🎉 You win! ${you} - ${cpu}`;
    winnerTile.classList.add("win");
    winnerValue.textContent = "🏆 You";
  } else if (cpu > you) {
    banner.className = "lose";
    banner.textContent = `🤖 Computer wins. ${cpu} - ${you}`;
    winnerTile.classList.add("lose");
    winnerValue.textContent = "🏆 Computer";
  } else {
    banner.className = "tie";
    banner.textContent = `🤝 It's a tie! ${you} - ${cpu}`;
    winnerTile.classList.add("tie");
    winnerValue.textContent = "🤝 Tie";
  }
}

/* ============================================================
   RENDERING
   ============================================================ */
function render() {
  document.getElementById("score-you").textContent = state.scores.you;
  document.getElementById("score-cpu").textContent = state.scores.cpu;
  document.getElementById("score-tile-you").classList.toggle("active", state.turn === "you" && !state.over);
  document.getElementById("score-tile-cpu").classList.toggle("active", state.turn === "cpu" && !state.over);

  const turnEl = document.getElementById("turn-indicator");
  const progress = state.endMode === "points"
    ? `first to ${state.targetPoints} pts`
    : `${state.history.length}/${state.maxTurns} turns`;
  if (state.over) {
    turnEl.innerHTML = `Game over — ${progress}`;
  } else {
    const who = state.turn === "you" ? "you" : "cpu";
    const label = state.turn === "you" ? "Your turn" : "Computer's turn";
    turnEl.innerHTML = `<span class="pill ${who}">${label}</span> &middot; ${progress}`;
  }

  renderBoard();
  renderHistory();
}

function scoredCellSet() {
  const set = new Set();
  const last = state.history[state.history.length - 1];
  if (!last) return set;
  for (const hit of last.hits) {
    const [r1, c1] = hit.start;
    const [r2, c2] = hit.end;
    if (hit.dir === "across") {
      for (let c = c1; c <= c2; c++) set.add(`${r1},${c}`);
    } else {
      for (let r = r1; r <= r2; r++) set.add(`${r},${c1}`);
    }
  }
  return set;
}

function renderBoard() {
  const el = document.getElementById("board-grid");
  el.style.gridTemplateColumns = `repeat(${state.cols}, 26px)`;
  el.innerHTML = "";
  const scored = scoredCellSet();
  const hasAnyMove = state.history.length > 0;
  const canSelect = !state.over && state.turn === "you";

  for (let r = 0; r < state.rows; r++) {
    for (let c = 0; c < state.cols; c++) {
      const cellData = state.grid[r][c];
      const div = document.createElement("div");
      div.className = "gcell";
      div.dataset.r = r;
      div.dataset.c = c;

      const input = document.createElement("input");
      input.maxLength = 1;
      input.autocomplete = "off";
      input.spellcheck = false;

      if (cellData) {
        div.classList.add("filled", cellData.player);
        if (scored.has(`${r},${c}`)) div.classList.add("scored");
        input.value = cellData.letter.toUpperCase();
        input.readOnly = true;
      } else {
        const legal = canSelect && isLegalCell(state.grid, state.rows, state.cols, r, c, hasAnyMove);
        if (legal) {
          div.classList.add("legal");
          div.addEventListener("click", () => selectCell(r, c));
          // Every legal cell is directly typable, not just the last-clicked
          // one - clicking (selectCell) is just a focus convenience.
          input.addEventListener("focus", () => { state.selected = [r, c]; div.classList.add("selected"); });
          // Desktop keyboards fire a usable keydown; most mobile virtual
          // keyboards don't (or give key:"Unidentified"), but do fire a
          // normal `input` event with the typed character in the value -
          // listen for both. The grid[r][c] check makes this idempotent
          // if a single keystroke somehow triggers both (playMove fills
          // the cell, so a second callback for the same keystroke no-ops).
          const tryPlay = (letter) => {
            if (!state || state.over || state.turn !== "you" || state.grid[r][c]) return;
            const k = (letter || "").toLowerCase();
            if (LETTERS.includes(k)) playMove(r, c, k);
          };
          input.addEventListener("keydown", (e) => {
            if (LETTERS.includes(e.key.toLowerCase())) { e.preventDefault(); tryPlay(e.key); }
          });
          input.addEventListener("input", (e) => {
            const typed = e.target.value.slice(-1);
            e.target.value = "";
            tryPlay(typed);
          });
        } else {
          input.readOnly = true;
          input.tabIndex = -1;
        }
        if (state.selected && state.selected[0] === r && state.selected[1] === c) {
          div.classList.add("selected");
        }
      }

      div.appendChild(input);
      el.appendChild(div);
    }
  }
}

function renderHistory() {
  const el = document.getElementById("history-rows");
  if (state.history.length === 0) {
    el.innerHTML = `<div class="hist-row"><span class="who">—</span><span>No moves yet</span></div>`;
    return;
  }
  el.innerHTML = state.history.slice().reverse().map(h => {
    const who = h.player === "you" ? "You" : "CPU";
    const whoCls = h.player === "you" ? "you" : "cpu";
    const words = h.hits.map(x => `${x.word} (${x.dir})`).join(", ");
    const pts = h.points > 0 ? `<span class="pts">+${h.points}</span>` : `<span class="pts zero">0</span>`;
    return `<div class="hist-row"><span class="who ${whoCls}">${who}</span><span>'${h.letter.toUpperCase()}' at (${h.r + 1},${h.c + 1})${words ? ` — <em>${words}</em>` : ""}</span>${pts}</div>`;
  }).join("");
}

/* ============================================================
   WIRE UP
   ============================================================ */
document.getElementById("new-game-btn").addEventListener("click", newGame);
document.getElementById("end-game-btn").addEventListener("click", () => { if (state && !state.over) endGame(); });
document.getElementById("difficulty-select").addEventListener("change", () => { if (state) state.difficulty = document.getElementById("difficulty-select").value; });
// Who-starts only makes sense at the start of a game - changing it
// mid-game would leave a stale board (already showing the old starter's
// move) sitting under the new choice, so just start over.
document.getElementById("starter-select").addEventListener("change", newGame);
document.getElementById("end-mode-select").addEventListener("change", () => {
  const points = document.getElementById("end-mode-select").value === "points";
  document.getElementById("turns-field").hidden = points;
  document.getElementById("target-field").hidden = !points;
});

newGame();
</script>
</body>
</html>
"""

html = HTML_TEMPLATE.replace("__WORDS__", words_json)
HTML_PATH.write_text(html, encoding="utf-8")
print(f"✅ Wrote self-contained HTML → {HTML_PATH}")
