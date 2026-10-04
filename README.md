# Stat Mania Portal

**Making Sense of Statistics and Data** · [statmania.info](https://www.statmania.info) · [blog](https://www.statmania.info/blog/)

A static site served by GitHub Pages (`CNAME` → `www.statmania.info`). The generated HTML is committed, so
**nothing is built at deploy time**: render locally with [Quarto](https://quarto.org), commit, push.

## Layout

| Folder | What it is | Edit | Output |
| :--- | :--- | :--- | :--- |
| `raw/` | The main site (home, snippets, resources, games/utility/courses hubs) | `raw/*.qmd`, `raw/styles.css` | repo root (`index.html`, …) |
| `blograw/` | The blog | `blograw/posts/*.qmd` | `blog/` |
| `slide/` | Lecture slide decks (reveal.js) | `slide/*.qmd`, `slide/_quarto.yml` | `slide/*.html` in place |
| `games/`, `utility/` | Hand-written static HTML tools and games (self-contained) | the `.html` files | themselves |
| `courses/` | Course material and code | see `courses/CLAUDE.md` | themselves |
| `research/` | Research pages | own Quarto project | `research/_site/` |
| `starfield.js` | Shared animated starfield background (never copy it into a section) | | |

`gre/`, `ielts/` and the Jekyll folders (`_layouts`, `_includes`, `_sass`, `_posts`, …) are legacy; the site does not rely on Jekyll.

Generated HTML is overwritten by the next render, so edit the `.qmd` source (or the hand-written `.html` for games and utility tools), not the rendered page.

## Rebuild a section

```
cd raw && quarto render          # main site -> repo root
cd blograw && quarto render posts/my-post.qmd   # one blog post (see below)
cd slide && quarto render deck.qmd              # one slide deck
```

Slides need no render when only `slide/css/styles.css` or `slide/styles.css` changes.

## The blog

Posts live in `blograw/posts/` and render to `blog/`. It has a dark/light theme toggle in the navbar (dark by default), a sidebar archive and tag cloud, tag pages, related posts, author pages, and hint/Reveal buttons for code exercises. These cross-post features are driven by one data file that is rewritten on every render, so publishing a new post only needs that post rendered.

- Publish: `cd blograw && ./publish.sh posts/my-post.qmd` (render, commit, push)
- Full step-by-step guide: [`blograw/README.md`](blograw/README.md)
- Design notes: [`blograw/CLAUDE.md`](blograw/CLAUDE.md)

## Design

New pages share a futuristic dark look (navy/black background, cyan/purple/pink accents, card grids). Games and utility tools follow it with inline CSS and JS; the blog adds a light theme.

## Automation

`.github/workflows/update.yml` runs daily and renders the R package dashboard (`ds/dash/rpkg.qmd`); it is the only automated render.

## Notes

- `CLAUDE.md` files hold guidance for working in each area with Claude Code.
- `search.json` and the sitemaps are generated; do not hand-edit them.
