#!/usr/bin/env python3
"""Render App Store / Google Play five-image galleries from real app screens."""

from __future__ import annotations

import argparse
import html
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _render import (  # noqa: E402
    contrast_ratio,
    image_aspect,
    load_manifest,
    parse_size,
    prepare_brand,
    render_html,
    resolve_path,
    save_rgb,
    typography,
    write_json,
)

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "assets" / "templates"

STORE_DEFAULTS = {
    "apple": {"size": (1320, 2868), "exports": [(1206, 2622)], "label": "App Store"},
    "play": {"size": (1440, 2560), "exports": [(1080, 1920)], "label": "Google Play"},
}

REQUIRED = ("slug", "feature", "title", "body", "bg", "ink", "accent", "footer")


def size_label(size: Tuple[int, int]) -> str:
    return f"{size[0]}x{size[1]}"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)


def validate_copy(image: Dict[str, Any], index: int) -> List[str]:
    problems: List[str] = []
    label = f"image {index:02d}"
    for field in REQUIRED:
        if field not in image:
            problems.append(f"{label}: missing '{field}'")
    for field in ("title", "body"):
        value = image.get(field)
        if not isinstance(value, list) or len(value) != 2:
            problems.append(f"{label}: '{field}' must be an array of exactly two lines")
        elif not all(str(line).strip() for line in value):
            problems.append(f"{label}: '{field}' contains an empty line")
    for field in ("bg", "ink", "accent"):
        try:
            contrast_ratio(str(image.get(field, "")), str(image.get(field, "")))
        except Exception:
            problems.append(f"{label}: '{field}' is not a 6-digit hex color")
    if not str(image.get("feature", "")).strip():
        problems.append(f"{label}: 'feature' is empty")
    if not str(image.get("footer", "")).strip():
        problems.append(f"{label}: 'footer' is empty")
    return problems


def screen_path(
    image: Dict[str, Any], base_dir: Path, assets_dir: Optional[Path]
) -> Optional[Path]:
    value = image.get("screen") or image.get("artwork") or image.get("src")
    if not value:
        return None
    base = assets_dir or base_dir
    path = resolve_path(str(value), base)
    return path if path.is_file() else None


def build_image_data(
    root: Dict[str, Any],
    image: Dict[str, Any],
    index: int,
    total: int,
    store: str,
    base_dir: Path,
    assets_dir: Optional[Path],
    frame_override: Optional[str] = None,
) -> Dict[str, Any]:
    ink = str(image["ink"])
    brand = prepare_brand(root, base_dir, ink)
    screen = screen_path(image, base_dir, assets_dir)
    if screen is None:
        raise FileNotFoundError(
            f"image {index:02d}: real screenshot not found; set 'screen' to a PNG/JPEG path"
        )
    aspect = image_aspect(screen, 9 / 16 if store == "play" else 1320 / 2868)
    layout = str(image.get("layout") or root.get("layout") or "editorial")
    default_frame = ("iphone" if store == "apple" else "pixel") if layout == "poster" else "phone"
    frame = frame_override or str(image.get("frame") or root.get("frame") or default_frame)
    mood = image.get("mood") or root.get("mood") or "plain"
    overflow = dict(image.get("overflow") or root.get("overflow") or {})
    if overflow.get("photo"):
        overflow_path = resolve_path(str(overflow["photo"]), assets_dir or base_dir)
        if not overflow_path.is_file():
            raise FileNotFoundError(f"image {index:02d}: overflow photo not found: {overflow_path}")
        overflow["photo"] = overflow_path.as_uri()
    return {
        "store": store,
        "width": 0,
        "height": 0,
        "brand": brand,
        "type": typography(root),
        "layout": layout,
        "mood": mood,
        "frame": frame,
        "image": {
            "index": index,
            "total": total,
            "slug": image.get("slug"),
            "feature": image.get("feature"),
            "title": image.get("title"),
            "body": image.get("body"),
            "footer": image.get("footer"),
            "bg": image.get("bg"),
            "ink": image.get("ink"),
            "accent": image.get("accent"),
            "accent2": image.get("accent2") or root.get("accent2") or image.get("accent"),
            "badge": image.get("badge") or root.get("badge") or "",
            "badge_ink": image.get("badge_ink") or root.get("badge_ink") or "#1A1012",
            "callout": image.get("callout") or root.get("callout") or "",
            "callout_side": image.get("callout_side") or root.get("callout_side") or "left",
            "sticker": image.get("sticker") or root.get("sticker") or "",
            "overflow": overflow,
            "tilt": float(image.get("tilt", root.get("tilt", -2))),
            "screenshot": screen.as_uri(),
            "aspect": aspect,
            "layout": layout,
            "mood": mood,
            "frame": frame,
            "notch": bool(image.get("notch", False)),
            "show_footer": image.get("show_footer", True),
        },
    }


