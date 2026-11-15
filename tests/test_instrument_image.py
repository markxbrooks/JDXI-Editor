"""Tests for instrument image resolution (name detection -> icon filename)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("."))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from jdxi_editor.ui.editors.synth.editor import SynthEditor
from jdxi_editor.ui.editors.synth.specs import (
    engine_image_basenames,
    keyword_in,
    preset_image_basenames,
    preset_match_text,
    preset_match_texts,
)


class ImageResolutionStub:
    """Drives the real SynthEditor image lookup without building a widget."""

    instrument_default_image = "jdxi_vector.png"

    # Methods under test, borrowed from the real editor.
    _icon_path = SynthEditor._icon_path
    _resolve_icon_path = SynthEditor._resolve_icon_path
    _preset_image_paths = SynthEditor._preset_image_paths
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


class TestKeywordMatching(unittest.TestCase):
    """Short keywords match on letter boundaries; long ones stay substrings."""

    def test_short_keyword_needs_a_letter_boundary(self):
        # "sh" must not match inside "WaveShape", "ep" not inside "Sweep".
        self.assertFalse(keyword_in("waveshapeld1", "sh"))
        self.assertFalse(keyword_in("sweep pad 1", "ep"))
        self.assertFalse(keyword_in("epicslow brs", "ep"))

    def test_short_keyword_matches_on_a_boundary(self):
        self.assertTrue(keyword_in("sh-101 bs", "sh"))
        self.assertTrue(keyword_in("trem ep 1", "ep"))

    def test_digits_may_sit_next_to_a_short_keyword(self):
        # The JD-Xi writes "Dist Flt TB1", with no space before the number.
        self.assertTrue(keyword_in("dist flt tb1", "tb"))

    def test_long_keyword_still_matches_a_run_together_name(self):
        self.assertTrue(keyword_in("s-sawstacld1", "sawstac"))

    def test_camel_case_split_form_is_matched_too(self):
        # "ResoPulseBs1" only yields "bs" once split on capitals.
        self.assertTrue(keyword_in(preset_match_texts("020: ResoPulseBs1"), "bs"))


class TestPresetImageBasenames(unittest.TestCase):
    """Artwork may be named after the preset itself."""

    def test_multi_word_label_is_offered_in_several_spellings(self):
        self.assertEqual(
            preset_image_basenames("164: Trem EP 1"),
            ("trem ep", "trem-ep", "trem_ep"),
        )

    def test_punctuation_is_offered_both_ways(self):
        self.assertIn("e-grand", preset_image_basenames("163: E. Grand 1"))

    def test_single_word_label_is_too_broad(self):
        self.assertEqual(preset_image_basenames("169: Clav"), ())


class TestInstrumentImageResolution(unittest.TestCase):
    """End-to-end: preset label -> icon file on disk."""

    def test_digital_tb_presets_use_the_tb_303_image(self):
        for preset in (
            "091: TB Bass 1",
            "129: TB Bass 2",
            "218: TB Saw Seq 1",
            "219: TB Sqr Seq 1",
            "061: Dist Flt TB1",
            "062: Dist TB Sqr1",
        ):
            with self.subTest(preset=preset):
                self.assertEqual(resolve("digital_synths", preset), "tb-303.png")

    def test_analog_tb_preset_uses_aliased_tb303_image(self):
        # analog_synths ships "tb303.png", digital_synths "tb-303.png".
        self.assertEqual(resolve("analog_synths", "012: Dist TB Bs 1"), "tb303.png")

    def test_sh_101_preset_uses_the_sh_101_image(self):
        self.assertEqual(resolve("digital_synths", "131: SH-101 Bs"), "sh-101.png")

    def test_preset_named_artwork_beats_the_family_image(self):
        # "trem-ep.png" is more specific than "piano.png" for the piano family.
        self.assertEqual(resolve("digital_synths", "164: Trem EP 1"), "trem-ep.png")

    def test_preset_named_artwork_is_found_regardless_of_filename_case(self):
        # The file on disk is "JD Piano.png".
        self.assertEqual(
            resolve("digital_synths", "162: JD Piano 1").lower(), "jd piano.png"
        )

    def test_sweep_presets_are_not_pianos(self):
        # "ep" used to match inside "Sweep" and show a piano.
        self.assertEqual(resolve("digital_synths", "020: Sweep Pad 1"), "pad.png")
        self.assertEqual(resolve("digital_synths", "023: FltSweep Pd1"), "pad.png")
        self.assertEqual(resolve("digital_synths", "102: Sweep Bass"), "bass.png")

    def test_waveshape_is_not_an_sh_101(self):
        # "sh" used to match inside "WaveShape".
        self.assertEqual(resolve("digital_synths", "054: WaveShapeLd1"), "lead.png")

    def test_strat_is_not_strings(self):
        # "str" used to match inside "Strat".
        self.assertEqual(resolve("digital_synths", "180: Bright Strat"), "strat.png")

    def test_run_together_name_still_resolves(self):
        self.assertEqual(resolve("digital_synths", "049: S-SawStacLd1"), "lead.png")
        self.assertEqual(resolve("analog_synths", "020: ResoPulseBs1"), "bass.png")

    def test_known_engine_without_a_family_still_resolves(self):
        self.assertEqual(resolve("digital_synths", "022: Sweep JD 1"), "jd.png")

    def test_known_special_cases_still_resolve(self):
        self.assertEqual(resolve("digital_synths", "001: JP8 Strings1"), "jp8.png")
        self.assertEqual(resolve("drum_kits", "002: TR-909 Kit1"), "909.png")


if __name__ == "__main__":
    unittest.main()
