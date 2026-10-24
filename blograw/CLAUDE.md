# CLAUDE.md — blograw/

Guidance for writing and publishing blog posts. `blograw/` is the Quarto
project that renders to `../blog/` (see the top-level `CLAUDE.md`). Posts are
`posts/*.qmd` (or `.md`); edit the source, never the generated `blog/*.html`.

## Front matter template

```yaml
---
title: "Descriptive Title, Not Just a Keyword"
description: "One or two sentences; used for the listing card, <meta>, and search results."
date: "YYYY-MM-DD"                          # today: run `date +%F`; never a future date
categories: [C, Programming, Tutorial]   # shown in the listing; used for filtering
tags: [c, struct, memory-layout]          # keep filling these in — see below
author: "Abdullah Al Mahmud"
image: ../img/<name>.png                  # PNG, see "Images"
---
```

### Tags (keep the vocabulary small)

Tags drive the tag cloud, `tags.html`, and related posts. Lowercase, hyphenated. The vocabulary was
merged from 195 near-duplicate tags down to about 40 (2026-10-17), so **reuse an existing tag before
inventing one**: list them with `grep -h '^tags:' posts/*.qmd`. Merge specific ideas into the broad tag:

- C: `c`, `control-flow`, `loops` (for/while/do-while/nested/break/patterns), `conditionals`
  (if-else/switch), `arrays`, `indexing`, `pointers`, `memory` (malloc/realloc/stack), `data-types`
  (struct/typedef/float/variables), `operators`, `input-output` (scanf/printf/fgets), `random-numbers`,
  `compiler`, `functions`, `math`, `beginners`, `practice-problems`
- Statistics: `statistics`, `probability` (distributions), `descriptive-statistics`, `hypothesis-testing`,
  `regression`, `time-series`, `machine-learning`, `spatial`, `visualization`, `imaging`
- R/Python: `r`, `r-package`, `python`
- Tools: `linux`, `command-line` (shell/bash/sed/ffmpeg), `git`, `quarto`, `latex`, `slides`, `workflow`, `writing`, `research`

A genuinely new topic may get its own tag, but only if at least a second post is likely to use it.
`categories` stay broad (language, subject, post type).

## Images: SVG in the body, PNG in the front matter

Whenever an edit to a post is sought, check if the post contains an image; if not, add one (follow the following).

Don't geenrate svg if an existing image name (svg or png) matches with the post topic. Generic images like r-shell.jpeg, journal.jpeg can be used in mahy posts. 

**When the user names no image, choose in this order:**
1. Look in `img/` for an existing image that matches the topic or is a generic fit (e.g. `linux-git.jpeg`
   for git posts, `r-shell.jpeg`, `fish-shell.jpeg`, `journal.jpeg`) and reuse it for both the body and
   `image:`. JPEG/PNG photos need no SVG twin.
2. Only if nothing is relevant, draw a new SVG: a sketch of a person using what the post covers
   (at a laptop or terminal), or a diagram when the post is about a process or structure.
3. Claude cannot make photorealistic images; if a photo is wanted, the user supplies it.

- **Inside the post body → SVG**, e.g. `![caption](../img/name.svg){fig-alt="..."}`.
  Sharp at any zoom, small, real text, and it takes alt text. Always add
  `fig-alt` (accessibility and image search) and a short caption.
- **`image:` in the front matter → PNG (1200×630)**. `image:` becomes the
  `og:image` / Twitter card / listing thumbnail, and Facebook, LinkedIn, X and
  WhatsApp do **not** render SVG, so an SVG there means a blank link preview.
- Keep both files in `blograw/img/` with the same base name
  (`img/foo.svg` + `img/foo.png`). Make the PNG from the SVG with:

  ```
  cd blograw && python3 svg2og.py img/foo.svg     # writes img/foo.png
  ```

  (needs `pip install cairosvg pillow`; it centres the figure on the site's
  dark background at 1200×630.) Check the PNG before publishing, since
  cairosvg ignores SVG filters (glow) and substitutes fonts.
