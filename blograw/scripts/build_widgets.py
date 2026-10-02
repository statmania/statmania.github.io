#!/usr/bin/env python3
"""Quarto pre-render hook: build the blog sidebar widgets (post archive + tag cloud).

Reads only the front matter (`title`, `date`, `tags`, `draft`) of the posts that
`_quarto.yml` renders (posts/*.qmd and posts/*.md) and writes `_widgets-body.html`,
which `index.qmd` pulls in with `{{< include _widgets.html >}}`.

It never touches Quarto's own listing/category markup, so Quarto upgrades can't
break it. Styles live in styles.css (`.sm-widget*`); behaviour is the small
inline script emitted at the end of the generated file.
"""
import html
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime
from urllib.parse import quote
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "posts"
OUT = ROOT / "_widgets-body.html"
TAGS_PAGE = ROOT / "tags.qmd"
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


def front_matter(path):
    m = re.match(r"^---\s*\n(.*?)\n---\s*(\n|$)", path.read_text(encoding="utf-8"), re.S)
    return (yaml.safe_load(m.group(1)) or {}) if m else {}


def as_date(v):
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    try:
        return datetime.strptime(str(v)[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def load_posts():
    posts = []
    for path in sorted(list(POSTS.glob("*.qmd")) + list(POSTS.glob("*.md"))):
        if path.name.startswith("_"):
            continue
        fm = front_matter(path)
        d = as_date(fm.get("date"))
        if fm.get("draft") or not fm.get("title") or d is None:
            if not fm.get("draft"):
                print(f"build_widgets: skipping {path.name} (needs title and date)", file=sys.stderr)
            continue
        tags = fm.get("tags") or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",")]
        posts.append({
            "title": str(fm["title"]),
            "desc": " ".join(str(fm.get("description") or "").split()),
            "href": f"posts/{path.stem}.html",
            "date": d,
            "tags": [str(t).strip().lower() for t in tags if str(t).strip()],
        })
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def link(p):
    h = html.escape(p["href"])
    return f'<li><a href="{h}" data-h="{h}">{html.escape(p["title"])}</a></li>'


def archive(posts):
    by_year = defaultdict(lambda: defaultdict(list))
    for p in posts:
        by_year[p["date"].year][p["date"].month].append(p)
    out = ['<nav class="sm-widget sm-archive" aria-label="Post archive">',
           '<h3 class="sm-widget-title">Archive</h3>']
    for i, year in enumerate(sorted(by_year, reverse=True)):
        n = sum(len(v) for v in by_year[year].values())
        out.append(f'<details class="sm-year"{" open" if i == 0 else ""}>'
                   f'<summary>{year} <span class="sm-count">{n}</span></summary>')
        for month in sorted(by_year[year], reverse=True):
            items = by_year[year][month]
            out.append(f'<details class="sm-month"><summary>{MONTHS[month - 1]} '
                       f'<span class="sm-count">{len(items)}</span></summary><ul>'
                       + "".join(link(p) for p in items) + "</ul></details>")
        out.append("</details>")
    out.append("</nav>")
    return "\n".join(out)


def tag_counts(posts):
    return Counter(t for p in posts for t in set(p["tags"]))


def chips(counts, tag="a", base="tags.html"):
    lo, hi = min(counts.values()), max(counts.values())
    out = []
    for t in sorted(counts, key=lambda t: (-counts[t], t)):
        size = 0.78 + (0.5 * (counts[t] - lo) / (hi - lo) if hi > lo else 0)
        h = f"{base}#tag={html.escape(quote(t))}"
        out.append(f'<a class="sm-tag" href="{h}" data-h="{h}" '
                   f'data-tag="{html.escape(t)}" style="font-size:{size:.2f}rem">'
                   f'{html.escape(t)} <span class="sm-count">{counts[t]}</span></a>')
    return "".join(out)


def tag_cloud(posts):
    counts = tag_counts(posts)
    if not counts:
        return ""
    return ('<section class="sm-widget sm-tags" aria-label="Tag cloud">'
            '<h3 class="sm-widget-title">Tags</h3>'
            f'<div class="sm-tag-cloud">{chips(counts)}</div></section>')


def tags_page(posts):
    """tags.qmd: one section per tag; the URL hash (#tag=name) picks which one shows."""
    counts = tag_counts(posts)
    secs = []
    for t in sorted(counts):
        items = "".join(
            f'<li><a href="{html.escape(p["href"])}">{html.escape(p["title"])}</a>'
            f'<span class="sm-tp-date">{p["date"].isoformat()}</span>'
            + (f'<p>{html.escape(p["desc"])}</p>' if p["desc"] else "") + "</li>"
            for p in posts if t in p["tags"])
        secs.append(f'<section class="sm-tag-section" data-tag="{html.escape(t)}" hidden>'
                    f'<h2>{html.escape(t)} <span class="sm-count">{counts[t]} '
                    f'post{"s" if counts[t] != 1 else ""}</span></h2><ul class="sm-tag-posts">{items}</ul></section>')
    return f"""---
title: "Posts by Tag"
description: "Browse every Stat Mania post by tag."
page-layout: article
toc: false
---

<!-- GENERATED by scripts/build_widgets.py on every render; do not edit. -->
```{{=html}}
<div id="sm-tags-page" class="sm-widget sm-tags">
<div class="sm-tag-cloud sm-tag-cloud-all">{chips(counts, base="tags.html")}</div>
<p class="sm-tags-hint">Pick a tag to see its posts.</p>
{"".join(secs)}
</div>
<script>
(function () {{
  var root = document.getElementById('sm-tags-page');
  function show() {{
    var m = location.hash.match(/tag=([^&]*)/);
    var tag = m ? decodeURIComponent(m[1]) : '';
    var found = false;
    root.querySelectorAll('.sm-tag-section').forEach(function (s) {{
      var on = s.dataset.tag === tag;
      s.hidden = !on;
      found = found || on;
    }});
    root.querySelectorAll('.sm-tag').forEach(function (c) {{
      c.classList.toggle('active', c.dataset.tag === tag);
    }});
    root.querySelector('.sm-tags-hint').hidden = found;
  }}
  window.addEventListener('hashchange', show);
  show();
}})();
</script>
```
"""


# The widgets go into Quarto's margin sidebar (below the category cloud on the
# homepage, below the TOC on posts) so they never float over anything. Links are
# blog-root-relative; the base is read from the page's own styles.css link.
# Pages without a margin sidebar simply drop them.
MOVE_JS = """<script>
(function () {
  var w = document.getElementById('sm-widgets');
  if (!w) return;
  var side = document.getElementById('quarto-margin-sidebar');
  if (!side) { w.remove(); return; }
  var css = document.querySelector('link[rel="stylesheet"][href$="styles.css"]');
  var base = css ? css.getAttribute('href').slice(0, -'styles.css'.length) : '';
  w.querySelectorAll('a[data-h]').forEach(function (a) { a.setAttribute('href', base + a.dataset.h); });
  side.appendChild(w);
})();
</script>"""


def main():
    posts = load_posts()
    OUT.write_text(
        "<!-- GENERATED by scripts/build_widgets.py on every render; do not edit. -->\n"
        "<div id=\"sm-widgets\">\n" + archive(posts) + "\n" + tag_cloud(posts) + "\n</div>\n" + MOVE_JS + "\n",
        encoding="utf-8",
    )
    TAGS_PAGE.write_text(tags_page(posts), encoding="utf-8")
    print(f"build_widgets: {len(posts)} posts -> {OUT.name}")


if __name__ == "__main__":
    main()
