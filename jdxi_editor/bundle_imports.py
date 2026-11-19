"""
Imports the optional native stacks where a freezer can see them.

FluidSynth, sounddevice, and LilyPond are otherwise imported from inside
functions. PyInstaller and py2app do not follow those, and sounddevice only
imports its PortAudio binaries when the system library is missing. The
statements below are at module level, and :func:`pyinstaller_args` is what
the Windows and Linux builds pass through.

The LilyPond program itself stays an install on the machine. What is bundled
is music21's translator, which calls it.
"""

# These names are also the PyInstaller hidden imports.
HIDDEN_IMPORTS = (
    "fluidsynth",
    "sounddevice",
    "_sounddevice",
    "_sounddevice_data",
    "cffi",
    "_cffi_backend",
    "music21.lily",
    "music21.lily.translate",
    "music21.lily.lilyObjects",
)

# Packages whose binaries and data files are not named by an import.
COLLECT_ALL = (
    "_sounddevice_data",
    "cffi",
)


def pyinstaller_args() -> list[str]:
    """
    Flags that put these libraries, and their binaries, in a PyInstaller build.

    :return: list[str]
    """
    args: list[str] = []
    for name in HIDDEN_IMPORTS:
        args.extend(("--hidden-import", name))
    for name in COLLECT_ALL:
        args.append(f"--collect-all={name}")
    return args


try:
    import fluidsynth  # noqa: F401
except Exception:
    fluidsynth = None

try:
    import sounddevice  # noqa: F401
    import _sounddevice  # noqa: F401
    import _sounddevice_data  # noqa: F401
    import cffi  # noqa: F401
except Exception:
    sounddevice = None

try:
    import music21.lily.translate  # noqa: F401
    import music21.lily.lilyObjects  # noqa: F401
except Exception:
    pass