- Draw figures in the site's dark theme: background dark (default `#05070d`→`#0a0f1e`),
  accents cyan `#00e5ff`, purple `#a855f7`, pink `#ff2fb4`, monospace text
  (`'JetBrains Mono','Fira Code',Consolas,monospace`); include `<title>` and
  `<desc>`. Existing figures (`img/if-else-flow.svg`, `img/c-struct-memory.svg`)
  are good starting points.
- **Vary the colours between posts.** Don't reuse the cyan/purple/pink palette on every
  figure: it makes all post thumbnails look alike. Pick a different accent set per post
  (e.g. green + amber, orange + teal, blue + yellow, red + lime) and tint the dark
  background to match (deep green, navy, warm brown, plum). Check the recent figures in
  `img/` and choose something that isn't used by the latest few posts.
- **Not every figure is a flowchart.** For many posts a themed illustration works better:
  a relevant logo (e.g. a hexagonal C logo, a Python snake, an R mark) blended with related
  elements such as scraps of code floating around, a monitor or terminal, a person at a
  computer. Simple, sketch-like and stylised is fine; it need not look realistic. Use a
  flowchart/diagram only when the post is about a process or structure. Keep the same SVG
  rules (dark tinted background, `<title>`/`<desc>`, varied palette). Examples:
  `img/c-test-code-quickly.svg`, `img/c-die-throw.svg`, `img/c-while-practice.svg`.
- **Every figure and cover must look right in BOTH the dark and the light theme.** Check both
  (navbar toggle) before publishing. How it works: figures are drawn dark. In the light theme the
  extension inverts them with a CSS filter (`invert(1) hue-rotate(180deg)`): post-body `.svg` images,
  plus PNG covers that have a same-named SVG in the same folder (the hook flags them `adapt` in
  `blogkit-data.js`), so a generated cover and its SVG should always share a base name. Photos,
  screenshots and real plots (JPEG, or a PNG without a same-named SVG) are never inverted. When drawing:
  - use a dark, tinted background and light text, with accents that stay readable once inverted (avoid
    near-white or near-black accents, which swap places);
  - don't rely on one exact colour to carry meaning, since hues shift a little after inverting;
  - put real pictures (a screenshot, a photo) inside a figure only as JPEG/PNG files, never embedded in
    the SVG, because the filter would invert them too.
- Photos/screenshots stay JPEG/PNG as usual.

## Writing conventions

- Name files by topic (`c-struct.qmd`), not by number.
- Dates: use the real current date (`date +%F`). Don't invent later dates for a batch of posts; a future date
  makes the post look unpublished or misdated.
- Compile/run code examples before publishing, and paste real output. State
  any needed flag (e.g. `-lm` for `<math.h>`).
