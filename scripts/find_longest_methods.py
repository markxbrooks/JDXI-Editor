#!/usr/bin/env python3
"""
Find the longest methods/functions in a Python file.

Usage:
    python scripts/find_longest_methods.py <path_to_file.py>
    python scripts/find_longest_methods.py jdxi_editor/ui/editors/pattern/pattern.py

Output: List of methods sorted by length (longest first), with line counts.
"""

import argparse
import ast
import sys


def get_definitions(node: ast.AST) -> list[tuple[str, int, int, str]]:
    """
    Recursively find function/method definitions and their line ranges.

    Returns list of (name, start_line, end_line, kind) where kind is
    'function', 'method', or 'class'.
    """
    results = []

    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.FunctionDef):
            end_line = child.end_lineno if hasattr(child, "end_lineno") else child.lineno
            length = end_line - child.lineno + 1
            kind = "method" if isinstance(node, ast.ClassDef) else "function"
            results.append((child.name, child.lineno, length, kind))

        if isinstance(child, ast.ClassDef):
            end_line = child.end_lineno if hasattr(child, "end_lineno") else child.lineno
            length = end_line - child.lineno + 1
            results.append((child.name, child.lineno, length, "class"))

        # Recurse into nested classes
        if isinstance(child, ast.ClassDef):
            results.extend(get_definitions(child))

    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Find the longest methods/functions in a Python file"
    )
    parser.add_argument(
        "file",
        help="Path to Python file",
    )
    parser.add_argument(
        "-n",
        "--top",
        type=int,
        default=20,
        help="Number of longest definitions to show (default: 20)",
    )
    parser.add_argument(
        "--classes",
        action="store_true",
        help="Include class definitions in the report",
    )
    parser.add_argument(
        "--min-lines",
        type=int,
        default=1,
        help="Minimum line count to include (default: 1)",
    )
    args = parser.parse_args()

    try:
        with open(args.file, encoding="utf-8") as f:
            source = f.read()
    except OSError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"Syntax error: {e}", file=sys.stderr)
        return 1

    definitions = get_definitions(tree)

    # Filter by kind and minimum length
    filtered = [
        (name, line, length, kind)
        for name, line, length, kind in definitions
        if length >= args.min_lines and (args.classes or kind != "class")
    ]

    # Sort by length descending
    filtered.sort(key=lambda x: x[2], reverse=True)

    # Take top N
    top = filtered[: args.top]

    if not top:
        print("No definitions found.")
        return 0

    print(f"Longest definitions in {args.file}\n")
    max_name = max(len(n) for n, _, _, _ in top)
    max_len = max(len(str(l)) for _, _, l, _ in top)

    for name, start_line, length, kind in top:
        print(f"  {length:{max_len}d} lines  {name:{max_name}s}  (line {start_line}, {kind})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
