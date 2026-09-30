# Games — ideas for what's next

A running list of game concepts in the same spirit as what's already here
(`add-sub`, `guess-number`, `math-challenge`, `tic-tac-toe`,
`reverse-tic-tac-toe`, `cross-word`, `wordweave`): self-contained,
single-file, dark-themed, no LLM/AI-model API — any "smart" opponent is
plain local search (minimax, greedy, word-list lookup), same as the
tic-tac-toe minimax bot and WordWeave's AI tiers.

## Word / vocabulary games

- ~~**Word Ladder**~~ **Built** — `games/word-ladder.html`. Turn one
  word into another one letter at a time; the ladder graph (wildcard
  pattern buckets, not an all-pairs comparison) and BFS shortest path
  are computed client-side on the fly from the WordWeave word list, so
  there's no separate build-time data step. "Computer's Best" par is
  shown alongside your step count, with Hint (BFS distance-to-target,
  costs a rating downgrade) and Give Up (reveals one optimal path).
  Length (3-6 letters) and difficulty (par-range) are selectable.
- ~~**Word Search / Boggle**~~ **Built** — `games/word-search.html`.
  Classic 4×4 or Big 5×5 boards rolled from the real Boggle/Big Boggle
  dice sets (including the "Qu" die face), found via pointer-drag
  selection across 8-directional adjacency. When the timer runs out, a
  trie + bitmask-DFS solver exhaustively finds every valid word on that
  exact board to reveal what you missed. Standard Boggle scoring
  (length-based points, no double-counting a word).
- **Word Chain (Shiritori)** — the *other* obvious mechanic once you
  have a word list and a lemma-checker: each player says a word
  starting with the last letter of the previous word, no repeats. Much
  simpler build than WordWeave (no grid, no adjacency, no dual-axis
  scoring) — good "quick win" alongside it.
- **Hangman** — classic, guess letters before the drawing completes.
  Computer picks the secret word; for an extra twist, computer could
  play adversarially (Knuth's "worst-case Hangman" — keeps the answer
  ambiguous as long as possible instead of committing to one word up
  front), which is a fun bit of algorithm to show off without any AI.
