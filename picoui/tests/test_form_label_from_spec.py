#!/usr/bin/env python3
"""Verify PicoUI factories attach ``_form_label`` when ``spec.label`` is set (Phase E / map manager)."""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import unittest

from picoui.specs.widgets import ComboBoxSpec, DoubleSpinBoxSpec, SpinBoxSpec
from PySide6.QtWidgets import QApplication

_FORM_LABEL_FACTORIES_OK = False
try:
    import qtawesome  # noqa: F401 — picoui.widget.helper dependency
    from picoui.widget.helper import (create_combo_box,
                                      create_double_spinbox_from_spec,
                                      create_spinbox_from_spec)
    _FORM_LABEL_FACTORIES_OK = True
except ImportError:
    create_combo_box = None  # type: ignore[assignment, misc]
    create_double_spinbox_from_spec = None  # type: ignore[assignment, misc]
    create_spinbox_from_spec = None  # type: ignore[assignment, misc]


def get_qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@unittest.skipUnless(
    _FORM_LABEL_FACTORIES_OK,
    "requires qtawesome and picoui.widget.helper dependencies",
)
class TestFormLabelFromSpec(unittest.TestCase):
    def setUp(self):
        get_qapp()

    def test_double_spinbox_sets_form_label(self):
        spec = DoubleSpinBoxSpec(
            label="Sigma:",
            min_val=0.1,
            max_val=5.0,
            value=1.0,
            step=0.1,
        )
        w = create_double_spinbox_from_spec(spec)
        self.assertEqual(getattr(w, "_form_label", None), "Sigma:")

    def test_double_spinbox_empty_label_omits_attribute_or_empty(self):
        spec = DoubleSpinBoxSpec(label="", min_val=0.0, max_val=1.0, value=0.5)
        w = create_double_spinbox_from_spec(spec)
        self.assertFalse(getattr(w, "_form_label", ""))

    def test_spinbox_sets_form_label(self):
        spec = SpinBoxSpec(label="Frames:", min_val=1, max_val=100, value=10)
        w = create_spinbox_from_spec(spec)
        self.assertEqual(getattr(w, "_form_label", None), "Frames:")

    def test_combo_box_spec_sets_form_label(self):
        spec = ComboBoxSpec(
            label="Mode:",
            items=["a", "b"],
        )
        w = create_combo_box(spec=spec)
        self.assertEqual(getattr(w, "_form_label", None), "Mode:")

    def test_combo_box_spec_empty_label(self):
        spec = ComboBoxSpec(label="", items=["x"])
        w = create_combo_box(spec=spec)
        self.assertFalse(getattr(w, "_form_label", ""))


if __name__ == "__main__":
    unittest.main()
