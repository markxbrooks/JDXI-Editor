#!/usr/bin/env python3
"""
Unit tests for picoui.helpers.groups.

Verifies:
- build_group with list of widgets, single widget, layout, and None
- build_group raises TypeError for invalid input
- group_with_layout with/without label and layout
- group_from_definition and optional set_attr
"""

import sys
from pathlib import Path

# Ensure project root (and picoui) are on path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (
    QApplication,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

import unittest

from picoui.helpers.groups import build_group, group_from_definition, group_with_layout
from picoui.helpers.layout import create_layout, create_layout_with_items


def get_qapp():
    """Get or create QApplication for widget tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class SimpleDefinition:
    """Minimal object satisfying GroupDefinition protocol."""

    def __init__(self, label: str, attr_name: str):
        self.label = label
        self.attr_name = attr_name


class TestBuildGroup(unittest.TestCase):
    """Tests for build_group."""

    def setUp(self):
        get_qapp()

    def test_with_list_of_widgets(self):
        w1, w2 = QLabel("a"), QLabel("b")
        group = build_group("Section", [w1, w2])
        self.assertIsInstance(group, QGroupBox)
        self.assertEqual(group.title(), "Section")
        layout = group.layout()
        self.assertIsNotNone(layout)
        # layout has stretch + w1 + w2 + stretch
        self.assertEqual(layout.count(), 4)
        self.assertEqual(layout.indexOf(w1), 1)
        self.assertEqual(layout.indexOf(w2), 2)

    def test_with_single_widget(self):
        w = QLabel("only")
        group = build_group("One", w)
        self.assertEqual(group.title(), "One")
        layout = group.layout()
        self.assertEqual(layout.count(), 3)  # stretch, widget, stretch
        self.assertEqual(layout.indexOf(w), 1)

    def test_with_layout(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel("x"))
        group = build_group("With Layout", layout)
        self.assertEqual(group.title(), "With Layout")
        self.assertIs(group.layout(), layout)
        self.assertEqual(layout.count(), 1)

    def test_with_none(self):
        group = build_group("Empty", None)
        self.assertEqual(group.title(), "Empty")
        layout = group.layout()
        self.assertIsInstance(layout, QVBoxLayout)
        self.assertEqual(layout.count(), 0)

    def test_invalid_type_raises(self):
        with self.assertRaises(TypeError) as ctx:
            build_group("Bad", "not a widget or layout")
        self.assertIn("layout_or_widget", str(ctx.exception))
        self.assertIn("list", str(ctx.exception))


class TestGroupWithLayout(unittest.TestCase):
    """Tests for group_with_layout."""

    def setUp(self):
        get_qapp()

    def test_no_label_no_layout_creates_vertical(self):
        group, layout = group_with_layout()
        self.assertIsInstance(group, QGroupBox)
        self.assertEqual(group.title(), "")
        self.assertIsInstance(layout, QVBoxLayout)
        self.assertIs(group.layout(), layout)

    def test_with_label_and_vertical(self):
        group, layout = group_with_layout(label="Box", vertical=True)
        self.assertEqual(group.title(), "Box")
        self.assertIsInstance(layout, QVBoxLayout)

    def test_with_existing_layout(self):
        existing = QGridLayout()
        group, layout = group_with_layout(label="Grid", layout=existing)
        self.assertEqual(group.title(), "Grid")
        self.assertIs(layout, existing)
        self.assertIs(group.layout(), existing)

    def test_with_stylesheet(self):
        group, layout = group_with_layout(
            label="Styled", style_sheet="QGroupBox { font-weight: bold; }"
        )
        self.assertIn("font-weight", group.styleSheet())


class TestGroupFromDefinition(unittest.TestCase):
    """Tests for group_from_definition."""

    def setUp(self):
        get_qapp()

    def test_creates_group_with_definition_label(self):
        key = SimpleDefinition(label="From Def", attr_name="my_group")
        w = QLabel("w")
        group = group_from_definition(key, [w])
        self.assertIsInstance(group, QGroupBox)
        self.assertEqual(group.title(), "From Def")
        self.assertEqual(group.layout().count(), 3)

    def test_set_attr(self):
        key = SimpleDefinition(label="Attr", attr_name="test_attr")
        container = type("Container", (), {})()
        group = group_from_definition(key, None, set_attr=container)
        self.assertIs(getattr(container, "test_attr"), group)

    def test_set_attr_custom_attr_name(self):
        key = SimpleDefinition(label="X", attr_name="default_name")
        container = type("C", (), {})()
        group = group_from_definition(
            key, None, set_attr=container, attr_name="custom_name"
        )
        self.assertFalse(hasattr(container, "default_name"))
        self.assertIs(getattr(container, "custom_name"), group)


if __name__ == "__main__":
    unittest.main()
