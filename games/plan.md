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
