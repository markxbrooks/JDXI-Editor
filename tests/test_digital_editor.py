#!/usr/bin/env python3
"""
Unit tests for DigitalSynthEditor.

This test suite verifies:
1. Basic editor initialization
2. UI setup and widget creation
3. Partial state management (enable/disable, select)
4. Filter mode button updates
5. Waveform button updates
6. LFO shape button updates
7. Mod LFO shape button updates
8. Partial controls updates
9. Common controls updates
10. Special parameter handling
"""

import sys
import os
import unittest
from unittest.mock import Mock

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest

from jdxi_editor.ui.editors.digital.editor import DigitalSynthEditor
from jdxi_editor.midi.data.digital import DigitalPartial, DigitalWaveOsc
from jdxi_editor.midi.data.digital.filter import DigitalFilterMode
from jdxi_editor.midi.data.digital.lfo import DigitalLFOShape
from jdxi_editor.midi.data.parameter.digital import DigitalPartialParam
from jdxi_editor.core.synth.type import JDXiSynth

# Create QApplication for tests if it doesn't exist
_app = None


def get_qapp():
    """Get or create QApplication instance for tests."""
    global _app
    if _app is None:
        _app = QApplication.instance()
        if _app is None:
            _app = QApplication([])
    return _app


class TestDigitalSynthEditor(unittest.TestCase):
    """Test suite for DigitalSynthEditor."""

    def setUp(self):
        """Set up test fixtures."""
        get_qapp()
        
        # Create mock MIDI helper
        self.mock_midi_helper = Mock()
        self.mock_midi_helper.send_midi_message = Mock(return_value=True)
        self.mock_midi_helper.send_sysex_message = Mock(return_value=True)
        
        # Create mock preset helper
        self.mock_preset_helper = Mock()
        
        # Create editor instance
        self.editor = DigitalSynthEditor(
            midi_helper=self.mock_midi_helper,
            preset_helper=self.mock_preset_helper,
            synth_number=1,
            parent=None
        )

    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'editor') and self.editor:
            self.editor.close()
            self.editor.deleteLater()
        QTest.qWait(100)

    def test_initialization(self):
        """Test editor initialization."""
        self.assertIsNotNone(self.editor)
        self.assertEqual(self.editor.synth_number, 1)
        self.assertEqual(self.editor.midi_helper, self.mock_midi_helper)
        self.assertEqual(self.editor.preset_helper, self.mock_preset_helper)
        self.assertEqual(self.editor.preset_type, JDXiSynth.DIGITAL_SYNTH_1)

    def test_initialization_synth_2(self):
        """Test editor initialization for synth 2."""
        editor = DigitalSynthEditor(
            midi_helper=self.mock_midi_helper,
            preset_helper=self.mock_preset_helper,
            synth_number=2,
            parent=None
        )
        self.assertEqual(editor.synth_number, 2)
        self.assertEqual(editor.preset_type, JDXiSynth.DIGITAL_SYNTH_2)
        editor.close()
        editor.deleteLater()

    def test_setup_ui(self):
        """Test UI setup."""
        self.editor.setup_ui()
        
        # Verify main components exist
        self.assertIsNotNone(self.editor.base_widget)
        self.assertIsNotNone(self.editor.tab_widget)
        self.assertIsNotNone(self.editor.partials_panel)
        self.assertIsNotNone(self.editor.instrument_preset)
        self.assertIsNotNone(self.editor.common_section)
        self.assertIsNotNone(self.editor.tone_modify_section)

    def test_partial_editors_created(self):
        """Test that partial editors are created."""
        self.editor.setup_ui()
        
        # Should have 3 partial editors
        self.assertEqual(len(self.editor.partial_editors), 3)
        self.assertIn(1, self.editor.partial_editors)
        self.assertIn(2, self.editor.partial_editors)
        self.assertIn(3, self.editor.partial_editors)

    def test_set_partial_state_enabled(self):
        """Test setting partial state to enabled."""
        self.editor.setup_ui()
        
        # Mock send_midi_parameter
        self.editor.send_midi_parameter = Mock(return_value=True)
        
        result = self.editor.set_partial_state(
            DigitalPartial.PARTIAL_1,
            enabled=True,
            selected=True
        )
        
        self.assertTrue(result)
        self.editor.send_midi_parameter.assert_called()

    def test_set_partial_state_disabled(self):
        """Test setting partial state to disabled."""
        self.editor.setup_ui()
        
        # Mock send_midi_parameter
        self.editor.send_midi_parameter = Mock(return_value=True)
        
        result = self.editor.set_partial_state(
            DigitalPartial.PARTIAL_2,
            enabled=False,
            selected=False
        )
        
        self.assertTrue(result)
        # Should send value 0 for disabled
        calls = self.editor.send_midi_parameter.call_args_list
        self.assertTrue(any(call[1]['value'] == 0 for call in calls))

    def test_on_partial_state_changed(self):
        """Test handling partial state changes."""
        self.editor.setup_ui()
        
        # Mock set_partial_state and tab widget methods
        self.editor.set_partial_state = Mock(return_value=True)
        self.editor.tab_widget.setTabEnabled = Mock()
        self.editor.tab_widget.setCurrentIndex = Mock()
        
        # Use actual DigitalPartial enum (which has .value attribute)
        from jdxi_editor.midi.data.digital import DigitalPartial
        
        self.editor._on_partial_state_changed(
            DigitalPartial.PARTIAL_1,  # value = 1
            enabled=True,
            selected=True
        )
        
        # Verify set_partial_state was called (with positional args, not keyword args)
        self.editor.set_partial_state.assert_called_once_with(
            DigitalPartial.PARTIAL_1,
            True,  # enabled
            True   # selected
        )
        # Tab index 1 corresponds to "Partial 1" (index 0 is "Presets")
        self.editor.tab_widget.setTabEnabled.assert_called_with(1, True)
        self.editor.tab_widget.setCurrentIndex.assert_called_with(1)

    def test_initialize_partial_states(self):
        """Test initializing partial states."""
        self.editor.setup_ui()
        
        # Mock partials panel switches
        for partial in DigitalPartial.get_partials():
            mock_switch = Mock()
            mock_switch.setState = Mock()
            self.editor.partials_panel.switches[partial] = mock_switch
        
        self.editor._initialize_partial_states()
        
        # Partial 1 should be enabled and selected
        self.editor.partials_panel.switches[DigitalPartial.PARTIAL_1].setState.assert_called_with(True, True)
        
        # Other partials should be disabled
        for partial in [DigitalPartial.PARTIAL_2, DigitalPartial.PARTIAL_3]:
            self.editor.partials_panel.switches[partial].setState.assert_called_with(False, False)

    def test_update_waveform_buttons(self):
        """Test updating waveform buttons."""
        self.editor.setup_ui()
        
        # Mock waveform buttons for partial 1
        mock_buttons = {}
        for wave in DigitalWaveOsc:
            mock_btn = Mock()
            mock_btn.setChecked = Mock()
            mock_btn.setStyleSheet = Mock()
            mock_buttons[wave] = mock_btn
        
        self.editor.partial_editors[1].oscillator_tab.wave_buttons = mock_buttons
        
        # Update to PW_SQUARE waveform (value 2) - based on actual waveform_map
        self.editor._update_waveform_buttons(1, 2)
        
        # PW_SQUARE button should be checked
        mock_buttons[DigitalWaveOsc.PW_SQUARE].setChecked.assert_called_with(True)
        mock_buttons[DigitalWaveOsc.PW_SQUARE].setStyleSheet.assert_called()

    def test_update_waveform_buttons_invalid_partial(self):
        """Test updating waveform buttons with invalid partial number."""
        self.editor.setup_ui()
        
        # Should not raise exception
        self.editor._update_waveform_buttons(99, 1)

    def test_update_filter_mode_buttons(self):
        """Test updating filter mode buttons."""
        self.editor.setup_ui()
        
        # Mock filter mode buttons for partial 1
        mock_buttons = {}
        for mode in DigitalFilterMode:
            mock_btn = Mock()
            mock_btn.setChecked = Mock()
            mock_btn.setStyleSheet = Mock()
            mock_buttons[mode] = mock_btn
        
        self.editor.partial_editors[1].filter_tab.filter_mode_buttons = mock_buttons
        
        # Update to LPF mode (value 1)
        self.editor._update_filter_mode_buttons(1, 1)
        
        # LPF button should be checked
        mock_buttons[DigitalFilterMode.LPF].setChecked.assert_called_with(True)
        mock_buttons[DigitalFilterMode.LPF].setStyleSheet.assert_called()

    def test_update_filter_mode_buttons_bypass(self):
        """Test updating filter mode buttons to bypass."""
        self.editor.setup_ui()
        
        # Mock filter mode buttons
        mock_buttons = {}
        for mode in DigitalFilterMode:
            mock_btn = Mock()
            mock_btn.setChecked = Mock()
            mock_btn.setStyleSheet = Mock()
            mock_buttons[mode] = mock_btn
        
        self.editor.partial_editors[1].filter_tab.filter_mode_buttons = mock_buttons
        
        # Update to BYPASS mode (value 0)
        self.editor._update_filter_mode_buttons(1, 0)
        
        # BYPASS button should be checked
        mock_buttons[DigitalFilterMode.BYPASS].setChecked.assert_called_with(True)

    def test_update_filter_mode_buttons_invalid_value(self):
        """Test updating filter mode buttons with invalid value."""
        self.editor.setup_ui()
        
        # Should not raise exception
        self.editor._update_filter_mode_buttons(1, 99)

    def test_update_lfo_shape_buttons(self):
        """Test updating LFO shape buttons."""
        self.editor.setup_ui()
        
        # Mock LFO shape buttons for partial 1
        mock_buttons = {}
        for shape in DigitalLFOShape:
            mock_btn = Mock()
            mock_btn.setChecked = Mock()
            mock_btn.setStyleSheet = Mock()
            mock_buttons[shape] = mock_btn
        
        self.editor.partial_editors[1].lfo_tab.wave_shape_buttons = mock_buttons
        
        # Update to SINE shape (value 1)
        self.editor._update_lfo_shape_buttons(1, 1)
        
        # SINE button should be checked
        mock_buttons[DigitalLFOShape.SINE].setChecked.assert_called_with(True)

    def test_update_mod_lfo_shape_buttons(self):
        """Test updating Mod LFO shape buttons."""
        self.editor.setup_ui()
        
        # Mock Mod LFO shape buttons for partial 1
        mock_buttons = {}
        for shape in DigitalLFOShape:
            mock_btn = Mock()
            mock_btn.setChecked = Mock()
            mock_btn.setStyleSheet = Mock()
            mock_buttons[shape] = mock_btn
        
        self.editor.partial_editors[1].mod_lfo_tab.wave_shape_buttons = mock_buttons
        
        # Update to SQUARE shape (value 3)
        self.editor._update_mod_lfo_shape_buttons(1, 3)
        
        # SQUARE button should be checked
        mock_buttons[DigitalLFOShape.SQUARE].setChecked.assert_called_with(True)

    def test_handle_special_params_osc_wave(self):
        """Test handling OSC_WAVE special parameter."""
        self.editor.setup_ui()
        self.editor._update_waveform_buttons = Mock()
        
        self.editor._handle_special_params(
            1,
            DigitalPartialParam.OSC_WAVE,
            2  # SAW waveform
        )
        
        self.editor._update_waveform_buttons.assert_called_once_with(1, 2)

    def test_handle_special_params_filter_mode(self):
        """Test handling FILTER_MODE_SWITCH special parameter."""
        self.editor.setup_ui()
        self.editor._update_filter_mode_buttons = Mock()
        self.editor._update_filter_state = Mock()
        
        self.editor._handle_special_params(
            1,
            DigitalPartialParam.FILTER_MODE_SWITCH,
            1  # LPF mode
        )
        
        self.editor._update_filter_mode_buttons.assert_called_once_with(1, 1)
        self.editor._update_filter_state.assert_called_once_with(1, 1)

    def test_handle_special_params_lfo_shape(self):
        """Test handling LFO_SHAPE special parameter."""
        self.editor.setup_ui()
        self.editor._update_lfo_shape_buttons = Mock()
        
        self.editor._handle_special_params(
            1,
            DigitalPartialParam.LFO_SHAPE,
            1  # SINE shape
        )
        
        self.editor._update_lfo_shape_buttons.assert_called_once_with(1, 1)

    def test_handle_special_params_mod_lfo_shape(self):
        """Test handling MOD_LFO_SHAPE special parameter."""
        self.editor.setup_ui()
        self.editor._update_mod_lfo_shape_buttons = Mock()
        
        self.editor._handle_special_params(
            1,
            DigitalPartialParam.MOD_LFO_SHAPE,
            2  # SAW shape
        )
        
        self.editor._update_mod_lfo_shape_buttons.assert_called_once_with(1, 2)

    def test_update_filter_state(self):
        """Test updating filter state."""
        self.editor.setup_ui()
        
        # Mock update_filter_controls_state method on partial editor
        mock_update_method = Mock()
        self.editor.partial_editors[1].update_controls_state = mock_update_method
        
        # Update filter state to LPF (value 1)
        self.editor._update_filter_state(1, 1)
        
        # Should call update_filter_controls_state on the partial editor
        mock_update_method.assert_called_once_with(1)

    def test_update_filter_state_bypass(self):
        """Test updating filter state to bypass."""
        self.editor.setup_ui()
        
        # Mock update_filter_controls_state method on partial editor
        mock_update_method = Mock()
        self.editor.partial_editors[1].update_controls_state = mock_update_method
        
        # Update filter state to BYPASS (value 0)
        self.editor._update_filter_state(1, 0)
        
        # Should call update_filter_controls_state on the partial editor
        mock_update_method.assert_called_once_with(0)

    def test_update_filter_state_hpf(self):
        """Test updating filter state to HPF."""
        self.editor.setup_ui()
        
        # Mock update_filter_controls_state method on partial editor
        mock_update_method = Mock()
        self.editor.partial_editors[1].update_controls_state = mock_update_method
        
        # Update filter state to HPF (value 2)
        self.editor._update_filter_state(1, 2)
        
        # Should call update_filter_controls_state on the partial editor
        mock_update_method.assert_called_once_with(2)

    def test_update_filter_state_bpf(self):
        """Test updating filter state to BPF."""
        self.editor.setup_ui()
        
        # Mock update_filter_controls_state method on partial editor
        mock_update_method = Mock()
        self.editor.partial_editors[1].update_controls_state = mock_update_method
        
        # Update filter state to BPF (value 3)
        self.editor._update_filter_state(1, 3)
        
        # Should call update_filter_controls_state on the partial editor
        mock_update_method.assert_called_once_with(3)

    def test_partial_tab_widget_tabs(self):
        """Test that partial tab widget has correct tabs."""
        self.editor.setup_ui()
        
        # Should have Presets tab + 3 Partial tabs + Common + Misc = 6 tabs
        self.assertEqual(self.editor.tab_widget.count(), 6)
        
        # Check tab names
        tab_names = [
            self.editor.tab_widget.tabText(i)
            for i in range(self.editor.tab_widget.count())
        ]
        
        self.assertIn("Presets", tab_names)
        self.assertIn("Partial 1", tab_names)
        self.assertIn("Partial 2", tab_names)
        self.assertIn("Partial 3", tab_names)
        self.assertIn("Common", tab_names)
        self.assertIn("Misc", tab_names)


if __name__ == '__main__':
    unittest.main()
