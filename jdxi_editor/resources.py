"""Resource path utilities for locating files in bundled applications."""

import os
import sys
from pathlib import Path


def resource_path(relative_path: str | Path) -> str:
    """
    resource_path

    :param relative_path: str
    :return: str string representation of the file path
    """
    relative_path = str(relative_path)
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
