"""
macOS build entry for buildsys.

Delegates to building/apple/build_macos.py which implements the full
macOS build (py2app, DMG, PKG).
"""

import sys
from pathlib import Path


def build(ctx):
    """Run the macOS build (py2app, optional DMG/PKG)."""
    # building/apple is not a package; add it to path and import the script as a module
    building_dir = Path(__file__).resolve().parent.parent
    apple_dir = building_dir / "apple"
    if str(apple_dir) not in sys.path:
        sys.path.insert(0, str(apple_dir))

    import build_macos as apple_build

    apple_build.main()
