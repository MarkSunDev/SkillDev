#!/usr/bin/env python3
"""Validate App Store metadata limits used by the PRD skill."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


CHAR_LIMITS = {
    "app_name": 30,
    "subtitle": 30,
    "promotional_text": 170,
    "description": 4000,
}

URL_FIELDS = {
    "support_url",
    "marketing_url",
    "privacy_policy_url",
    "terms_url",
}

EMAIL_FIELDS = {"contact_email"}


def char_count(value: str) -> int:
    return len(value)


def byte_count(value: str) -> int:
    return len(value.encode("utf-8"))


def word_count(value: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", value, flags=re.UNICODE))


def is_placeholder(value: str) -> bool:
    stripped = value.strip()
    return not stripped or stripped in {"[待确认]", "[待提供]", "待确认", "待提供"}


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

    if "keywords" in data:
        value = str(data["keywords"])
        keywords_bytes = byte_count(value)
        rows.append(
            {
                "field": "keywords",
                "characters": char_count(value),
                "utf8_bytes": keywords_bytes,
                "limit": 100,
                "unit": "bytes",
                "ok": keywords_bytes <= 100,
            }
        )
        if keywords_bytes > 100:
            errors.append(f"keywords: {keywords_bytes} bytes exceeds the 100-byte limit")
        if re.search(r"\s", value):
            errors.append("keywords: contains whitespace; use commas without spaces")
        tokens = [token for token in value.split(",") if token]
        if any(not token.strip() for token in value.split(",")):
            errors.append("keywords: contains an empty comma-separated token")
        if len(tokens) != len(set(token.casefold() for token in tokens)):
            errors.append("keywords: contains duplicate tokens")
        app_name = str(data.get("app_name", "")).strip().casefold()
        if app_name:
            keyword_tokens = {token.strip().casefold() for token in tokens}
            if app_name in keyword_tokens:
                errors.append("keywords: repeats the App Name as a keyword token")
            elif app_name in value.casefold():
                warnings.append("keywords: may repeat the App Name; review manually")
        if is_placeholder(value):
            warnings.append("keywords: placeholder or empty value")

    if "description" in data:
        value = str(data["description"])
        if re.search(r"<[A-Za-z/][^>]*>", value):
            errors.append("description: contains HTML-like markup; use plain text")

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
            errors.append(f"review_notes: {words} words exceeds the 300-word limit")
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
