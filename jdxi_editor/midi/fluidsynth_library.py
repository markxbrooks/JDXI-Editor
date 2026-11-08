"""
Native FluidSynth library lookup

pyfluidsynth (``import fluidsynth``) is only the Python interface: it loads the
native FluidSynth library when imported. On Windows it finds
``libfluidsynth-3.dll`` only through PATH or ``C:\\tools\\fluidsynth\\bin``, so
call :func:`prepare_fluidsynth_library` before importing it. That adds the
first folder that has the DLL, searched in this order:

1. ``FLUIDSYNTH_DIR`` (environment variable): the folder holding the DLL, or
   a FluidSynth install whose ``bin`` folder holds it
2. ``fluidsynth/bin`` in the application bundle (the Windows build ships it)
   or the repository checkout (it is committed there)
3. the folder of the executable (frozen builds)
4. ``C:\\tools\\fluidsynth\\bin``, ``%ProgramFiles%\\FluidSynth\\bin`` and a
   Chocolatey install (``choco install fluidsynth``)

On macOS and Linux the system loader finds Homebrew or distribution packages,
so nothing is done there.

Example:
    >>> prepare_fluidsynth_library()
    >>> import fluidsynth
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Iterable, Optional

FLUIDSYNTH_DIR_ENV = "FLUIDSYNTH_DIR"
DLL_PATTERN = "libfluidsynth*.dll"

_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
_dll_directory_handles: list = []  # keep add_dll_directory registrations alive
_prepared_dir: Optional[Path] = None


def candidate_dirs() -> list[Path]:
    """Folders that may hold libfluidsynth-*.dll, most specific first."""
    from jdxi_editor.resources import resource_path

    dirs: list[Path] = []
    configured = os.environ.get(FLUIDSYNTH_DIR_ENV, "").strip()
    if configured:
        dirs += [Path(configured), Path(configured) / "bin"]
    dirs.append(Path(resource_path(os.path.join("fluidsynth", "bin"))))
    dirs.append(_REPOSITORY_ROOT / "fluidsynth" / "bin")
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        dirs += [exe_dir / "fluidsynth" / "bin", exe_dir]
    dirs.append(Path(r"C:\tools\fluidsynth\bin"))
    program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
    dirs.append(Path(program_files) / "FluidSynth" / "bin")
    chocolatey = os.environ.get("ChocolateyInstall", r"C:\ProgramData\chocolatey")
    dirs.append(Path(chocolatey) / "lib" / "fluidsynth" / "tools")

    unique: list[Path] = []
    for folder in dirs:
        if folder not in unique:
            unique.append(folder)
    return unique


def find_library_dir(dirs: Optional[Iterable[Path]] = None) -> Optional[Path]:
    """The first folder that contains libfluidsynth-*.dll, or None."""
    for folder in candidate_dirs() if dirs is None else dirs:
        try:
            if not folder.is_dir():
                continue
            if any(folder.glob(DLL_PATTERN)):
                return folder
            # Chocolatey unpacks the release archive below tools\
            for dll in sorted(folder.glob(f"*/bin/{DLL_PATTERN}")):
                return dll.parent
        except OSError:
            continue
    return None


def prepare_fluidsynth_library(platform: str = sys.platform) -> Optional[Path]:
    """
    Make the native FluidSynth library findable before ``import fluidsynth``.

    :return: the folder added to the DLL search (Windows), else None
    """
    global _prepared_dir
    if not platform.startswith("win"):
        return None
    if _prepared_dir is not None:
        return _prepared_dir
    folder = find_library_dir()
    if folder is None:
        return None
    if hasattr(os, "add_dll_directory"):  # dependencies (SDL3, sndfile) too
        _dll_directory_handles.append(os.add_dll_directory(str(folder)))
    # pyfluidsynth locates the DLL with ctypes.util.find_library, which
    # searches PATH only
    os.environ["PATH"] = f"{folder}{os.pathsep}{os.environ.get('PATH', '')}"
    _prepared_dir = folder
    return folder


def missing_library_message(platform: str = sys.platform) -> str:
    """How to install the native library, for this platform."""
    if platform.startswith("win"):
        return (
            "FluidSynth library (libfluidsynth-3.dll) not found: install it "
            "(choco install fluidsynth) or set FLUIDSYNTH_DIR to its folder"
        )
    if platform == "darwin":
        return "FluidSynth library not found: brew install fluid-synth"
    return "FluidSynth library not found: install libfluidsynth3 (e.g. apt install libfluidsynth3)"


def import_error_message(error: str, platform: str = sys.platform) -> str:
    """A status line for a failed ``import fluidsynth``."""
    if "Couldn't find" in error or "FluidSynth library" in error:
        return missing_library_message(platform)
    if "No module named" in error:
        return "FluidSynth not installed: pip install pyfluidsynth"
    return f"FluidSynth could not be loaded: {error}"
