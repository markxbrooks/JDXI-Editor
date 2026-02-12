#!/usr/bin/env python3
"""
Unit tests for ModeButtonGroup and ModeButtonSpec.

This test suite verifies:
1. ModeButtonSpec dataclass
2. Basic widget construction with and without icons
3. icon_factory path (custom icon resolution, e.g. waveform pixmaps)
4. set_mode programmatic selection and exclusive state
5. on_mode_changed callback and mode_changed signal
6. Optional MIDI send on selection
7. Button click triggers callback/signal
8. buttons property and tooltips
"""

import sys
from pathlib import Path
from unittest.mock import Mock

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest

import unittest

from jdxi_editor.ui.widgets.editor.mode_button_group import (
    ModeButtonGroup,
    ModeButtonSpec,
)


def get_qapp():
    """Get or create QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class SimpleMode:
    """Simple mode with int value for group id."""

    def __init__(self, value: int, label: str):
        self.value = value
        self.label = label

    def __hash__(self):
        return hash((self.value, self.label))

    def __eq__(self, other):
        if not isinstance(other, SimpleMode):
            return NotImplemented
        return self.value == other.value and self.label == other.label


class TestModeButtonSpec(unittest.TestCase):
    """Tests for ModeButtonSpec dataclass."""

    def test_spec_minimal(self):
        """ModeButtonSpec with required fields only."""
        spec = ModeButtonSpec(mode=0, label="A")
        self.assertEqual(spec.mode, 0)
        self.assertEqual(spec.label, "A")
        self.assertIsNone(spec.icon_name)
        self.assertIsNone(spec.tooltip)

    def test_spec_with_optional(self):
        """ModeButtonSpec with icon_name and tooltip."""
        spec = ModeButtonSpec(
            mode=1,
            label="B",
            icon_name="mdi6.waveform",
            tooltip="Wave",
        )
        self.assertEqual(spec.icon_name, "mdi6.waveform")
        self.assertEqual(spec.tooltip, "Wave")

    def test_spec_frozen(self):
        """ModeButtonSpec is immutable."""
        spec = ModeButtonSpec(mode=0, label="X")
        with self.assertRaises(Exception):
            spec.label = "Y"  # type: ignore


class TestModeButtonGroup(unittest.TestCase):
    """Tests for ModeButtonGroup widget."""

    def setUp(self):
        get_qapp()

    def tearDown(self):
        if hasattr(self, "widget") and self.widget:
            self.widget.close()
            self.widget.deleteLater()
        QTest.qWait(50)

    def _make_specs_no_icons(self):
        """Specs without icons (safe for default QTA path)."""
        return [
            ModeButtonSpec(mode=SimpleMode(0, "One"), label="One"),
            ModeButtonSpec(mode=SimpleMode(1, "Two"), label="Two"),
            ModeButtonSpec(mode=SimpleMode(2, "Three"), label="Three"),
        ]

    def test_construction_basic(self):
        """Widget builds with specs and no icons."""
        specs = self._make_specs_no_icons()
        self.widget = ModeButtonGroup(specs)
        self.assertIsNotNone(self.widget)
        self.assertEqual(len(self.widget.buttons), 3)
        for spec in specs:
            self.assertIn(spec.mode, self.widget.buttons)
            btn = self.widget.buttons[spec.mode]
            self.assertEqual(btn.text(), spec.label)
            self.assertTrue(btn.isCheckable())

    def test_buttons_property_is_copy(self):
        """buttons property returns a dict copy (mode -> button)."""
        specs = self._make_specs_no_icons()
        self.widget = ModeButtonGroup(specs)
        b1 = self.widget.buttons
        b2 = self.widget.buttons
        self.assertEqual(b1, b2)
        self.assertIsNot(b1, b2)

    def test_set_mode_programmatic(self):
        """set_mode selects the correct button and deselects others."""
        specs = self._make_specs_no_icons()
        self.widget = ModeButtonGroup(specs)
        modes = [s.mode for s in specs]
        self.widget.set_mode(modes[1], send_midi=False)
        self.assertFalse(self.widget.buttons[modes[0]].isChecked())
        self.assertTrue(self.widget.buttons[modes[1]].isChecked())
        self.assertFalse(self.widget.buttons[modes[2]].isChecked())

    def test_set_mode_emits_callback(self):
        """set_mode calls on_mode_changed with the selected mode (may run twice due to QButtonGroup.idToggled)."""
        specs = self._make_specs_no_icons()
        received = []
        self.widget = ModeButtonGroup(
            specs,
            on_mode_changed=lambda m: received.append(m),
        )
        modes = [s.mode for s in specs]
        self.widget.set_mode(modes[2], send_midi=False)
        self.assertGreaterEqual(len(received), 1)
        self.assertEqual(received[-1], modes[2])

    def test_set_mode_emits_signal(self):
        """set_mode emits mode_changed signal with the selected mode (may run twice due to QButtonGroup.idToggled)."""
        specs = self._make_specs_no_icons()
        received = []
        self.widget = ModeButtonGroup(specs)
        self.widget.mode_changed.connect(lambda m: received.append(m))
        modes = [s.mode for s in specs]
        self.widget.set_mode(modes[0], send_midi=False)
        self.assertGreaterEqual(len(received), 1)
        self.assertEqual(received[-1], modes[0])

    def test_set_mode_send_midi_calls_callback(self):
        """set_mode with send_midi=True calls send_midi_parameter (may be called twice due to QButtonGroup.idToggled)."""
        specs = self._make_specs_no_icons()
        send_midi = Mock()
        midi_param = Mock()
        self.widget = ModeButtonGroup(
            specs,
            send_midi_parameter=send_midi,
            midi_param=midi_param,
        )
        modes = [s.mode for s in specs]
        self.widget.set_mode(modes[1], send_midi=True)
        self.assertGreaterEqual(send_midi.call_count, 1)
        send_midi.assert_any_call(midi_param, 1)

    def test_set_mode_without_midi_param_does_not_send(self):
        """When midi_param is None, set_mode never calls send_midi_parameter even when send_midi=True."""
        specs = self._make_specs_no_icons()
        send_midi = Mock()
        self.widget = ModeButtonGroup(
            specs,
            send_midi_parameter=send_midi,
            midi_param=None,  # no param -> no send
        )
        self.widget.set_mode(specs[0].mode, send_midi=True)
        send_midi.assert_not_called()

    def test_set_mode_unknown_mode_no_op(self):
        """set_mode with mode not in specs does nothing."""
        specs = self._make_specs_no_icons()
        self.widget = ModeButtonGroup(specs)
        on_changed = Mock()
        self.widget.mode_changed.connect(on_changed)
        self.widget.set_mode(999, send_midi=False)  # not a valid mode
        on_changed.assert_not_called()

    def test_icon_factory_sets_icon(self):
        """When icon_factory is provided and returns QPixmap, button gets icon."""
        pix = QPixmap(16, 16)
        pix.fill(0xFF00FF00)
        specs = [
            ModeButtonSpec(mode=0, label="A", icon_name="fake"),
        ]
        self.widget = ModeButtonGroup(
            specs,
            icon_factory=lambda _: pix,
        )
        btn = self.widget.buttons[0]
        self.assertFalse(btn.icon().isNull())

    def test_icon_factory_returning_none_no_icon(self):
        """When icon_factory returns None, button has no icon."""
        specs = [
            ModeButtonSpec(mode=0, label="A", icon_name="x"),
        ]
        self.widget = ModeButtonGroup(
            specs,
            icon_factory=lambda _: None,
        )
        btn = self.widget.buttons[0]
        self.assertTrue(btn.icon().isNull())

    def test_icon_factory_returning_qicon(self):
        """icon_factory can return QIcon directly."""
        icon = QIcon(QPixmap(8, 8))
        specs = [
            ModeButtonSpec(mode=0, label="A", icon_name="x"),
        ]
        self.widget = ModeButtonGroup(
            specs,
            icon_factory=lambda _: icon,
        )
        btn = self.widget.buttons[0]
        self.assertFalse(btn.icon().isNull())

    def test_tooltips_set_on_buttons(self):
        """Specs with tooltip set button toolTip."""
        specs = [
            ModeButtonSpec(mode=0, label="A", tooltip="Tip A"),
            ModeButtonSpec(mode=1, label="B"),
        ]
        self.widget = ModeButtonGroup(specs)
        self.assertEqual(self.widget.buttons[0].toolTip(), "Tip A")
        self.assertEqual(self.widget.buttons[1].toolTip(), "")

    def test_click_button_triggers_callback(self):
        """Clicking a button triggers on_mode_changed and mode_changed."""
        specs = self._make_specs_no_icons()
        callback_received = []
        signal_received = []
        self.widget = ModeButtonGroup(
            specs,
            on_mode_changed=lambda m: callback_received.append(m),
        )
        self.widget.mode_changed.connect(lambda m: signal_received.append(m))
        self.widget.show()
        QTest.qWait(100)
        # Click second button (index 1)
        modes = [s.mode for s in specs]
        btn = self.widget.buttons[modes[1]]
        QTest.mouseClick(btn, Qt.MouseButton.LeftButton)
        QTest.qWait(50)
        self.assertEqual(len(callback_received), 1)
        self.assertEqual(callback_received[0], modes[1])
        self.assertEqual(len(signal_received), 1)
        self.assertEqual(signal_received[0], modes[1])

    def test_analog_construction(self):
        """Widget builds with analog=True (styling applied)."""
        specs = self._make_specs_no_icons()
        self.widget = ModeButtonGroup(specs, analog=True)
        self.assertIsNotNone(self.widget)
        self.assertEqual(len(self.widget.buttons), 3)

    def test_single_spec(self):
        """Widget works with a single button spec."""
        specs = [ModeButtonSpec(mode=0, label="Only")]
        self.widget = ModeButtonGroup(specs)
        self.assertEqual(len(self.widget.buttons), 1)
        self.widget.set_mode(0, send_midi=False)
        self.assertTrue(self.widget.buttons[0].isChecked())


if __name__ == "__main__":
    unittest.main()
