#!/usr/bin/env python3
"""
Unit tests for SearchableFilterableComboBox widget.

This test suite verifies:
1. Basic widget initialization
2. Search filtering functionality
3. Category filtering functionality
4. Combined search and category filtering
5. Value mapping correctness (critical for MIDI commands)
6. setValue and value() methods
7. Filter clearing
8. Signal emissions
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from PySide6.QtTest import QTest

from jdxi_editor.ui.widgets.combo_box.searchable_filterable import (
    SearchableFilterableComboBox,
)

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


class TestSearchableFilterableComboBox(unittest.TestCase):
    """Test suite for SearchableFilterableComboBox widget."""

    def setUp(self):
        """Set up test fixtures."""
        get_qapp()
        
        # Sample data for testing
        self.test_options = [
            "Apple",
            "Banana",
            "Cherry",
            "Date",
            "Elderberry",
            "Fig",
            "Grape",
            "Honeydew",
        ]
        
        self.test_values = list(range(len(self.test_options)))
        
        self.test_categories = ["Fruit", "Berry", "Tropical"]
        
        # Category filter function
        def category_filter(option: str, category: str) -> bool:
            """Simple category filter for testing."""
            if not category:
                return True
            category_map = {
                "Fruit": ["Apple", "Banana", "Cherry", "Date", "Fig", "Grape"],
                "Berry": ["Cherry", "Elderberry", "Grape"],
                "Tropical": ["Banana", "Date", "Honeydew"],
            }
            terms = category_map.get(category, [])
            return any(term.lower() in option.lower() for term in terms)
        
        self.category_filter_func = category_filter

    def test_basic_initialization(self):
        """Test basic widget initialization."""
        widget = SearchableFilterableComboBox(
            label="Test Label",
            options=self.test_options,
            values=self.test_values,
        )
        
        self.assertIsNotNone(widget)
        self.assertEqual(widget.label_widget.text(), "Test Label")
        self.assertEqual(widget.combo_box.count(), len(self.test_options))
        
        # Check that all options are present
        for i, option in enumerate(self.test_options):
            self.assertEqual(widget.combo_box.itemText(i), option)

    def test_initialization_with_categories(self):
        """Test initialization with categories."""
        widget = SearchableFilterableComboBox(
            label="Test Label",
            options=self.test_options,
            values=self.test_values,
            categories=self.test_categories,
            category_filter_func=self.category_filter_func,
        )
        
        self.assertIsNotNone(widget)
        self.assertIsNotNone(widget.category_combo)
        self.assertEqual(widget.category_combo.count(), len(self.test_categories) + 1)  # +1 for "All Categories"
        self.assertEqual(widget.category_combo.itemText(0), "All Categories")

    def test_initialization_without_search(self):
        """Test initialization without search box."""
        widget = SearchableFilterableComboBox(
            label="Test Label",
            options=self.test_options,
            values=self.test_values,
            show_search=False,
        )
        
        self.assertIsNone(widget.search_box)

    def test_initialization_without_category(self):
        """Test initialization without category selector."""
        widget = SearchableFilterableComboBox(
            label="Test Label",
            options=self.test_options,
            values=self.test_values,
            show_category=False,
        )
        
        self.assertIsNone(widget.category_combo)

    def test_search_filtering(self):
        """Test search filtering functionality."""
        widget = SearchableFilterableComboBox(
            label="Test Label",
            options=self.test_options,
            values=self.test_values,
            show_search=True,
        )
        
        # Initial state: all items should be visible
        self.assertEqual(widget.combo_box.count(), len(self.test_options))
        
        # Filter by "a" - should match Apple, Banana, Date, Grape, etc.
        widget.search_box.setText("a")
        QTest.qWait(100)  # Wait for signal processing
        
        # Should have filtered results
        filtered_count = widget.combo_box.count()
        self.assertGreater(filtered_count, 0)
        self.assertLess(filtered_count, len(self.test_options))
        
        # Verify all filtered items contain "a"
        for i in range(filtered_count):
            item_text = widget.combo_box.itemText(i)
            self.assertIn("a", item_text.lower())

    def test_category_filtering(self):
        """Test category filtering functionality."""
        widget = SearchableFilterableComboBox(
            label="Test Label",
            options=self.test_options,
            values=self.test_values,
            categories=self.test_categories,
            category_filter_func=self.category_filter_func,
        )
        
        # Initial state: all items should be visible
        self.assertEqual(widget.combo_box.count(), len(self.test_options))
        
        # Select "Berry" category
        widget.category_combo.setCurrentText("Berry")
        QTest.qWait(100)  # Wait for signal processing
        
        # Should have filtered results (Cherry, Elderberry, Grape)
        filtered_count = widget.combo_box.count()
        self.assertGreater(filtered_count, 0)
        self.assertLess(filtered_count, len(self.test_options))
        
        # Verify all filtered items are berries
        berry_items = ["Cherry", "Elderberry", "Grape"]
        for i in range(filtered_count):
            item_text = widget.combo_box.itemText(i)
            self.assertIn(item_text, berry_items)

    def test_combined_search_and_category_filtering(self):
        """Test combined search and category filtering."""
        widget = SearchableFilterableComboBox(
            label="Test Label",
            options=self.test_options,
            values=self.test_values,
            categories=self.test_categories,
            category_filter_func=self.category_filter_func,
        )
        
        # Set category to "Berry"
        widget.category_combo.setCurrentText("Berry")
        QTest.qWait(100)
        
        # Set search to "e" (should match Elderberry, Grape from berries)
        widget.search_box.setText("e")
        QTest.qWait(100)
        
        # Should have filtered results
        filtered_count = widget.combo_box.count()
        self.assertGreater(filtered_count, 0)
        
        # Verify all filtered items are berries containing "e"
        for i in range(filtered_count):
            item_text = widget.combo_box.itemText(i)
            self.assertIn("e", item_text.lower())
            self.assertIn(item_text, ["Cherry", "Elderberry", "Grape"])

    def test_value_mapping_correctness(self):
        """Test that value mapping is correct when filtering (critical for MIDI)."""
        widget = SearchableFilterableComboBox(
            label="Test Label",
            options=self.test_options,
            values=self.test_values,
        )
        
        # Filter to only items containing "a"
        widget.search_box.setText("a")
        QTest.qWait(100)
        
        # Get the filtered items and their original values
        filtered_count = widget.combo_box.count()
        self.assertGreater(filtered_count, 0)
        
        # Test that valueChanged emits correct original values
        emitted_values = []
        
        def capture_value(value: int):
            emitted_values.append(value)
        
        widget.valueChanged.connect(capture_value)
        
        # Select each filtered item and verify the emitted value
        for i in range(filtered_count):
            widget.combo_box.setCurrentIndex(i)
            QTest.qWait(50)
            
            # Get the displayed text
            displayed_text = widget.combo_box.itemText(i)
            
            # Find its original index
            original_index = self.test_options.index(displayed_text)
            
            # Verify the emitted value matches the original index
            if emitted_values:
                self.assertEqual(emitted_values[-1], original_index)
                self.assertEqual(emitted_values[-1], self.test_values[original_index])

    def test_setValue(self):
        """Test setValue method."""
        widget = SearchableFilterableComboBox(
            label="Test Label",
            options=self.test_options,
            values=self.test_values,
        )
        
        # Set value to 2 (Cherry)
        widget.setValue(2)
        QTest.qWait(50)
        
        # Verify combo box is set to Cherry
        current_text = widget.combo_box.currentText()
        self.assertEqual(current_text, "Cherry")
        
        # Verify value() returns correct value
        self.assertEqual(widget.value(), 2)

    def test_setValue_with_filtering(self):
        """Test setValue when list is filtered."""
        widget = SearchableFilterableComboBox(
            label="Test Label",
            options=self.test_options,
            values=self.test_values,
        )
        
        # Filter to only items containing "a"
        widget.search_box.setText("a")
        QTest.qWait(100)
        
        # Try to set value to 2 (Cherry) - should not be in filtered list
        widget.setValue(2)
        QTest.qWait(50)
        
        # Cherry doesn't contain "a", so it shouldn't be in filtered list
        # The widget should handle this gracefully
        # (current implementation logs a warning but doesn't crash)

    def test_setValue_with_filtering_matching_item(self):
        """Test setValue when list is filtered and item matches filter."""
        widget = SearchableFilterableComboBox(
            label="Test Label",
            options=self.test_options,
            values=self.test_values,
        )
        
        # Filter to only items containing "a"
        widget.search_box.setText("a")
        QTest.qWait(100)
        
        # Set value to 0 (Apple) - should be in filtered list
        widget.setValue(0)
        QTest.qWait(50)
        
        # Verify combo box is set to Apple
        current_text = widget.combo_box.currentText()
        self.assertEqual(current_text, "Apple")
        
        # Verify value() returns correct value
        self.assertEqual(widget.value(), 0)

    def test_value_method(self):
        """Test value() method returns correct original value."""
        widget = SearchableFilterableComboBox(
            label="Test Label",
            options=self.test_options,
            values=self.test_values,
        )
        
        # Select item at index 3 (Date)
        widget.combo_box.setCurrentIndex(3)
        QTest.qWait(50)
        
        # Verify value() returns original value (3)
        self.assertEqual(widget.value(), 3)

    def test_value_method_with_filtering(self):
        """Test value() method when list is filtered."""
        widget = SearchableFilterableComboBox(
            label="Test Label",
            options=self.test_options,
            values=self.test_values,
        )
        
        # Filter to only items containing "a"
        widget.search_box.setText("a")
        QTest.qWait(100)
        
        # Find Apple in filtered list (should be first)
        filtered_count = widget.combo_box.count()
        apple_index = None
        for i in range(filtered_count):
            if widget.combo_box.itemText(i) == "Apple":
                apple_index = i
                break
        
        if apple_index is not None:
            widget.combo_box.setCurrentIndex(apple_index)
            QTest.qWait(50)
            
            # Verify value() returns original value (0 for Apple)
            self.assertEqual(widget.value(), 0)

    def test_clearFilters(self):
        """Test clearFilters method."""
        widget = SearchableFilterableComboBox(
            label="Test Label",
            options=self.test_options,
            values=self.test_values,
            categories=self.test_categories,
            category_filter_func=self.category_filter_func,
        )
        
        # Apply filters
        widget.search_box.setText("a")
        widget.category_combo.setCurrentText("Berry")
        QTest.qWait(100)
        
        # Verify filters are applied
        self.assertLess(widget.combo_box.count(), len(self.test_options))
        
        # Clear filters
        widget.clearFilters()
        QTest.qWait(100)
        
        # Verify all items are visible again
        self.assertEqual(widget.combo_box.count(), len(self.test_options))
        self.assertEqual(widget.search_box.text(), "")
        self.assertEqual(widget.category_combo.currentText(), "All Categories")

    def test_valueChanged_signal(self):
        """Test that valueChanged signal emits correct values."""
        widget = SearchableFilterableComboBox(
            label="Test Label",
            options=self.test_options,
            values=self.test_values,
        )
        
        # Wait for initialization to complete
        QTest.qWait(100)
        
        emitted_values = []
        
        def capture_value(value: int):
            emitted_values.append(value)
        
        widget.valueChanged.connect(capture_value)
        
        # Get the current index - after _populate_combo(), it should be -1 (no selection)
        # or 0 (first item). Let's ensure we change it.
        current_idx = widget.combo_box.currentIndex()
        
        # If already at 0, change to a different index first
        if current_idx == 0:
            widget.combo_box.setCurrentIndex(len(self.test_options) - 1)
            QTest.qWait(100)
        
        # Now set to index 0 (Apple, value 0) - this should trigger the signal
        widget.combo_box.setCurrentIndex(0)
        QTest.qWait(150)  # Wait for signal processing
        self.assertGreater(len(emitted_values), 0, "Signal should have been emitted")
        self.assertEqual(emitted_values[-1], 0)
        
        # Change to index 3 (Date, value 3)
        widget.combo_box.setCurrentIndex(3)
        QTest.qWait(150)
        self.assertGreater(len(emitted_values), 1, "Second signal should have been emitted")
        self.assertEqual(emitted_values[-1], 3)
        
        # Change to index 5 (Fig, value 5)
        widget.combo_box.setCurrentIndex(5)
        QTest.qWait(150)
        self.assertGreater(len(emitted_values), 2, "Third signal should have been emitted")
        self.assertEqual(emitted_values[-1], 5)

    def test_valueChanged_signal_with_filtering(self):
        """Test that valueChanged signal emits correct values when filtered."""
        widget = SearchableFilterableComboBox(
            label="Test Label",
            options=self.test_options,
            values=self.test_values,
        )
        
        # Wait for initialization
        QTest.qWait(100)
        
        # Filter to items containing "a"
        widget.search_box.setText("a")
        QTest.qWait(150)
        
        emitted_values = []
        
        def capture_value(value: int):
            emitted_values.append(value)
        
        widget.valueChanged.connect(capture_value)
        
        # Find Apple in filtered list
        filtered_count = widget.combo_box.count()
        apple_index = None
        for i in range(filtered_count):
            if widget.combo_box.itemText(i) == "Apple":
                apple_index = i
                break
        
        self.assertIsNotNone(apple_index, "Apple should be in filtered results")
        
        # Get current index - if already at apple_index, change it first
        current_idx = widget.combo_box.currentIndex()
        if current_idx == apple_index and filtered_count > 1:
            # Change to a different index first
            other_idx = 1 if apple_index == 0 else 0
            widget.combo_box.setCurrentIndex(other_idx)
            QTest.qWait(100)
        
        # Now set to apple_index - this should trigger the signal
        widget.combo_box.setCurrentIndex(apple_index)
        QTest.qWait(150)  # Wait for signal processing
        
        # Verify signal was emitted
        self.assertGreater(len(emitted_values), 0, "Signal should have been emitted")
        # Verify emitted value is 0 (Apple's original index), not apple_index
        self.assertEqual(emitted_values[-1], 0)

    def test_setLabelVisible(self):
        """Test setLabelVisible method."""
        widget = SearchableFilterableComboBox(
            label="Test Label",
            options=self.test_options,
            values=self.test_values,
        )
        
        # Show the widget to ensure visibility is properly set
        widget.show()
        QTest.qWait(50)
        
        # Label should be visible by default when show_label=True
        # Note: isVisible() checks if widget is visible in its parent hierarchy
        # Since we're showing the widget, the label should be visible
        self.assertTrue(widget.label_widget.isVisible())
        
        # Hide label
        widget.setLabelVisible(False)
        QTest.qWait(50)
        self.assertFalse(widget.label_widget.isVisible())
        
        # Show label
        widget.setLabelVisible(True)
        QTest.qWait(50)
        self.assertTrue(widget.label_widget.isVisible())

    def test_setEnabled(self):
        """Test setEnabled method."""
        widget = SearchableFilterableComboBox(
            label="Test Label",
            options=self.test_options,
            values=self.test_values,
        )
        
        # Widget should be enabled by default
        self.assertTrue(widget.isEnabled())
        self.assertTrue(widget.combo_box.isEnabled())
        
        # Disable widget
        widget.setEnabled(False)
        self.assertFalse(widget.isEnabled())
        self.assertFalse(widget.combo_box.isEnabled())
        
        # Enable widget
        widget.setEnabled(True)
        self.assertTrue(widget.isEnabled())
        self.assertTrue(widget.combo_box.isEnabled())

    def test_setLabel(self):
        """Test setLabel method."""
        widget = SearchableFilterableComboBox(
            label="Test Label",
            options=self.test_options,
            values=self.test_values,
        )
        
        self.assertEqual(widget.label_widget.text(), "Test Label")
        
        widget.setLabel("New Label")
        self.assertEqual(widget.label_widget.text(), "New Label")

    def test_default_category_filter(self):
        """Test default category filter function."""
        # Use a category that actually appears in the option names
        widget = SearchableFilterableComboBox(
            label="Test Label",
            options=self.test_options,
            values=self.test_values,
            categories=["Apple"],  # "Apple" appears in option "Apple"
        )
        
        # Default filter uses substring matching
        widget.category_combo.setCurrentText("Apple")
        QTest.qWait(100)
        
        # Should filter items containing "Apple" (case-insensitive)
        filtered_count = widget.combo_box.count()
        self.assertGreater(filtered_count, 0)
        
        # Verify Apple is in the filtered results
        self.assertEqual(widget.combo_box.itemText(0), "Apple")

    def test_empty_options(self):
        """Test widget with empty options list."""
        widget = SearchableFilterableComboBox(
            label="Test Label",
            options=[],
            values=[],
        )
        
        self.assertEqual(widget.combo_box.count(), 0)

    def test_single_option(self):
        """Test widget with single option."""
        widget = SearchableFilterableComboBox(
            label="Test Label",
            options=["Apple"],
            values=[0],
        )
        
        self.assertEqual(widget.combo_box.count(), 1)
        self.assertEqual(widget.combo_box.itemText(0), "Apple")

    def test_no_values_provided(self):
        """Test widget when values list is None (should use indices)."""
        widget = SearchableFilterableComboBox(
            label="Test Label",
            options=self.test_options,
            values=None,
        )
        
        # Should use indices as values
        widget.combo_box.setCurrentIndex(2)
        QTest.qWait(50)
        
        # value() should return the index
        self.assertEqual(widget.value(), 2)


if __name__ == '__main__':
    unittest.main()
