#!/usr/bin/env python3
"""Report exact and near-duplicate source/assets between two app trees.

This is a review aid, not proof of originality. It catches obvious copy-paste,
renamed-symbol ports, and reused binaries so a human can inspect the rest.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SKIP_DIRS = {
    ".git", ".build", "build", "DerivedData", "node_modules", "Pods", "vendor",
    ".dart_tool", ".gradle", "target", "dist", "coverage", "__pycache__",
    ".idea", ".vscode", "artifacts", "docs/screenshots",
}

CODE_EXTENSIONS = {
    ".swift", ".m", ".mm", ".h", ".c", ".cc", ".cpp", ".hpp", ".kt", ".kts",
    ".java", ".dart", ".ts", ".tsx", ".js", ".jsx", ".py", ".rb", ".go", ".rs",
    ".cs", ".php", ".vue", ".svelte", ".html", ".css", ".scss", ".sass",
    ".less", ".json", ".yaml", ".yml", ".toml", ".xml", ".plist", ".strings",
    ".storyboard", ".xib", ".graphql", ".sql",
}

ASSET_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".heic", ".mp4", ".mov", ".m4v",
    ".pdf", ".ttf", ".otf", ".woff", ".woff2", ".wav", ".mp3", ".aac",
}

TOKEN_RE = re.compile(
    r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|'
    r"[A-Za-z_][A-Za-z0-9_]*|\d+(?:\.\d+)?"
)


@dataclass(frozen=True)
class SourceFile:
    path: Path
    relative: str
    extension: str
    tokens: tuple[str, ...]
    normalized_hash: str


def is_allowed(relative: str, patterns: list[str]) -> bool:
    normalized = relative.replace(os.sep, "/")
    return any(fnmatch.fnmatch(normalized, pattern) for pattern in patterns)


def iter_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        parts = set(relative.split("/"))
        if parts & SKIP_DIRS:
            continue
        if any(segment.startswith(".") and segment not in {".", ".."} for segment in relative.split("/")[:-1]):
            continue
        yield path


def strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    text = re.sub(r"(?m)^\s*//.*$", " ", text)
    text = re.sub(r"(?m)^\s*#(?!include|import|pragma).*$", " ", text)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    return text


def tokens_for(text: str) -> tuple[str, ...]:
    return tuple(TOKEN_RE.findall(strip_comments(text)))


def ngrams(tokens: tuple[str, ...], size: int) -> set[tuple[str, ...]]:
    if len(tokens) < size:
        return set()
    return {tokens[index:index + size] for index in range(len(tokens) - size + 1)}


def jaccard(left: set[tuple[str, ...]], right: set[tuple[str, ...]]) -> float:
    if not left or not right:
        return 0.0
    union = len(left | right)
    return len(left & right) / union if union else 0.0


def structural_tokens(tokens: tuple[str, ...]) -> tuple[str, ...]:
    result = []
    for token in tokens:
        if token[:1] in {'"', "'"}:
            result.append("S")
        elif token[0].isdigit():
            result.append("N")
        else:
            result.append("I")
    return tuple(result)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def scan_source(root: Path, allow: list[str]) -> tuple[list[SourceFile], list[tuple[str, str]]]:
    files: list[SourceFile] = []
    duplicates: list[tuple[str, str]] = []
    seen_raw: dict[str, str] = {}
    for path in iter_files(root):
        if path.suffix.lower() not in CODE_EXTENSIONS:
            continue
        relative = path.relative_to(root).as_posix()
        if is_allowed(relative, allow):
            continue
        try:
            data = path.read_bytes()
            text = data.decode("utf-8", errors="replace")
        except OSError:
            continue
        raw_hash = sha(data)
        if raw_hash in seen_raw and len(data) > 256:
            duplicates.append((seen_raw[raw_hash], relative))
        else:
            seen_raw[raw_hash] = relative
        tokens = tokens_for(text)
        if len(tokens) < 40:
            continue
        normal = " ".join(tokens)
        files.append(SourceFile(
            path=path,
            relative=relative,
            extension=path.suffix.lower(),
            tokens=tokens,
            normalized_hash=sha(normal.encode()),
        ))
    return files, duplicates


def scan_assets(root: Path, allow: list[str]) -> dict[str, str]:
    assets: dict[str, str] = {}
    for path in iter_files(root):
        if path.suffix.lower() not in ASSET_EXTENSIONS:
            continue
        relative = path.relative_to(root).as_posix()
        if is_allowed(relative, allow):
            continue
        try:
            assets.setdefault(sha(path.read_bytes()), relative)
        except OSError:
            continue
    return assets


def compare(
    reference: Path,
    candidate: Path,
    allow: list[str],
    ngram_size: int,
    threshold: float,
    structural_threshold: float,
    min_tokens: int,
) -> dict:
    reference_files, reference_duplicates = scan_source(reference, allow)
    candidate_files, candidate_duplicates = scan_source(candidate, allow)
    reference_assets = scan_assets(reference, allow)
    candidate_assets = scan_assets(candidate, allow)

    reference_grams: dict[str, set[tuple[str, ...]]] = {}
    reference_structs: dict[str, set[tuple[str, ...]]] = {}
    for item in reference_files:
        reference_grams[str(item.path)] = ngrams(item.tokens, ngram_size)
        reference_structs[str(item.path)] = ngrams(structural_tokens(item.tokens), ngram_size)

    pairs: list[dict] = []
    candidate_global: set[tuple[str, ...]] = set()
    for item in candidate_files:
        candidate_grams = ngrams(item.tokens, ngram_size)
        candidate_global |= candidate_grams
        if len(item.tokens) < min_tokens:
            continue
        best: dict | None = None
        for other in reference_files:
            if item.extension != other.extension or len(other.tokens) < min_tokens:
                continue
            raw_score = jaccard(candidate_grams, reference_grams[str(other.path)])
            struct_score = jaccard(
                ngrams(structural_tokens(item.tokens), ngram_size),
                reference_structs[str(other.path)],
            )
            if raw_score >= threshold or struct_score >= structural_threshold:
                row = {
                    "candidate": item.relative,
                    "reference": other.relative,
                    "token_jaccard": round(raw_score, 4),
                    "structural_jaccard": round(struct_score, 4),
                }
                if best is None or (row["token_jaccard"], row["structural_jaccard"]) > (
                    best["token_jaccard"], best["structural_jaccard"]
                ):
                    best = row
        if best:
            pairs.append(best)

    reference_global: set[tuple[str, ...]] = set()
    for grams in reference_grams.values():
        reference_global |= grams
    global_overlap = len(candidate_global & reference_global) / len(candidate_global) if candidate_global else 0.0

    exact_source = []
    candidate_hashes = {item.normalized_hash: item.relative for item in candidate_files}
    for item in reference_files:
        if item.normalized_hash in candidate_hashes:
            exact_source.append({
                "reference": item.relative,
                "candidate": candidate_hashes[item.normalized_hash],
            })

    shared_assets = [
        {"reference": reference_assets[digest], "candidate": candidate_assets[digest]}
        for digest in sorted(set(reference_assets) & set(candidate_assets))
    ]

    pairs.sort(key=lambda row: (row["token_jaccard"], row["structural_jaccard"]), reverse=True)

    return {
        "reference": str(reference),
        "candidate": str(candidate),
        "ngram_size": ngram_size,
        "source_files_compared": {
            "reference": len(reference_files),
            "candidate": len(candidate_files),
        },
        "duplicate_files_inside_reference": reference_duplicates[:50],
        "duplicate_files_inside_candidate": candidate_duplicates[:50],
        "exact_normalized_source_matches": exact_source[:50],
        "shared_assets": shared_assets[:100],
        "high_similarity_pairs": pairs[:50],
        "global_ngram_overlap": round(global_overlap, 4),
    }


def print_report(report: dict) -> None:
    print("Between originality audit")
    print(f"reference: {report['reference']}")
    print(f"candidate: {report['candidate']}")
    print(
        "source files compared: "
        f"{report['source_files_compared']['reference']} reference / "
        f"{report['source_files_compared']['candidate']} candidate"
    )
    print(f"global {report['ngram_size']}-gram overlap: {report['global_ngram_overlap']:.2%}")

    sections = [
        ("exact normalized source matches", report["exact_normalized_source_matches"]),
        ("shared assets", report["shared_assets"]),
        ("high-similarity pairs", report["high_similarity_pairs"]),
    ]
    for title, rows in sections:
        print(f"\n{title}: {len(rows)}")
        for row in rows[:30]:
            if "token_jaccard" in row:
                print(
                    f"  token={row['token_jaccard']:.2%} "
                    f"struct={row['structural_jaccard']:.2%}\n"
                    f"    {row['candidate']}\n"
                    f"    <- {row['reference']}"
                )
            else:
                print(f"  {row.get('candidate', '?')}\n    <- {row.get('reference', '?')}")

    if len(report["duplicate_files_inside_reference"]):
        print(f"\nduplicate files inside reference: {len(report['duplicate_files_inside_reference'])}")
        for left, right in report["duplicate_files_inside_reference"][:10]:
            print(f"  {left} == {right}")
    if len(report["duplicate_files_inside_candidate"]):
        print(f"\nduplicate files inside candidate: {len(report['duplicate_files_inside_candidate'])}")
        for left, right in report["duplicate_files_inside_candidate"][:10]:
            print(f"  {left} == {right}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--allow-glob", action="append", default=[], help="Relative glob to ignore; repeatable")
    parser.add_argument("--ngram", type=int, default=12)
    parser.add_argument("--threshold", type=float, default=0.55, help="Raw token Jaccard threshold")
    parser.add_argument("--structural-threshold", type=float, default=0.82)
    parser.add_argument("--min-tokens", type=int, default=80)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    reference = args.reference.expanduser().resolve()
    candidate = args.candidate.expanduser().resolve()
    if not reference.is_dir() or not candidate.is_dir():
        parser.error("--reference and --candidate must both be directories")

    allow = ["**/LICENSE*", "**/COPYING*"] + args.allow_glob
    report = compare(
        reference=reference,
        candidate=candidate,
        allow=allow,
        ngram_size=max(4, args.ngram),
        threshold=args.threshold,
        structural_threshold=args.structural_threshold,
        min_tokens=max(20, args.min_tokens),
    )

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_report(report)

    failures = (
        report["exact_normalized_source_matches"]
        or report["shared_assets"]
        or report["high_similarity_pairs"]
    )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
