# CLAUDE.md — courses/

Guidance for adding to or working on the `courses/` section. Read this before
touching anything here; it documents real bugs already hit and fixed once —
don't re-derive them from scratch.

## How to Name Files

* Name them by topic
* Example: variables.qmd, functions.qmd
* Not: lesson1.qmd, lesson2.qmd
* We would then order them in _quarto.yml as required

## Structure

- `courses/index.html` — the course **hub page**. Quarto-rendered from
  `raw/courses/index.qmd` (part of the `raw/` project — see the top-level
  `CLAUDE.md`), using the shared site navbar and the `.sm-*` hero/card/footer
  components in `raw/styles.css`. One card per course, links to
  `<slug>/index.html`. Edit `raw/courses/index.qmd` and run
  `quarto render` from `raw/` when adding a new course card — don't hand-edit
  `courses/index.html` directly, it will be overwritten.
- `courses/<slug>/` — one self-contained **Quarto website project per
  course** (its own `_quarto.yml`, own `site_libs/`, own dark theme). Each
  course is independent — don't share `_quarto.yml` or theme files across
  courses; copy and adapt the reference implementation instead.
- `courses/rprogramming/` is the **reference implementation**. Copy its
  structure for any new course rather than starting from a blank
  `_quarto.yml` — it already has every fix below baked in.

## Why a separate Quarto project per course

A multi-lesson course needs per-page sidebar navigation with active-page
highlighting, breadcrumbs, and prev/next links. Quarto's `website: sidebar:`
and `page-navigation: true` give all of that for free from a list in
`_quarto.yml`; hand-rolling it in static HTML means duplicating and
hand-syncing nav state across every lesson file. This was a deliberate
choice after prototyping both — see git history around the `courses/`
directory for the reasoning if you want the full comparison.

The hub page (`courses/index.html`) is a single flat page — no sidebar/prev-
next needed — so it's just a normal `raw/` qmd page like the games/utility
hubs, not its own Quarto project.

If a future course is a single self-contained interactive page (not a
multi-lesson sequence), hand-written HTML matching individual `games/`/
`utility/` tool pages is still the better fit — don't force everything into
Quarto.

## Design system: match the site's futuristic dark theme

Every course project needs its own `dark.scss` (copy
`courses/rprogramming/dark.scss` as the starting point) with these tokens,
matching `raw/styles.css` and `games/css/dark-theme.css`:

```scss
$sm-bg: #05070d;      // page background
$sm-bg2: #0a0f1e;     // panel / code-block background — NOT $sm-bg.
$sm-cyan: #00e5ff;
$sm-purple: #a855f7;
$sm-pink: #ff2fb4;
```

**Use `$sm-bg2` for anything that should read as a distinct panel** (code
blocks, cards, the sidebar). Using `$sm-bg` for panels makes them blend into
the page — this was a real bug, caught and fixed once already.

### Sidebar width

Don't set `width` on `#quarto-sidebar` directly — Quarto bakes the sidebar
width into the page's CSS grid track widths **at build time** from the
`$grid-sidebar-width` SCSS variable (default 250px). A plain CSS width
override resizes only the sidebar box, not the grid, which clips the
content column. Set the variable instead:

```scss
$grid-sidebar-width: 300px !default;
```

### Sidebar item styling

Default Quarto sidebar items are color-only on hover/active with no padding
or background. To match the site's card/pill aesthetic, give
`.sidebar-item-container > a` real padding + border-radius, and give the
active item (`.sidebar-item a.active`) a background tint + a
`box-shadow: inset 3px 0 0 0 $sm-cyan` left border instead of just changing
text color. See `dark.scss` for the exact rules.

### The navbar logo bug (real, already hit)

Quarto auto-classifies a theme as "dark" from `$body-bg` and always renders
the navbar logo (`logo:` in `_quarto.yml`) wrapped in a `.light-content`
class — Quarto's own base CSS then does
`body.quarto-dark .light-content { display: none !important; }`, which
hides the logo, even though there's no light/dark toggle UI anywhere on the
page. Fix (already in `dark.scss`, copy it):

```scss
.navbar-logo.light-content {
  display: inline-block !important;
}
```

Don't try to fix this by adding the `quarto-dark` class to `<body>`
yourself — that's what triggers the bug in the first place if you do it for
an unrelated reason (see the quarto-webr section below for exactly that
trap).

## Live code with quarto-webr (if the course needs it)

`courses/rprogramming` uses the `coatless/quarto-webr` extension
(`_extensions/coatless/webr/`, installed via
`quarto add coatless/quarto-webr`) for real client-side R execution —
Monaco editor + a shared R session per page. A `.qmd` lesson using it:

```markdown
---
title: "..."
engine: knitr
filters:
  - webr
webr:
  show-startup-message: false
---

​```{webr-r}
1 + 1
​```
```

### Monaco stays white without help

The extension's Monaco editor hardcodes `theme: 'vs-light'` at creation and
only switches to `vs-dark` in response to that same `quarto-dark` body
class — which, again, this site never sets (no light/dark toggle). Two
wrong ways to fix this, both already tried and reverted:

1. Setting `document.body.classList.add('quarto-dark')` — fixes Monaco but
   triggers the navbar-logo bug above (and any other `.light-content` /
   `.dark-content` conditional content on the page).
