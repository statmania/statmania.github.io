# Games — ideas for what's next

A running list of game concepts in the same spirit as what's already here
(`add-sub`, `guess-number`, `math-challenge`, `tic-tac-toe`,
`reverse-tic-tac-toe`, `cross-word`, `wordweave`): self-contained,
single-file, dark-themed, no LLM/AI-model API — any "smart" opponent is
plain local search (minimax, greedy, word-list lookup), same as the
tic-tac-toe minimax bot and WordWeave's AI tiers.

## Word / vocabulary games

- **Word Ladder** — turn one word into another one letter at a time,
  each step a valid word (`cat` → `cot` → `cog` → `dog`). Single-player
  against a par (shortest path via BFS over the word list, computed at
  build time or on the fly), or race the computer to see who finds a
  shorter chain. Reuses the WordWeave word list directly.
- **Word Search / Boggle** — random letter grid (fixed or rolling
  dice-style), find as many valid words as possible (reading in any of
  8 directions) before time runs out. Scoring by word length, same
  word-list lookup as WordWeave. No opponent needed for a first version;
  could add a "computer also searches the same grid" race mode later.
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

- **Sudoku** — generate + validate puzzles at a chosen difficulty,
  highlight conflicts live. Popular, no AI opponent required, purely a
  generator/validator problem (backtracking solver used at build/generate
  time only).
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
bigger ones (Sudoku, Nonogram, Word Search) as time allows.
