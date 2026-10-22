#!/usr/bin/env python3
"""Check an SVG logo for app-icon fitness and render a small-size QA sheet."""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _render import inline_svg, render_html  # noqa: E402
from render_icon import pixel_font, squircle_mask  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "assets" / "templates"
DRAWABLE = {"path", "circle", "rect", "line", "polygon", "polyline", "ellipse", "use"}
BAD = {"text", "image", "foreignObject"}
COLOR_OK = {"none", "currentColor", "inherit", "transparent"}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_viewbox(root: ET.Element) -> Tuple[float, float, float, float]:
    raw = root.get("viewBox") or root.get("viewbox") or ""
    parts = [part for part in re.split(r"[,\s]+", raw.strip()) if part]
    if len(parts) != 4:
        return 0.0, 0.0, 100.0, 100.0
    try:
        return tuple(float(part) for part in parts)  # type: ignore[return-value]
    except ValueError:
        return 0.0, 0.0, 100.0, 100.0


def parse_number(value: str) -> Optional[float]:
    match = re.match(r"^\s*(-?\d+(?:\.\d+)?)", value)
    return float(match.group(1)) if match else None


def collect(svg: Path) -> Dict[str, Any]:
    tree = ET.parse(svg)
    root = tree.getroot()
    vx, vy, vw, vh = parse_viewbox(root)
    scale = 100.0 / vw if vw else 1.0

    elements: List[str] = []
    stroke_widths: List[float] = []
    colors: List[str] = []
    bad: List[str] = []

    for element in root.iter():
        name = local_name(element.tag)
        if name in DRAWABLE:
            elements.append(name)
        if name in BAD:
            bad.append(name)
        for attribute in ("stroke-width",):
            value = element.get(attribute)
            if value:
                number = parse_number(value)
                if number is not None:
                    stroke_widths.append(number * scale)
        style = element.get("style") or ""
        for match in re.finditer(r"stroke-width\s*:\s*(-?\d+(?:\.\d+)?)", style):
            stroke_widths.append(float(match.group(1)) * scale)
        for attribute in ("fill", "stroke"):
            value = (element.get(attribute) or "").strip()
            if value and value not in COLOR_OK and not value.startswith("url("):
                colors.append(value)

    return {
        "viewbox": [vx, vy, vw, vh],
        "viewbox_is_100": abs(vw - 100) < 0.01 and abs(vh - 100) < 0.01,
        "elements": elements,
        "stroke_widths": stroke_widths,
        "colors": sorted(set(colors)),
        "bad_elements": sorted(set(bad)),
        "element_count": len(elements),
    }


def render_mark(
    svg_text: str,
    out: Path,
    size: int,
    ink: str,
    browser: Optional[str],
) -> Path:
    data = {
        "width": size,
        "height": size,
        "bg": "#000000",
        "bg2": None,
        "angle": 135,
        "ink": ink,
        "svg": svg_text,
        "mark_ratio": 0.80,
        "show_bg": False,
    }
    return render_html(
        TEMPLATES / "icon.html",
        data,
        out,
        size,
        size,
        transparent=True,
        wait_ms=3000,
        browser=browser,
    )


def alpha_stats(path: Path) -> Dict[str, Any]:
    import numpy as np
    from PIL import Image

    with Image.open(path) as img:
        rgba = img.convert("RGBA")
        array = np.asarray(rgba)
        alpha = array[:, :, 3]
        ys, xs = np.where(alpha > 16)
        if len(xs) == 0:
            return {"empty": True, "coverage": 0.0, "bbox": None, "margin": 0.0, "center_offset": 1.0}
        bbox = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
        width, height = rgba.size
        margin = min(bbox[0], bbox[1], width - bbox[2], height - bbox[3]) / width
        center_x = (bbox[0] + bbox[2]) / 2
        center_y = (bbox[1] + bbox[3]) / 2
        center_offset = max(abs(center_x - width / 2), abs(center_y - height / 2)) / width
        coverage = float((alpha > 16).sum()) / (width * height)
        box_area = max(1, (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]))
        box_coverage = float((alpha > 16).sum()) / box_area
        return {
            "empty": False,
            "coverage": coverage,
            "box_coverage": box_coverage,
            "bbox": bbox,
            "margin": margin,
            "center_offset": center_offset,
        }


def composite(mark: Path, bg: str, size: int):
    from PIL import Image

    canvas = Image.new("RGB", (size, size), bg)
    with Image.open(mark) as source:
        tile = source.convert("RGBA").resize((size, size), Image.LANCZOS)
    canvas.paste(tile, (0, 0), tile)
    return canvas


