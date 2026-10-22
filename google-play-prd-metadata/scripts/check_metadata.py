#!/usr/bin/env python3
"""Validate Google Play metadata limits used by the PRD skill."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


CHAR_LIMITS = {
    "app_name": 30,
    "short_description": 80,
    "full_description": 4000,
}

URL_FIELDS = {
    "website",
    "privacy_policy_url",
    "terms_url",
    "account_deletion_url",
    "promo_video_url",
}

EMAIL_FIELDS = {"contact_email"}

EMOJI_RE = re.compile(
    "["
    "\U0001f000-\U0001faff"
    "\U00002600-\U000027bf"
    "\U00002b00-\U00002bff"
    "\U0001f1e6-\U0001f1ff"
    "\U0000fe0f"
    "]+"
)

CTA_RE = re.compile(
    r"\b(download|install|free|best|top|new|update|no\.?\s*1|#1)\b",
    flags=re.IGNORECASE,
)
TRADEMARK_RE = re.compile(r"\b(google|android|play)\b", flags=re.IGNORECASE)
HTML_RE = re.compile(r"<[A-Za-z/][^>]*>")


def char_count(value: str) -> int:
    return len(value)


def byte_count(value: str) -> int:
    return len(value.encode("utf-8"))


def word_count(value: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", value, flags=re.UNICODE))


def is_placeholder(value: str) -> bool:
    stripped = value.strip()
    return not stripped or stripped in {
        "[待确认]",
        "[待提供]",
        "[待截图]",
        "待确认",
        "待提供",
        "待截图",
        "不适用",
        "N/A",
    }


def validate(data: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    warnings: list[str] = []

    for field, limit in CHAR_LIMITS.items():
        if field not in data:
            continue
        value = str(data[field])
        chars = char_count(value)
        ok = chars <= limit
        rows.append(
            {
                "field": field,
                "characters": chars,
                "utf8_bytes": byte_count(value),
                "limit": limit,
                "unit": "characters",
                "ok": ok,
            }
        )
        if not ok:
            errors.append(f"{field}: {chars} characters exceeds the {limit}-character limit")
        if is_placeholder(value):
            warnings.append(f"{field}: placeholder or empty value")

    for field in ("app_name", "short_description"):
        if field not in data:
            continue
        value = str(data[field])
        if EMOJI_RE.search(value):
            errors.append(f"{field}: contains emoji or decorative symbols; Play metadata must use plain text")
        if field == "app_name":
            cta = sorted({match.group(1).lower() for match in CTA_RE.finditer(value)})
            if cta:
                warnings.append(
                    f"app_name: contains call-to-action or ranking wording ({', '.join(cta)}); review Play metadata policy"
                )
            trademarks = sorted({match.group(1).lower() for match in TRADEMARK_RE.finditer(value)})
            if trademarks:
                warnings.append(
                    f"app_name: contains Google/Android/Play trademark wording ({', '.join(trademarks)}); review Play policy"
                )

    if "full_description" in data:
        value = str(data["full_description"])
        if HTML_RE.search(value):
            errors.append("full_description: contains HTML-like markup; use plain text")

    if "review_notes" in data:
        value = str(data["review_notes"])
        words = word_count(value)
        rows.append(
            {
                "field": "review_notes",
                "characters": char_count(value),
                "utf8_bytes": byte_count(value),
                "words": words,
                "limit": 300,
                "unit": "words",
                "ok": words <= 300,
            }
        )
        if words > 300:
            errors.append(
                f"review_notes: {words} words exceeds the 300-word editorial limit (not a Play limit)"
            )
        if is_placeholder(value):
            warnings.append("review_notes: placeholder or empty value")

    for field in URL_FIELDS:
        if field not in data:
            continue
        value = str(data[field]).strip()
        ok = bool(re.match(r"^https://[^\s]+\.[^\s]+$", value, flags=re.IGNORECASE))
        rows.append(
            {
                "field": field,
                "characters": char_count(value),
                "utf8_bytes": byte_count(value),
                "unit": "URL",
                "ok": ok,
            }
        )
        if not ok:
            errors.append(f"{field}: must be a non-empty HTTPS URL")
        if is_placeholder(value):
            warnings.append(f"{field}: placeholder or empty value")
        if field == "promo_video_url" and ok:
            host = (urlparse(value).hostname or "").lower()
            if host not in {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"}:
                warnings.append("promo_video_url: Play promo videos must be hosted on YouTube")

    for field in EMAIL_FIELDS:
        if field not in data:
            continue
        value = str(data[field]).strip()
        ok = bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value))
        rows.append(
            {
                "field": field,
                "characters": char_count(value),
                "utf8_bytes": byte_count(value),
                "unit": "email",
                "ok": ok,
            }
        )
        if not ok:
            errors.append(f"{field}: must be a valid email address")
        if is_placeholder(value):
            warnings.append(f"{field}: placeholder or empty value")

    if "privacy_policy_url" not in data:
        warnings.append("privacy_policy_url: Google Play requires a privacy policy URL for every app")

    has_accounts = data.get("has_accounts")
    if has_accounts:
        value = str(data.get("account_deletion_url", "")).strip()
        if is_placeholder(value):
            errors.append(
                "account_deletion_url: required when has_accounts is true; provide the public web deletion URL"
            )

    return rows, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_file", type=Path, help="JSON file with metadata fields, or - for stdin")
    parser.add_argument("--pretty", action="store_true", help="Print a human-readable table")
    args = parser.parse_args()

    raw = sys.stdin.read() if str(args.json_file) == "-" else args.json_file.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON: {exc}", file=sys.stderr)
        return 2

    if not isinstance(data, dict):
        print("Metadata JSON must be an object", file=sys.stderr)
        return 2

    rows, errors, warnings = validate(data)
    result = {"ok": not errors, "rows": rows, "errors": errors, "warnings": warnings}

    if args.pretty:
        for row in rows:
            field = row["field"]
            if row.get("unit") == "bytes":
                amount = f'{row["characters"]} chars / {row["utf8_bytes"]} bytes'
            elif row.get("unit") == "words":
                amount = f'{row["characters"]} chars / {row.get("words", 0)} words'
            else:
                amount = f'{row["characters"]} chars'
            print(f'{field:22} {amount:32} {"OK" if row["ok"] else "FAIL"}')
        for warning in warnings:
            print(f"WARN: {warning}")
        for error in errors:
            print(f"ERROR: {error}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))

    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
