# Snowball

A crossword/Scrabble-style word-building duel against a local (no
LLM/API) computer opponent, built entirely from a static dictionary and
plain JS search — no network calls, no model.

## Rules

- **Grid.** Rectangular, size chosen by the user before starting
  (rows × cols freely, e.g. 20×20, 30×10, 10×15 — not limited to
  squares), default 20×20.
- **Turns.** Players alternate. On your turn, click an empty *legal*
  cell to select it, then type one letter into it (no on-screen
  keyboard — same click-then-type interaction as the crossword game's
  cells).
- **Legal placement.** The first letter of the game can go anywhere.
  Every letter after that must be placed orthogonally adjacent
  (up/down/left/right, not diagonal) to an already-filled cell, so the
  board grows as one connected cluster. Legal cells are highlighted on
  your turn.
- **Scoring.** After a letter is placed, check the maximal contiguous
  run through that cell in both directions: across (its row) and down
  (its column). Each run of length ≥2 that is a valid dictionary word
  scores points equal to its length, for whoever just placed the
  letter — one move can score twice (once across, once down).
- **No overwriting.** Cells are permanent once filled; a word only
  scores again if a new letter extends it into a longer valid word.
- **Computer opponent.** Three tiers, all local search over the word
  list (no model): Easy (random legal cell + letter), Medium (greedy —
  picks the cell/letter scoring the most right now), Hard (shallow
  lookahead that also avoids setting up a big score for the opponent).
- **Game end.** Chosen before "New Game": a fixed number of turns, or
  first player to reach a target score (both configurable), plus a
  manual "End Game" button always available. A "Winner" tile sits to
  the right of the score tiles and fills in once the game ends.
- **Who starts.** Chosen before "New Game": You, Computer, or Coin
  Toss. Note the first move of any game always scores 0 (no run can be
  ≥2 letters yet), so whoever goes first is at a small structural
  disadvantage — the second mover gets the first real shot at scoring.

## Word list

System dictionary (`/usr/share/dict/american-english`), filtered to
lowercase-only, 2–8 letters plus `a`/`i`/`o`, with abbreviations/units/
Roman numerals stripped, keeping only root-form vocabulary (no
plurals, past tense, `-ing`, comparative/superlative, or `-ly`
adverbs): if removing a trailing s/es/ies/ed/ing/er/est/ly leaves
another word already in the list, the longer one is dropped as
derived — with a manual exception list for coincidental matches
(`pass`/`mass`/`yes`, `sheer`/`sober`/`archer`, `apply`/`early`/
`curly`, etc.) that only happen to end like a derived form without
actually being one. ~17.3k words. Embedded at build time
— same pipeline as `cross-word/build_puzzles.py`.

## Files

```
games/snowball/
  wordlist_raw.txt     # source dictionary
  build_wordlist.py    # filters -> wordlist.json
  build_game.py         # embeds wordlist.json -> ../snowball.html
games/snowball.html     # generated, self-contained
```
## Word sources

If we keep getting unwanted words, we'll use one these sources. 

- **ENABLE1** (Enhanced North American Benchmark Lexicon) — a public-domain word list built specifically for word games, ~173k words, no plurals/proper-nouns/abbreviations mixed in the way a spellcheck dictionary has.
- **TWL06 / OWL (Tournament Word List)** or **SOWPODS/Collins Scrabble Words** — the actual word lists used in competitive Scrabble. These are curated precisely to answer "is this a valid word," which is exactly the game's need, and they already exclude proper nouns and abbreviations by design.
- **SCOWL** (Spell Checking Oriented Word Lists) — what the current `/usr/share/dict/american-english` is derived from; SCOWL itself can be regenerated with different size/strictness levels and word-class filters (it has tags for abbreviations, proper nouns, etc.), so a more carefully-configured SCOWL export would already exclude most of what's being manually stripped now.

Any of these would sidestep the whole "reconstruct which words are abbreviations/plurals/derived forms by hand" effort — the source list simply wouldn't contain them in the first place. The catch is they're not already sitting on disk the way `/usr/share/dict/american-english` was, so pulling one in requires fetching a file into the project rather than reusing something local.
