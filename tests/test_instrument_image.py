"""Tests for instrument image resolution (engine detection -> icon filename)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("."))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from jdxi_editor.ui.editors.synth.editor import SynthEditor
from jdxi_editor.ui.editors.synth.specs import (
    engine_image_basenames,
    preset_match_text,
)


class ImageResolutionStub:
    """Drives the real SynthEditor image lookup without building a widget."""

    instrument_default_image = "jdxi_vector.png"

    # Methods under test, borrowed from the real editor.
    _name_image_paths = SynthEditor._name_image_paths
    _try_load_specific_or_generic_image = (
        SynthEditor._try_load_specific_or_generic_image
    )
    _parse_instrument_text = SynthEditor._parse_instrument_text
    update_instrument_image = SynthEditor.update_instrument_image

    def __init__(self, instrument_icon_folder: str, text: str):
        self.instrument_icon_folder = instrument_icon_folder
        self._text = text
        self.loaded = None

    def _get_selected_instrument_text(self) -> str:
        return self._text

    def load_and_set_image(self, image_path, secondary_image_path=None) -> bool:
        for path in (image_path, secondary_image_path):
            if path and os.path.exists(path):
                self.loaded = os.path.basename(path)
                return True
        return False

    def _fallback_to_default_image(self, reason: str) -> None:
        self.loaded = self.instrument_default_image


def resolve(folder: str, text: str) -> str:
    stub = ImageResolutionStub(folder, text)
    stub.update_instrument_image()
    return stub.loaded


class TestEngineImageBasenames(unittest.TestCase):
    """Engine names expand to every filename the artwork may use."""

    def test_tb_expands_to_tb_303_variants(self):
        self.assertEqual(
            engine_image_basenames("tb"), ("tb", "tb-303", "tb303")
        )

    def test_unknown_name_is_used_as_is(self):
        self.assertEqual(engine_image_basenames("trem"), ("trem",))

    def test_empty_name_yields_no_candidates(self):
        self.assertEqual(engine_image_basenames(""), ())
        self.assertEqual(engine_image_basenames(None), ())

    def test_name_is_normalized(self):
        self.assertEqual(engine_image_basenames(" SH "), ("sh", "sh-101", "sh101"))


class TestPresetMatchText(unittest.TestCase):
    """A leading preset index must not be read as a model number."""

    def test_colon_index_is_stripped(self):
        self.assertEqual(preset_match_text("101: MKS-50 Bass1"), "mks-50 bass1")

    def test_dash_index_is_stripped(self):
        self.assertEqual(preset_match_text("001 - Power 3"), "power 3")

    def test_non_numeric_head_is_kept(self):
        self.assertEqual(preset_match_text("TB Bass 1"), "tb bass 1")


class TestInstrumentImageResolution(unittest.TestCase):
    """TB-303 presets find their icon in each resource folder."""

    def test_digital_tb_presets_use_tb_image(self):
        for preset in (
            "091: TB Bass 1",
            "129: TB Bass 2",
            "218: TB Saw Seq 1",
            "219: TB Sqr Seq 1",
            "061: Dist Flt TB1",
            "062: Dist TB Sqr1",
        ):
            with self.subTest(preset=preset):
                self.assertEqual(resolve("digital_synths", preset), "tb.png")

    def test_analog_tb_preset_uses_aliased_tb303_image(self):
        # analog_synths ships "tb303.png", not "tb.png".
        self.assertEqual(resolve("analog_synths", "012: Dist TB Bs 1"), "tb303.png")

    def test_known_special_cases_still_resolve(self):
        self.assertEqual(resolve("digital_synths", "001: JP8 Strings1"), "jp8.png")
        self.assertEqual(resolve("digital_synths", "003: JD Piano 1"), "piano.png")
        self.assertEqual(resolve("drum_kits", "002: TR-909 Kit1"), "909.png")


if __name__ == "__main__":
    unittest.main()
