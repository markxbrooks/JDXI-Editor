# setup.py
from setuptools import setup, find_packages

APP = ["jdxi_editor/main.py"]  # Path to your main script
DATA_FILES = [
    "jdxi_editor.icns",
    "resources/jdxi_icon.png",
    "resources/fonts/JdLCD.ttf",
]  # Include any additional files your app needs
OPTIONS = {
    "argv_emulation": False,
    "packages": [
        "PySide6",
        "pubsub",
        "qtpy",
        "mido",
        "qtawesome",
        "mido",
    ],  # List any packages your app uses
    "iconfile": "jdxi_editor.icns",  # Path to your app icon file (optional)
    "excludes": ["Carbon"],
    "plist": {
        "CFBundleShortVersionString": "0.1.0",
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    name="jdxi_editor",
    version="0.30",
    packages=find_packages(),
    install_requires=[
        "PySide6",
        "python-rtmidi",
        "pubsub",
        "qtpy",
        "qtawesome",
        "mido",
    ],
    entry_points={
        "console_scripts": [
            "jdxi_editor=jdxi_editor.main:main",
        ],
    },
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
