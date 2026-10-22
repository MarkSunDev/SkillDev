#!/usr/bin/env python3
"""Repair a placeholder/photo region in a screenshot without changing the UI.

Examples:
  # fill a Likes placeholder card image area
  python3 scripts/repair_region.py base/likes.png people/isabella.png \
    --rect 18,300,265,245 --radius 30 --centering 0.5,0.25 \
    --fade-bottom 80 --fade-color "#2B1E24" --out screens/likes.png

  # replace a circular avatar
  python3 scripts/repair_region.py base/feed.png people/crystal.png \
    --rect 30,238,54,54 --shape circle --out screens/feed-avatar.png

The script changes only the requested rectangle/circle. Headers, text, buttons,
and navigation outside the region remain untouched.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps


def parse_rect(value: str) -> tuple[int, int, int, int]:
    parts = [part.strip() for part in value.replace("x", ",").split(",") if part.strip()]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("rect must be x,y,w,h")
    x, y, w, h = (int(part) for part in parts)
    if w <= 0 or h <= 0:
        raise argparse.ArgumentTypeError("rect width and height must be positive")
    return x, y, w, h


def parse_centering(value: str) -> tuple[float, float]:
    parts = [part.strip() for part in value.split(",") if part.strip()]
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("centering must be x,y between 0 and 1")
    x, y = (float(part) for part in parts)
    if not (0 <= x <= 1 and 0 <= y <= 1):
        raise argparse.ArgumentTypeError("centering values must be between 0 and 1")
    return x, y


def hex_rgb(value: str) -> tuple[int, int, int]:
    value = value.strip().lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    if len(value) != 6:
        raise argparse.ArgumentTypeError("color must be #RRGGBB")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def mask_for(size: tuple[int, int], shape: str, radius: int, scale: int = 4) -> Image.Image:
    w, h = size
    mask = Image.new("L", (w * scale, h * scale), 0)
    draw = ImageDraw.Draw(mask)
    if shape == "circle":
        draw.ellipse((0, 0, w * scale - 1, h * scale - 1), fill=255)
    else:
        draw.rounded_rectangle(
            (0, 0, w * scale - 1, h * scale - 1),
            radius=max(0, radius) * scale,
            fill=255,
        )
    return mask.resize((w, h), Image.LANCZOS)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base", type=Path)
    parser.add_argument("image", type=Path)
    parser.add_argument("--rect", type=parse_rect, required=True, help="x,y,w,h")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--shape", choices=("rect", "circle"), default="rect")
    parser.add_argument("--radius", type=int, default=0)
    parser.add_argument("--centering", type=parse_centering, default=(0.5, 0.25))
    parser.add_argument("--fade-bottom", type=int, default=0, help="pixels to fade at the bottom")
    parser.add_argument("--fade-color", type=hex_rgb, default=None)
    parser.add_argument("--quality", type=int, default=95)
    args = parser.parse_args()

    if not args.base.is_file():
        raise SystemExit(f"base not found: {args.base}")
    if not args.image.is_file():
        raise SystemExit(f"image not found: {args.image}")
    x, y, w, h = args.rect

    with Image.open(args.base) as src:
        base = src.convert("RGBA")
    with Image.open(args.image) as src:
        replacement = src.convert("RGB")

    tile = ImageOps.fit(
        replacement,
        (w, h),
        method=Image.LANCZOS,
        centering=args.centering,
    ).convert("RGBA")

    if args.fade_bottom > 0 and args.fade_color:
        fade_h = min(h, args.fade_bottom)
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        px = overlay.load()
        r, g, b = args.fade_color
        start = h - fade_h
        for yy in range(start, h):
            t = (yy - start) / max(1, fade_h - 1)
            alpha = int(255 * (t ** 1.35))
            for xx in range(w):
                px[xx, yy] = (r, g, b, alpha)
        tile = Image.alpha_composite(tile, overlay)

    mask = mask_for((w, h), args.shape, args.radius)
    base.paste(tile, (x, y), mask)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    if args.out.suffix.lower() in (".jpg", ".jpeg"):
        base.convert("RGB").save(args.out, "JPEG", quality=args.quality, subsampling=0)
    else:
        base.save(args.out, "PNG", optimize=True)
    print(f"wrote {args.out} ({base.width}x{base.height}), repaired {x},{y},{w},{h}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
