# CLAUDE.md — blograw/

Guidance for writing and publishing blog posts. `blograw/` is the Quarto
project that renders to `../blog/` (see the top-level `CLAUDE.md`). Posts are
`posts/*.qmd` (or `.md`); edit the source, never the generated `blog/*.html`.

## Front matter template

```yaml
---
title: "Descriptive Title, Not Just a Keyword"
description: "One or two sentences; used for the listing card, <meta>, and search results."
date: "YYYY-MM-DD"
categories: [C, Programming, Tutorial]   # shown in the listing; used for filtering
tags: [c, struct, memory-layout]          # keep filling these in — see below
author: "Abdullah Al Mahmud"
image: ../img/<name>.png                  # PNG, see "Images"
---
```

### Tags (for later use)

`tags:` is **not displayed or used by the site yet**, but fill it in on every
new post anyway (lowercase, hyphenated, specific: `c`, `struct`, `typedef`,
`python-dict`). We plan to use them later for related-posts and topic pages,
and it is much cheaper to tag posts as you write than to backfill. `categories`
stay broad (language, subject, post type); `tags` are the specific concepts.
Every existing post has been backfilled (2026-09-26); keep tags lowercase and hyphenated for consistency.

## Images: SVG in the body, PNG in the front matter

Whenever an edit to a post is sought, check if the post contains an image; if not, add one (follow the following).

Don't geenrate svg if an existing image name (svg or png) matches with the post topic. Generic images like r-shell.jpeg, journal.jpeg can be used in mahy posts. 

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
- Draw figures in the site's dark theme: background `#05070d`→`#0a0f1e`,
  accents cyan `#00e5ff`, purple `#a855f7`, pink `#ff2fb4`, monospace text
  (`'JetBrains Mono','Fira Code',Consolas,monospace`); include `<title>` and
  `<desc>`. Existing figures (`img/if-else-flow.svg`, `img/c-struct-memory.svg`)
  are good starting points.
- Photos/screenshots stay JPEG/PNG as usual.

## Writing conventions

- Name files by topic (`c-struct.qmd`), not by number.
- Compile/run code examples before publishing, and paste real output. State
  any needed flag (e.g. `-lm` for `<math.h>`).
- Use `::: {.callout-note}` / `-tip` / `-warning` for asides (styled for the
  dark theme in `styles.css`).
- Voice: first-person plural for tutorials ("we", "us", "let's") rather than "you"; keep instructions short and concrete.
- Don't include personal details (course codes, degree info) in public posts.
- Only list references you actually used.

## Render and publish

```
cd blograw
quarto render posts/<post>.qmd     # renders one post, refreshes the listing
```

The `Refusing to remove directory ... _files` and "path configuration" warnings
are harmless (the output dir `../blog` is outside the project); ignore them.
Publish = commit the `.qmd`, `img/` files and the regenerated `blog/` output,
then push to `master` on GitHub Pages.

## Dynamic widgets (site.js + site-data.js)

Everything cross-post is **dynamic**, so a new post needs no re-render of other pages:

- `scripts/build_site_data.py` is the project `pre-render` hook (`_quarto.yml`). On every
  `quarto render`, even of one post, it reads post front matter (`title`, `description`,
  `date`, `tags`, `categories`, `author`; `draft: true` is skipped) and `authors.yml`,
  writes `../blog/site-data.js`, copies `site.js` next to it, and rewrites the small
  `authors/<slug>.qmd` stubs (never hand-edit those).
- `site.js` (hand-written, loaded on every page by `_site-include.html`) fetches the JSON
  and builds: the homepage/post sidebar archive and tag cloud (below the TOC on posts,
  under the article on small screens), each post's tags row, up to 5 related posts
  (ranked by shared tags/categories, rarer ones weigh more), the author card and
  byline links, `tags.html#tag=<name>` (10 per page) and the author pages
  (category/tag filters, 10 per page), plus the sticky small-screen "On this page" menu.
- Workflow: write the post, `quarto render posts/<post>.qmd` (~7 s), commit `blog/`.
  A full `quarto render` (~40 s) is only needed when `site.js`, CSS or `_quarto.yml`
  change. Browsers may cache `site-data.js` for a few minutes after publishing.
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

`_quarto.yml` has `theme: {dark: [cosmo, theme-dark.scss], light: cosmo}` (dark listed first = default;
the empty-looking `theme-dark.scss` only exists because Quarto decides dark vs light from `$body-bg`,
so a dark scheme must actually be dark) and `highlight-style: {light: github, dark: dracula}`.
Quarto adds a navbar toggle and puts `quarto-light` / `quarto-dark` on `<body>`. `styles.css` is the
dark design; its final "Light theme" section overrides variables on `:root:has(body.quarto-light)` and
fixes hardcoded colours under `body.quarto-light`. Navbar, post title banner and homepage hero re-assert
the dark palette locally (dark bands on a light page); the starfield is hidden in light mode. Use `--sm-*`
variables, not hex colours, in new CSS.

## Starfield background

The blog pages get the site-wide starfield via `../starfield-include.html`
(see the top-level `CLAUDE.md`). Post bodies sit on an opaque panel so stars
never run behind text.