def qa_sheet(
    mark_path: Path,
    light_mark_path: Path,
    small_path: Path,
    light_small_path: Path,
    out: Path,
    report: List[str],
    bg: str,
    ink: str,
    stats: Dict[str, Any],
) -> Path:
    from PIL import Image, ImageDraw

    canvas = Image.new("RGB", (1800, 1200), bg)
    draw = ImageDraw.Draw(canvas)
    title = pixel_font("InstrumentSerif-Regular.ttf", 56)
    body = pixel_font("PublicSans.ttf", 19)
    label = pixel_font("PublicSans.ttf", 16)
    mono = pixel_font("PublicSans.ttf", 15)

    draw.text((80, 58), "Logo structural & small-size check", font=title, fill=ink)
    draw.text((82, 132), "One mark, four masks, and the sizes that decide whether it survives.", font=body, fill=ink)

    dark = "#111111"
    field = "#1E2A2A"
    tiles = [
        ("On paper", composite(mark_path, bg, 300), 80),
        ("On dark", composite(light_mark_path, dark, 300), 470),
    ]
    for caption, tile, x in tiles:
        canvas.paste(tile, (x, 200))
        draw.text((x, 516), caption, font=label, fill=ink)

    # Mask previews use a dark field icon so the mask silhouette is visible.
    circle = composite(light_mark_path, field, 300)
    mask = Image.new("L", (300, 300), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, 299, 299), fill=255)
    circle.putalpha(mask)
    canvas.paste(circle, (860, 200), circle)
    draw.text((860, 516), "Circle mask", font=label, fill=ink)

    squircle = composite(light_mark_path, field, 300)
    squircle.putalpha(squircle_mask(300))
    canvas.paste(squircle, (1250, 200), squircle)
    draw.text((1250, 516), "Squircle mask", font=label, fill=ink)

    draw.text((80, 604), "Small sizes", font=body, fill=ink)
    x = 80
    with Image.open(small_path) as source:
        small = source.convert("RGBA")
    for size in (128, 64, 32, 16):
        tile = small.resize((size, size), Image.LANCZOS)
        canvas.paste(tile, (x, 660), tile)
        draw.text((x, 660 + 136), f"{size}px", font=label, fill=ink)
        x += 190

    dark_panel = Image.new("RGB", (760, 210), dark)
    dx = 24
    with Image.open(light_small_path) as source:
        light_small = source.convert("RGBA")
    for size in (128, 64, 32, 16):
        tile = light_small.resize((size, size), Image.LANCZOS)
        dark_panel.paste(tile, (dx, 40 + (128 - size) // 2), tile)
        dx += 180
    canvas.paste(dark_panel, (900, 620))
    draw.text((900, 842), "On dark", font=label, fill=ink)

    draw.text((80, 900), "Report", font=body, fill=ink)
    y = 936
    for line in report:
        draw.text((80, y), line, font=mono, fill=ink)
        y += 27

    status = "PASS" if not stats.get("errors") else "CHECK"
    draw.text((1460, 900), status, font=pixel_font("InstrumentSerif-Regular.ttf", 64), fill=ink)

    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, "PNG", optimize=True)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logo", type=Path)
    parser.add_argument("--out", type=Path, default=Path.cwd() / "logo-qa")
    parser.add_argument("--ink", default="#111111")
    parser.add_argument("--bg", default="#F7F4ED")
    parser.add_argument("--browser", default=None)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    logo = args.logo.resolve()
    if not logo.is_file() or logo.suffix.lower() != ".svg":
        print(f"ERROR: expected an SVG file: {logo}", file=sys.stderr)
        return 2

    info = collect(logo)
    svg_text = inline_svg(logo, args.ink)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)

    mark_512 = render_mark(svg_text, out / "_mark-512.png", 512, args.ink, args.browser)
    mark_32 = render_mark(svg_text, out / "_mark-32.png", 32, args.ink, args.browser)
    light_ink = "#F7F4ED"
    light_svg = inline_svg(logo, light_ink)
    light_512 = render_mark(light_svg, out / "_mark-light-512.png", 512, light_ink, args.browser)
    light_32 = render_mark(light_svg, out / "_mark-light-32.png", 32, light_ink, args.browser)
    stats_512 = alpha_stats(mark_512)
    stats_32 = alpha_stats(mark_32)

    errors: List[str] = []
    warnings: List[str] = []

    if not info["viewbox_is_100"]:
        warnings.append("viewBox is not '0 0 100 100'; scale coordinates to the 100-grid")
    if info["bad_elements"]:
        errors.append(f"remove non-logo elements: {', '.join(info['bad_elements'])}")
    if info["element_count"] > 24:
        errors.append(f"{info['element_count']} drawable elements; simplify to 1-2 core elements")
    elif info["element_count"] > 12:
        warnings.append(f"{info['element_count']} drawable elements; check that every element earns its place")
    if info["element_count"] == 0:
        errors.append("no drawable elements found")

    thin = [value for value in info["stroke_widths"] if value < 2.0]
    if thin:
        message = f"thinnest stroke is {min(thin):.2f}/100; primary strokes should be 2.5-4"
        if min(thin) < 1.0:
            errors.append(message)
        else:
            warnings.append(message)

    if len(info["colors"]) > 1:
        warnings.append(
            f"{len(info['colors'])} hardcoded colors; use currentColor for a one-color icon master"
        )

    if stats_512.get("empty"):
        errors.append("the 512 px render is empty")
    else:
        if stats_512["margin"] < 0.06:
            errors.append(f"mark touches the edge (margin {stats_512['margin']:.0%}); keep >= 8% padding")
        elif stats_512["margin"] < 0.08:
            warnings.append(f"tight margin {stats_512['margin']:.0%}; use >= 8% padding")
        elif stats_512["margin"] > 0.26:
            warnings.append(f"mark uses only {1 - 2 * stats_512['margin']:.0%} of the canvas; consider a larger mark")
        if stats_512["center_offset"] > 0.02:
            warnings.append(f"optical center is off by {stats_512['center_offset']:.1%}")
        if stats_512["box_coverage"] < 0.05:
            warnings.append("the mark is very sparse inside its bounding box")
        if stats_512["box_coverage"] > 0.92:
            warnings.append("the mark looks like a solid field; use a transparent mark for the logo master")

    if stats_32.get("empty"):
        errors.append("the mark disappears at 32 px")
    elif stats_32["coverage"] < 0.02:
        errors.append(f"only {stats_32['coverage']:.1%} ink at 32 px; it will disappear as a favicon")
    elif stats_32["coverage"] < 0.05:
        warnings.append(f"only {stats_32['coverage']:.1%} ink at 32 px; test it as a favicon")

    report = [
        f"File: {logo.name}",
        f"Drawable elements: {info['element_count']}",
        f"ViewBox: {'0 0 100 100' if info['viewbox_is_100'] else 'non-standard ' + str(info['viewbox'])}",
        f"Thinnest stroke: {min(info['stroke_widths']):.2f}/100" if info["stroke_widths"] else "Thinnest stroke: not set",
        f"Hardcoded colors: {len(info['colors'])}",
        f"512 px margin: {stats_512.get('margin', 0):.1%}",
        f"512 px ink: {stats_512.get('coverage', 0):.1%}",
        f"32 px ink: {stats_32.get('coverage', 0):.1%}",
    ]
    report.append("Status: " + ("PASS" if not errors else "CHECK REQUIRED"))

    sheet = qa_sheet(
        mark_512, light_512, mark_32, light_32,
        out / "logo-qa.png", report, args.bg, "#1F1D1A",
        {"errors": errors, "warnings": warnings},
    )

    final_mark = out / "logo-mark-512.png"
    from PIL import Image

    with Image.open(mark_512) as source:
        source.convert("RGBA").save(final_mark, "PNG", optimize=True)
    final_small = out / "logo-mark-32.png"
    with Image.open(mark_32) as source:
        source.convert("RGBA").save(final_small, "PNG", optimize=True)
    mark_512.unlink(missing_ok=True)
    mark_32.unlink(missing_ok=True)
    light_512.unlink(missing_ok=True)
    light_32.unlink(missing_ok=True)

    result = {
        "ok": not errors,
        "logo": str(logo),
        "structure": {
            "element_count": info["element_count"],
            "viewbox": info["viewbox"],
            "viewbox_is_100": info["viewbox_is_100"],
            "stroke_widths": info["stroke_widths"],
            "colors": info["colors"],
            "bad_elements": info["bad_elements"],
        },
        "render": {"512": stats_512, "32": stats_32},
        "errors": errors,
        "warnings": warnings,
        "outputs": [str(sheet), str(final_mark), str(final_small)],
    }
    (out / "logo-report.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    if args.pretty:
        for warning in warnings:
            print(f"WARN: {warning}")
        for error in errors:
            print(f"ERROR: {error}")
        print("logo is valid" if not errors else f"FAILED: {len(errors)} error(s)")
        print(f"wrote {sheet}")
        print(f"wrote {out / 'logo-report.json'}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
