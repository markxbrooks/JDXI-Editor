"""
py2app configuration for the macOS "JD-Xi Editor.app" bundle.

This is NOT the package definition. pyproject.toml is the single source of
truth for the project's metadata, version, and dependencies (hatchling builds
the sdist and wheel that go to PyPI). This file exists only so that

    python setup.py py2app

can freeze the app, and it is driven by building/apple/make_pkg.sh,
building/apple/make_dmg.sh, and building/apple/build_macos.py. Nothing here is
uploaded anywhere. Add a runtime dependency to pyproject.toml; add it here only
when py2app's module graph fails to find it on its own (OPTIONS below).
"""

import glob
import re
import sys
from pathlib import Path

# modulegraph uses recursive AST traversal; deeply nested code (e.g. long if/elif chains)
# in jdxi_editor or dependencies can exceed Python's default recursion limit
sys.setrecursionlimit(5000)

from jdxi_editor.bundle_imports import HIDDEN_IMPORTS
from setuptools import setup, find_packages

# run with
# python setup.py py2app -A

APP = ['run_editor.py']
# The app's version is the project's: the PKG installer skips an app whose
# version is lower than the installed one, so it must not stay at a fixed value
VERSION = re.search(
    r'__version__ = "([^"]+)"', Path("jdxi_editor/project.py").read_text()
).group(1)
DATA_FILES = [
    "resources/jdxi_icon.png",
    "resources/fonts/JdLCD.ttf",
    ("resources", glob.glob("resources/*.png")),
    ("resources/analog_synths", glob.glob("resources/analog_synths/*.png")),
    ("resources/arpeggiator", glob.glob("resources/arpeggiator/*.png")),
    ("resources/drum_kits", glob.glob("resources/drum_kits/*.png")),
    ("resources/digital_synths", glob.glob("resources/digital_synths/*.png")),
    ("resources/effects", glob.glob("resources/effects/*.png")),
    ("resources/presets", glob.glob("resources/presets/*.png")),
    ("resources/vocal_fx", glob.glob("resources/vocal_fx/*.png")),
]  # Include any additional files your app needs
OPTIONS = {
    'packages': ['jdxi_editor', 'rtmidi', 'decologr', 'picomidi', 'qtawesome',
                 '_sounddevice_data', 'cffi', 'music21.lily'],
    'argv_emulation': False,
    'iconfile': 'jdxi_icon_512.icns',  # Path to the .icns file
    'includes': ['PySide6',
                 "imp",
                 "rtmidi._rtmidi",
                 'mido',
                 'mido.backends',
                 'mido.backends.rtmidi',
                 'PIL',
                 'PIL._imaging',  # <- explicitly include the C extension
                 'PIL.Image',
                 'PIL.ImageDraw',
                 'PIL.ImageColor',
                 'PIL',
                 'decologr',      # Logging library
                 'picomidi',      # MIDI library
                 'qtawesome',     # Icon library
                 'qtawesome.iconic_font',  # Ensure PySide6 is bundled
                 'PySide6.QtNetwork',  # update check (GitHub Releases)
                 *HIDDEN_IMPORTS],
    "excludes": [
                 'Image',
                 "Carbon",
                 'PySide2',  # you're using PySide6, exclude PySide2 entirely
                 'PyQt5',  # not used, exclude it too
                 'PyInstaller',  # the source of the hook-related confusion
                 'site'  # exclude site module to avoid sitecustomize circular import issues
                 ],
    "plist": {
        "CFBundleShortVersionString": VERSION,
        "CFBundleVersion": VERSION,
        'CFBundleIconFile': 'jdxi_icon_512',  # Should match the iconfile name without .icns
        'CFBundleName': 'JD-Xi Editor',
        'CFBundleDisplayName': 'JD-Xi Editor',
        'CFBundleExecutable': 'JD-Xi Editor',
        'CFBundleIdentifier': 'com.jdxi.editor',
    },
}

setup(
    name="jdxi-editor",
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    # The two packages this repository ships, as in pyproject.toml's
    # [tool.hatch.build.targets.wheel] only-include. tests/ is not shipped.
    packages=find_packages(include=["jdxi_editor*", "picoui*"]),
    # No install_requires: the dependency list lives in pyproject.toml. The
    # copy that used to be here had drifted (it asked for qtpy, which the app
    # does not import, and was missing numpy, music21, SQLAlchemy, and
    # pyqtdarktheme, darkdetect, and the tomli backport).
)