#!/usr/bin/env python3
"""Regenerate sitemap-tools.xml for the hand-written, non-Quarto-rendered
sections of the site (utility/, games/, courses/index.html, ds/, slide/)
plus the R package dashboard, none of which are covered by Quarto's own
generated sitemap.xml, blog/sitemap.xml, or courses/rprogramming/sitemap.xml.

Run from the repo root: python3 scripts/gen_sitemap_tools.py
"""
import datetime
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://www.statmania.info/"

# Full-page fragments/embeds that aren't real standalone pages (no <head>,
# not linked anywhere) and shouldn't be indexed.
EXCLUDE = {
    "ds/viz/map/svg/bd-select.html",
    "ds/viz/map/d3/bd-district-map.html",
}


def collect_files():
    files = []
    files += sorted((ROOT / "utility").glob("*.html"))
    files += sorted((ROOT / "games").glob("*.html"))
    # courses/index.html is hand-written (no Quarto sitemap of its own);
    # courses/rprogramming/ is a Quarto website project with site-url set,
    # so it generates and maintains its own sitemap.xml — not duplicated here.
    files += sorted((ROOT / "courses").glob("*.html"))
    files += sorted((ROOT / "ds/viz").glob("*.html"))
    files += sorted((ROOT / "ds/analysis").glob("*.html"))
    files += sorted((ROOT / "ds/viz/map").glob("*.html"))
    files += sorted((ROOT / "ds/viz/map/svg").glob("*.html"))
    files += [ROOT / "ds/dash/rpkg.html"]
    files += sorted((ROOT / "slide").glob("*.html"))

    out = []
    for f in files:
        rel = f.relative_to(ROOT).as_posix()
        if rel in EXCLUDE or not f.exists():
            continue
        out.append(f)
    return out


def lastmod(path: pathlib.Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    result = subprocess.run(
        ["git", "log", "-1", "--format=%cI", "--", rel],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    ts = result.stdout.strip()
    if ts:
        dt = datetime.datetime.fromisoformat(ts)
    else:
        dt = datetime.datetime.fromtimestamp(path.stat().st_mtime, tz=datetime.timezone.utc)
    return dt.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def main():
    files = collect_files()
    entries = [(BASE + f.relative_to(ROOT).as_posix(), lastmod(f)) for f in files]
    entries.sort()

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, mod in entries:
        lines.append(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{mod}</lastmod>\n  </url>")
    lines.append("</urlset>")
    lines.append("")

    out_path = ROOT / "sitemap-tools.xml"
    out_path.write_text("\n".join(lines))
    print(f"Wrote {len(entries)} URLs to {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
