#!/usr/bin/env python3
"""Validate store icons, five-image galleries, and the Play feature graphic."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _render import contrast_ratio, parse_size  # noqa: E402

APPLE_SIZES = {
    (1320, 2868),
    (1260, 2736),
    (1290, 2796),
    (1206, 2622),
    (1179, 2556),
    (1242, 2208),
    (2064, 2752),
    (2048, 2732),
}
HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]")
CJK_RE = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af]")
CLAIM_RE = re.compile(
    r"\b(#1|no\.?\s*1|number one|best app|top app|award|award[- ]winning|"
    r"editor'?s choice|download now|install now)\b",
    re.IGNORECASE,
)
REQUIRED = ("slug", "feature", "title", "body", "src", "bg", "ink", "accent", "footer")


def add(errors: List[str], warnings: List[str], condition: bool, message: str, error: bool = False) -> None:
    if condition:
        (errors if error else warnings).append(message)


def check_copy(
    images: List[Dict[str, Any]],
    errors: List[str],
    warnings: List[str],
    exact_five: bool = True,
) -> None:
    if len(images) == 5:
        pass
    elif exact_five:
        errors.append(f"gallery must contain exactly 5 images, found {len(images)}")
    elif not 2 <= len(images) <= 8:
        errors.append(f"Google Play accepts 2-8 screenshots, found {len(images)}")
    else:
        warnings.append(f"{len(images)} screenshots; the house convention is 5")

    slugs: List[str] = []
    sources: List[str] = []
    screens: List[str] = []

    for index, image in enumerate(images, start=1):
        label = f"image {index:02d}"
        if not isinstance(image, dict):
            errors.append(f"{label}: must be an object")
            continue

        missing = [field for field in REQUIRED if field not in image]
        if missing:
            errors.append(f"{label}: missing fields: {', '.join(missing)}")
            continue

        slug = str(image.get("slug", "")).strip()
        slugs.append(slug)
        add(errors, warnings, not slug.startswith(f"{index:02d}-"),
            f"{label}: slug should start with '{index:02d}-'")

        feature = str(image.get("feature", "")).strip()
        words = feature.split()
        add(errors, warnings, not feature.isupper(), f"{label}: eyebrow is not uppercase")
        add(errors, warnings, len(words) > 5, f"{label}: eyebrow has {len(words)} words; keep to 2-5", error=len(words) > 7)

        for field in ("title", "body"):
            value = image.get(field)
            if not isinstance(value, list) or len(value) != 2 or not all(str(line).strip() for line in value):
                errors.append(f"{label}: '{field}' must be exactly two non-empty lines")
                continue
            limit_error, limit_warn = ((34, 26) if field == "title" else (58, 42))
            cjk = any(CJK_RE.search(str(line)) for line in value)
            if cjk:
                limit_error, limit_warn = ((20, 15) if field == "title" else (36, 24))
            for line_no, line in enumerate(value, start=1):
                length = len(str(line))
                add(errors, warnings, length > limit_warn,
                    f"{label}: {field} line {line_no} is {length} chars (warn >{limit_warn})",
                    error=length > limit_error)
                add(errors, warnings, bool(EMOJI_RE.search(str(line))),
                    f"{label}: {field} line {line_no} contains emoji")

        footer = str(image.get("footer", "")).strip()
        add(errors, warnings, len(footer.split()) > 8,
            f"{label}: footer has {len(footer.split())} words; keep to 8 or fewer")

        for field in ("bg", "ink", "accent"):
            value = str(image.get(field, "")).strip()
            if not HEX_RE.match(value):
                errors.append(f"{label}: {field} must be a 6-digit hex color such as #F7F4ED")

        if HEX_RE.match(str(image.get("bg", ""))) and HEX_RE.match(str(image.get("ink", ""))):
            ratio = contrast_ratio(str(image["ink"]), str(image["bg"]))
            add(errors, warnings, ratio < 4.5,
                f"{label}: ink/bg contrast is {ratio:.1f}:1; body text needs 4.5:1",
                error=ratio < 3.0)
            add(errors, warnings, ratio < 7.0,
                f"{label}: ink/bg contrast is {ratio:.1f}:1; 7:1 is safer for thumbnails")
        if HEX_RE.match(str(image.get("bg", ""))) and HEX_RE.match(str(image.get("accent", ""))):
            accent_ratio = contrast_ratio(str(image["accent"]), str(image["bg"]))
            add(errors, warnings, accent_ratio < 3.0,
                f"{label}: accent/bg contrast is {accent_ratio:.1f}:1; large headline needs 3:1")

        combined = " ".join(
            [str(image.get("feature", "")), str(image.get("footer", ""))]
            + [str(line) for line in image.get("title", [])]
            + [str(line) for line in image.get("body", [])]
        )
        match = CLAIM_RE.search(combined)
        if match:
            warnings.append(
                f"{label}: possible unverifiable claim '{match.group(0)}' in screenshot copy"
            )

        sources.append(str(image.get("src", "")).strip())
        if image.get("screen") and not image.get("allow_reuse"):
            screens.append(str(image.get("screen")).strip())
        elif image.get("allow_reuse"):
            warnings.append(f"{label}: reuses a source screen for a detail composition")

    if len(slugs) != len(set(slugs)):
        errors.append("gallery contains duplicate slugs")
    if len(sources) != len(set(sources)):
        errors.append("gallery reuses the same output filename")
    if screens and len(screens) != len(set(screens)):
        errors.append("gallery reuses the same source screenshot")


def check_gallery_files(
    images: List[Dict[str, Any]],
    store: str,
    assets_dir: Path,
    errors: List[str],
    warnings: List[str],
) -> None:
    from PIL import Image

    for index, image in enumerate(images, start=1):
        label = f"image {index:02d}"
        src = str(image.get("src", "")).strip()
        if not src:
            continue
        path = Path(src)
        if not path.is_absolute():
            path = assets_dir / path
        if not path.is_file():
            errors.append(f"{label}: file not found: {path}")
            continue

        try:
            with Image.open(path) as img:
                width, height = img.size
                fmt = (img.format or "").upper()
                bands = img.getbands()
                has_alpha = "A" in bands or "transparency" in img.info
        except OSError as exc:
            errors.append(f"{label}: cannot read {path}: {exc}")
            continue

        if fmt not in ("PNG", "JPEG"):
            errors.append(f"{label}: must be PNG or JPEG, found {fmt or 'unknown'}")
        if has_alpha:
            errors.append(f"{label}: contains alpha/transparency; export flattened RGB")
        if path.stat().st_size > 10 * 1024 * 1024:
            warnings.append(f"{label}: file is {path.stat().st_size / 1048576:.1f} MB; check the current store limit")

        if store == "apple":
            if (width, height) not in APPLE_SIZES:
                allowed = ", ".join(f"{w}x{h}" for w, h in sorted(APPLE_SIZES))
                errors.append(f"{label}: size {width}x{height} is not in the accepted set: {allowed}")
        else:
            if not (320 <= width <= 3840 and 320 <= height <= 3840):
                errors.append(f"{label}: each side must be 320-3840 px; found {width}x{height}")
            ratio = max(width, height) / min(width, height)
            if ratio > 2.0 + 1e-6:
                errors.append(f"{label}: aspect ratio {ratio:.3f}:1 exceeds Play's 2:1 limit")
            if path.stat().st_size > 8 * 1024 * 1024:
                warnings.append(f"{label}: Play screenshots are usually kept under 8 MB")

        declared = str(image.get("size", "")).strip()
        if declared:
            try:
                expected = parse_size(declared)
            except ValueError:
                errors.append(f"{label}: invalid 'size' value '{declared}'")
            else:
                if (width, height) != expected:
                    errors.append(
                        f"{label}: size is {width}x{height}, manifest declares {expected[0]}x{expected[1]}"
                    )

        screen = image.get("screen")
        if screen:
            screen_path = Path(str(screen))
            if not screen_path.is_absolute():
                screen_path = assets_dir / screen_path
            if screen_path.is_file():
                try:
                    with Image.open(screen_path) as source:
                        source_ratio = source.width / source.height
                    if source_ratio < 0.35:
                        warnings.append(
                            f"{label}: source aspect {source_ratio:.3f} is unusually tall; "
                            "check that the device frame does not clip the capture"
                        )
                    elif source_ratio > 1.0:
                        warnings.append(
                            f"{label}: source is landscape; portrait gallery layouts expect a portrait capture"
                        )
                except OSError:
                    pass


def check_icon_dir(directory: Path, errors: List[str], warnings: List[str]) -> None:
    from PIL import Image

    core = {
        "icon-ios-1024.png": (1024, 1024, False, "iOS / App Store"),
        "icon-play-512.png": (512, 512, True, "Google Play"),
        "icon-mark-1024.png": (1024, 1024, True, "transparent mark"),
    }
    for name, (width, height, want_alpha, purpose) in core.items():
        path = directory / name
        if not path.is_file():
            errors.append(f"icons: missing {name} ({purpose})")
            continue
        with Image.open(path) as img:
            if img.size != (width, height):
                errors.append(f"icons: {name} is {img.width}x{img.height}, expected {width}x{height}")
            if (img.format or "").upper() != "PNG":
                errors.append(f"icons: {name} must be PNG, found {img.format}")
            has_alpha = "A" in img.getbands() or "transparency" in img.info
            if want_alpha and not has_alpha:
                errors.append(f"icons: {name} must include an alpha channel")
            if not want_alpha and has_alpha:
                errors.append(f"icons: {name} must be flattened RGB with no alpha")
        if name == "icon-play-512.png" and path.stat().st_size > 1024 * 1024:
            errors.append(
                f"icons: icon-play-512.png is {path.stat().st_size / 1048576:.2f} MB; Play limit is 1 MB"
            )

    adaptive = {
        "icon-adaptive-foreground-432.png": True,
        "icon-adaptive-background-432.png": False,
        "icon-monochrome-432.png": True,
    }
    for name, want_alpha in adaptive.items():
        path = directory / name
        if not path.is_file():
            warnings.append(f"icons: optional Android layer missing: {name}")
            continue
        with Image.open(path) as img:
            if img.size != (432, 432):
                errors.append(f"icons: {name} is {img.width}x{img.height}, expected 432x432")
            has_alpha = "A" in img.getbands() or "transparency" in img.info
            if want_alpha and not has_alpha:
                errors.append(f"icons: {name} must include an alpha channel")
            if not want_alpha and has_alpha:
                errors.append(f"icons: {name} must be flattened RGB with no alpha")
            if want_alpha and has_alpha:
                bbox = img.getchannel("A").getbbox()
                safe = round(432 * 66 / 108)
                left = (432 - safe) // 2
                right = left + safe
                if bbox is None:
                    errors.append(f"icons: {name} is fully transparent")
                elif bbox[0] < left - 2 or bbox[1] < left - 2 or bbox[2] > right + 2 or bbox[3] > right + 2:
                    errors.append(
                        f"icons: {name} content {bbox} breaches the central {safe}px safe zone"
                    )

    preview = directory / "icon-mask-preview.png"
    if not preview.is_file():
        warnings.append("icons: icon-mask-preview.png not found; render without --no-preview to inspect masks")


def check_feature(path: Path, errors: List[str], warnings: List[str]) -> None:
    from PIL import Image

    if not path.is_file():
        errors.append(f"feature graphic not found: {path}")
        return
    with Image.open(path) as img:
        if img.size != (1024, 500):
            errors.append(f"feature graphic is {img.width}x{img.height}, expected 1024x500")
        if (img.format or "").upper() not in ("PNG", "JPEG"):
            errors.append(f"feature graphic must be PNG or JPEG, found {img.format}")
        if "A" in img.getbands() or "transparency" in img.info:
            errors.append("feature graphic must have no alpha channel")
    if path.stat().st_size > 15 * 1024 * 1024:
        errors.append("feature graphic exceeds 15 MB")
    elif path.stat().st_size > 10 * 1024 * 1024:
        warnings.append("feature graphic is larger than 10 MB; compress it")


def load_images(data: Any) -> List[Dict[str, Any]]:
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        images = data.get("images")
        if isinstance(images, list):
            return images
    raise ValueError("Expected an array of images or an object with an images array")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--icons", type=Path, default=None)
    parser.add_argument("--gallery", type=Path, default=None)
    parser.add_argument("--feature", type=Path, default=None)
    parser.add_argument("--store", choices=("apple", "play"), default="apple")
    parser.add_argument(
        "--allow-count",
        action="store_true",
        help="Allow 2-8 images instead of the five-image house convention",
    )
    parser.add_argument("--assets-dir", type=Path, default=None)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    if not any((args.icons, args.gallery, args.feature)):
        parser.error("pass at least one of --icons, --gallery, or --feature")

    errors: List[str] = []
    warnings: List[str] = []
    counts: Dict[str, int] = {}

    if args.icons:
        counts["icons"] = 1
        check_icon_dir(args.icons.resolve(), errors, warnings)

    if args.gallery:
        manifest_path = args.gallery.resolve()
        data = None
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            images = load_images(data)
            counts["images"] = len(images)
            check_copy(images, errors, warnings, exact_five=not args.allow_count)
            assets_dir = args.assets_dir or manifest_path.parent
            check_gallery_files(images, args.store, assets_dir, errors, warnings)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"gallery: {exc}")

        if isinstance(data, dict):
            fg = data.get("feature_graphic")
            if isinstance(fg, dict) and fg.get("src") and not args.feature:
                args.feature = manifest_path.parent / str(fg["src"])
            if isinstance(fg, dict):
                counts["feature_graphic"] = 1
                headline = fg.get("headline")
                if headline:
                    if not isinstance(headline, list) or not 1 <= len(headline) <= 2:
                        errors.append("feature graphic headline must be one or two lines")
                    else:
                        for line_no, line in enumerate(headline, start=1):
                            length = len(str(line))
                            add(errors, warnings, length > 30,
                                f"feature graphic headline {line_no} is {length} chars; keep it short",
                                error=length > 40)
                support = str(fg.get("support") or "")
                if len(support) > 56:
                    add(errors, warnings, len(support) > 80,
                        f"feature graphic support line is {len(support)} chars; keep one short line",
                        error=len(support) > 80)

    if args.feature:
        check_feature(args.feature.resolve(), errors, warnings)

    result = {
        "ok": not errors,
        "counts": counts,
        "errors": errors,
        "warnings": warnings,
    }
    if args.pretty:
        if warnings:
            for warning in warnings:
                print(f"WARN: {warning}")
        if errors:
            for error in errors:
                print(f"ERROR: {error}")
            print(f"FAILED: {len(errors)} error(s), {len(warnings)} warning(s)")
        else:
            print(f"OK: {len(warnings)} warning(s)")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
