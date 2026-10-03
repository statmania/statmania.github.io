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
            "author": str(fm.get("author") or "").strip(),
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


def post_items(posts):
    return "".join(
        f'<li><a href="../{html.escape(p["href"])}">{html.escape(p["title"])}</a>'
        f'<span class="sm-tp-date">{p["date"].isoformat()}</span>'
        + (f'<p>{html.escape(p["desc"])}</p>' if p["desc"] else "") + "</li>"
        for p in posts)


def tags_page(posts):
    """tags.qmd: tag cloud in the margin, posts of the tag chosen by the URL hash in the body."""
    counts = tag_counts(posts)
    secs = []
    for t in sorted(counts):
        items = post_items([p for p in posts if t in p["tags"]]).replace('href="../', 'href="')
        secs.append(f'<section class="sm-tag-section" data-tag="{html.escape(t)}" hidden>'
                    f'<h2>{html.escape(t)} <span class="sm-count">{counts[t]} '
                    f'post{"s" if counts[t] != 1 else ""}</span></h2><ul class="sm-post-list">{items}</ul></section>')
    return f"""---
title: "Posts by Tag"
description: "Browse every Stat Mania post by tag."
page-layout: article
toc: false
---

<!-- GENERATED by scripts/build_widgets.py on every render; do not edit. -->
::: {{.column-margin}}
```{{=html}}
<div class="sm-widget sm-tags sm-tags-side"><h3 class="sm-widget-title">Tags</h3>
<div class="sm-tag-cloud">{chips(counts, base="tags.html")}</div></div>
```
:::

```{{=html}}
<div id="sm-tags-page">
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
    document.querySelectorAll('.sm-tags-side .sm-tag').forEach(function (c) {{
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


# ---- authors -------------------------------------------------------------

def load_authors():
    f = ROOT / "authors.yml"
    return (yaml.safe_load(f.read_text(encoding="utf-8")) or {}) if f.exists() else {}


def author_posts(posts, a):
    names = {a["name"].lower(), *[str(x).lower() for x in a.get("aliases") or []]}
    return [p for p in posts if p["author"].lower() in names]


def author_page(slug, a, mine):
    links = "".join(f'<a class="sm-tag" href="{html.escape(l["href"])}" rel="noopener">{html.escape(l["text"])}</a>'
                    for l in a.get("links") or [])
    img = (f'<img class="sm-author-img" src="../{html.escape(a["image"])}" alt="{html.escape(a["name"])}">'
           if a.get("image") else "")
    return f"""---
title: "{a["name"]}"
description: "{" ".join(str(a.get("tagline") or "").split())}"
page-layout: article
toc: false
---

<!-- GENERATED by scripts/build_widgets.py from authors.yml; do not edit. -->
```{{=html}}
<div class="sm-author-head">
{img}
<div><p class="sm-author-bio">{html.escape(" ".join(str(a.get("bio") or "").split()))}</p>
<div class="sm-tag-cloud sm-tag-cloud-all">{links}</div></div>
</div>
<h2 class="sm-author-count">{len(mine)} post{"s" if len(mine) != 1 else ""}</h2>
<ul class="sm-post-list">{post_items(mine)}</ul>
```
"""


def write_authors(posts):
    authors = load_authors()
    out_dir = ROOT / "authors"
    out_dir.mkdir(exist_ok=True)
    data = {}
    for slug, a in authors.items():
        mine = author_posts(posts, a)
        (out_dir / f"{slug}.qmd").write_text(author_page(slug, a, mine), encoding="utf-8")
        for name in {a["name"], *[str(x) for x in a.get("aliases") or []]}:
            data[name.lower()] = {
                "slug": slug, "name": a["name"], "image": a.get("image") or "",
                "tagline": a.get("tagline") or "", "bio": " ".join(str(a.get("bio") or "").split()),
                "n": len(mine),
            }
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    (ROOT / "_authors-body.html").write_text(
        "<!-- GENERATED by scripts/build_widgets.py from authors.yml; do not edit. -->\n"
        "<script>\n(function () {\n  var authors = " + payload + ";\n" + AUTHORS_JS + "})();\n</script>\n",
        encoding="utf-8")


# Links bylines to the author page and adds an author card under each post.
AUTHORS_JS = r"""
  var css = document.querySelector('link[rel="stylesheet"][href$="styles.css"]');
  var base = css ? css.getAttribute('href').slice(0, -'styles.css'.length) : '';
  function find(name) { return authors[(name || '').trim().toLowerCase()]; }
  function link(el, a) {
    var k = document.createElement('a');
    k.href = base + 'authors/' + a.slug + '.html';
    k.className = 'sm-author-link';
    // homepage cards sit inside one big <a>; navigate ourselves so the author link wins
    k.addEventListener('click', function (e) { e.preventDefault(); e.stopPropagation(); location.href = k.href; });
    k.textContent = el.textContent.trim();
    el.textContent = '';
    el.appendChild(k);
  }
  // post title block: the <p> after the "Author" heading
  var first = null;
  document.querySelectorAll('.quarto-title-meta-heading').forEach(function (h) {
    if (!/^authors?$/i.test(h.textContent.trim())) return;
    h.nextElementSibling.querySelectorAll('p').forEach(function (p) {
      var a = find(p.textContent);
      if (a) { link(p, a); first = first || a; }
    });
  });
  // homepage cards
  document.querySelectorAll('.listing-author').forEach(function (el) {
    var a = find(el.textContent);
    if (a) link(el, a);
  });
  // author card at the end of a post
  var main = document.getElementById('quarto-document-content');
  if (first && main && /\/posts\//.test(location.pathname)) {
    var card = document.createElement('aside');
    card.className = 'sm-author-card';
    var img = first.image ? '<img class="sm-author-img" src="' + base + first.image + '" alt="">' : '';
    card.innerHTML = img + '<div><div class="sm-author-card-name"></div><p></p>' +
      '<a class="sm-author-more"></a></div>';
    card.querySelector('.sm-author-card-name').textContent = first.name;
    card.querySelector('p').textContent = first.tagline || first.bio;
    var more = card.querySelector('.sm-author-more');
    more.href = base + 'authors/' + first.slug + '.html';
    more.textContent = 'All ' + first.n + ' posts by ' + first.name + ' →';
    main.appendChild(card);
  }
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
    write_authors(posts)
    print(f"build_widgets: {len(posts)} posts -> {OUT.name}")


if __name__ == "__main__":
    main()
