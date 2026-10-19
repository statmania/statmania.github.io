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
- refreshes `blog/blogkit-data.js`, so the archive, tag cloud, tags page, related posts and author page include the post automatically. **You do not need to re-render other posts.**

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
| `site.css` | full `quarto render` (it is a project CSS file) |
| `_extensions/blogkit/` (widgets, related posts, pagers, generic CSS) | `quarto update extension statmania/quarto-blogkit`, then a full render. Edit the extension in the `quarto-blogkit` repo, not here |
| `authors.yml`: photo, name, tagline, bio, links | `quarto render authors/<slug>.qmd` for the author page header; post cards update from the data file on the next render of anything |
| a **new author** in `authors.yml` + photo in `img/` | `quarto render` (creates `authors/<slug>.qmd` and builds it) |
| `about.qmd`, `index.qmd`, `tags.qmd` | `quarto render <that file>` |
| `_quarto.yml`, `posts/_metadata.yml` | full `quarto render` (they change every page, ~40 s) |
| a **deleted post** | delete `posts/x.qmd`, delete `../blog/posts/x.html` (and `../blog/posts/x_files/` if present), then `quarto render index.qmd` |
| a new image only | render the post that uses it (images are copied when a page references them) |

Code in `{python}`/`{r}` chunks is cached (`freeze: true`). To re-run it, delete `_freeze/posts/<post>/` and render that post.

## Shortcut: `publish.sh`

`blograw/publish.sh` does steps 2/3 and 6 in one go (render, commit `blog/` and `blograw/` only, pull --rebase, push):

```
./publish.sh posts/my-post.qmd                  # one post
./publish.sh posts/a.qmd posts/b.qmd            # several posts
./publish.sh --all                              # full render (site.css / config / extension changes)
./publish.sh                                    # no render; commit and push whatever is pending
./publish.sh -m "Blog: add srand post" posts/c-srand-time-null.qmd
./publish.sh --no-push posts/x.qmd              # render + commit, check locally, push later
```

It stops if a render fails, skips the commit when nothing changed, and never touches files outside `blog/` and `blograw/`. Preview first (step 5) with `--no-push` if you want to look before publishing.

## 5. Check it locally

```
cd ../blog
python3 -m http.server 8000      # then open http://localhost:8000
```

Use a hard refresh (Ctrl+Shift+R) so the browser does not show cached CSS or `blogkit-data.js`. Check: the post page, the homepage card, the tags page (`/tags.html#tag=c`) and your author page.

## 6. Publish

```
cd ~/Documents/smroot
git add blog blograw
git commit -m "Blog: add <post title>"
git pull --rebase --autostash
git push
```

GitHub Pages updates in a minute or two. Readers' browsers may keep the old `blogkit-data.js` for up to ~10 minutes.

## Light / dark theme

The navbar has a sun/moon toggle; dark is the default and the choice is remembered per browser. Quarto does the switching (`theme:` in `_quarto.yml`: `dark: [cosmo, theme-dark.scss]`, `light: cosmo`; code highlighting `dracula` / `github`), set by the Blogkit extension. The dark look is the base of the extension's `styles.css`; the light overrides are in the last section of that file under `body.quarto-light`, and `site.css` keeps the navbar, post banner and homepage hero dark bands in light mode. When you add new components, give them colours through the `--bk-*` CSS variables so both themes work.

## Editing manual: where each thing on the pages comes from

| You see | Edit this | Then run |
| :--- | :--- | :--- |
| Homepage headline and the tagline in the stats line ("Tutorials, theory and dev notes...") | `index.qmd`, the `<div class="sm-hero">` block near the top: the headline is `.sm-title`. The tagline is `hero-tagline:` under `blogkit:` in `_quarto.yml` (full `quarto render`). Plain HTML text; keep the headline a `<p role="heading">`, because Quarto turns a raw `<h1>` into the hidden page title | `quarto render index.qmd` |
| Hero search box, topic chips, stats strip ("62 posts · 40 topics...") | Generated into `_bk-hero-tools.html` on every render (never edit it) and pulled into the hero by `{{< include _bk-hero-tools.html >}}` in `index.qmd`, so it is in the page from the first paint. The tagline is `hero-tagline:` under `blogkit:` in `_quarto.yml`. Change the look in `quarto-blogkit` (`blogkit.js`, `styles.css`), the number of chips with `hero-topics` under `blogkit:` in `_quarto.yml` (see the extension README) | update the extension, then full `quarto render` |
| Hero colours, size, corner brackets, starfield strength | `site.css` (`.sm-hero`, `.sm-title`, `#sm-canvas { opacity }`) | full `quarto render` |
| Star animation on the hero | `index.qmd`, the `<script>` below the hero (particle count, speed) | `quarto render index.qmd` |
| Homepage post cards, sort, page size | `index.qmd` front matter, `listing:` (`page-size`, `sort`, `fields`) | `quarto render index.qmd` |
| Navbar links, footer text and links, site title, logo | `_quarto.yml` (`website: navbar:` and `page-footer:`) | full `quarto render` |
| Tag and category lists (sidebar cloud, `tags.html`, `categories.html`) | Nothing to edit by hand: they come from each post's `tags` and `categories`. The two pages' intro text lives in `tags.qmd` and `categories.qmd` (created once by the hook, then yours) | render any post |
| Post thumbnails (listing, related, prev/next, tag pages) | the post's `image:` front matter (1200x630 PNG; a post without one gets `img/placeholder.svg`) | render that post |
| Author card and author page | `authors.yml` (never `authors/<slug>.qmd`) | `quarto render` for a new author |
| About page | `about.qmd` | `quarto render about.qmd` |
| Labels such as "Related posts", "Previous post", "All posts" | the extension's `blogkit.js` (`LABELS`); override per site with `labels:` in the `blogkit` options | full `quarto render` |
| Anything in `blog/` | never edit by hand; it is overwritten on render | n/a |

Rule of thumb: text that belongs to this site (headline, tagline, nav, footer, colours) is edited here. Behaviour or layout that any blog would want (widgets, pages, CSS for them) is edited in `quarto-blogkit`, pushed, then pulled in with `quarto update extension statmania/quarto-blogkit` (see `CLAUDE.md`).

## What is generated (never hand-edit)

- `../blog/` (the whole built site), including `blog/blogkit-data.js` and `blog/blogkit.js`
- `authors/<slug>.qmd` (from `authors.yml`), and `tags.qmd` / `categories.qmd` on first creation only

Hand-written: posts, `authors.yml`, `site.css`, `tags.qmd`, `index.qmd`, `about.qmd`, `publish.sh`.

`CLAUDE.md` has the detailed design notes (images, writing conventions, how the dynamic widgets work).