- Use `::: {.callout-note}` / `-tip` / `-warning` for asides (styled for the
  dark theme in the extension's `styles.css`; site-only tweaks go in `site.css`).
- Voice: first-person plural for tutorials ("we", "us", "let's") rather than "you"; keep instructions short and concrete.
- Don't include personal details (course codes, degree info) in public posts.
- Only list references you actually used.

## Render and publish

```
cd blograw
quarto render posts/<post>.qmd     # renders one post
# (the project's post-render hook, _extensions/blogkit/repair_index.py, then re-renders index.qmd:
#  Quarto's listing refresh would otherwise strip the homepage theme)
```

The `Refusing to remove directory ... _files` and "path configuration" warnings
are harmless (the output dir `../blog` is outside the project); ignore them.
Publish = commit the `.qmd`, `img/` files and the regenerated `blog/` output,
then push to `master` on GitHub Pages.

## Blogkit extension (the engine) and site.css (this site's overrides)

> **Rule: new blog features and fixes go into quarto-blogkit first, never straight into this repo.**
> Whenever an idea for the blog comes up while working here (a widget, a layout or CSS change, a
> script fix, a new option, anything that is not specific to Stat Mania), do it like this:
>
> 1. Implement it in `../../quarto-blogkit/_extensions/blogkit/` (use `bk-` / `--bk-` names, keep it
>    generic, add a line to its `CHANGELOG.md`), commit and push that repo.
> 2. Here run `cd blograw && quarto update extension statmania/quarto-blogkit` (or
>    `quarto add ../../quarto-blogkit` to test before pushing), then a full `quarto render`.
> 3. Only things that are truly specific to this site (starfield, `.sm-*` hero, branding)
>    go in `site.css` / `_quarto.yml` / `index.qmd` here.
>
> Never hand-edit `_extensions/blogkit/` in this repo: the next update overwrites it, and the
> improvement would be lost from blogkit.

The blog runs on the **quarto-blogkit** extension (`../../quarto-blogkit`, GitHub
`statmania/quarto-blogkit`), installed in `_extensions/blogkit/`. **Do not edit files in
`_extensions/blogkit/`**: they are overwritten on update. Generic features and fixes (theme,
`styles.css`, `blogkit.js`, `build_site_data.py`, code-reveal) are made in the quarto-blogkit repo and
pulled in here:

```
# after committing/pushing a change in quarto-blogkit:
cd blograw && quarto update extension statmania/quarto-blogkit   # or: quarto add ../../quarto-blogkit
quarto render                                                      # full render; every page changes
```

Site-specific things stay in `blograw/`: `site.css` (starfield canvas, homepage hero with `.sm-*`
classes, dark navbar and post banner bands in light mode; the hero itself follows the theme), `_quarto.yml` (`format: blogkit-html` plus
`../starfield-include.html`), `index.qmd`, `about.qmd`, `authors.yml`. The extension's CSS uses
`--bk-*` variables and `.bk-*` classes (this site used `sm-` before the switch).

How it works: the extension's `build_site_data.py` is the `pre-render` hook. On every
`quarto render`, even of one post, it reads post front matter (`title`, `description`, `date`,
`tags`, `categories`, `author`; `draft: true` is skipped) and `authors.yml`, writes
`../blog/blogkit-data.js`, copies `blogkit.js` next to it, rewrites the small `authors/<slug>.qmd`
stubs (never hand-edit those) and creates `tags.qmd` if missing. `blogkit.js` fetches the data and
builds the sidebar archive and tag cloud, each post's tags row, related posts, author cards and
pages, `tags.html#tag=<name>`, and the sticky small-screen "On this page" menu.

- Workflow: write the post, `quarto render posts/<post>.qmd` (~7 s), commit `blog/` (or just `./publish.sh posts/<post>.qmd`). The `post-render` hook repairs the homepage automatically.
  A full `quarto render` (~40 s) is only needed when `site.css`, `_quarto.yml` or the extension
  change. Browsers may cache `blogkit-data.js` for a few minutes after publishing.
- Needs `title` and `date` in the front matter; `tags:` (lowercase, hyphenated) drive
  the tag cloud and related posts.
- Posts get a margin TOC (`posts/_metadata.yml`: `toc-depth: 3`, since many posts use
  `###` as their top heading).

## Authors

Profiles live in `authors.yml` (slug → `name`, `aliases`, `image`, `tagline`, `bio`,
`links`). Posts keep `author: "Name"` as plain text; a post belongs to the profile whose
`name`/`aliases` match it. Add an author = add an entry (and a photo under `img/`), then
render; the hook creates `authors/<slug>.qmd`. Authors not in `authors.yml` get no link.

## Light / dark theme

The extension sets `theme: {dark: [cosmo, theme-dark.scss], light: cosmo}` (dark listed first = default;
the empty-looking `theme-dark.scss` only exists because Quarto decides dark vs light from `$body-bg`,
so a dark scheme must actually be dark) and `highlight-style: {light: github, dark: dracula}`.
Quarto adds a navbar toggle and puts `quarto-light` / `quarto-dark` on `<body>`. the extension's `styles.css` is the
dark design; its final "Light theme" section overrides variables on `:root:has(body.quarto-light)` and
fixes hardcoded colours under `body.quarto-light`. Navbar, post title banner and homepage hero all follow the theme; the starfield is hidden in light mode. Use `--sm-*`
variables, not hex colours, in new CSS.

## Starfield background

The blog pages get the site-wide starfield via `../starfield-include.html`
(see the top-level `CLAUDE.md`). Post bodies sit on an opaque panel so stars
never run behind text.
