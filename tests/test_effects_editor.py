#!/usr/bin/env python3
"""
Unit tests for EffectsCommonEditor (Phase 0 baseline).

This test suite verifies:
1. Basic editor initialization
2. Tab structure (Effect 1, Effect 2, Delay, Reverb)
3. Controls registration for key parameters
4. send_midi_parameter address routing
5. Effect type label updates (update_efx1_labels, update_efx2_labels)

Run: pytest tests/test_effects_editor.py -v
"""

import sys
import os
import unittest
from unittest.mock import Mock

# Add the project root to the path
sys.path.insert(0, os.path.abspath("."))

from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest

from jdxi_editor.ui.editors.effects.common import EffectsCommonEditor
from jdxi_editor.midi.data.parameter.effects.effects import (
    Effect1Param,
    Effect2Param,
    DelayParam,
    ReverbParam,
)

_app = None


def get_qapp():
    """Get or create QApplication instance for tests."""
    global _app
    if _app is None:
        _app = QApplication.instance()
        if _app is None:
            _app = QApplication([])
    return _app


class TestEffectsCommonEditor(unittest.TestCase):
    """Test suite for EffectsCommonEditor."""

    def setUp(self):
        """Set up test fixtures."""
        get_qapp()

        self.mock_midi_helper = Mock()
        self.mock_midi_helper.send_midi_message = Mock(return_value=True)
        self.mock_midi_helper.midi_sysex_json = Mock()

        self.mock_preset_helper = Mock()

        self.editor = EffectsCommonEditor(
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
        """Test that EffectsCommonEditor initializes without error."""
        self.assertIsNotNone(self.editor)
        self.assertEqual(self.editor.windowTitle(), "Effects")

    def test_tabs_exist(self):
        """Test that Effects 1 & 2 and Delay & Reverb tabs are present."""
        tabs = self.editor.tabs
        self.assertIsNotNone(tabs)
        tab_count = tabs.count()
        self.assertGreaterEqual(tab_count, 2, "Expected at least 2 tabs")
        tab_labels = [tabs.tabText(i) for i in range(tab_count)]
        self.assertIn("Effects 1 & 2", tab_labels)
        self.assertIn("Delay & Reverb", tab_labels)

    def test_effect1_controls_registered(self):
        """Test that Effect 1 key controls are in the controls dict."""
        self.assertIn(Effect1Param.EFX1_TYPE, self.editor.controls)
        self.assertIn(Effect1Param.EFX1_LEVEL, self.editor.controls)
        self.assertIn(Effect1Param.EFX1_OUTPUT_ASSIGN, self.editor.controls)

    def test_effect2_controls_registered(self):
        """Test that Effect 2 key controls are in the controls dict."""
        self.assertIn(Effect2Param.EFX2_TYPE, self.editor.controls)
        self.assertIn(Effect2Param.EFX2_LEVEL, self.editor.controls)

    def test_delay_controls_registered(self):
        """Test that Delay key controls are in the controls dict."""
        self.assertIn(DelayParam.DELAY_LEVEL, self.editor.controls)
        self.assertIn(DelayParam.DELAY_ON_OFF, self.editor.controls)
        self.assertIn(DelayParam.DELAY_TYPE, self.editor.controls)
        self.assertIn(DelayParam.DELAY_TIME_NOTE_MODE, self.editor.controls)
        self.assertIn(DelayParam.DELAY_FEEDBACK, self.editor.controls)

    def test_reverb_controls_registered(self):
        """Test that Reverb key controls are in the controls dict."""
        self.assertIn(ReverbParam.REVERB_LEVEL, self.editor.controls)
        self.assertIn(ReverbParam.REVERB_ON_OFF, self.editor.controls)
        self.assertIn(ReverbParam.REVERB_TYPE, self.editor.controls)
        self.assertIn(ReverbParam.REVERB_TIME, self.editor.controls)

    def test_send_midi_parameter_effect1(self):
        """Test that send_midi_parameter sends for Effect1Param."""
        result = self.editor.send_midi_parameter(Effect1Param.EFX1_LEVEL, 64)
        self.assertTrue(result)
        self.mock_midi_helper.send_midi_message.assert_called_once()

    def test_send_midi_parameter_effect2(self):
        """Test that send_midi_parameter sends for Effect2Param."""
        result = self.editor.send_midi_parameter(Effect2Param.EFX2_LEVEL, 64)
        self.assertTrue(result)
        self.mock_midi_helper.send_midi_message.assert_called_once()

    def test_send_midi_parameter_delay(self):
        """Test that send_midi_parameter sends for DelayParam."""
        result = self.editor.send_midi_parameter(DelayParam.DELAY_LEVEL, 64)
        self.assertTrue(result)
        self.mock_midi_helper.send_midi_message.assert_called_once()

    def test_send_midi_parameter_reverb(self):
        """Test that send_midi_parameter sends for ReverbParam."""
        result = self.editor.send_midi_parameter(ReverbParam.REVERB_LEVEL, 64)
        self.assertTrue(result)
        self.mock_midi_helper.send_midi_message.assert_called_once()

    def test_update_efx1_labels_no_exception(self):
        """Test that update_efx1_labels runs without exception for each type."""
        for effect_type in range(5):  # Thru, Distortion, Fuzz, Compressor, Bit Crusher
            self.editor.update_efx1_labels(effect_type)

    def test_update_efx2_labels_no_exception(self):
        """Test that update_efx2_labels runs without exception for each type."""
        for effect_type in [0, 1, 2, 3, 4]:  # Thru, Flanger, Phaser, Ring Mod, Slicer
            self.editor.update_efx2_labels(effect_type)

    def test_midi_requests_includes_effects(self):
        """Test that midi_requests includes the four effect blocks (Effect1, Effect2, Delay, Reverb)."""
        self.assertIsNotNone(self.editor.midi_requests)
        self.assertGreaterEqual(
            len(self.editor.midi_requests),
            4,
            "midi_requests should include Effect1, Effect2, Delay, Reverb",
        )

    def test_dispatch_sysex_effect1_no_exception(self):
        """Test that _dispatch_sysex_to_area handles EFFECT_1 data without crashing."""
        import json

        data = {
            "TEMPORARY_AREA": "TEMPORARY_PROGRAM",
            "SYNTH_TONE": "EFFECT_1",
            "EFX1_TYPE": 1,
            "EFX1_LEVEL": 64,
        }
        self.editor._dispatch_sysex_to_area(json.dumps(data))

    def test_dispatch_sysex_effect2_no_exception(self):
        """Test that _dispatch_sysex_to_area handles EFFECT_2 data without crashing."""
        import json

        data = {
            "TEMPORARY_AREA": "TEMPORARY_PROGRAM",
            "SYNTH_TONE": "EFFECT_2",
            "EFX2_TYPE": 1,
            "EFX2_LEVEL": 64,
        }
        self.editor._dispatch_sysex_to_area(json.dumps(data))

    def test_dispatch_sysex_delay_reverb_no_exception(self):
        """Test that _dispatch_sysex_to_area handles DELAY and REVERB data without crashing."""
        import json

        data_delay = {
            "TEMPORARY_AREA": "TEMPORARY_PROGRAM",
            "SYNTH_TONE": "DELAY",
            "DELAY_LEVEL": 64,
            "DELAY_ON_OFF": 1,
        }
        self.editor._dispatch_sysex_to_area(json.dumps(data_delay))

        data_reverb = {
            "TEMPORARY_AREA": "TEMPORARY_PROGRAM",
            "SYNTH_TONE": "REVERB",
            "REVERB_LEVEL": 64,
            "REVERB_ON_OFF": 1,
        }
        self.editor._dispatch_sysex_to_area(json.dumps(data_reverb))

    def test_dispatch_sysex_records_applied(self):
        """Test that dispatching SysEx records applied params when registry and controls resolve."""
        filtered = {"DELAY_LEVEL": 80}
        stats = self.editor._sysex_dispatcher.dispatch(filtered)
        self.assertIn(
            "DELAY_LEVEL",
            stats.applied,
            "DELAY_LEVEL should be in applied when registry and controls resolve",
        )


if __name__ == "__main__":
    unittest.main()
