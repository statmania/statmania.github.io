# Snowball

A two-player letter-by-letter word-building duel: you and the computer take
turns appending one letter to a shared, ever-growing string. Whenever the
new letter completes a real word (checked as a suffix of the current
string), the player who placed it scores points equal to that word's
length. The string keeps growing turn after turn — old words don't get
rescored, but a longer word can "swallow" a previous one and score again
(`on` → 2 pts, then `ono` re-forms the word `no` → 2 pts, even though `on`
was already scored and `ono` itself isn't a word).

## 1. Is this possible without an LLM/AI API?

Yes — fully. Nothing here needs language understanding beyond "is this
exact string a dictionary word," which is a lookup, not generation. The
whole game is:

- a static word list (bundled at build time, like `cross-word`'s `cw.xlsx`
  → `cross-word.html` pipeline),
- a `Set`/Trie for O(1) "is this a word" checks,
- a scoring rule applied after every move,
- a computer opponent that's just a search over "which single letter,
  appended now, gives me the best outcome" — a heuristic/minimax over a
  known word list, not a model call.

This is the same category of program as a Scrabble bot or a hangman
solver: deterministic, local, no network calls, no API keys, works
offline once the word list is loaded.

## 2. Rules (as I understand them — please confirm/correct)

These aren't fully pinned down by the two examples given, so I'm stating
my working assumptions explicitly. Anything marked **[ASSUMPTION]** is a
default I'd build to unless you say otherwise.

1. **Turn order & moves.** Players alternate. On your turn you pick one
   letter (a–z) and it is **appended to the end** of the shared string.
   **[ASSUMPTION]** Append-only (not insert-anywhere-in-the-string) — the
   `o → on → ono` example only ever grows at the end. Insert-anywhere
   would be a valid, more complex v2 variant (real "Ghost"-style games
   sometimes allow it), but it roughly doubles the AI search space and
   the UI complexity, so I'd keep it out of v1.
2. **Scoring trigger.** After a letter is appended, look at every suffix
   of the new string (i.e. every substring ending at the letter you just
   placed): `...t.string[i:]` for all `i`. Any suffix that is a valid
   dictionary word scores **[ASSUMPTION: the longest one only]** — points
   equal to its length, awarded to the player who just moved.
   - Why "longest only" and not "sum of all matching suffixes": in the
     `ono` example, if `o` (1-letter) were also separately scored on top
     of `no` (2-letter), the point examples given wouldn't isolate
     cleanly. Longest-suffix-only is simpler to reason about and matches
     how similar games ("Anagrams"/"Snatch"-style) usually score. Happy
     to switch to "sum all valid suffixes" if you want denser scoring.
3. **No rescoring.** A word only scores the turn it's newly formed as a
   suffix. If it remains a substring later (not as a suffix, since the
   string keeps growing past it) it's never checked again — this falls
   out naturally from rule 2 (only suffixes of the *current* string are
   checked, and once more letters are appended, the old word is no longer
   a suffix).
4. **Passing/forced moves.** **[ASSUMPTION]** A player may append *any*
   letter, even one that leads nowhere (no valid word, dead branch) — the
   game doesn't require you to be building toward something. There's no
   "bluff and challenge" mechanic (unlike classic Ghost, where you can be
   challenged to prove a real word is achievable) — Snowball only rewards
   you *when* you complete a word, so a "throwaway" letter is a legal,
   zero-point move.
5. **Round length / end condition.** **[ASSUMPTION]** Game ends after a
   fixed number of total turns (e.g. 20, configurable), or when the
   string hits a max length (e.g. 15 letters), or either player clicks
   "End Game." Highest cumulative score wins. Open to a different end
   condition (e.g. "first to N points," or "play until no valid letter
   exists in the whole dictionary as a continuation" — that last one is
   rare in practice since almost any letter keeps *some* word reachable).
6. **Valid letters.** a–z only, case-insensitive, no spaces/hyphens/
   apostrophes even if the dictionary contains words with them (we'd
   filter those out of the loaded word list).
7. **Starting state.** **[ASSUMPTION]** The string starts empty; the
   first move is really "player 1 places 1 letter," which can itself
   score 1 point if that letter alone is a dictionary word (e.g. `a`,
   `i`, `o` are valid Scrabble words). Matches the `o` → 1pt (implied) →
   `on` → 2pt progression in your example.

None of these need to be locked in before I start — flagging them now so
the first playable version matches what you actually pictured, since
"scoring on suffix only" vs "scoring on any substring" meaningfully
changes both the scoring feel and the AI's strategy.

## 3. Word list

- Source: a public-domain English word list (e.g. SCOWL/ENABLE1 or the
  Scrabble TWL/SOWPODS word lists — both freely redistributable, no
  license issues, and reasonably standard for exactly this kind of
  game).
- Size/trim: full lists run 170k–280k words; we don't need obscure
  8-letter words for a casual browser game. Plan: filter to words of
  length 1–8 (or a configurable cap) and drop anything with non a–z
  characters, cutting the list to a manageable size (rough estimate:
  40–70k words, which gzips to a small enough JSON/JS payload to embed
  directly — no runtime fetch needed, same self-contained-HTML approach
  the other games already use).
- Build step: a small Python script (mirroring `cross-word/build_puzzles.py`)
  reads the raw word list once, filters/lowercases/dedupes it, and bakes
  it into the page as a JSON array (or a compact Trie serialization) —
  not something the browser downloads from a third party at runtime.
- Lookup structure: load the list into a `Set<string>` for exact-word
  checks. For the AI (which needs "does *any* word start with this
  prefix" during search, not just exact matches), build a **Trie** from
  the same list at page load — cheap in JS, done once.

## 4. Computer opponent (no AI model, just search)

Three difficulty tiers, all pure algorithm:

- **Easy** — picks a random legal letter (a–z) that keeps at least one
  word reachable from the resulting prefix (checked via the Trie, so it
  never fully dead-ends the game). Doesn't optimize for points.
- **Medium (default)** — greedy: for each candidate letter, compute the
  score it would immediately score this turn (longest valid suffix), and
  pick the best-scoring legal letter. Ties broken randomly.
- **Hard** — shallow lookahead (minimax/expectimax 2–3 ply) over the
  Trie: also considers what scoring opportunity it's handing the human on
  the *next* turn, and avoids letters that set up a big score for the
  opponent. This is the same kind of small-search-tree logic as a
  tic-tac-toe minimax bot (already in `games/tic-tac-toe.html`) — no
  external model, just recursion over a bounded branching factor (26
  letters, a few ply deep).

## 5. UI/UX plan

Matches the site's existing dark "futuristic" game-page template (see
`games/cross-word.html` for the current reference implementation):

- Header/hero identical pattern to other games (logo, Home/All
  Games/Contact nav, dark starfield hero).
- Main card: 
  - Large display of the current growing string, with the most recent
    scoring word visually highlighted/underlined for a beat after it's
    formed.
  - Score board: You vs Computer, running totals.
  - A log/history panel listing each turn: who played, which letter,
    resulting string, points scored (if any) and the word that scored.
  - Turn indicator + a simple on-screen keyboard (or just a text input
    capturing one keypress) for the human's move, disabled during the
    computer's turn.
  - Difficulty selector (Easy/Medium/Hard) and a "New Game" / "End Game"
    control, styled like the existing button set.
- No build step at runtime — same self-contained single HTML file
  pattern as the other games, with the word list baked in.

## 6. File plan

```
games/snowball/
  build_wordlist.py   # filters raw word list -> embeddable JSON, like build_puzzles.py
  wordlist_raw.txt     # source list (or a pinned download step)
  README / notes
games/snowball.html    # generated, self-contained, same pattern as cross-word.html
```

`games/index.html` gets a new card once this is built, same as the
Crossword card was added.

## 7. Build order (once rules are confirmed)

1. Word list build script + embed into a scratch HTML page; verify
   lookup + Trie prefix search work as expected in the browser console.
2. Core game loop: turn state, append-letter move, suffix-scoring logic,
   score board — playable with **two human players** first (fastest way
   to validate the scoring rule feels right before writing any AI).
2b. Sanity-check the scoring rule against your two examples plus a few
    more by hand before moving on.
3. Computer opponent: Easy → Medium → Hard, in that order.
4. Visual polish to match the dark theme + add to `games/index.html`.
5. Playtest pass, tune difficulty/AI behavior.

## 8. Open questions for you

- Suffix-only scoring vs. "sum every valid suffix word found," per §2.2.
- Append-only vs. insert-anywhere (§2.1) — insert-anywhere is meaningfully
  more work but is closer to real "Ghost"/"Snatch." -- anywhere. 
- Game end condition (§2.5) — fixed turns, max length, point target, or
  manual end? (Allow user to choose -- no of turns, point target whoever reaches first wins etc.)
- Should proper nouns/abbreviations be excluded from the word list (they
  usually are in Scrabble lists already)? --Yes
- Any minimum word length to score (e.g. should 1-letter words like `a`,
  `i`, `o` count, or should scoring only kick in at 2+ letters)? NO
  
# New rules
overrides any conflicting one
- Make a box having certain number of cells, like 20 by 20 or user can determine a cell. Well, by default 20x20 but user can change grid size. 
- If, for example, 'on' is made into 'one', maker gets 3. conversion to 'none' if there is an empty cell before 'o', gives 4 new points, 'nonet' gives 5. 
