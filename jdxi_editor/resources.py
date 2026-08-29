"""Resource path utilities for locating files in bundled applications."""

import os
import sys
from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parent.parent


def resource_path(relative_path: str | Path) -> str:
    """
    Resolve a path relative to the project / bundle root.

    :param relative_path: Path relative to the repository root (e.g. ``resources/foo.png``).
    :return: Absolute path string.
    """
    relative_path = str(relative_path)
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = str(_PACKAGE_ROOT)
    return os.path.join(base_path, relative_path)
