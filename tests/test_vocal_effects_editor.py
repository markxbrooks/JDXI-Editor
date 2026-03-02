#!/usr/bin/env python3
"""
Unit tests for VocalFXEditor (Phase 0 baseline, Phase 3 polymorphic).

This test suite verifies:
1. Basic editor initialization
2. Tab structure (Common, Vocoder & Auto Pitch, Mixer)
3. Controls registration for key parameters
4. send_midi_parameter address routing

Run: pytest tests/test_vocal_effects_editor.py -v
"""

import sys
import os
import unittest
from unittest.mock import Mock

# Add the project root to the path
sys.path.insert(0, os.path.abspath("."))

from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest

from jdxi_editor.ui.editors.effects.vocal import VocalFXEditor
from jdxi_editor.midi.data.parameter.program.common import ProgramCommonParam
from jdxi_editor.midi.data.parameter.vocal_fx import VocalFXParam

_app = None


def get_qapp():
    """Get or create QApplication instance for tests."""
    global _app
    if _app is None:
        _app = QApplication.instance()
        if _app is None:
            _app = QApplication([])
    return _app


class TestVocalFXEditor(unittest.TestCase):
    """Test suite for VocalFXEditor."""

    def setUp(self):
        """Set up test fixtures."""
        get_qapp()

        self.mock_midi_helper = Mock()
        self.mock_midi_helper.send_midi_message = Mock(return_value=True)
        self.mock_midi_helper.midi_sysex_json = Mock()

        self.mock_preset_helper = Mock()

        self.editor = VocalFXEditor(
            midi_helper=self.mock_midi_helper,
            preset_helper=self.mock_preset_helper,
            parent=None,
        )

    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, "editor") and self.editor:
            self.editor.close()
            self.editor.deleteLater()
        QTest.qWait(100)

    def test_initialization(self):
        """Test that VocalFXEditor initializes without error."""
        self.assertIsNotNone(self.editor)
        self.assertEqual(self.editor.windowTitle(), "Vocal FX")

    def test_tabs_exist(self):
        """Test that Common, Vocoder & Auto Pitch, Mixer tabs are present."""
        tab_widget = self.editor.tab_widget
        self.assertIsNotNone(tab_widget)
        tab_count = tab_widget.count()
        self.assertGreaterEqual(tab_count, 3, "Expected at least 3 tabs")
        tab_labels = [tab_widget.tabText(i) for i in range(tab_count)]
        self.assertIn("Common", tab_labels)
        self.assertIn("Vocoder & Auto Pitch", tab_labels)
        self.assertIn("Mixer", tab_labels)

    def test_common_controls_registered(self):
        """Test that Common tab key controls are in the controls dict."""
        self.assertIn(ProgramCommonParam.VOCAL_EFFECT, self.editor.controls)
        self.assertIn(ProgramCommonParam.VOCAL_EFFECT_NUMBER, self.editor.controls)
        self.assertIn(ProgramCommonParam.VOCAL_EFFECT_PART, self.editor.controls)

    def test_vocal_fx_controls_registered(self):
        """Test that Vocal FX key controls are in the controls dict."""
        self.assertIn(VocalFXParam.VOCODER_SWITCH, self.editor.controls)
        self.assertIn(VocalFXParam.VOCODER_LEVEL, self.editor.controls)
        self.assertIn(VocalFXParam.VOCODER_ENVELOPE, self.editor.controls)

    def test_mixer_controls_registered(self):
        """Test that Mixer tab key controls are in the controls dict."""
        self.assertIn(VocalFXParam.LEVEL, self.editor.controls)
        self.assertIn(VocalFXParam.PAN, self.editor.controls)
        self.assertIn(VocalFXParam.DELAY_SEND_LEVEL, self.editor.controls)
        self.assertIn(VocalFXParam.REVERB_SEND_LEVEL, self.editor.controls)
        self.assertIn(VocalFXParam.OUTPUT_ASSIGN, self.editor.controls)

    def test_auto_pitch_controls_registered(self):
        """Test that Auto Pitch tab key controls are in the controls dict."""
        self.assertIn(VocalFXParam.AUTO_PITCH_SWITCH, self.editor.controls)
        self.assertIn(VocalFXParam.AUTO_PITCH_TYPE, self.editor.controls)
        self.assertIn(VocalFXParam.AUTO_PITCH_BALANCE, self.editor.controls)

    def test_send_midi_parameter_common(self):
        """Test that send_midi_parameter sends for ProgramCommonParam."""
        result = self.editor.send_midi_parameter(ProgramCommonParam.VOCAL_EFFECT, 1)
        self.assertTrue(result)
        self.mock_midi_helper.send_midi_message.assert_called_once()

    def test_send_midi_parameter_vocal_fx(self):
        """Test that send_midi_parameter sends for VocalFXParam."""
        result = self.editor.send_midi_parameter(VocalFXParam.LEVEL, 64)
        self.assertTrue(result)
        self.mock_midi_helper.send_midi_message.assert_called_once()

    def test_midi_requests_set(self):
        """Test that midi_requests includes Program Common and Program Vocal Effect."""
        self.assertIsNotNone(self.editor.midi_requests)
        self.assertGreaterEqual(len(self.editor.midi_requests), 2)

    def test_dispatch_sysex_no_exception(self):
        """Test that _dispatch_sysex_to_area handles COMMON and VOCAL_EFFECT data."""
        import json

        common_data = {
            "TEMPORARY_AREA": "TEMPORARY_PROGRAM",
            "SYNTH_TONE": "COMMON",
            "VOCAL_EFFECT": 1,
            "VOCAL_EFFECT_PART": 0,
        }
        self.editor._dispatch_sysex_to_area(json.dumps(common_data))

        vocal_data = {
            "TEMPORARY_AREA": "TEMPORARY_PROGRAM",
            "SYNTH_TONE": "VOCAL_EFFECT",
            "LEVEL": 64,
            "PAN": 64,
        }
        self.editor._dispatch_sysex_to_area(json.dumps(vocal_data))

    def test_vocal_effect_stack_switches(self):
        """Test that _update_vocal_effect_stack switches stack page by index."""
        self.editor._update_vocal_effect_stack(0)
        self.assertEqual(self.editor.vocal_effect_stack.currentIndex(), 0)
        self.editor._update_vocal_effect_stack(1)
        self.assertEqual(self.editor.vocal_effect_stack.currentIndex(), 1)
        self.editor._update_vocal_effect_stack(2)
        self.assertEqual(self.editor.vocal_effect_stack.currentIndex(), 2)


if __name__ == "__main__":
    unittest.main()
