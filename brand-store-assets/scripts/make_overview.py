#!/usr/bin/env python3
"""Assemble a wide review sheet from a rendered five-image gallery."""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _render import render_html  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "assets" / "templates"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="Directory containing gallery.json")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--title", default=None, help="Plain title text")
    parser.add_argument("--subtitle", default=None)
    parser.add_argument("--bg", default="#F7F4ED")
    parser.add_argument("--ink", default="#1F1D1A")
    parser.add_argument("--accent", default=None)
    parser.add_argument("--jpeg", action="store_true")
    parser.add_argument("--browser", default=None)
    parser.add_argument("--wait-ms", type=int, default=4000)
    args = parser.parse_args()

    directory = args.directory.resolve()
    manifest_path = directory / "gallery.json"
    if not manifest_path.is_file():
        print(f"ERROR: {manifest_path} not found; run render_gallery.py first", file=sys.stderr)
        return 2
    with manifest_path.open(encoding="utf-8") as handle:
        manifest = json.load(handle)

    images = manifest.get("images") or []
    if not images:
        print("ERROR: gallery.json has no images", file=sys.stderr)
        return 2

    app = str(manifest.get("app") or "App")
    version = str(manifest.get("version") or "").strip()
    store = str(manifest.get("store") or "apple")
    label = "Google Play" if store == "play" else "App Store"
    canvas = str(manifest.get("canvas") or "")

    if args.title:
        title_html = html.escape(args.title)
    elif version:
        title_html = f"{html.escape(app)} <em>/ {html.escape(version)}</em>"
    else:
        title_html = f"{html.escape(app)} <em>/ {label}</em>"

    subtitle = args.subtitle or f"FIVE-IMAGE SET · {label.upper()} · {canvas}"

    first_image: Optional[dict] = images[0] if isinstance(images[0], dict) else None
    accent = args.accent or (
        str(first_image.get("accent")) if first_image and first_image.get("accent") else "#A98232"
    )

    items = []
    for index, image in enumerate(images, start=1):
        if not isinstance(image, dict):
            continue
        src = Path(str(image.get("src") or ""))
        if not src.is_absolute():
            src = directory / src
        if not src.is_file():
            print(f"ERROR: image not found: {src}", file=sys.stderr)
            return 2
        items.append(
            {
                "url": src.as_uri(),
                "label": f"{index:02d}",
                "name": image.get("feature") or image.get("slug") or "",
            }
        )

    out = args.out or (directory / ("overview.jpg" if args.jpeg else "overview.png"))
    aspect = 1320 / 2868
    canvas = str(manifest.get("canvas") or "").strip()
    if "x" in canvas:
        try:
            width, height = (int(part) for part in canvas.lower().split("x", 1))
            aspect = width / height
        except ValueError:
            pass
    elif items:
        from PIL import Image

        with Image.open(directory / str(images[0].get("src"))) as image:
            aspect = image.width / image.height
    gap = 44
    thumb_w = round(880 * aspect)
    if len(items) * thumb_w + max(0, len(items) - 1) * gap > 3000:
        thumb_w = (3000 - max(0, len(items) - 1) * gap) // max(1, len(items))
        thumb_h = round(thumb_w / aspect)
    else:
        thumb_h = 880
    data = {
        "title_html": title_html,
        "subtitle": subtitle,
        "bg": args.bg,
        "ink": args.ink,
        "accent": accent,
        "images": items,
        "thumb_w": thumb_w,
        "thumb_h": thumb_h,
        "gap": gap,
    }
    render_html(
        TEMPLATES / "overview.html",
        data,
        out,
        3200,
        1280,
        wait_ms=args.wait_ms,
        browser=args.browser,
    )
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
