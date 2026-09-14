#!/usr/bin/env python3
"""
Reads wordlist.json (built by build_wordlist.py) from this folder and
writes a single self-contained games/snowball.html to the parent folder.
"""
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent      # snowball/
PARENT_DIR = SCRIPT_DIR.parent                    # games/
WORDLIST_PATH = SCRIPT_DIR / "wordlist.json"
HTML_PATH = PARENT_DIR / "snowball.html"

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
<title>Stat Mania - Snowball</title>
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
  .toolbar-left { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; }
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
  button.action:disabled { opacity: 0.4; cursor: not-allowed; transform: none; box-shadow: none; }

  .scoreboard { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }
  .score-tile { background: var(--card); border: 1px solid rgba(255,255,255,0.08);
                border-radius: 14px; padding: 16px 20px; text-align: center;
                transition: border-color 0.2s, box-shadow 0.2s; }
  .score-tile.active { border-color: var(--accent); box-shadow: 0 0 20px rgba(0,229,255,0.25); }
  .score-tile .label { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.08em;
                        color: var(--muted); margin-bottom: 6px; }
  .score-tile .num { font-size: 2.2rem; font-weight: 800; color: var(--ink); }
  .score-tile.you .num { color: var(--accent); }
  .score-tile.cpu .num { color: #a855f7; }

  .board-wrap { background: var(--card); border: 1px solid rgba(255,255,255,0.08);
                border-radius: 14px; padding: 28px 20px; text-align: center; margin-bottom: 20px;
                min-height: 90px; display: flex; align-items: center; justify-content: center; }
  .board-string { font-family: 'Courier New', monospace; font-size: 2.2rem; font-weight: 700;
                   letter-spacing: 0.15em; color: var(--muted); word-break: break-all; }
  .board-string .placed { color: var(--ink); }
  .board-string .scored { color: var(--good); text-shadow: 0 0 14px rgba(74,222,128,0.6); }
  .board-string .empty-hint { color: var(--muted); font-size: 1.1rem; letter-spacing: normal;
                               font-family: 'Inter', sans-serif; font-weight: 500; }

  .turn-indicator { text-align: center; margin-bottom: 16px; font-size: 0.9rem; color: var(--muted); }
  .turn-indicator .pill { display: inline-block; padding: 4px 14px; border-radius: 999px;
                           font-weight: 700; border: 1px solid rgba(255,255,255,0.18); }
  .turn-indicator .pill.you { color: var(--accent); border-color: rgba(0,229,255,0.4); }
  .turn-indicator .pill.cpu { color: #a855f7; border-color: rgba(168,85,247,0.4); }

  .keyboard { display: grid; grid-template-columns: repeat(9, 1fr); gap: 6px; max-width: 560px;
              margin: 0 auto 24px; }
  .keyboard button { border: none; background: rgba(255,255,255,0.05); color: var(--ink);
              border: 1px solid rgba(255,255,255,0.14); border-radius: 8px; padding: 10px 0;
              font-size: 1rem; font-weight: 700; cursor: pointer; font-family: inherit;
              transition: background 0.12s, border-color 0.12s, transform 0.1s; }
  .keyboard button:hover:not(:disabled) { border-color: var(--accent); background: rgba(0,229,255,0.1); }
  .keyboard button:active:not(:disabled) { transform: scale(0.93); }
  .keyboard button:disabled { opacity: 0.3; cursor: not-allowed; }
  @media (max-width: 560px) { .keyboard { grid-template-columns: repeat(7, 1fr); } }

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
                    Snowball
                </h1>
                <p class="text-lg sm:text-xl sm-subtitle-sm">Add one letter at a time and outscore the computer at making words</p>
            </div>
        </section>

        <!-- Game Section -->
        <section class="py-12 px-4 sm:px-6 lg:px-8 bg-slate-50">
            <div class="container mx-auto max-w-3xl">
                <div class="sm-card p-8">
                    <div class="toolbar">
                        <div class="toolbar-left">
                            <select id="difficulty-select" aria-label="Computer difficulty">
                                <option value="easy">Easy</option>
                                <option value="medium" selected>Medium</option>
                                <option value="hard">Hard</option>
                            </select>
                            <select id="length-select" aria-label="Round length">
                                <option value="12">Short (12)</option>
                                <option value="20" selected>Medium (20)</option>
                                <option value="30">Long (30)</option>
                            </select>
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
                    </div>

                    <div class="turn-indicator" id="turn-indicator"></div>

                    <div class="board-wrap">
                        <div class="board-string" id="board-string"></div>
                    </div>

                    <div class="keyboard" id="keyboard"></div>

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
            <p class="mb-4">&copy; 2024 Stat Mania. All rights reserved.</p>
            <div class="flex justify-center space-x-6">
                <a href="#" class="text-slate-300 hover:text-white transition duration-300">Privacy Policy</a>
                <a href="#" class="text-slate-300 hover:text-white transition duration-300">Terms of Service</a>
                <a href="#" class="text-slate-300 hover:text-white transition duration-300">Sitemap</a>
            </div>
        </div>
    </footer>

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
   CORE RULES
   Longest suffix of the current string that is a real word scores
   (points = word length) for whoever just moved. Append-only.
   ============================================================ */
function bestSuffix(str) {
  for (let i = 0; i < str.length; i++) {
    const sub = str.slice(i);
    if (WORD_SET.has(sub)) return { word: sub, len: sub.length };
  }
  return null;
}

function scoreLetter(str, letter) {
  const next = str + letter;
  const hit = bestSuffix(next);
  return { next, hit, points: hit ? hit.len : 0 };
}

/* ============================================================
   COMPUTER AI
   Easy: uniform random letter.
   Medium: greedy - picks the letter that scores the most right now.
   Hard: 2-ply - also minimizes the best reply the opponent could
   score next turn (str + myLetter + theirLetter).
   ============================================================ */
function aiPickLetter(str, difficulty) {
  if (difficulty === "easy") {
    return LETTERS[Math.floor(Math.random() * LETTERS.length)];
  }

  if (difficulty === "medium") {
    let best = [];
    let bestPts = -1;
    for (const l of LETTERS) {
      const { points } = scoreLetter(str, l);
      if (points > bestPts) { bestPts = points; best = [l]; }
      else if (points === bestPts) { best.push(l); }
    }
    return best[Math.floor(Math.random() * best.length)];
  }

  // hard: 2-ply
  let best = [];
  let bestValue = -Infinity;
  for (const l of LETTERS) {
    const { next, points } = scoreLetter(str, l);
    let oppBest = 0;
    for (const l2 of LETTERS) {
      const { points: p2 } = scoreLetter(next, l2);
      if (p2 > oppBest) oppBest = p2;
    }
    const value = points - oppBest;
    if (value > bestValue) { bestValue = value; best = [l]; }
    else if (value === bestValue) { best.push(l); }
  }
  return best[Math.floor(Math.random() * best.length)];
}

/* ============================================================
   STATE
   ============================================================ */
let state = null;

function newGame() {
  state = {
    str: "",
    turn: "you",
    scores: { you: 0, cpu: 0 },
    history: [],
    roundLength: parseInt(document.getElementById("length-select").value, 10),
    difficulty: document.getElementById("difficulty-select").value,
    over: false,
  };
  document.getElementById("end-banner").style.display = "none";
  render();
}

/* ============================================================
   MOVES
   ============================================================ */
function playLetter(letter) {
  if (!state || state.over) return;
  const player = state.turn;
  const { next, hit, points } = scoreLetter(state.str, letter);
  state.str = next;
  state.scores[player] += points;
  state.history.push({ player, letter, str: next, word: hit ? hit.word : null, points });

  if (state.str.length >= state.roundLength) {
    endGame();
    return;
  }

  state.turn = player === "you" ? "cpu" : "you";
  render();

  if (state.turn === "cpu" && !state.over) {
    document.getElementById("keyboard").querySelectorAll("button").forEach(b => b.disabled = true);
    setTimeout(() => {
      if (!state || state.over) return;
      const cpuLetter = aiPickLetter(state.str, state.difficulty);
      playLetter(cpuLetter);
    }, 550);
  }
}

function endGame() {
  if (!state) return;
  state.over = true;
  render();
  const banner = document.getElementById("end-banner");
  const { you, cpu } = state.scores;
  banner.style.display = "block";
  if (you > cpu) {
    banner.className = "win";
    banner.textContent = `🎉 You win! ${you} - ${cpu}`;
  } else if (cpu > you) {
    banner.className = "lose";
    banner.textContent = `🤖 Computer wins. ${cpu} - ${you}`;
  } else {
    banner.className = "tie";
    banner.textContent = `🤝 It's a tie! ${you} - ${cpu}`;
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
  if (state.over) {
    turnEl.innerHTML = `Game over — ${state.str.length}/${state.roundLength} letters played`;
  } else {
    const who = state.turn === "you" ? "you" : "cpu";
    const label = state.turn === "you" ? "Your turn" : "Computer's turn";
    turnEl.innerHTML = `<span class="pill ${who}">${label}</span> &middot; ${state.str.length}/${state.roundLength} letters`;
  }

  renderBoard();
  renderHistory();
  renderKeyboard();
}

function renderBoard() {
  const el = document.getElementById("board-string");
  if (!state.str) {
    el.innerHTML = `<span class="empty-hint">Pick a letter to begin</span>`;
    return;
  }
  const lastMove = state.history[state.history.length - 1];
  let html = "";
  for (let i = 0; i < state.str.length; i++) {
    const inLastWord = lastMove && lastMove.word && i >= state.str.length - lastMove.word.length;
    const cls = inLastWord ? "scored" : "placed";
    html += `<span class="${cls}">${state.str[i].toUpperCase()}</span>`;
  }
  el.innerHTML = html;
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
    const desc = h.word ? `+${h.player === "you" ? "you" : "cpu"} played '${h.letter}' → ${h.str} (${h.word})` : `played '${h.letter}' → ${h.str}`;
    const pts = h.points > 0 ? `<span class="pts">+${h.points}</span>` : `<span class="pts zero">0</span>`;
    return `<div class="hist-row"><span class="who ${whoCls}">${who}</span><span>${h.str}${h.word ? ` — <em>${h.word}</em>` : ""}</span>${pts}</div>`;
  }).join("");
}

function renderKeyboard() {
  const el = document.getElementById("keyboard");
  el.innerHTML = "";
  const disabled = state.over || state.turn !== "you";
  LETTERS.forEach(l => {
    const btn = document.createElement("button");
    btn.textContent = l.toUpperCase();
    btn.disabled = disabled;
    btn.addEventListener("click", () => playLetter(l));
    el.appendChild(btn);
  });
}

/* ============================================================
   WIRE UP
   ============================================================ */
document.getElementById("new-game-btn").addEventListener("click", newGame);
document.getElementById("end-game-btn").addEventListener("click", () => { if (state && !state.over) endGame(); });
document.getElementById("difficulty-select").addEventListener("change", () => { if (state) state.difficulty = document.getElementById("difficulty-select").value; });

document.addEventListener("keydown", (e) => {
  if (!state || state.over || state.turn !== "you") return;
  const k = e.key.toLowerCase();
  if (LETTERS.includes(k)) playLetter(k);
});

newGame();
</script>
</body>
</html>
"""

html = HTML_TEMPLATE.replace("__WORDS__", words_json)
HTML_PATH.write_text(html, encoding="utf-8")
print(f"✅ Wrote self-contained HTML → {HTML_PATH}")
