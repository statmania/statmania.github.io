# Plan: courses repo, login, unified quiz storage

Status: draft for discussion (2026-09-26). Three related pieces; the suggested order is at the bottom.

## 1. Move `courses/` to its own repo

**Why:** courses will grow (webR, per-course builds, large `site_libs/`), need their own release cycle, and are the part that will get login and a back end.

**Keep the same URLs.** GitHub Pages serves a project repo under the org's custom domain. A repo `statmania/courses` with Pages enabled is served at `www.statmania.info/courses/`, so no redirects or SEO loss. Two conditions:
- the main repo must stop containing a `courses/` folder, otherwise the two conflict;
- the new repo must be named `courses`.

A subdomain (`courses.statmania.info`) is the alternative, but it is a different origin: a login session would not be shared with the main site, and cookies/storage split. **Recommendation: stay on the path `/courses/`.**

**Shared assets.** Courses currently use relative paths (`../../starfield.js`, `../../img/statmania_logo.svg`, `../../starfield-include.html`). In production, switch to root-absolute paths (`/starfield.js`, `/img/...`), which work because both repos share one domain. For local preview, either copy those files in a git-ignored `dev/` folder or run a tiny dev server that serves both repos.

**Things that reference courses and must be updated**
- `raw/courses/index.qmd` (the hub page) moves to the new repo as its own `index.qmd`; the main navbar keeps linking to `/courses/`.
- `courses/discover_quiz_banks.py` and `question/build_quiz.py` currently glob `courses/*/*_question_bank.tex` across the tree. That coupling disappears with section 3.
- `robots.txt` and sitemap lines for `courses/<slug>/sitemap.xml`.
- The `CLAUDE.md` files (split: courses guidance goes to the new repo).

**How:** `git filter-repo --path courses/` (keeps history), push to the new repo, enable Pages, then delete `courses/` from the main repo in the same day. Optional later: a GitHub Action running `quarto render` on push, so rendered HTML no longer has to be committed.

## 2. Login with Firebase (free Spark tier)

**Decide first what login is for. A static site cannot hide its files.** Anything on GitHub Pages is public to anyone with the URL, so client-side login cannot protect lessons.

- **Option A (recommended to start): identity + saved progress.** Lessons stay public (good for SEO and sharing). Signing in unlocks saved quiz scores, per-lesson progress, bookmarks and streaks. Fits the free tier and needs no server.
- **Option B (later, if a course becomes paid or private): real gating.** Needs a server-side check: Firebase Hosting with Cloud Functions (requires the Blaze pay-as-you-go plan, though small usage is usually near zero), or another host with edge auth. Design lessons now with a `premium: true` flag so some can be gated later while the rest stay public.

**Firebase pieces (all client-side JS from a CDN, no build step)**
- **Auth:** Google sign-in plus email link (passwordless), so there are no passwords to reset. Skip phone/SMS auth, which is not free.
- **Firestore:** `users/{uid}/attempts/{questionId}` and `users/{uid}/progress/{lesson}`. Security rules: each user reads and writes only their own `users/{uid}/...`. Add `www.statmania.info` to Firebase's authorized domains.
- **UI:** one small `auth.js` loaded via `include-after-body`. The navbar shows "Sign in" or an avatar. Anonymous visitors keep using `localStorage`; results are migrated to Firestore at first sign-in.
- The Firebase web config is public by design. Safety comes from the security rules (and optionally App Check), not from hiding keys.
- Because the courses stay on the same domain, one session can also drive an avatar on the main site.

**Also needed:** a privacy policy page, an account-deletion path (GDPR-style), and budget alerts. The free tier has hard limits (Auth and Firestore quotas; check the current numbers before launch). Spark does not bill overage, it just stops working.

**Lock-in note:** if we later want relational queries or per-row security, Supabase is the main alternative. Keeping the attempt data as plain JSON documents makes that move easy.

## 3. One place for all quizzes

**Today:** questions live in several LaTeX banks (`question/bank/stat1_mcq_bank.tex`, `stat2_mcq_bank.tex`, `courses/*/*_question_bank.tex`), and the same style of question is hand-written again as HTML `sm-quiz` blocks inside each lesson `.qmd`. `build_quiz.py` (~1400 lines) parses LaTeX to make `stat-prob.html`.

**Proposal: two data files, one per question type, plus a build step.** The types have different shapes, so two files is cleaner than one:
- `quiz/data/mcq.yml`
- `quiz/data/short.yml` (short answer and fill-in-the-blank)

YAML for authoring (multiline text, LaTeX math, easy diffs), compiled to JSON for the browser. Delivery is sharded by course/topic so pages don't download the whole bank.

**Sketch of the schema**
```yaml
# mcq.yml
- id: rprog-variables-001
  course: rprogramming        # or stat1, stat2
  chapter: Variables
  topic: assignment
  tags: [r, assignment]
  difficulty: 1
  stem: "Which operator is the idiomatic way to assign a value in R?"
  choices: ["=", "<-", "==", "->>"]
  answer: 1                   # index into choices
  explanation: "..."
  set: null                   # shared passage id for situation sets
# short.yml
- id: rprog-vectors-004
  type: fitb                  # or short
  prompt: "Fill in the blank: ____(x) returns the number of elements."
  answers: ["length"]         # accepted variants
  case_sensitive: true
```
Situation sets get a shared `context`; "multiple completion" questions are ordinary MCQs whose stem lists the statements.

**Consequences**
- Lessons contain only `<div data-quiz-set="rprogramming/variables">`, and `quiz.js` fetches and renders. No hand-written quiz HTML per lesson.
- With the repo split, the data file lives in the **main** repo and courses fetch `/quiz/data/*.json` (same domain), so there is one source of truth for both repos.
- Add a validator (unique ids, answer within range, non-empty fields) run before each build.
- Keep LaTeX for printed exams: generate `.tex` from the YAML later, instead of hand-editing banks in two formats.
- Answers are visible in the JSON. That is fine for practice; anything graded or paid would need server-side checking (Option B).
- Firestore attempts reference `questionId`, which enables per-question statistics and weak-topic suggestions later.

**Migration:** write a one-time converter reusing the existing LaTeX parser in `build_quiz.py`, review the output, then retire `discover_quiz_banks.py`.

## Suggested order

1. **Quiz data files + renderer** (no external dependencies; settles the data shape).
2. **Split the courses repo** (so auth code lands in the right place).
3. **Firebase login, Option A** (progress and scores).
4. Later: gating (Option B), YAML→LaTeX export, CI render.

## Decisions needed

- Are courses free, paid, or mixed? That decides whether Option B is a real requirement.
- Path (`/courses/`) or subdomain? (Recommend path.)
- Sign-in methods: Google + email link only?
- YAML or JSON for authoring the quiz files?
