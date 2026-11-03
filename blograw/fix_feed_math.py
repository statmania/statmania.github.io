#!/usr/bin/env python3
"""Post-render hook: shrink the math images in the RSS feeds.

Quarto renders math in feeds as codecogs `png.latex` images, which are 300 dpi, so they show
several times larger than the surrounding text in feed readers and aggregators (R-bloggers).
Rewrite them to `png.image` with \\dpi{110}, which matches body text size. Idempotent.
"""
import os
from pathlib import Path

OLD = "https://latex.codecogs.com/png.latex?"
NEW = "https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D"

out = Path(os.environ.get("QUARTO_PROJECT_OUTPUT_DIR") or "../blog")
if not out.is_absolute():
    out = Path(os.environ.get("QUARTO_PROJECT_DIR") or Path.cwd()) / out
for feed in sorted(out.glob("index*.xml")):
    text = feed.read_text(encoding="utf-8")
    if OLD in text:
        feed.write_text(text.replace(OLD, NEW), encoding="utf-8")
        print(f"fix_feed_math: shrank math images in {feed.name}")
