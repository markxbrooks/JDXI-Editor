"""The frozen build is told about FluidSynth, sounddevice, and LilyPond."""

from pathlib import Path

from jdxi_editor import bundle_imports
from jdxi_editor.bundle_imports import COLLECT_ALL, HIDDEN_IMPORTS, pyinstaller_args


def test_the_imports_are_written_where_a_freezer_can_see_them():
    source = Path(bundle_imports.__file__).read_text()
    for statement in (
        "import fluidsynth",
        "import sounddevice",
        "import _sounddevice",
        "import _sounddevice_data",
        "import cffi",
        "import music21.lily.translate",
        "import music21.lily.lilyObjects",
    ):
        assert statement in source


def test_pyinstaller_is_given_the_modules_and_their_binaries():
    assert "fluidsynth" in HIDDEN_IMPORTS
    assert "sounddevice" in HIDDEN_IMPORTS
    assert "music21.lily.translate" in HIDDEN_IMPORTS
    assert "_sounddevice_data" in COLLECT_ALL
    args = pyinstaller_args()
    assert args.count("--hidden-import") == len(HIDDEN_IMPORTS)
    assert "--collect-all=_sounddevice_data" in args
    assert "--collect-all=cffi" in args