- **Mastermind / Bulls & Cows** — guess a secret 4-letter/4-digit code,
  get "exact match" / "right symbol wrong spot" feedback each round.
  Classic constraint-search puzzle; computer-as-codemaker is trivial,
  computer-as-codebreaker (Knuth's 5-guess algorithm) is a nice small
  search-algorithm showcase similar to the tic-tac-toe minimax bot.
- **Anagram Sprint** — scrambled letters, find every valid word you can
  make (or the longest one) before time runs out. Reuses the word list;
  scoring by length, same shape as Math Challenge's timed format.

## Classic board games (minimax/heuristic AI, like tic-tac-toe)

- **Connect Four** — natural next step up in complexity from the
  existing tic-tac-toe / misère tic-tac-toe pair; minimax with
  alpha-beta pruning and a shallow depth cap plays strong without being
  unbeatable.
- **Othello / Reversi** — same minimax-family AI, more visually
  distinctive (flipping discs) than another X/O grid.
- **Nim** — deceptively simple pile-based game with a *provably
  optimal* strategy (binary XOR of pile sizes) — the "AI" is a one-line
  formula, not search, which is a neat one to build fast.

## Logic / puzzle (single-player, no opponent needed)

- ~~**Sudoku**~~ **Built (mini sizes)** — `games/sudoku.html`. 10 puzzles
  across three sizes: 4×4 and 6×6 (classic square variants) plus 6×4
  (4 rows × 6 cols — rows/boxes are full 1-6 permutations same as any
  sudoku; columns are just too short to contain every digit, so they're
  only checked for "no repeat"). Backtracking generator + uniqueness
  checker at build time (`games/sudoku/build_sudoku.py`), all 10
  verified to have exactly one solution. Full 9×9 not attempted yet -
  same pipeline should scale, just slower to generate/verify.
- **Minesweeper** — classic grid-reveal puzzle, no opponent at all,
  just a good first-click-is-always-safe generator and flood-fill reveal.
- **2048** — sliding-tile merge puzzle, single-player, satisfying to
  build (grid animation) and to play.
- **Nonogram (Picross)** — row/column numeric clues resolve into a
  picture; more build effort (puzzle generation needs care to guarantee
  a unique solution) but a good fit for the site's puzzle-game shelf.

## Probability / stats-flavored (fits the site's "Stat Mania" identity)

- ~~**Monty Hall Simulator**~~ **Built** — `games/monty-hall.html`. Play
  the classic three-door problem repeatedly (stick vs. switch), tally
  win rates live against the theoretical 1/3 vs 2/3, plus an
  auto-simulate mode (instant N trials) to watch the law of large
  numbers converge on the theoretical odds.
- **Dice/Coin Streak Prediction** — guess how long a streak will run
  before it breaks; scores against the actual geometric-distribution
  odds. Similar spirit to Guess the Number but framed around a
  probability concept.

## Suggested order

If picking a next one: **Word Chain** (cheapest — reuses the WordWeave
word list and build pipeline almost as-is) → **Connect Four** (reuses
the tic-tac-toe minimax pattern, rounds out the board-game shelf) →
**Mastermind** (novel mechanic, still a small self-contained build) →
bigger ones (Nonogram, Minesweeper, 2048) as time allows.

## For Understanding Data (ranked by fun)

A handful of number/stats-flavored games would fit this site's "Stat
Mania" identity nicely (same spirit as the existing Monty Hall
simulator). Ordered by how fun/replayable each would actually be to
play, not by build effort or pedagogical value — the two don't always
line up; a couple of the most pedagogically important ones (Confidence
Interval Coverage, Simpson's Paradox) are deliberately last because
they're closer to a watch-it-happen simulator than a scored game.

- **Higher or Lower: Data Edition** — classic "which is bigger" streak
  game (à la higherlowergame.com), but the trivia deck is real stats
  (populations, GDPs, record highs, distances). Dead simple to build,
  a proven-addictive format, and endless replay from just reshuffling
  the deck.
- **Monte Carlo Pi Darts** — throw random darts at a square with an
  inscribed circle to estimate π, racing the clock to land within some
  tolerance. Same "click and watch it happen" satisfaction as Dirt
  Toss/Particle Pop, and a genuinely elegant demo of Monte Carlo
  estimation.
- **Guess the Correlation** — shown a scatterplot, guess r (score by
  closeness). The best-known "stats game" format for a reason: fast,
  satisfying, and builds real intuition for what a given r looks like.
- **Chart Crimes** — shown a manipulated chart (truncated y-axis, dual
  axes, cherry-picked range, reversed axis), spot what's wrong. Quiz
  format with a "gotcha" reveal; doubles as media-literacy content.
- **Regression Golf** — drag a line through a scatterplot, scored by
  sum-of-squared-errors against "par" (the true least-squares fit)
  across a few holes of increasing noise. A more game-shaped version of
  the original "Fit the Regression Line" idea.
- **Number Sense Sprint** — Math Challenge's timed rapid-fire format,
  aimed at data literacy instead of arithmetic: "which is closer to a
  million," quick percent-of, order-of-magnitude estimates. Cheap to
  build by reusing the existing Math Challenge scaffolding.
- **Benford's Law Detective** — shown a dataset's leading-digit
  distribution, guess whether it's real-world data (which tends to
  follow Benford's Law) or fabricated. Mystery framing turns an obscure
  statistical fact into a fun "aha."
- **Birthday Paradox Roulette** — guess how many people are needed in a
  room before there's a 50/50 chance two share a birthday, then watch a
  simulated room fill up and reveal the answer. One classic
  counterintuitive result, gamified as a bet-then-reveal.
- **Random Walk Race** — watch a live random walk (stock-price-style)
  and bet whether it'll be up or down N steps later. Cheap thrill, and
  a good vehicle for teaching that a pure random walk still "looks"
  trendy with zero real signal behind it.
- **Which Average?** — rapid-fire multiple choice: given a weird
  dataset (skewed, bimodal, categorical, with outliers), pick whichever
  of mean/median/mode is the least misleading summary. Same fast-quiz
  shape as Number Sense Sprint.
- **Distribution Guesser** — shown a histogram or sample, guess which
  distribution generated it (normal, uniform, exponential, skewed,
  bimodal). More academic than the above, but a solid visual
  pattern-matching game.
- **Data Detective: Correlation vs. Causation** — given a real
  correlated pair of variables, pick the likeliest explanation (causal,
  reverse-causal, confounder, coincidence). Quiz format, same
  media-literacy spirit as Chart Crimes.
- **Spot the Outlier / Box Plot Hunt** — identify outliers or
  misleading points in a visualized dataset. Solid but more puzzle than
  game — lower replay value once you've learned to spot the trick.
- **Bayesian Update Game** — a repeated decision game on a base-rate
  scenario (e.g. disease testing): update your probability estimate
  each round as new evidence arrives, scored against the true
  posterior. Teaches base-rate neglect well, but more cerebral than fun.
- **Confidence Interval Coverage** — simulate many random samples and
  their CIs, watch visually how often they capture the true parameter.
  Excellent for building intuition for what "95% confidence" actually
  means, but it's a watch-it-converge simulator (like Monty Hall) more
  than a scored game.
- **Simpson's Paradox Explorer** — toggle between aggregated and
  grouped views of a dataset to watch a correlation reverse. Same
  category as Confidence Interval Coverage: a great "aha" tool, low on
  game mechanics.

## Particle Pop — global leaderboard (future)

Current state: the Top 10 is stored per time limit in the browser's
`localStorage` (`particlePop.top10.<seconds>`), so it is per-device only
and can be edited by the player. A shared/global board needs a small
backend. The site is static (GitHub Pages), so the options are:

**Free**
- **Supabase** (Postgres + auto REST API, free tier ~500 MB). Best fit:
  one `scores` table, Row Level Security allowing public insert/select,
  and a `top10` view. Call it from the page with plain `fetch`.
  Caveat: free projects pause after ~1 week of inactivity.
- **Firebase Firestore** (Spark plan, generous free quota). Simple JS
  SDK, security rules can validate score ranges. Client SDK adds weight.
- **Cloudflare Workers + D1 (or KV)** (free tier, no pausing). A ~30-line
  Worker exposes `POST /score` and `GET /top10`; validation and rate
  limiting live server-side. Most robust free option, slightly more setup.
- **Google Sheets + Apps Script web app** — zero-cost hack; fine for a
  hobby board but slow and easy to abuse.
- **GitHub Pages stays as hosting** for the game itself in all cases;
  only the score API needs a host.

**Paid / scalable**
- Supabase Pro (~$25/mo), Firebase Blaze (pay-as-you-go), PlanetScale /
  Neon, or a small VPS (~$4–6/mo) running Node + SQLite. Only worth it
  if traffic or anti-cheat needs outgrow the free tiers.

**Recommendation:** Cloudflare Worker + D1 (or Supabase for the least
code). Store `{name, score, clicks, hits, seconds, ts}`, keep only the
top 10 per time limit (delete rows below rank 10 on insert), and reject
impossible submissions server-side (score ≤ clicks × 20, hits ≤ clicks,
clicks ≤ a sane per-second cap). Client-side scores can always be faked,
so treat the board as for-fun, not tamper-proof.

## Next click-style games (ideas, in the spirit of Particle Pop)

Fast, replayable, top-10-board-friendly games that also teach a stats idea.
Shared top-10/localStorage code from Particle Pop could be factored into
one reusable file first.

1. **Bias Buster** — dots appear from a hidden distribution; click the
   ones you think are outliers before they fade. Scores like Particle
   Pop, teaches z-scores / spotting outliers. *Best fit for the site.*
2. **Streak Chaser** — rounds of coin flips or dice; click to lock in a
   "hot hand" before the streak breaks. Shows how streaks appear in pure
   randomness.
3. **Whack-a-Mean** — numbers pop up in a grid; tap the ones above the
   running average before they vanish. The target moves as the average
   updates.
4. **Target Tempo** — a shrinking ring; click at the right moment, with
   points based on timing accuracy. Same top-10 board fits.
5. **Sequence Sniper** — Simon-style memory game using number patterns.
