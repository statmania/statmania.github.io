#!/usr/bin/env python3
"""
Reads wordlist.json (built by wordweave/build_wordlist.py) from the
sibling wordweave/ folder and writes a single self-contained
games/word-ladder.html to the parent folder. Same pattern as
wordweave/build_game.py and sudoku/build_game.py - one HTML_TEMPLATE
string with the word list spliced in at __WORDS__.
"""
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent          # word-ladder/
PARENT_DIR = SCRIPT_DIR.parent                        # games/
WORDLIST_PATH = PARENT_DIR / "wordweave" / "wordlist.json"
HTML_PATH = PARENT_DIR / "word-ladder.html"

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
<title>Stat Mania - Word Ladder</title>
    <meta name="description" content="Play Word Ladder: change one word into another one letter at a time, and try to beat the computer's shortest path.">
    <link rel="canonical" href="https://www.statmania.info/games/word-ladder.html">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://www.statmania.info/games/word-ladder.html">
    <meta property="og:site_name" content="Stat Mania">
    <meta property="og:title" content="Stat Mania - Word Ladder">
    <meta property="og:description" content="Play Word Ladder: change one word into another one letter at a time, and try to beat the computer's shortest path.">
    <meta property="og:image" content="https://www.statmania.info/assets/images/logo.png">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="Stat Mania - Word Ladder">
    <meta name="twitter:description" content="Play Word Ladder: change one word into another one letter at a time, and try to beat the computer's shortest path.">
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

  .meta-row { display: flex; flex-wrap: wrap; gap: 10px 22px; justify-content: center;
              align-items: center; margin-bottom: 20px; }
  .meta-stat { text-align: center; }
  .meta-stat .num { font-size: 1.6rem; font-weight: 800; color: var(--ink); font-family: 'Courier New', monospace; }
  .meta-stat .lbl { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); }
  .meta-stat.par .num { color: var(--accent); }

  .endpoints { display: flex; align-items: center; justify-content: center; gap: 18px;
               flex-wrap: wrap; margin-bottom: 22px; }
  .endpoint-card { background: var(--card); border: 1px solid rgba(255,255,255,0.08);
                    border-radius: 14px; padding: 14px 22px; text-align: center; }
  .endpoint-card .tag { font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.1em;
                         color: var(--muted); margin-bottom: 6px; }
  .endpoint-card .word { font-family: 'Courier New', monospace; font-size: 1.5rem; font-weight: 800;
                          letter-spacing: 0.08em; text-transform: uppercase; }
  .endpoint-card.start .word { color: var(--accent); }
  .endpoint-card.target .word { color: #a855f7; }
  .endpoint-arrow { color: var(--muted); font-size: 1.4rem; }

  .chain-wrap { display: flex; flex-direction: column; gap: 8px; margin-bottom: 18px;
                max-height: 320px; overflow-y: auto; padding: 4px 2px; }
  .chain-row { display: flex; align-items: center; gap: 10px; }
  .chain-idx { width: 22px; flex: none; text-align: right; font-size: 0.75rem; color: var(--muted);
               font-family: 'Courier New', monospace; }
  .wl-tiles { display: flex; gap: 4px; }
  .wl-tile { width: 34px; height: 34px; border-radius: 8px; background: var(--card);
             border: 1px solid rgba(255,255,255,0.12); display: flex; align-items: center;
             justify-content: center; font-family: 'Courier New', monospace; font-weight: 800;
             font-size: 1rem; text-transform: uppercase; color: var(--ink); }
  .chain-row.is-start .wl-tile { border-color: rgba(0,229,255,0.4); color: var(--accent); }
  .chain-row.is-target .wl-tile { border-color: rgba(168,85,247,0.5); color: #c084fc;
                                   background: rgba(168,85,247,0.12); }
  .chain-row .diff-flag { color: var(--good); font-size: 0.8rem; }

  .input-row { display: flex; gap: 10px; margin-bottom: 8px; flex-wrap: wrap; }
  .input-row input[type="text"] { flex: 1; min-width: 180px; background: rgba(255,255,255,0.04);
           color: var(--ink); border: 1px solid rgba(255,255,255,0.18); border-radius: 10px;
           padding: 10px 14px; font-size: 1rem; font-family: 'Courier New', monospace;
           letter-spacing: 0.08em; text-transform: uppercase; outline: none; }
  .input-row input[type="text"]:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(0,229,255,0.15); }
  #wl-error { min-height: 1.4em; font-size: 0.85rem; color: var(--bad); margin-bottom: 14px; }
  #wl-hint { min-height: 1.2em; font-size: 0.85rem; color: var(--accent); margin-bottom: 4px; }

  #win-banner { display: none; flex-wrap: wrap; gap: 12px; justify-content: center;
                align-items: stretch; margin: 0 0 20px; animation: pop 0.4s ease; }
  @keyframes pop { 0% { transform: scale(0.9); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
  .win-box { padding: 14px 24px; border-radius: 12px; font-weight: 700; font-size: 1.05rem;
             display: flex; align-items: center; color: white;
             box-shadow: 0 6px 20px rgba(34,197,94,0.35); }
  .win-box.message { background: linear-gradient(135deg, #22c55e, #16a34a); }
  .win-box.info { background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.18);
                   color: var(--ink); box-shadow: none; }

  .hidden { display: none !important; }

  .turn-banner { text-align: center; margin-bottom: 16px; }
  .turn-banner .pill { display: inline-block; padding: 6px 18px; border-radius: 999px;
                        font-weight: 700; font-size: 0.9rem; border: 1px solid rgba(255,255,255,0.18); }
  .turn-banner .pill.p1 { color: var(--accent); border-color: rgba(0,229,255,0.4); background: rgba(0,229,255,0.08); }
  .turn-banner .pill.p2 { color: #c084fc; border-color: rgba(168,85,247,0.4); background: rgba(168,85,247,0.08); }

  .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 18px; }
  @media (max-width: 640px) { .two-col { grid-template-columns: 1fr; } }
  .player-col { background: var(--card); border: 1px solid rgba(255,255,255,0.08); border-radius: 14px;
                padding: 12px; transition: border-color 0.2s, box-shadow 0.2s; }
  .player-col.active { border-color: var(--accent); box-shadow: 0 0 20px rgba(0,229,255,0.2); }
  .player-col.p2.active { border-color: #a855f7; box-shadow: 0 0 20px rgba(168,85,247,0.25); }
  .player-col-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
  .player-col-head .name { font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); }
  .player-col.p1 .player-col-head .name { color: var(--accent); }
  .player-col.p2 .player-col-head .name { color: #c084fc; }
  .player-col-head .steps { font-size: 0.85rem; color: var(--ink); font-family: 'Courier New', monospace; }
  .player-col .chain-wrap { max-height: 220px; margin-bottom: 0; }

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
                        <path stroke-linecap="round" stroke-linejoin="round" d="M6 3v18M18 3v18M6 7h12M6 12h12M6 17h12" />
                    </svg>
                    Word Ladder
                </h1>
                <p class="text-lg sm:text-xl sm-subtitle-sm">Change one word into another, one letter at a time &mdash; can you match the computer's shortest path?</p>
            </div>
        </section>

        <!-- Game Section -->
        <section class="py-12 px-4 sm:px-6 lg:px-8 bg-slate-50">
            <div class="container mx-auto max-w-3xl">
                <div class="sm-card p-8">
                    <div class="toolbar">
                        <div class="toolbar-left">
                            <div class="select-group">
                                <span class="select-label">Word length</span>
                                <select id="length-select" aria-label="Word length">
                                    <option value="3">3 letters</option>
                                    <option value="4" selected>4 letters</option>
                                    <option value="5">5 letters</option>
                                    <option value="6">6 letters</option>
                                </select>
                            </div>
                            <div class="select-group">
                                <span class="select-label">Difficulty</span>
                                <select id="difficulty-select" aria-label="Difficulty">
                                    <option value="easy">Easy</option>
                                    <option value="medium" selected>Medium</option>
                                    <option value="hard">Hard</option>
                                </select>
                            </div>
                            <div class="select-group">
                                <span class="select-label">Players</span>
                                <select id="mode-select" aria-label="Number of players">
                                    <option value="1p" selected>1 Player</option>
                                    <option value="2p">2 Player (pass &amp; play)</option>
                                </select>
                            </div>
                        </div>
                        <div class="toolbar-right">
                            <span id="assist-actions">
                                <button id="hint-btn" class="action ghost">💡 Hint</button>
                                <button id="give-up-btn" class="action ghost">🏳️ Give Up</button>
                            </span>
                            <button id="new-game-btn" class="action">🔄 New Ladder</button>
                        </div>
                    </div>

                    <div class="meta-row" id="meta-row-1p">
                        <div class="meta-stat">
                            <div class="num" id="steps-count">0</div>
                            <div class="lbl">Your Steps</div>
                        </div>
                        <div class="meta-stat par">
                            <div class="num" id="par-count">–</div>
                            <div class="lbl">Computer's Best</div>
                        </div>
                        <div class="meta-stat">
                            <div class="num" id="hints-count">0</div>
                            <div class="lbl">Hints Used</div>
                        </div>
                    </div>

                    <div class="meta-row hidden" id="meta-row-2p">
                        <div class="meta-stat par">
                            <div class="num" id="par-count-2p">–</div>
                            <div class="lbl">Computer's Best</div>
                        </div>
                    </div>

                    <div class="endpoints">
                        <div class="endpoint-card start">
                            <div class="tag">Start</div>
                            <div class="word" id="start-word">----</div>
                        </div>
                        <div class="endpoint-arrow">&rarr;</div>
                        <div class="endpoint-card target">
                            <div class="tag">Target</div>
                            <div class="word" id="target-word">----</div>
                        </div>
                    </div>

                    <div class="turn-banner hidden" id="turn-banner">
                        <span class="pill p1" id="turn-pill">Player 1's turn</span>
                    </div>

                    <div id="win-banner"></div>

                    <div class="chain-wrap" id="chain-wrap"></div>

                    <div class="two-col hidden" id="two-col-wrap">
                        <div class="player-col p1" id="player-col-1">
                            <div class="player-col-head"><span class="name">Player 1</span><span class="steps" id="p1-steps">0</span></div>
                            <div class="chain-wrap" id="chain-wrap-p1"></div>
                        </div>
                        <div class="player-col p2" id="player-col-2">
                            <div class="player-col-head"><span class="name">Player 2</span><span class="steps" id="p2-steps">0</span></div>
                            <div class="chain-wrap" id="chain-wrap-p2"></div>
                        </div>
                    </div>

                    <div id="wl-hint"></div>
                    <div class="input-row">
                        <input type="text" id="word-input" placeholder="Type the next word..." autocomplete="off" autocapitalize="off" spellcheck="false">
                        <button id="submit-word-btn" class="action">Add Word</button>
                    </div>
                    <div id="wl-error"></div>

                    <div class="rules-panel">
                        <h3>How to Play</h3>
                        <ul>
                            <li>Turn the <em>start</em> word into the <em>target</em> word, changing <em>exactly one letter</em> at each step.</li>
                            <li>Every step along the way must itself be a <em>real word</em> of the same length.</li>
                            <li>You can't repeat a word you've already used in the chain.</li>
                            <li><em>Computer's Best</em> is the shortest possible chain length, found by the computer via breadth-first search &mdash; try to match or beat it.</li>
                            <li>Stuck? <em>Hint</em> suggests one valid next word (cheap, but it counts against your final rating). <em>Give Up</em> reveals a full shortest path.</li>
                            <li>In <em>2 Player</em> mode, pass the device back and forth: the same start/target is shared, each player builds their own chain, and whoever reaches the target first in fewer moves wins.</li>
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
   WORD LIST + LADDER GRAPH (built lazily per length via wildcard
   patterns, so we never compare every pair of words directly)
   ============================================================ */
const WORDS = __WORDS__;
const WORD_SET = new Set(WORDS);

const WORDS_BY_LEN = {};
for (const w of WORDS) {
  (WORDS_BY_LEN[w.length] ??= []).push(w);
}

const patternCache = {};
function getPatternMap(len) {
  if (patternCache[len]) return patternCache[len];
  const map = new Map();
  const words = WORDS_BY_LEN[len] || [];
  for (const w of words) {
    for (let i = 0; i < len; i++) {
      const pat = w.slice(0, i) + "*" + w.slice(i + 1);
      let bucket = map.get(pat);
      if (!bucket) map.set(pat, (bucket = []));
      bucket.push(w);
    }
  }
  patternCache[len] = map;
  return map;
}

function neighbors(word) {
  const map = getPatternMap(word.length);
  const out = new Set();
  for (let i = 0; i < word.length; i++) {
    const pat = word.slice(0, i) + "*" + word.slice(i + 1);
    const bucket = map.get(pat);
    if (bucket) for (const w of bucket) if (w !== word) out.add(w);
  }
  return out;
}

function bfs(start) {
  const dist = new Map([[start, 0]]);
  const parent = new Map();
  const queue = [start];
  for (let qi = 0; qi < queue.length; qi++) {
    const cur = queue[qi];
    for (const nb of neighbors(cur)) {
      if (!dist.has(nb)) {
        dist.set(nb, dist.get(cur) + 1);
        parent.set(nb, cur);
        queue.push(nb);
      }
    }
  }
  return { dist, parent };
}

function hammingDistance(a, b) {
  let d = 0;
  for (let i = 0; i < a.length; i++) if (a[i] !== b[i]) d++;
  return d;
}

const DIFFICULTY_RANGES = {
  easy: [2, 3],
  medium: [4, 6],
  hard: [7, 20],
};

function pickPuzzle(len, minPar, maxPar, maxAttempts) {
  const words = WORDS_BY_LEN[len];
  if (!words || words.length < 2) return null;
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    const start = words[Math.floor(Math.random() * words.length)];
    const { dist, parent } = bfs(start);
    const candidates = [];
    for (const [w, d] of dist) if (d >= minPar && d <= maxPar) candidates.push(w);
    if (candidates.length) {
      const target = candidates[Math.floor(Math.random() * candidates.length)];
      return { start, target, dist, parent };
    }
  }
  return null;
}

function reconstructPath(target, parent) {
  const path = [target];
  let cur = target;
  while (parent.has(cur)) {
    cur = parent.get(cur);
    path.unshift(cur);
  }
  return path;
}

/* ============================================================
   GAME STATE
   ============================================================ */
const state = {
  length: 4, start: "", target: "", dist: null, parent: null, distToTarget: null,
  mode: "1p", chains: [[]], current: 0, finished: false, winner: null, hintsUsed: 0,
};

function activeChain() {
  return state.mode === "2p" ? state.chains[state.current] : state.chains[0];
}

const lengthSelect = document.getElementById("length-select");
const difficultySelect = document.getElementById("difficulty-select");
const modeSelect = document.getElementById("mode-select");
const startWordEl = document.getElementById("start-word");
const targetWordEl = document.getElementById("target-word");
const chainWrapEl = document.getElementById("chain-wrap");
const stepsCountEl = document.getElementById("steps-count");
const parCountEl = document.getElementById("par-count");
const parCount2El = document.getElementById("par-count-2p");
const hintsCountEl = document.getElementById("hints-count");
const errorEl = document.getElementById("wl-error");
const hintEl = document.getElementById("wl-hint");
const inputEl = document.getElementById("word-input");
const winBannerEl = document.getElementById("win-banner");
const giveUpBtn = document.getElementById("give-up-btn");
const hintBtn = document.getElementById("hint-btn");
const submitBtn = document.getElementById("submit-word-btn");
const assistActionsEl = document.getElementById("assist-actions");
const metaRow1pEl = document.getElementById("meta-row-1p");
const metaRow2pEl = document.getElementById("meta-row-2p");
const turnBannerEl = document.getElementById("turn-banner");
const turnPillEl = document.getElementById("turn-pill");
const twoColWrapEl = document.getElementById("two-col-wrap");
const chainWrapP1El = document.getElementById("chain-wrap-p1");
const chainWrapP2El = document.getElementById("chain-wrap-p2");
const p1StepsEl = document.getElementById("p1-steps");
const p2StepsEl = document.getElementById("p2-steps");
const playerCol1El = document.getElementById("player-col-1");
const playerCol2El = document.getElementById("player-col-2");

function newGame() {
  const len = parseInt(lengthSelect.value, 10);
  const mode = modeSelect.value;
  const [minPar, maxPar] = DIFFICULTY_RANGES[difficultySelect.value];
  const puzzle = pickPuzzle(len, minPar, maxPar, 60) || pickPuzzle(len, 2, 999, 60);
  if (!puzzle) {
    errorEl.textContent = "Couldn't find a ladder for this length - try another one.";
    return;
  }
  const is2p = mode === "2p";
  state.length = len;
  state.mode = mode;
  state.start = puzzle.start;
  state.target = puzzle.target;
  state.dist = puzzle.dist;
  state.parent = puzzle.parent;
  state.distToTarget = bfs(puzzle.target).dist;
  state.chains = is2p ? [[puzzle.start], [puzzle.start]] : [[puzzle.start]];
  state.current = 0;
  state.finished = false;
  state.winner = null;
  state.hintsUsed = 0;
  errorEl.textContent = "";
  hintEl.textContent = "";
  winBannerEl.style.display = "none";
  winBannerEl.innerHTML = "";
  inputEl.value = "";
  inputEl.disabled = false;
  inputEl.placeholder = is2p ? "Player 1: type the next word..." : "Type the next word...";
  submitBtn.disabled = false;
  giveUpBtn.disabled = is2p;
  hintBtn.disabled = is2p;

  metaRow1pEl.classList.toggle("hidden", is2p);
  metaRow2pEl.classList.toggle("hidden", !is2p);
  turnBannerEl.classList.toggle("hidden", !is2p);
  chainWrapEl.classList.toggle("hidden", is2p);
  twoColWrapEl.classList.toggle("hidden", !is2p);
  assistActionsEl.classList.toggle("hidden", is2p);

  render();
  inputEl.focus();
}

function renderChainHTML(chain, target, revealTarget) {
  return chain.map((word, i) => {
    const isStart = i === 0;
    const isTarget = revealTarget && word === target;
    const tiles = word.split("").map(ch => `<span class="wl-tile">${ch}</span>`).join("");
    const cls = isStart ? "is-start" : (isTarget ? "is-target" : "");
    return `<div class="chain-row ${cls}"><span class="chain-idx">${i}.</span><div class="wl-tiles">${tiles}</div></div>`;
  }).join("");
}

function render() {
  startWordEl.textContent = state.start;
  targetWordEl.textContent = state.target;
  if (state.mode === "2p") render2p(); else render1p();
}

function render1p() {
  const chain = state.chains[0];
  stepsCountEl.textContent = String(chain.length - 1);
  parCountEl.textContent = state.finished ? String(state.dist.get(state.target)) : "?";
  hintsCountEl.textContent = String(state.hintsUsed);
  chainWrapEl.innerHTML = renderChainHTML(chain, state.target, state.finished);
  chainWrapEl.scrollTop = chainWrapEl.scrollHeight;
}

function render2p() {
  parCount2El.textContent = state.finished ? String(state.dist.get(state.target)) : "?";
  const [c1, c2] = state.chains;
  p1StepsEl.textContent = String(c1.length - 1);
  p2StepsEl.textContent = String(c2.length - 1);
  chainWrapP1El.innerHTML = renderChainHTML(c1, state.target, state.winner === 0);
  chainWrapP2El.innerHTML = renderChainHTML(c2, state.target, state.winner === 1);
  chainWrapP1El.scrollTop = chainWrapP1El.scrollHeight;
  chainWrapP2El.scrollTop = chainWrapP2El.scrollHeight;
  playerCol1El.classList.toggle("active", state.winner === null && state.current === 0);
  playerCol2El.classList.toggle("active", state.winner === null && state.current === 1);
  if (state.winner === null) {
    turnPillEl.className = `pill p${state.current + 1}`;
    turnPillEl.textContent = `Player ${state.current + 1}'s turn`;
    inputEl.placeholder = `Player ${state.current + 1}: type the next word...`;
  } else {
    turnPillEl.className = `pill p${state.winner + 1}`;
    turnPillEl.textContent = `🏆 Player ${state.winner + 1} wins!`;
  }
}

function showError(msg) {
  errorEl.textContent = msg;
}

function submitWord() {
  if (state.finished) return;
  const raw = inputEl.value;
  const word = raw.trim().toLowerCase();
  hintEl.textContent = "";
  if (!word) return;
  if (word.length !== state.length) {
    showError(`Must be a ${state.length}-letter word.`);
    return;
  }
  if (!WORD_SET.has(word)) {
    showError(`"${word}" is not a recognized word.`);
    return;
  }
  const chain = activeChain();
  const prev = chain[chain.length - 1];
  if (hammingDistance(word, prev) !== 1) {
    showError(`Must differ from "${prev}" by exactly one letter.`);
    return;
  }
  if (chain.includes(word)) {
    showError(`You already used "${word}" in this chain.`);
    return;
  }
  showError("");
  chain.push(word);
  inputEl.value = "";
  if (word === state.target) {
    finishGame(state.mode === "2p" ? state.current : 0);
    return;
  }
  if (state.mode === "2p") state.current = 1 - state.current;
  render();
}

function finishGame(playerIdx) {
  state.finished = true;
  state.winner = playerIdx;
  inputEl.disabled = true;
  submitBtn.disabled = true;
  giveUpBtn.disabled = true;
  hintBtn.disabled = true;
  const steps = state.chains[playerIdx].length - 1;
  const par = state.dist.get(state.target);
  winBannerEl.style.display = "flex";
  if (state.mode === "2p") {
    winBannerEl.innerHTML = `
      <div class="win-box message">🏆 Player ${playerIdx + 1} wins in ${steps} step${steps === 1 ? "" : "s"}!</div>
      <div class="win-box info">Computer's best: ${par} step${par === 1 ? "" : "s"}</div>
    `;
  } else {
    let rating;
    if (state.hintsUsed > 0) rating = "✅ Solved (with hints)!";
    else if (steps <= par) rating = "🏆 Optimal!";
    else if (steps <= par + 2) rating = "🎉 Great job!";
    else rating = "✅ Solved!";
    winBannerEl.innerHTML = `
      <div class="win-box message">${rating} ${steps} step${steps === 1 ? "" : "s"}</div>
      <div class="win-box info">Computer's best: ${par} step${par === 1 ? "" : "s"}</div>
    `;
  }
  render();
}

function giveUp() {
  if (state.finished || state.mode === "2p") return;
  const path = reconstructPath(state.target, state.parent);
  state.chains[0] = path;
  state.finished = true;
  inputEl.disabled = true;
  submitBtn.disabled = true;
  giveUpBtn.disabled = true;
  hintBtn.disabled = true;
  const par = state.dist.get(state.target);
  winBannerEl.style.display = "flex";
  winBannerEl.innerHTML = `<div class="win-box info">Here's one shortest path &mdash; ${par} step${par === 1 ? "" : "s"}.</div>`;
  render();
}

function giveHint() {
  if (state.finished || state.mode === "2p") return;
  const cur = state.chains[0][state.chains[0].length - 1];
  if (cur === state.target) return;
  const curDist = state.distToTarget.get(cur);
  if (curDist === undefined) {
    hintEl.textContent = "No path to the target from here - try Give Up to see a valid route.";
    return;
  }
  const options = [...neighbors(cur)].filter(w => state.distToTarget.get(w) === curDist - 1);
  if (!options.length) {
    hintEl.textContent = "No path to the target from here - try Give Up to see a valid route.";
    return;
  }
  const pick = options[Math.floor(Math.random() * options.length)];
  state.hintsUsed++;
  hintsCountEl.textContent = String(state.hintsUsed);
  hintEl.textContent = `Hint: try "${pick}"`;
}

document.getElementById("new-game-btn").addEventListener("click", newGame);
lengthSelect.addEventListener("change", newGame);
difficultySelect.addEventListener("change", newGame);
modeSelect.addEventListener("change", newGame);
submitBtn.addEventListener("click", submitWord);
giveUpBtn.addEventListener("click", giveUp);
hintBtn.addEventListener("click", giveHint);
inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter") submitWord();
});

newGame();
</script>
</body>
</html>
"""

html = HTML_TEMPLATE.replace("__WORDS__", words_json)
HTML_PATH.write_text(html, encoding="utf-8")
print(f"✅ Wrote {len(html):,} bytes to {HTML_PATH}")
