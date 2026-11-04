"""Resource path utilities for locating files in bundled applications."""

import os
import sys
from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parent.parent


def _macos_app_resources_dir() -> Path | None:
    """
    Return ``Contents/Resources`` for a macOS ``.app`` bundle.

    ``sys.executable`` is ``…/MyApp.app/Contents/MacOS/MyApp`` under py2app.
    """
    try:
        executable = Path(sys.executable).resolve()
    except (OSError, ValueError):
        return None

    if executable.parent.name != "MacOS":
        return None

    contents = executable.parent.parent
    if contents.name != "Contents":
        return None

    resources = contents / "Resources"
    return resources if resources.is_dir() else None


def _resource_base_path() -> str:
    """Directory that contains ``resources/``, ``doc/``, etc."""
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS

    resourcepath = os.environ.get("RESOURCEPATH")
    if resourcepath and os.path.isdir(resourcepath):
        return resourcepath

    bundle_resources = _macos_app_resources_dir()
    if bundle_resources is not None:
        return str(bundle_resources)

    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        for candidate in (exe_dir / "Resources", exe_dir):
            if (candidate / "resources").is_dir():
                return str(candidate)

    return str(_PACKAGE_ROOT)


def resource_path(relative_path: str | Path) -> str:
    """
    Resolve a path relative to the project / bundle root.

    :param relative_path: Path relative to the repository root (e.g. ``resources/foo.png``).
    :return: Absolute path string.
    """
    return os.path.join(_resource_base_path(), str(relative_path))
