#!/usr/bin/env python3
"""Pick one of the built-in dating/social art-direction packs.

Examples:
  python3 scripts/style_packs.py --list
  python3 scripts/style_packs.py --random
  python3 scripts/style_packs.py --next
  python3 scripts/style_packs.py --get after-hours-amber
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FILE = ROOT / "assets" / "style-packs" / "dating.json"
DEFAULT_STATE = Path.cwd() / ".style-pack-state.json"


def load_packs(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    packs = data.get("packs")
    if not isinstance(packs, list) or not packs:
        raise ValueError(f"{path} has no 'packs' array")
    return packs


def read_state(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def write_state(path: Path, index: int, pack: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {"last_index": index, "last_id": pack.get("id")},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def print_list(packs: List[Dict[str, Any]]) -> None:
    for index, pack in enumerate(packs):
        print(f"{index + 1:02d}  {pack['id']:<22} {pack['name']:<22} {pack['mood']}")


def emit(pack: Dict[str, Any], index: int) -> None:
    payload = {"index": index + 1, "total": 0, "pack": pack}
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, default=DEFAULT_FILE)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--seed", type=int, default=None)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--list", action="store_true", help="List all packs")
    group.add_argument("--random", action="store_true", help="Pick a random pack")
    group.add_argument("--next", action="store_true", help="Pick the next pack after the last one")
    group.add_argument("--get", metavar="ID", help="Print a specific pack")
    args = parser.parse_args()

    try:
        packs = load_packs(args.file)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.list:
        print_list(packs)
        return 0

    if args.get:
        for index, pack in enumerate(packs):
            if pack.get("id") == args.get:
                payload = {"index": index + 1, "total": len(packs), "pack": pack}
                print(json.dumps(payload, ensure_ascii=False, indent=2))
                return 0
        print(f"ERROR: no pack with id '{args.get}'", file=sys.stderr)
        print_list(packs)
        return 2

    state = read_state(args.state)
    if args.next:
        last = int(state.get("last_index", -1))
        index = (last + 1) % len(packs)
    else:
        # --random is the default when no action is given.
        if args.seed is not None:
            random.seed(args.seed)
        index = random.randrange(len(packs))

    pack = packs[index]
    write_state(args.state, index, pack)
    payload = {"index": index + 1, "total": len(packs), "pack": pack}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
