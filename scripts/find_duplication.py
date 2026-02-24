#!/usr/bin/env python3
"""
Detect code duplication in a grep-like style. Uses only stdlib.

Searches for repeated sequences of lines (n-grams) across files.
"""

import argparse
import hashlib
from collections import defaultdict
from pathlib import Path


def normalize_line(line: str) -> str:
    """Reduce line to comparable form: strip, collapse whitespace."""
    return " ".join(line.strip().split())


def extract_ngrams(lines: list[str], n: int, normalize: bool = True) -> list[tuple[int, str]]:
    """Yield (start_line, hashable_block) for each n-line window."""
    result = []
    for i in range(len(lines) - n + 1):
        block = lines[i : i + n]
        if normalize:
            block_str = "\n".join(normalize_line(ln) for ln in block)
        else:
            block_str = "\n".join(ln.rstrip() for ln in block)
        # Skip if block is mostly empty
        if not block_str.strip():
            continue
        result.append((i + 1, block_str))  # 1-based line numbers
    return result


def find_duplicates(
    root: Path,
    block_size: int = 4,
    min_occurrences: int = 2,
    extensions: tuple[str, ...] = (".py",),
    exclude_dirs: set[str] | None = None,
    normalize: bool = True,
) -> dict[str, list[tuple[Path, int]]]:
    """
    Find duplicated blocks of code. Returns mapping from block_hash to
    list of (file_path, start_line).
    """
    exclude_dirs = exclude_dirs or {"__pycache__", ".git", "venv", ".venv", "node_modules"}
    block_to_locations: dict[str, list[tuple[Path, int]]] = defaultdict(list)

    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in extensions:
            continue
        if any(part in exclude_dirs for part in path.parts):
            continue

        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        lines = text.splitlines()
        if len(lines) < block_size:
            continue

        for start_line, block_str in extract_ngrams(lines, block_size, normalize):
            block_hash = hashlib.md5(block_str.encode()).hexdigest()
            block_to_locations[block_hash].append((path, start_line))

    # Keep only blocks that appear more than once
    return {
        h: locs
        for h, locs in block_to_locations.items()
        if len(locs) >= min_occurrences
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Find duplicated code blocks (grep-style, minimal deps)"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="File or directory to scan (default: current dir)",
    )
    parser.add_argument(
        "-n",
        "--block-size",
        type=int,
        default=4,
        help="Number of consecutive lines per block (default: 4)",
    )
    parser.add_argument(
        "-m",
        "--min-occurrences",
        type=int,
        default=2,
        help="Minimum occurrences to report (default: 2)",
    )
    parser.add_argument(
        "--no-normalize",
        action="store_true",
        help="Match exact lines (don't collapse whitespace)",
    )
    parser.add_argument(
        "-e",
        "--extensions",
        default=".py",
        help="Comma-separated extensions to scan (default: .py)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Only print file:line, no block preview",
    )
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.exists():
        parser.error(f"Path does not exist: {root}")
    if root.is_file():
        root = root.parent

    extensions = tuple(ext.strip() for ext in args.extensions.split(","))

    dupes = find_duplicates(
        root,
        block_size=args.block_size,
        min_occurrences=args.min_occurrences,
        extensions=extensions,
        normalize=not args.no_normalize,
    )

    # For each duplicate, we need the actual block text for display
    # Re-scan to get block content for reported hashes
    block_contents: dict[str, str] = {}
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in extensions:
            continue
        if any(p in {"__pycache__", ".git", "venv", ".venv"} for p in path.parts):
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for start_line, block_str in extract_ngrams(
            lines, args.block_size, not args.no_normalize
        ):
            h = hashlib.md5(block_str.encode()).hexdigest()
            if h in dupes and h not in block_contents:
                block_contents[h] = block_str

    count = 0
    for block_hash, locations in dupes.items():
        count += 1
        preview = block_contents.get(block_hash, "(block)")
        print(f"\n--- Duplicate #{count} ({len(locations)} occurrences) ---")
        if not args.quiet:
            for line in preview.split("\n")[:6]:
                print(f"  | {line[:76]}{'...' if len(line) > 76 else ''}")
            if preview.count("\n") >= 6:
                print("  | ...")
        for path, line_no in sorted(locations):
            rel = path.relative_to(root) if root != Path(".") else path
            print(f"  {rel}:{line_no}")


if __name__ == "__main__":
    main()
