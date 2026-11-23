"""
hexify
"""

from __future__ import annotations


def hexify(data: list[int], begin: int, end: int) -> str:
    return "".join(f"{b:02x}" for b in data[begin:end])
