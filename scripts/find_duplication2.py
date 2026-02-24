#!/usr/bin/env python3
"""
Detect code duplication in a grep-like style (stdlib only).

Features:
- Single-pass indexing
- Generator-based n-grams
- Overlap merging (maximal regions)
- Optional token normalization (Python-aware)
- JSON output support
- Sorted by severity
"""

import argparse
import hashlib
import json
import tokenize
from collections import defaultdict
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Iterator


# ----------------------------
# Data structures
# ----------------------------

@dataclass
class BlockOccurrence:
    path: Path
    start: int
    end: int


@dataclass
class DuplicateBlock:
    content: str
    occurrences: list[BlockOccurrence]


# ----------------------------
# Normalization
# ----------------------------

def normalize_line(line: str) -> str:
    return " ".join(line.strip().split())


def normalize_tokens(text: str) -> str:
    """
    Python-aware normalization:
    - Replace identifiers with NAME
    - Replace literals with CONST
    - Preserve keywords and operators
    """
    out = []
    try:
        tokens = tokenize.generate_tokens(StringIO(text).readline)
        for tok_type, tok_str, *_ in tokens:
            if tok_type == tokenize.NAME:
                out.append("NAME")
            elif tok_type in (tokenize.NUMBER, tokenize.STRING):
                out.append("CONST")
            elif tok_type == tokenize.NEWLINE:
                out.append("\n")
            elif tok_type == tokenize.INDENT:
                out.append("INDENT")
            elif tok_type == tokenize.DEDENT:
                out.append("DEDENT")
            else:
                out.append(tok_str)
    except tokenize.TokenError:
        return text
    return " ".join(out)


# ----------------------------
# N-gram extraction
# ----------------------------

def extract_ngrams(
    lines: list[str],
    n: int,
    normalize: bool,
    token_mode: bool,
) -> Iterator[tuple[int, int, str]]:
    """
    Yield (start_line, end_line, block_string)
    """
    for i in range(len(lines) - n + 1):
        block = lines[i : i + n]

        if token_mode:
            block_str = normalize_tokens("\n".join(block))
        elif normalize:
            block_str = "\n".join(normalize_line(l) for l in block)
        else:
            block_str = "\n".join(l.rstrip() for l in block)

        if not block_str.strip():
            continue

        yield (i + 1, i + n, block_str)


# ----------------------------
# Duplicate detection
# ----------------------------

def find_duplicates(
    root: Path,
    block_size: int,
    min_occurrences: int,
    extensions: tuple[str, ...],
    normalize: bool,
    token_mode: bool,
    exclude_dirs: set[str],
) -> list[DuplicateBlock]:

    index: dict[str, DuplicateBlock] = {}

    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in extensions:
            continue
        if any(part in exclude_dirs for part in path.parts):
            continue

        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue

        for start, end, block_str in extract_ngrams(
            lines, block_size, normalize, token_mode
        ):
            h = hashlib.md5(block_str.encode()).hexdigest()

            if h not in index:
                index[h] = DuplicateBlock(
                    content=block_str,
                    occurrences=[]
                )

            index[h].occurrences.append(BlockOccurrence(path, start, end))

    # Filter
    duplicates = [
        block
        for block in index.values()
        if len(block.occurrences) >= min_occurrences
    ]

    # Merge overlapping occurrences
    for block in duplicates:
        block.occurrences = merge_occurrences(block.occurrences)

    # Sort by severity
    duplicates.sort(
        key=lambda b: (len(b.occurrences), len(b.content)),
        reverse=True,
    )

    return duplicates


# ----------------------------
# Merge overlapping windows
# ----------------------------

def merge_occurrences(
    occurrences: list[BlockOccurrence],
) -> list[BlockOccurrence]:

    merged: list[BlockOccurrence] = []
    occurrences.sort(key=lambda o: (o.path, o.start))

    for occ in occurrences:
        if not merged:
            merged.append(occ)
            continue

        last = merged[-1]
        if (
            occ.path == last.path
            and occ.start <= last.end + 1
        ):
            # Extend region
            last.end = max(last.end, occ.end)
        else:
            merged.append(occ)

    return merged


# ----------------------------
# CLI
# ----------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Find duplicated code blocks (stdlib-only)"
    )
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("-n", "--block-size", type=int, default=4)
    parser.add_argument("-m", "--min-occurrences", type=int, default=2)
    parser.add_argument("-e", "--extensions", default=".py")
    parser.add_argument("--no-normalize", action="store_true")
    parser.add_argument("--tokens", action="store_true",
                        help="Use Python token-based normalization")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("-q", "--quiet", action="store_true")

    args = parser.parse_args()

    root = Path(args.path).resolve()
    if root.is_file():
        root = root.parent

    extensions = tuple(ext.strip() for ext in args.extensions.split(","))
    exclude_dirs = {"__pycache__", ".git", "venv", ".venv", "node_modules"}

    duplicates = find_duplicates(
        root=root,
        block_size=args.block_size,
        min_occurrences=args.min_occurrences,
        extensions=extensions,
        normalize=not args.no_normalize,
        token_mode=args.tokens,
        exclude_dirs=exclude_dirs,
    )

    if args.json:
        print(json.dumps([
            {
                "occurrences": [
                    {
                        "file": str(o.path),
                        "start": o.start,
                        "end": o.end,
                    }
                    for o in block.occurrences
                ],
                "lines": block.content,
            }
            for block in duplicates
        ], indent=2))
        return

    total_regions = 0

    for i, block in enumerate(duplicates, 1):
        total_regions += len(block.occurrences)

        print(f"\n--- Duplicate #{i} "
              f"({len(block.occurrences)} regions, "
              f"{block.content.count(chr(10)) + 1} lines) ---")

        if not args.quiet:
            preview = block.content.splitlines()
            for line in preview[:6]:
                print(f"  | {line[:80]}")
            if len(preview) > 6:
                print("  | ...")

        for occ in block.occurrences:
            rel = occ.path.relative_to(root)
            print(f"  {rel}:{occ.start}-{occ.end}")

    print(f"\nTotal duplicate regions: {total_regions}")


if __name__ == "__main__":
    main()