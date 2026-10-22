#!/usr/bin/env python3
"""Render deterministic app-screen mockups from a JSON spec.

Use this for concept/marketing mockups with a fictional cast. It is not a
substitute for a real build capture when the store requires the shipped UI.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _render import render_html, resolve_path  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "assets" / "templates" / "app-screen.html"


def resolve_media(spec: Dict[str, Any], base: Path) -> None:
    for person in (spec.get("cast") or {}).values():
        if isinstance(person, dict) and person.get("photo"):
            path = resolve_path(str(person["photo"]), base)
            if not path.is_file():
                raise FileNotFoundError(f"cast photo not found: {path}")
            person["photo"] = path.as_uri()
    for post in spec.get("feed") or []:
        if isinstance(post, dict) and post.get("photo"):
            path = resolve_path(str(post["photo"]), base)
            if not path.is_file():
                raise FileNotFoundError(f"feed photo not found: {path}")
            post["photo"] = path.as_uri()
    for message in spec.get("thread") or []:
        if isinstance(message, dict) and message.get("photo"):
            path = resolve_path(str(message["photo"]), base)
            if not path.is_file():
                raise FileNotFoundError(f"thread photo not found: {path}")
            message["photo"] = path.as_uri()
    me = spec.get("me") or {}
    for index, photo in enumerate(me.get("photos") or []):
        path = resolve_path(str(photo), base)
        if not path.is_file():
            raise FileNotFoundError(f"profile photo not found: {path}")
        me["photos"][index] = path.as_uri()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=2400)
    parser.add_argument("--only", default=None, help="Comma-separated screen slugs")
    parser.add_argument("--browser", default=None)
    parser.add_argument("--wait-ms", type=int, default=4000)
    args = parser.parse_args()

    spec_path = args.spec.resolve()
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    resolve_media(spec, spec_path.parent)
    screens = spec.get("screens") or []
    if not screens:
        print("ERROR: spec has no 'screens' array", file=sys.stderr)
        return 2

    only = {item.strip() for item in args.only.split(",")} if args.only else None
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    rendered: List[Dict[str, Any]] = []

    for entry in screens:
        slug = str(entry.get("slug") or entry.get("type") or "")
        if not slug or (only and slug not in only):
            continue
        data = copy.deepcopy(spec)
        data["width"] = args.width
        data["height"] = args.height
        data["screen"] = entry.get("type") or slug
        target = out / f"{slug}-{args.width}x{args.height}.png"
        print(f"render {target.name} ({data['screen']}) ...", end=" ", flush=True)
        render_html(
            TEMPLATE,
            data,
            target,
            args.width,
            args.height,
            wait_ms=args.wait_ms,
            browser=args.browser,
        )
        print("ok")
        rendered.append({"slug": slug, "screen": data["screen"], "file": target.name})

    (out / f"mockups-{args.width}x{args.height}.json").write_text(
        json.dumps(
            {
                "app": spec.get("app"),
                "width": args.width,
                "height": args.height,
                "screens": rendered,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(rendered)} screens to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
