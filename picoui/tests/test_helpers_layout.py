#!/usr/bin/env python3
"""
Unit tests for picoui.helpers.layout.

Verifies:
- create_layout returns correct layout type with/without parent
- create_layout_with_widgets adds widgets and stretches as expected
- create_row_with_widgets, create_left_aligned_row
- create_vertical_layout, create_form_layout
- create_header_row, create_layout_with_inner_layouts
"""

import sys
from pathlib import Path

# Ensure project root (and picoui) are on path when running from repo root or picoui/tests
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PySide6.QtCore import QMargins
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

import unittest

from picoui.helpers.layout import (
    create_form_layout,
    create_header_row,
    create_layout,
    create_layout_with_inner_layouts,
    create_layout_with_widgets,
    create_left_aligned_row,
    create_row_with_widgets,
    create_vertical_layout,
)


def get_qapp():
    """Get or create QApplication for widget/layout tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestCreateLayout(unittest.TestCase):
    """Tests for create_layout."""

    def setUp(self):
        get_qapp()

    def test_vertical_without_parent(self):
        layout = create_layout(vertical=True)
        self.assertIsInstance(layout, QVBoxLayout)
        self.assertEqual(layout.count(), 0)

    def test_horizontal_without_parent(self):
        layout = create_layout(vertical=False)
        from PySide6.QtWidgets import QHBoxLayout

        self.assertIsInstance(layout, QHBoxLayout)
        self.assertEqual(layout.count(), 0)

    def test_vertical_with_parent(self):
        parent = QWidget()
        layout = create_layout(vertical=True, parent=parent)
        self.assertIsInstance(layout, QVBoxLayout)
        self.assertIs(layout.parent(), parent)
        self.assertIs(parent.layout(), layout)


class TestCreateLayoutWithWidgets(unittest.TestCase):
    """Tests for create_layout_with_widgets."""

    def setUp(self):
        get_qapp()

    def test_empty_list_default_stretches(self):
        layout = create_layout_with_widgets([])
        # top_stretch + bottom_stretch = 2 stretch items
        self.assertEqual(layout.count(), 2)

    def test_empty_list_no_stretches(self):
        layout = create_layout_with_widgets(
            [], start_stretch=False, end_stretch=False
        )
        self.assertEqual(layout.count(), 0)

    def test_one_widget_default_stretches(self):
        w = QLabel("x")
        layout = create_layout_with_widgets([w])
        self.assertEqual(layout.count(), 3)  # stretch, widget, stretch
        self.assertEqual(layout.indexOf(w), 1)

    def test_spacing_and_margins(self):
        w = QLabel("a")
        layout = create_layout_with_widgets(
            [w],
            spacing=10,
            margins=QMargins(1, 2, 3, 4),
            start_stretch=False,
            end_stretch=False,
        )
        self.assertEqual(layout.spacing(), 10)
        left, top, right, bottom = layout.getContentsMargins()
        self.assertEqual((left, top, right, bottom), (1, 2, 3, 4))

    def test_vertical_layout(self):
        w1, w2 = QLabel("1"), QLabel("2")
        layout = create_layout_with_widgets(
            [w1, w2], vertical=True, start_stretch=False, end_stretch=False
        )
        self.assertIsInstance(layout, QVBoxLayout)
        self.assertEqual(layout.indexOf(w1), 0)
        self.assertEqual(layout.indexOf(w2), 1)


class TestCreateRowWithWidgets(unittest.TestCase):
    """Tests for create_row_with_widgets."""

    def setUp(self):
        get_qapp()

    def test_empty(self):
        row = create_row_with_widgets([])
        self.assertEqual(row.count(), 0)
        self.assertEqual(row.spacing(), 4)

    def test_custom_spacing(self):
        row = create_row_with_widgets([], spacing=8)
        self.assertEqual(row.spacing(), 8)

    def test_two_widgets(self):
        a, b = QLabel("A"), QLabel("B")
        row = create_row_with_widgets([a, b])
        self.assertEqual(row.count(), 2)
        self.assertEqual(row.indexOf(a), 0)
        self.assertEqual(row.indexOf(b), 1)


class TestCreateLeftAlignedRow(unittest.TestCase):
    """Tests for create_left_aligned_row."""

    def setUp(self):
        get_qapp()

    def test_one_widget_has_stretch_at_end(self):
        w = QLabel("x")
        row = create_left_aligned_row([w])
        self.assertEqual(row.count(), 2)  # widget + stretch
        self.assertEqual(row.indexOf(w), 0)


class TestCreateVerticalLayout(unittest.TestCase):
    """Tests for create_vertical_layout."""

    def setUp(self):
        get_qapp()

    def test_default(self):
        layout = create_vertical_layout()
        self.assertIsInstance(layout, QVBoxLayout)
        self.assertEqual(layout.count(), 0)

    def test_with_spacing_and_margins(self):
        layout = create_vertical_layout(spacing=6, margins=QMargins(5, 5, 5, 5))
        self.assertEqual(layout.spacing(), 6)
        left, top, right, bottom = layout.getContentsMargins()
        self.assertEqual((left, top, right, bottom), (5, 5, 5, 5))


class TestCreateFormLayout(unittest.TestCase):
    """Tests for create_form_layout."""

    def setUp(self):
        get_qapp()

    def test_without_parent(self):
        layout = create_form_layout()
        self.assertEqual(layout.spacing(), 4)
        left, top, right, bottom = layout.getContentsMargins()
        self.assertEqual((left, top, right, bottom), (0, 0, 0, 0))

    def test_with_parent(self):
        parent = QWidget()
        layout = create_form_layout(parent=parent)
        self.assertIs(layout.parent(), parent)


class TestCreateHeaderRow(unittest.TestCase):
    """Tests for create_header_row."""

    def setUp(self):
        get_qapp()

    def test_returns_layout_and_label(self):
        row, label = create_header_row("Title", show_label=True)
        self.assertEqual(row.count(), 1)
        self.assertEqual(label.text(), "Title")
        self.assertTrue(label.isVisible())

    def test_hidden_label(self):
        row, label = create_header_row("Hidden", show_label=False)
        self.assertFalse(label.isVisible())


class TestCreateLayoutWithInnerLayouts(unittest.TestCase):
    """Tests for create_layout_with_inner_layouts."""

    def setUp(self):
        get_qapp()

    def test_empty_inner_list(self):
        layout = create_layout_with_inner_layouts([])
        self.assertEqual(layout.count(), 1)  # only the bottom stretch

    def test_one_inner_layout(self):
        inner = create_layout(vertical=False)
        layout = create_layout_with_inner_layouts([inner])
        self.assertEqual(layout.count(), 2)  # inner + stretch
        self.assertEqual(layout.indexOf(inner), 0)


if __name__ == "__main__":
    unittest.main()
