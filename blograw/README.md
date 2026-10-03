# Publishing to the Stat Mania blog

`blograw/` holds the **sources**; `blog/` (one level up) is the **built site** that GitHub Pages serves. You edit `blograw/`, render, then commit both folders.

All commands below run from `blograw/`:

```
cd ~/Documents/smroot/blograw
```

Requirements: Quarto CLI and Python 3 with PyYAML (`pip install pyyaml`).

## 1. Before you render

Every post is `posts/<topic>.qmd` (name it by topic, not by number) and must start with:

```yaml
---
title: "Descriptive Title"
description: "One or two sentences (card, search results, link previews)."
date: "YYYY-MM-DD"
categories: [C, Programming, Tutorial]   # broad
tags: [c, srand, rand]                   # specific, lowercase, hyphenated
author: "Abdullah Al Mahmud"             # must match a name in authors.yml
image: ../img/<name>.png                 # 1200x630 PNG for link previews
---
```

- `title` and `date` are required, or the post is skipped (a warning is printed).
- `tags` feed the tag cloud, tag pages and **related posts**; `author` links to the author page.
- Put `draft: true` in the front matter to keep a post out of the site data.
- Images: SVG in the body, PNG in `image:` (see `CLAUDE.md` for how to make the PNG).
- Compile and run code examples first, and paste the real output.

## 2. Publish ONE new or edited post

```
quarto render posts/my-post.qmd
```

This takes a few seconds and does everything needed:

- builds `blog/posts/my-post.html` (and copies the images it uses),
- refreshes the homepage list,
- refreshes `blog/site-data.js`, so the archive, tag cloud, tags page, related posts and author page include the post automatically. **You do not need to re-render other posts.**

## 3. Publish SEVERAL posts

`quarto render` takes one file at a time (extra file names are treated as options and fail), so use one of:

```fish
# a few specific posts (fish shell; in bash use: for f in a b; do ...; done)
for f in posts/a.qmd posts/b.qmd
    quarto render $f
end

# every post
quarto render posts/

# the whole site (also pages, authors, tags)
quarto render
```

Rendering many posts is only for bulk edits. Because everything cross-post is dynamic, a new post never requires it.

## 4. Other files: what to run

| You changed | Run |
| :--- | :--- |
| `posts/x.qmd` (text, code, images used by it) | `quarto render posts/x.qmd` |
| `styles.css` | any render, e.g. `quarto render posts/x.qmd` (copies it); other pages pick it up on reload |
| `site.js` (widgets, related posts, pagers) | `python3 scripts/build_site_data.py` (copies it to `blog/`; no Quarto needed) |
| `authors.yml`: photo, name, tagline, bio, links | `quarto render authors/<slug>.qmd` for the author page header; post cards update from the data file on the next render of anything |
| a **new author** in `authors.yml` + photo in `img/` | `quarto render` (creates `authors/<slug>.qmd` and builds it) |
| `about.qmd`, `index.qmd`, `tags.qmd` | `quarto render <that file>` |
| `_quarto.yml`, `_site-include.html`, `code-reveal.html`, `posts/_metadata.yml` | full `quarto render` (they change every page, ~40 s) |
| a **deleted post** | delete `posts/x.qmd`, delete `../blog/posts/x.html` (and `../blog/posts/x_files/` if present), then `quarto render index.qmd` |
| a new image only | render the post that uses it (images are copied when a page references them) |

Code in `{python}`/`{r}` chunks is cached (`freeze: true`). To re-run it, delete `_freeze/posts/<post>/` and render that post.

## 5. Check it locally

```
cd ../blog
python3 -m http.server 8000      # then open http://localhost:8000
```

Use a hard refresh (Ctrl+Shift+R) so the browser does not show cached CSS or `site-data.js`. Check: the post page, the homepage card, the tags page (`/tags.html#tag=c`) and your author page.

## 6. Publish

```
cd ~/Documents/smroot
git add blog blograw
git commit -m "Blog: add <post title>"
git pull --rebase --autostash
git push
```

GitHub Pages updates in a minute or two. Readers' browsers may keep the old `site-data.js` for up to ~10 minutes.

## What is generated (never hand-edit)

- `../blog/` (the whole built site), including `blog/site-data.js` and `blog/site.js`
- `authors/<slug>.qmd` (from `authors.yml`)

Hand-written: posts, `authors.yml`, `site.js`, `styles.css`, `tags.qmd`, `index.qmd`, `about.qmd`.

`CLAUDE.md` has the detailed design notes (images, writing conventions, how the dynamic widgets work).
