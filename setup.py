import glob

from setuptools import setup, find_packages

# run with
# python setup.py py2app -A

APP = ['run_editor.py']
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
    'packages': ['jdxi_editor', 'rtmidi'],
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
                 'PIL'],           # Ensure PySide6 is bundled
    "excludes": [
                 'Image',
                 "Carbon",
                 'PySide2',  # you're using PySide6, exclude PySide2 entirely
                 'PyQt5',  # not used, exclude it too
                 'PyInstaller',  # the source of the hook-related confusion
                 'site'  # exclude site module to avoid sitecustomize circular import issues
                 ],
    "plist": {
        "CFBundleShortVersionString": "0.1.0",
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
    packages=find_packages(),
    install_requires=[
        "PySide6",
        "python-rtmidi",
        "qtpy",
        "qtawesome",
        "mido",
        "Pillow",
    ],
)
