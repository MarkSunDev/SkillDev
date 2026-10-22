#!/usr/bin/env python3
"""Composite a deterministic brand showcase over an AI-generated backdrop."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _render import inline_svg, render_html  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "assets" / "templates"


def mean_color(path: Path):
    from PIL import Image

    with Image.open(path) as image:
        small = image.convert("RGB").resize((64, 64), Image.LANCZOS)
    pixels = list(small.getdata())
    count = len(pixels)
    rgb = tuple(sum(channel[i] for channel in pixels) // count for i in range(3))
    luminance = (
        0.2126 * (rgb[0] / 255) ** 2.2
        + 0.7152 * (rgb[1] / 255) ** 2.2
        + 0.0722 * (rgb[2] / 255) ** 2.2
    )
    return rgb, luminance


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("backdrop", type=Path)
    parser.add_argument("logo", type=Path)
    parser.add_argument("--name", required=True)
    parser.add_argument("--tagline", default="")
    parser.add_argument("--out", type=Path, default=Path.cwd() / "showcase.png")
    parser.add_argument("--ink", default=None)
    parser.add_argument("--field", default=None)
    parser.add_argument("--accent", default="#D7EA8E")
    parser.add_argument("--scrim", type=float, default=None)
    parser.add_argument("--micro", default="BRAND MARK / 01")
    parser.add_argument("--footer", default="Identity system")
    parser.add_argument("--browser", default=None)
    parser.add_argument("--wait-ms", type=int, default=4000)
    args = parser.parse_args()

    backdrop = args.backdrop.resolve()
    logo = args.logo.resolve()
    if not backdrop.is_file():
        print(f"ERROR: backdrop not found: {backdrop}", file=sys.stderr)
        return 2
    if not logo.is_file() or logo.suffix.lower() != ".svg":
        print(f"ERROR: logo must be an SVG: {logo}", file=sys.stderr)
        return 2

    rgb, luminance = mean_color(backdrop)
    dark_field = luminance < 0.42
    ink = args.ink or ("#F7F4ED" if dark_field else "#1F1D1A")
    field = args.field or "#{:02X}{:02X}{:02X}".format(*rgb)
    scrim = args.scrim if args.scrim is not None else (0.32 if dark_field else 0.06)

    data = {
        "backdrop": backdrop.as_uri(),
        "logo_svg": inline_svg(logo, ink),
        "name": args.name,
        "tagline": args.tagline,
        "ink": ink,
        "field": field,
        "accent": args.accent,
        "scrim": scrim,
        "micro": args.micro,
        "footer": args.footer,
    }
    out = args.out.resolve()
    print(f"showcase: {backdrop.name} + {logo.name} -> {out.name} "
          f"(ink {ink}, field {field}, scrim {scrim:.2f})")
    render_html(
        TEMPLATES / "showcase.html",
        data,
        out,
        1600,
        1200,
        wait_ms=args.wait_ms,
        browser=args.browser,
    )
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
