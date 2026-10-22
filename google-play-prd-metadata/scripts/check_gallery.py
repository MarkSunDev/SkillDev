#!/usr/bin/env python3
"""Validate a Google Play screenshot manifest with optional icon and feature graphic."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = ("slug", "feature", "title", "body", "src", "bg", "ink", "accent", "footer")
HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
SIZE_RE = re.compile(r"^(\d+)\s*[xX×]\s*(\d+)$")

MIN_SIDE = 320
MAX_SIDE = 3840
MAX_RATIO = 2.0
ICON_SIZE = (512, 512)
FEATURE_GRAPHIC_SIZE = (1024, 500)
ICON_MAX_BYTES = 1024 * 1024
FEATURE_GRAPHIC_MAX_BYTES = 15 * 1024 * 1024


def parse_size(value: str) -> tuple[int, int]:
    match = SIZE_RE.match(value.strip())
    if not match:
        raise ValueError(f"'{value}' is not a size such as 1440x2560")
    width, height = int(match.group(1)), int(match.group(2))
    if width <= 0 or height <= 0:
        raise ValueError(f"'{value}' must contain positive dimensions")
    return width, height


def load_images(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        images = data.get("images")
        if isinstance(images, list):
            return images
    raise ValueError("Expected an array of images or an object containing an images array")


def load_asset(data: Any, key: str) -> dict[str, Any] | None:
    if not isinstance(data, dict):
        return None
    value = data.get(key)
    if value is None:
        return None
    if isinstance(value, str):
        return {"src": value}
    if isinstance(value, dict):
        return value
    raise ValueError(f"'{key}' must be a path or an object with src/size")


def validate(images: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not 2 <= len(images) <= 8:
        errors.append(f"gallery must contain 2-8 screenshots per device type, found {len(images)}")
    elif len(images) != 5:
        warnings.append(
            f"gallery contains {len(images)} screenshots; five is this skill's editorial convention"
        )

    slugs: list[str] = []
    sources: list[str] = []

    for index, image in enumerate(images, start=1):
        label = f"image {index:02d}"
        if not isinstance(image, dict):
            errors.append(f"{label}: must be an object")
            continue

        missing = [field for field in REQUIRED_FIELDS if field not in image]
        if missing:
            errors.append(f"{label}: missing fields: {', '.join(missing)}")

        slug = str(image.get("slug", ""))
        if slug:
            slugs.append(slug)
            expected = f"{index:02d}-"
            if not slug.startswith(expected):
                warnings.append(f"{label}: slug should start with '{expected}'")

        title = image.get("title")
        if not isinstance(title, list) or len(title) != 2 or not all(str(line).strip() for line in title):
            errors.append(f"{label}: title must be exactly two non-empty lines")

        body = image.get("body")
        if not isinstance(body, list) or len(body) != 2 or not all(str(line).strip() for line in body):
            errors.append(f"{label}: body must be exactly two non-empty lines")

        src = str(image.get("src", "")).strip()
        if src:
            sources.append(src)

        for field in ("bg", "ink", "accent"):
            value = str(image.get(field, "")).strip()
            if not HEX_RE.match(value):
                errors.append(f"{label}: {field} must be a 6-digit hex color such as #F7F4ED")

        if not str(image.get("feature", "")).strip():
            errors.append(f"{label}: feature/eyebrow is empty")
        if not str(image.get("footer", "")).strip():
            errors.append(f"{label}: footer is empty")

        if "size" in image:
            try:
                parse_size(str(image.get("size", "")))
            except ValueError:
                errors.append(f"{label}: size must look like 1440x2560")

    if len(slugs) != len(set(slugs)):
        errors.append("gallery contains duplicate slugs")
    if len(sources) != len(set(sources)):
        errors.append("gallery reuses the same screenshot source")

    return errors, warnings


def resolve_path(src: str, assets_dir: Path) -> Path:
    path = Path(src)
    return path if path.is_absolute() else assets_dir / path


def check_screenshot(
    image: dict[str, Any],
    index: int,
    assets_dir: Path,
    expected_sizes: list[tuple[int, int]],
    errors: list[str],
    warnings: list[str],
) -> None:
    label = f"image {index:02d}"
    src = str(image.get("src", "")).strip()
    if not src:
        return

    path = resolve_path(src, assets_dir)
    if not path.is_file():
        errors.append(f"{label}: file not found: {path}")
        return

    try:
        from PIL import Image
    except ImportError:
        errors.append("--check-files requires Pillow; install with: python3 -m pip install Pillow")
        return

    try:
        with Image.open(path) as img:
            width, height = img.size
            image_format = (img.format or "").upper()
            mode = img.mode
            has_alpha = "A" in img.getbands() or "transparency" in img.info
    except OSError as exc:
        errors.append(f"{label}: cannot read {path}: {exc}")
        return

    if image_format not in ("PNG", "JPEG"):
        errors.append(f"{label}: must be PNG or JPEG, found {image_format or 'unknown'}")
    if has_alpha:
        errors.append(f"{label}: contains an alpha channel or transparency; Play screenshots must be flattened RGB")
    elif mode != "RGB":
        warnings.append(f"{label}: mode is {mode}, expected RGB")

    if min(width, height) < MIN_SIDE or max(width, height) > MAX_SIDE:
        errors.append(
            f"{label}: size is {width}x{height}; each side must be between {MIN_SIDE} and {MAX_SIDE} px"
        )
    ratio = max(width, height) / min(width, height)
    if ratio > MAX_RATIO + 1e-9:
        errors.append(
            f"{label}: aspect ratio is {ratio:.2f}:1, wider than Play's 2:1 limit; compose on a 9:16 canvas"
        )

    declared = str(image.get("size", "")).strip()
    if declared:
        try:
            expected = parse_size(declared)
        except ValueError:
            return
        if (width, height) != expected:
            errors.append(
                f"{label}: size is {width}x{height}, manifest declares {expected[0]}x{expected[1]}"
            )
    elif expected_sizes:
        if (width, height) not in expected_sizes:
            allowed = ", ".join(f"{w}x{h}" for w, h in expected_sizes)
            errors.append(f"{label}: size is {width}x{height}; allowed: {allowed}")


def check_icon(asset: dict[str, Any] | None, assets_dir: Path, errors: list[str], warnings: list[str]) -> None:
    if asset is None:
        warnings.append("manifest has no icon entry; verify the 512x512 32-bit PNG separately")
        return

    src = str(asset.get("src", "")).strip()
    if not src:
        errors.append("icon: missing src")
        return

    path = resolve_path(src, assets_dir)
    if not path.is_file():
        errors.append(f"icon: file not found: {path}")
        return

    try:
        from PIL import Image
    except ImportError:
        errors.append("--check-files requires Pillow; install with: python3 -m pip install Pillow")
        return

    try:
        with Image.open(path) as img:
            width, height = img.size
            image_format = (img.format or "").upper()
            mode = img.mode
            has_alpha = "A" in img.getbands() or "transparency" in img.info
    except OSError as exc:
        errors.append(f"icon: cannot read {path}: {exc}")
        return

    if image_format != "PNG":
        errors.append(f"icon: must be PNG, found {image_format or 'unknown'}")
    if (width, height) != ICON_SIZE:
        errors.append(f"icon: size is {width}x{height}; Play requires {ICON_SIZE[0]}x{ICON_SIZE[1]}")
    if not has_alpha:
        errors.append("icon: missing alpha channel; Play requires a 32-bit PNG with alpha")
    elif mode != "RGBA":
        warnings.append(f"icon: mode is {mode}; export a true-color 32-bit RGBA PNG")

    size_bytes = path.stat().st_size
    if size_bytes > ICON_MAX_BYTES:
        errors.append(
            f"icon: file is {size_bytes} bytes; Play allows at most {ICON_MAX_BYTES} bytes (1 MB)"
        )


def check_feature_graphic(
    asset: dict[str, Any] | None,
    assets_dir: Path,
    errors: list[str],
    warnings: list[str],
) -> None:
    if asset is None:
        warnings.append("manifest has no feature_graphic entry; Play requires a 1024x500 graphic")
        return

    src = str(asset.get("src", "")).strip()
    if not src:
        errors.append("feature_graphic: missing src")
        return

    path = resolve_path(src, assets_dir)
    if not path.is_file():
        errors.append(f"feature_graphic: file not found: {path}")
        return

    try:
        from PIL import Image
    except ImportError:
        errors.append("--check-files requires Pillow; install with: python3 -m pip install Pillow")
        return

    try:
        with Image.open(path) as img:
            width, height = img.size
            image_format = (img.format or "").upper()
            mode = img.mode
            has_alpha = "A" in img.getbands() or "transparency" in img.info
    except OSError as exc:
        errors.append(f"feature_graphic: cannot read {path}: {exc}")
        return

    if image_format not in ("PNG", "JPEG"):
        errors.append(f"feature_graphic: must be PNG or JPEG, found {image_format or 'unknown'}")
    if has_alpha:
        errors.append("feature_graphic: contains an alpha channel or transparency; export flattened RGB")
    elif mode != "RGB":
        warnings.append(f"feature_graphic: mode is {mode}, expected RGB")
    if (width, height) != FEATURE_GRAPHIC_SIZE:
        errors.append(
            f"feature_graphic: size is {width}x{height}; Play requires "
            f"{FEATURE_GRAPHIC_SIZE[0]}x{FEATURE_GRAPHIC_SIZE[1]}"
        )

    size_bytes = path.stat().st_size
    if size_bytes > FEATURE_GRAPHIC_MAX_BYTES:
        errors.append(
            f"feature_graphic: file is {size_bytes} bytes; Play allows at most "
            f"{FEATURE_GRAPHIC_MAX_BYTES} bytes (15 MB)"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_file", type=Path, help="Gallery JSON file, or - for stdin")
    parser.add_argument("--pretty", action="store_true", help="Print a human-readable summary")
    parser.add_argument(
        "--check-files",
        action="store_true",
        help="Validate screenshot, icon, and feature graphic files, formats, alpha rules, and dimensions",
    )
    parser.add_argument(
        "--assets-dir",
        type=Path,
        default=None,
        help="Base directory for relative src paths (default: the manifest's directory)",
    )
    parser.add_argument(
        "--size",
        action="append",
        default=[],
        metavar="WxH",
        help="Require an exact screenshot size; repeat for multiple allowed sizes",
    )
    args = parser.parse_args()

    raw = sys.stdin.read() if str(args.json_file) == "-" else args.json_file.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
        images = load_images(data)
        icon = load_asset(data, "icon")
        feature_graphic = load_asset(data, "feature_graphic")
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"Invalid gallery manifest: {exc}", file=sys.stderr)
        return 2

    expected_sizes: list[tuple[int, int]] = []
    for value in args.size:
        try:
            expected_sizes.append(parse_size(value))
        except ValueError as exc:
            print(f"Invalid --size: {exc}", file=sys.stderr)
            return 2

    errors, warnings = validate(images)
    if args.check_files:
        try:
            from PIL import Image  # noqa: F401
        except ImportError:
            errors.append("--check-files requires Pillow; install with: python3 -m pip install Pillow")
        else:
            assets_dir = args.assets_dir or (
                args.json_file.parent if str(args.json_file) != "-" else Path.cwd()
            )
            for index, image in enumerate(images, start=1):
                if isinstance(image, dict):
                    check_screenshot(image, index, assets_dir, expected_sizes, errors, warnings)
            check_icon(icon, assets_dir, errors, warnings)
            check_feature_graphic(feature_graphic, assets_dir, errors, warnings)

    result = {"ok": not errors, "count": len(images), "errors": errors, "warnings": warnings}

    if args.pretty:
        print(f"images: {len(images)}")
        for warning in warnings:
            print(f"WARN: {warning}")
        for error in errors:
            print(f"ERROR: {error}")
        if not errors:
            print("gallery is valid")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))

    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
