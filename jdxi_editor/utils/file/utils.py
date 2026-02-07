"""
Documentation file path & os_file_open
"""

import os
import platform
import subprocess
from pathlib import Path

from decologr import Decologr as log

from jdxi_editor.resources import resource_path


def documentation_file_path(file_name: str) -> str:
    """
    documentation_file_path

    :param file_name: str The file name to return a path for the documentation file
    :return: str The file path
    """
    return resource_path(os.path.join("doc", "build", "html", file_name))


def os_file_open(file_name: str) -> None:
    """Open file using the OS default handler (non-blocking)."""

    path = Path(file_name)
    if not path.exists():
        log.warning("File does not exist: %s", file_name)
        return

    system = platform.system()

    try:
        if system == "Windows":
            os.startfile(path)  # type: ignore[attr-defined]

        elif system == "Darwin":
            subprocess.Popen(["open", str(path)])

        else:  # Linux / BSD
            subprocess.Popen(["xdg-open", str(path)])

    except Exception as exc:
        log.error("Failed to open file %s: %s", file_name, exc)
