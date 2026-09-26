#!/usr/bin/env python3
"""Turn a blog SVG figure into a 1200x630 PNG for use as the post's `image:`
(og:image / thumbnail), because social platforms don't render SVG.

Usage (from blograw/):  python3 svg2og.py img/my-figure.svg [more.svg ...]
Writes img/my-figure.png next to each SVG, centred on the site's dark
background. Needs: pip install cairosvg pillow
"""
import io
import sys

import cairosvg
from PIL import Image

W, H, BG = 1200, 630, (5, 7, 13, 255)


def convert(svg, png):
    fig = Image.open(io.BytesIO(cairosvg.svg2png(url=svg, output_width=W - 100))).convert("RGBA")
    if fig.height > H - 40:  # tall figure: fit to height instead
        fig = Image.open(io.BytesIO(cairosvg.svg2png(url=svg, output_height=H - 40))).convert("RGBA")
    canvas = Image.new("RGBA", (W, H), BG)
    canvas.paste(fig, ((W - fig.width) // 2, (H - fig.height) // 2), fig)
    canvas.convert("RGB").save(png, optimize=True)
    print(png, canvas.size)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for s in sys.argv[1:]:
        convert(s, s.rsplit(".", 1)[0] + ".png")