2. Nothing — editor stays white, mismatched with the rest of the dark UI.

The actual fix, already in `courses/rprogramming/qwebr-force-dark.js`:
bypass the class-driven helper entirely and set each Monaco instance's
`theme` option directly, polled for a few seconds after load (editors mount
asynchronously as webR initializes):

```js
(window.qwebrEditorInstances || []).forEach(function (editor) {
  editor.updateOptions({ theme: 'vs-dark' });
});
```

Wire it via `format.html.include-after-body` in `_quarto.yml`.

### Error output styling

`quarto-webr` output already distinguishes stdout from stderr —
`.qwebr-output-code-stdout` vs `.qwebr-output-code-stderr` — so error text
just needs `color: #ff8a8a !important` on the `-stderr` class. No JS
MutationObserver hacking needed (an earlier attempt built one before
noticing the extension already provides this).

### Don't hand-write prev/next links

Quarto's `page-navigation: true` (in `website:`) generates working
previous/next footer links automatically from the sidebar's `contents:`
order. Don't add manual "Previous: ... · Next: ..." lines to lesson
content — remove them if you find them, they're redundant and can drift out
of sync with the actual sidebar order.

## Per-lesson quizzes and "discuss first" prompts

`courses/rprogramming` has a small, self-contained quiz component
(`quiz.js` + styles in `dark.scss`) — no server, no R needed to grade it,
so it works the same whether or not webR has finished loading. Wire it via
`format.html.include-after-body` in `_quarto.yml` (already done for this
course; copy for a new one). Two raw-HTML block types:

- **Discussion prompt**, placed *before* the `{webr-r}` chunk so learners
  form an expectation before running/seeing the answer:
  ```html
  <div class="sm-discuss">
    <p class="sm-discuss-label"><i class="fa-solid fa-comments"></i>Discuss first</p>
    <p>Before you run the code below: ... what do you expect and why?</p>
  </div>
  ```
- **Quiz block**, placed after the chunk under a `## Check your understanding`
  heading. `data-quiz="mcq"` + `data-answer` (matches a radio `value`,
  case-insensitive):
  ```html
  <div class="sm-quiz" data-quiz="mcq" data-answer="b">
    <p class="sm-quiz-q"><strong>Q1.</strong> ...?</p>
    <div class="sm-quiz-options">
      <label><input type="radio" name="q-<lesson>-1" value="a"> ...</label>
      <label><input type="radio" name="q-<lesson>-1" value="b"> ...</label>
    </div>
    <button class="sm-quiz-check">Check Answer</button>
    <div class="sm-quiz-feedback"></div>
  </div>
  ```
  `data-quiz="fitb"` (fill-in-the-blank, exact-string match after trimming —
  case-sensitive, since R identifiers are) wraps a `.sm-quiz-blank` text
  input, e.g. for "what function goes in the blank of `____(x)`":
  ```html
  <div class="sm-quiz" data-quiz="fitb" data-answer="length">
    <p class="sm-quiz-q"><strong>Q2.</strong> Fill in the blank: ...</p>
    <div class="sm-quiz-fitb-row">
      <span>____(x)</span>
      <input type="text" class="sm-quiz-blank" placeholder="function name" autocomplete="off" spellcheck="false">
    </div>
    <button class="sm-quiz-check">Check Answer</button>
    <div class="sm-quiz-feedback"></div>
  </div>
  ```
  Use a unique `name="q-<lesson>-N"` per MCQ radio group per lesson page so
  multiple quizzes on one page don't collide.

The `your-turn.qmd`-style sandbox/practice page doesn't get a quiz — it has
no single "correct" answer to check.

## Navbar branding format

Every course's `_quarto.yml` navbar should read, left to right: **logo,
"Stat Mania", the course name**, then a link back to the hub. Set this via
`website.title`, not a separate hard-coded element:

```yaml
website:
  title: "Stat Mania · <Course Name>"
  navbar:
    logo: ../../img/statmania_logo.png
    left:
      - href: ../../index.html
        text: Home
        icon: house
      - href: ../index.html
        text: All Courses
        icon: mortarboard
```

(The `sidebar.title` can stay just the course name — that's fine, it's
inside the course's own context already.)

## Checklist for a new course

1. `mkdir courses/<slug> && cd courses/<slug>`
2. Copy `_quarto.yml`, `dark.scss`, `styles.css` from `courses/rprogramming/`
   and adapt: `website.title`, `sidebar.title`, `sidebar.contents`,
   `site-url`.
3. If it needs live code: `quarto add coatless/quarto-webr`, copy
   `qwebr-force-dark.js` and its `include-after-body` wiring.
4. Write `index.qmd` + one `.qmd` per lesson.
5. `quarto render`.
6. Add a card for it in `raw/courses/index.qmd`, then `quarto render` from
   `raw/` to regenerate `courses/index.html`.
7. `courses/<slug>/sitemap.xml` is auto-generated by Quarto (since
   `site-url` is set) — don't add the course to
   `scripts/gen_sitemap_tools.py`, that script deliberately skips
   Quarto-rendered sections that already maintain their own sitemap.
   Add `Sitemap: https://www.statmania.info/courses/<slug>/sitemap.xml` to
   both `robots.txt` and `raw/robots.txt`.