def feature_data(
    root: Dict[str, Any], base_dir: Path, fallback_ink: str, fallback_bg: str
) -> Optional[Dict[str, Any]]:
    fg = root.get("feature_graphic")
    if not isinstance(fg, dict):
        return None
    headline = fg.get("headline")
    if not isinstance(headline, list) or not headline:
        return None
    ink = str(fg.get("ink") or fallback_ink)
    brand = prepare_brand(root, base_dir, ink)
    return {
        "width": 1024,
        "height": 500,
        "brand": brand,
        "type": typography(root),
        "headline": headline[:2],
        "support": fg.get("support") or "",
        "footerline": fg.get("footerline") or "",
        "bg": fg.get("bg") or fallback_bg,
        "bg2": fg.get("bg2"),
        "ink": ink,
        "accent": fg.get("accent") or root.get("accent") or "#D7EA8E",
        "mood": fg.get("mood") or "glow",
    }


def overview_data(
    root: Dict[str, Any],
    store: str,
    outputs: List[Tuple[Dict[str, Any], Path]],
    size: Tuple[int, int],
) -> Dict[str, Any]:
    app = str(root.get("app") or (root.get("brand") or {}).get("name") or "App")
    version = str(root.get("version") or "").strip()
    label = STORE_DEFAULTS[store]["label"]
    if version:
        title_html = f"{html.escape(app)} <em>/ {html.escape(version)}</em>"
    else:
        title_html = f"{html.escape(app)} <em>/ {label}</em>"
    images = []
    for index, (image, path) in enumerate(outputs, start=1):
        images.append(
            {
                "url": path.as_uri(),
                "label": f"{index:02d}",
                "name": image.get("feature") or image.get("slug") or "",
            }
        )
    aspect = size[0] / size[1]
    gap = 44
    target_height = 880
    thumb_width = round(target_height * aspect)
    if len(images) * thumb_width + (len(images) - 1) * gap > 3000:
        thumb_width = (3000 - (len(images) - 1) * gap) // max(1, len(images))
        thumb_height = round(thumb_width / aspect)
    else:
        thumb_height = target_height
    return {
        "title_html": title_html,
        "subtitle": f"{len(images)}-IMAGE SET · {label.upper()} · {size[0]} × {size[1]}",
        "bg": root.get("overview_bg") or "#F7F4ED",
        "ink": root.get("overview_ink") or "#1F1D1A",
        "accent": root.get("overview_accent") or "#A98232",
        "images": images,
        "thumb_w": thumb_width,
        "thumb_h": thumb_height,
        "gap": gap,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="Gallery JSON manifest")
    parser.add_argument("--store", choices=("apple", "play"), default=None)
    parser.add_argument("--out", type=Path, default=None, help="Output directory")
    parser.add_argument("--size", default=None, help="Master canvas, e.g. 1320x2868")
    parser.add_argument(
        "--export-sizes",
        nargs="*",
        default=None,
        help="Additional canvases to export, e.g. 1206x2622 1080x1920",
    )
    parser.add_argument("--assets-dir", type=Path, default=None)
    parser.add_argument("--frame", choices=("pixel", "iphone", "card"), default=None)
    parser.add_argument("--only", default=None, help="Comma-separated slugs to render")
    parser.add_argument("--jpeg", action="store_true", help="Export JPEG instead of PNG")
    parser.add_argument("--feature-graphic", action="store_true")
    parser.add_argument("--overview", action="store_true")
    parser.add_argument("--browser", default=None)
    parser.add_argument("--wait-ms", type=int, default=5000)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    manifest_path, root, images = load_manifest(args.manifest)
    base_dir = manifest_path.parent
    store = args.store or str(root.get("store") or "apple")
    if store not in STORE_DEFAULTS:
        fail(f"unknown store '{store}'")
        return 2

    default = STORE_DEFAULTS[store]
    if args.size:
        try:
            master = parse_size(args.size)
        except ValueError as exc:
            fail(str(exc))
            return 2
    else:
        master = default["size"]

    if args.export_sizes is None:
        exports = default["exports"] if master == default["size"] else []
    else:
        exports = []
        for value in args.export_sizes:
            try:
                exports.append(parse_size(value))
            except ValueError as exc:
                fail(str(exc))
                return 2

    out_dir = (args.out or (Path.cwd() / "store-assets" / store)).resolve()
    only = {item.strip() for item in args.only.split(",")} if args.only else None

    problems: List[str] = []
    selected: List[Tuple[int, Dict[str, Any]]] = []
    for index, image in enumerate(images, start=1):
        problems.extend(validate_copy(image, index))
        slug = str(image.get("slug") or "")
        if only and slug not in only:
            continue
        selected.append((index, image))
    if problems:
        for problem in problems:
            fail(problem)
        return 2
    if not selected:
        fail("no images selected")
        return 2

    total = len(images)
    plan: List[Tuple[int, Dict[str, Any], Path]] = []
    for index, image in selected:
        screen = screen_path(image, base_dir, args.assets_dir)
        if screen is None:
            fail(f"image {index:02d}: screenshot not found")
            return 2
        suffix = ".jpg" if args.jpeg else ".png"
        output = out_dir / f"{image['slug']}{suffix}"
        plan.append((index, image, output))

        ratio = contrast_ratio(str(image["ink"]), str(image["bg"]))
        accent_ratio = contrast_ratio(str(image["accent"]), str(image["bg"]))
        print(
            f"{index:02d} {image['slug']}: {screen.name} "
            f"({image_aspect(screen):.3f}) -> {output.name} "
            f"ink/bg {ratio:.1f}:1 accent/bg {accent_ratio:.1f}:1"
        )

    print(f"store: {store}; master: {size_label(master)}; exports: "
          f"{', '.join(size_label(size) for size in exports) or 'none'}")

    if args.dry_run:
        print("dry run: no files written")
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    layout_mode = str(root.get("layout") or "editorial")
    template = TEMPLATES / ("poster.html" if layout_mode == "poster" else "gallery.html")
    rendered: List[Tuple[Dict[str, Any], Path]] = []
    for index, image, output in plan:
        data = build_image_data(
            root, image, index, total, store, base_dir, args.assets_dir, args.frame
        )
        data["width"], data["height"] = master
        print(f"render {output.name} ...", end=" ", flush=True)
        render_html(
            template,
            data,
            output,
            master[0],
            master[1],
            wait_ms=args.wait_ms,
            browser=args.browser,
        )
        print("ok")
        rendered.append((image, output))

        for export_size in exports:
            export_path = out_dir / "exports" / f"{image['slug']}-{size_label(export_size)}{output.suffix}"
            save_rgb(output, export_path, export_size, jpeg=args.jpeg)
            print(f"  export {export_path.name}")

    output_manifest: Dict[str, Any] = {
        "app": root.get("app"),
        "version": root.get("version"),
        "store": store,
        "canvas": size_label(master),
        "exports": [size_label(size) for size in exports],
        "images": [],
    }
    for image, output in rendered:
        item = dict(image)
        item["src"] = output.name
        item["size"] = size_label(master)
        item["screen"] = str(
            screen_path(image, base_dir, args.assets_dir) or image.get("screen", "")
        )
        output_manifest["images"].append(item)

    if args.feature_graphic:
        fg = root.get("feature_graphic")
        if isinstance(fg, dict) and fg.get("src") and not fg.get("headline"):
            print(f"feature graphic: keeping supplied file {fg['src']}")
            output_manifest["feature_graphic"] = fg
        else:
            first = rendered[0][0]
            data = feature_data(
                root, base_dir, str(first["ink"]), str(first["bg"])
            )
            if data is None:
                fail("--feature-graphic needs feature_graphic.headline in the manifest")
                return 2
            fg_path = out_dir / ("feature-graphic-1024x500.jpg" if args.jpeg else "feature-graphic-1024x500.png")
            print(f"render {fg_path.name} ...", end=" ", flush=True)
            render_html(
                TEMPLATES / "feature.html",
                data,
                fg_path,
                1024,
                500,
                wait_ms=args.wait_ms,
                browser=args.browser,
            )
            print("ok")
            output_manifest["feature_graphic"] = {
                "src": fg_path.name,
                "size": "1024x500",
                "headline": data["headline"],
                "support": data["support"],
                "bg": data["bg"],
                "ink": data["ink"],
                "accent": data["accent"],
            }

    if args.overview:
        data = overview_data(root, store, rendered, master)
        overview_path = out_dir / ("overview.jpg" if args.jpeg else "overview.png")
        print(f"render {overview_path.name} ...", end=" ", flush=True)
        render_html(
            TEMPLATES / "overview.html",
            data,
            overview_path,
            3200,
            1280,
            wait_ms=args.wait_ms,
            browser=args.browser,
        )
        print("ok")
        output_manifest["overview"] = overview_path.name

    write_json(out_dir / "gallery.json", output_manifest)
    print(f"wrote {out_dir / 'gallery.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
