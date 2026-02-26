#!/usr/bin/env python3
"""
List presets (instruments) from a SoundFont (.sf2) file.

Uses sf2utils for parsing - no FluidSynth/audio required.

Usage:
    python scripts/sftest.py <path-to-soundfont.sf2>
    python scripts/sftest.py FluidR3_GM.sf2
    python scripts/sftest.py /path/to/FluidR3_GM.sf2

Install sf2utils if needed:  pip install sf2utils
"""

import argparse
import sys

try:
    from sf2utils.sf2parse import Sf2File
except ImportError:
    print("sf2utils is required. Install with: pip install sf2utils", file=sys.stderr)
    sys.exit(1)


def list_presets(sf2_path: str) -> None:
    with open(sf2_path, "rb") as f:
        sf2 = Sf2File(f)

        for preset in sf2.presets:
            if preset.name == "EOP":
                continue
            print(f"Bank {preset.bank:3d} | Prog {preset.preset:3d} | {preset.name}")


def main() -> int:
    parser = argparse.ArgumentParser(description="List presets from a SoundFont (.sf2) file")
    parser.add_argument(
        "soundfont",
        nargs="?",
        default="FluidR3_GM.sf2",
        help="Path to .sf2 file (default: FluidR3_GM.sf2 in cwd)",
    )
    args = parser.parse_args()

    sf2_path = args.soundfont
    if not sf2_path.lower().endswith(".sf2"):
        sf2_path = f"{sf2_path}.sf2"

    try:
        list_presets(sf2_path)
    except FileNotFoundError:
        print(f"File not found: {sf2_path}", file=sys.stderr)
        print("Download FluidR3_GM.sf2 or pass the path to your .sf2 file.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
