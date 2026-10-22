#!/usr/bin/env python3
"""Generate fictional cast portraits or lifestyle photos for app mockups.

Use text prompts only. Never pass a real person's photo or a supplied app
screenshot into this script. The output is for concept/mockup marketing assets,
not for presenting a real user or a real build screenshot.

Example:
  python3 scripts/generate_cast.py --config /path/to/ai_config.md \
    --style portrait --size 1024x1536 \
    --prompt "Maya, a fictional 27-year-old woman with shoulder-length dark hair, black denim jacket, city street at night, warm bokeh, fully clothed, candid" \
    --out flicker/cast/maya.png
"""

from __future__ import annotations

import argparse
import io
import os
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_backdrop import (  # noqa: E402
    choose_models,
    generate,
    list_models,
    parse_config,
)

STYLE_PREFIX = {
    "portrait": (
        "Professional casting portrait of a fictional adult, head and shoulders, modest "
        "fully buttoned clothing with a high neckline, natural skin, friendly candid "
        "expression, 35mm film, shallow depth of field. The person is not a real public "
        "figure and does not resemble one."
    ),
    "fullbody": (
        "Editorial dating-app photo of a fictional adult, three-quarter or full body, "
        "fully clothed with a high neckline and knee-length bottoms, standing in a real "
        "interior, natural light, 35mm film, modest, candid. The person is not a real "
        "public figure and does not resemble one."
    ),
    "lifestyle": (
        "Editorial lifestyle photograph for a dating app, no people, warm night tones, "
        "35mm film, shallow depth of field, quiet and atmospheric."
    ),
}

NEGATIVE = (
    "No text, no letters, no logos, no brand marks, no watermarks, no celebrity likeness, "
    "no real person, no nudity, no exposed chest, no cleavage, no open jacket, no bare "
    "shoulders, no midriff, no tight clothing, no suggestive pose, no bedroom setting, "
    "no swimwear, no lingerie, no explicit content, no children, no minors, no app UI, "
    "no phone, no screenshot."
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--style", choices=("portrait", "fullbody", "lifestyle"), default="portrait")
    parser.add_argument("--size", default="1024x1536")
    parser.add_argument("--quality", default="high")
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--model", default=None)
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--api-key-env", default="IMAGE_API_KEY")
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()

    config = parse_config(args.config.resolve()) if args.config else {}
    key = (
        args.api_key
        or os.environ.get(args.api_key_env)
        or config.get("api_key")
        or ""
    )
    base = (
        args.base_url
        or os.environ.get("IMAGE_API_BASE")
        or config.get("base_url")
        or "https://api.krill-code.net/v1"
    ).rstrip("/")
    explicit_model = args.model or os.environ.get("IMAGE_MODEL") or None
    config_model = config.get("model") or None

    if not key:
        print(
            f"ERROR: no API key. Set {args.api_key_env}, pass --api-key, or use --config.",
            file=sys.stderr,
        )
        return 2

    prompt = (
        STYLE_PREFIX[args.style]
        + ". "
        + args.prompt.strip().rstrip(".")
        + ". "
        + NEGATIVE
    )

    try:
        available = list_models(base, key, args.timeout)
        models = choose_models(explicit_model, available, config_model)
        if not models:
            print("ERROR: no image model available", file=sys.stderr)
            return 1

        for index in range(1, max(1, args.count) + 1):
            raw, used_model = generate(
                base, key, models, prompt, args.size, args.quality, args.timeout, False
            )
            suffix = "" if args.count == 1 else f"-{index}"
            target = args.out.with_name(f"{args.out.stem}{suffix}{args.out.suffix or '.png'}")
            target.parent.mkdir(parents=True, exist_ok=True)
            with Image.open(io.BytesIO(raw)) as image:
                image = image.convert("RGB")
                if target.suffix.lower() in (".jpg", ".jpeg"):
                    image.save(target, "JPEG", quality=94, subsampling=0, optimize=True)
                else:
                    image.save(target, "PNG", optimize=True)
                width, height = image.size
            print(f"wrote {target} ({width}x{height}, model {used_model})")
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
