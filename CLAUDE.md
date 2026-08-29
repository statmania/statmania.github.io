# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

"Stat Mania" (statmania.info / portal.statmania.info) is a static site with **two coexisting build systems that must not be confused**:

1. **Jekyll (lone-wolf-theme)** — the underlying site scaffold: `_config.yml`, `_layouts/`, `_includes/`, `_sass/`, `_pages/`, `_posts/`, `_data/`. Served via GitHub Pages (`CNAME` → `www.statmania.info`).
2. **Multiple independent Quarto projects** — each is a self-contained `_quarto.yml` project whose *rendered output* lands in the repo root or a sibling folder, checked into git. Quarto is not run at deploy time by GitHub Pages; someone runs `quarto render` locally/in CI and commits the generated HTML.

Because the rendered HTML is committed, **most of the actual page content on the live site (index.html, snippets.html, resources.html, games.html, lectures.html, blog/, gre/, ielts/, slide/, research/) is generated output, not hand-authored**. Editing the generated `.html` directly works for quick tweaks but will be silently overwritten the next time the corresponding `.qmd` source is re-rendered — always find and edit the `.qmd`/source file when one exists.

## Folder structure

- The parent website is rendered from 'raw' directory. 
- 'blograw' generates 'blog'
- gre and ielts were temporary projects. Ignore them unless explicitly made relevant later.
- One of the primary tasks is in 'slide' directory. Here the lecture slides are stored. Slightly less important is 'utility'
- Slides in 'slide' directory don't need rendering when only the css is changed in css/styles.css or styles.css.

## Quarto projects → output mapping

| Source dir | `_quarto.yml` output-dir | Renders to |
|---|---|---|
| `raw/` | `../` (repo root) | `index.html`, `snippets.html`, `resources.html`, `games.html`, `lectures.html`, `404.html` |
| `blograw/` | `../blog` | `blog/` |
| `gre/` | `.` (in place) | `gre/*.html` |
| `ielts/` | `.` (in place) | `ielts/*.html` |
| `slide/` | `.` (in place, revealjs) | `slide/*.html` (lecture slide decks) |
| `research/` | (own `_site`) | `research/_site/` |

To rebuild a section, `cd` into its source dir and run `quarto render` (requires the Quarto CLI). Example: editing the homepage means editing `raw/index.qmd`, then `quarto render` from `raw/`, which regenerates `index.html` at the repo root.

`ds/`, `games/`, `utility/` are **not** Quarto-rendered — they're hand-written static HTML pages (each self-contained with inline `<style>`/`<script>`, no shared build step). Edit those `.html` files directly.

The `.github/workflows/update.yml` GitHub Action runs on a daily cron: it renders `ds/dash/rpkg.qmd` (an R package dashboard, using R + `ggplot2`/`DT`/`dplyr`/etc. via `r-lib/actions`) and commits the result — the only automated render in this repo. [If not already done, opt out from this GHA and then delete this line]

## Design system

Newer pages (games, utility, the redesigned homepage) share a "futuristic dark" visual language: dark navy/black background (`#05070d`/`#0a0f1e`), cyan/purple/pink accent gradient (`#00e5ff`, `#a855f7`, `#ff2fb4`), animated canvas backgrounds, card-grid layouts. When adding new utility or game pages, match this look rather than the older Bootstrap/bootswatch ("united" theme) styling used by the Jekyll-rendered pages — check a recent file like `utility/timer.html` or `games/index.html` as a reference, and keep new pages self-contained (inline CSS/JS) consistent with the existing ones rather than pulling in the Jekyll asset pipeline.

Site-wide nav/branding conventions used across utility and game pages: logo/title links back to the homepage, and any "back" or CTA link points to that section's own index page (e.g. `utility/*.html` → `utility/index.html`).

## Jekyll development

The user doen't rely on Jekyll. Raher Quarto + Raw html.

## Notes

- `blograw/posts/` mixes `.qmd` and plain `.md` posts.
- `search.json` is a generated search index (Quarto/Jekyll search) — don't hand-edit.
