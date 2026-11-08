"""Unit tests for partial clipboard kind matching (no Qt / theme deps)."""

import importlib.util
import unittest
from pathlib import Path


def _load_module(name: str, relative: str):
    root = Path(__file__).resolve().parents[1]
    path = root / relative
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


pc = _load_module(
    "partial_clipboard_under_test",
    "jdxi_editor/ui/editors/helpers/partial_clipboard.py",
)
ar = _load_module(
    "analog_random_under_test",
    "jdxi_editor/ui/editors/helpers/analog_random.py",
)


class TestPartialClipboard(unittest.TestCase):
    def setUp(self) -> None:
        pc._CLIPBOARD = None

    def tearDown(self) -> None:
        pc._CLIPBOARD = None

    def test_copy_paste_same_kind(self) -> None:
        pc.copy_partial("digital_partial", {"LEVEL": 64, "CUTOFF": 100})
        out = pc.paste_partial("digital_partial")
        self.assertEqual(out, {"LEVEL": 64, "CUTOFF": 100})

    def test_paste_rejects_mismatched_kind(self) -> None:
        pc.copy_partial("digital_partial", {"LEVEL": 10})
        self.assertIsNone(pc.paste_partial("drum_partial"))

    def test_paste_empty(self) -> None:
        self.assertIsNone(pc.paste_partial("digital_partial"))


class TestAnalogRandomRanges(unittest.TestCase):
    def test_tone_name_uses_digit_range(self) -> None:
        import inspect

        src = inspect.getsource(ar.randomize_analog_editor)
        self.assertIn("48", src)
        self.assertIn("57", src)
        self.assertIn("TONE_NAME_", src)


if __name__ == "__main__":
    unittest.main()
