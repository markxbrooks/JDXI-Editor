"""
Searchable Filterable ComboBox Widget

This module provides a reusable combo box widget that supports:
1. Searchable filtering by text
2. Category/group filtering
3. Bank filtering (optional)
4. Unfilterable mode (show all items)
5. Proper MIDI value mapping when filtered

The widget maintains a mapping between filtered combo box indices and original values,
ensuring MIDI commands are sent correctly even when the list is filtered.

Classes:
--------
- SearchableFilterableComboBox: A combo box with search, category, and bank filtering capabilities.
"""

import re
from typing import Any, Callable, List, Optional

from decologr import Decologr as log
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSizePolicy,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from picoui.widget.helper import (
    create_combo_row,
    create_form_layout,
    create_header_row,
    create_line_edit,
    create_row_with_widgets,
)


class SearchableFilterableComboBox(QWidget):
    """
    A reusable combo box widget with search, category, and bank filtering.

    Maintains proper value mapping when filtered, ensuring MIDI commands
    are sent correctly regardless of filter state.

    Features:
    - Text search filtering
    - Category/group filtering
    - Bank filtering (optional)
    - Unfilterable mode (show all items)
    - Proper value mapping for MIDI commands
    """

    valueChanged = Signal(
        int
    )  # --- Emitted when selected value changes (original value, not filtered index)

    def __init__(
        self,
        label: str,
        options: List[str],
        values: Optional[List[int]] = None,
        categories: Optional[List[str]] = None,
        category_filter_func: Optional[Callable[[str, str], bool]] = None,
        banks: Optional[List[str]] = None,
        bank_filter_func: Optional[Callable[[str, str], bool]] = None,
        show_label: bool = True,
        show_search: bool = True,
        show_category: bool = True,
        show_bank: bool = False,
        search_placeholder: str = "Search...",
        category_label: str = "Category:",
        bank_label: str = "Bank:",
        search_label: str = "Search:",
        use_analog_style: bool = False,
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize the SearchableFilterableComboBox.

        :param label: Label text for the combo box
        :param options: Full list of option strings to digital
        :param values: Full list of corresponding integer values (if None, uses indices)
        :param categories: List of category strings for filtering (optional)
        :param category_filter_func: Function to determine if an option matches a category.
                                    Signature: (option: str, category: str) -> bool
                                    If None, uses simple substring matching
        :param banks: List of bank strings for filtering (optional)
        :param bank_filter_func: Function to determine if an option matches a bank.
                                Signature: (option: str, bank: str) -> bool
                                If None, uses simple substring matching
        :param show_label: Whether to show the main label
        :param show_search: Whether to show the search box
        :param show_category: Whether to show the category selector
        :param show_bank: Whether to show the bank selector
        :param search_placeholder: Placeholder text for search box
        :param category_label: Label text for category selector
        :param bank_label: Label text for bank selector
        :param search_label: Label text for search box
        :param use_analog_style: If True, use blue (analog) accent for search QLineEdit
        :param parent: Parent widget
        """
        super().__init__(parent)

        # --- Store original data
        self._full_options = options.copy() if options else []
        self._full_values = (
            values.copy() if values else list(range(len(self._full_options)))
        )
        self._categories = categories or []
        self._category_filter_func = (
            category_filter_func or self._default_category_filter
        )
        self._banks = banks or []
        self._bank_filter_func = bank_filter_func or self._default_bank_filter

        # --- Mapping from filtered combo box index to original value index
        self._filtered_to_original: List[int] = []

        # --- Current filter state
        self._current_search_text = ""
        self._current_category = ""
        self._current_bank = ""

        self.category_combo = None
        self.bank_combo = None

        # --- Search box (optional; set when show_search=True and search row exists)
        self.search_box: Optional[QLineEdit] = None

        layout = create_form_layout(parent=self)
        top_bar, self.label_widget = create_header_row(label, show_label, spacing=4)
        layout.addRow(top_bar)
        if show_category and self._categories:
            category_bar = self.add_categories(category_label)
            layout.addRow(category_bar)
        if show_bank and self._banks:
            bank_bar = self.add_banks(bank_label)
            layout.addRow(bank_bar)
        if show_search:
            search_row = self.add_search(
                search_label, search_placeholder, use_analog_style
            )
            layout.addRow(search_row)

        # --- Main combo box
        main_bar, self.combo_box = create_combo_row(
            label=label, slot=self._on_combo_index_changed
        )
        self.set_combo_dimensions(self.combo_box)
        layout.addRow(main_bar)

        # --- Initial population
        self._populate_combo()

    def add_search(
        self, search_label: str, search_placeholder: str, use_analog_style: bool
    ) -> Any:
        """add search"""
        search_row = self._create_search_row(
            search_label, search_placeholder, use_analog_style
        )
        return search_row

    def add_categories(self, category_label: str):
        """add categories"""
        category_bar, self.category_combo = create_combo_row(
            label=category_label,
            all_items_label="All Categories",
            items=self._categories,
            slot=self._on_category_changed,
        )
        self.set_combo_dimensions(self.category_combo)
        return category_bar

    def add_banks(self, bank_label: str) -> QHBoxLayout:
        bank_bar, self.bank_combo = create_combo_row(
            label=bank_label,
            all_items_label="All Banks",
            items=self._banks,
            slot=self._on_bank_changed,
        )
        self.set_combo_dimensions(self.bank_combo)
        return bank_bar

    def set_combo_dimensions(self, widget: QWidget):
        """set combo box dimensions"""
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        widget.setMaximumWidth(JDXi.UI.Dimensions.Combo.WIDTH)
        widget.setMaximumHeight(JDXi.UI.Dimensions.Combo.HEIGHT)

    def _create_search_row(
        self, search_label: str, search_placeholder: str, use_analog_style: bool
    ) -> QHBoxLayout:
        line_edit_style = (
            JDXi.UI.Style.QLINEEDIT_ANALOG
            if use_analog_style
            else JDXi.UI.Style.QLINEEDIT
        )
        self.search_box = create_line_edit(
            style_sheet=line_edit_style,
            placeholder=search_placeholder,
            slot=self._on_search_changed,
        )
        search_label_widget = QLabel(search_label)
        widgets = [search_label_widget, self.search_box]
        search_row = create_row_with_widgets(widgets)
        return search_row

    def _default_category_filter(self, option: str, category: str) -> bool:
        """
        Default category filter function using substring matching.

        :param option: Option string to check
        :param category: Category string to match
        :return: True if option matches category
        """
        return category.lower() in option.lower()

    def _default_bank_filter(self, option: str, bank: str) -> bool:
        """
        Default bank filter function using substring matching.
        Checks if the bank letter appears at the start of the option (e.g., "A01 - Program Name").

        :param option: Option string to check
        :param bank: Bank string to match
        :return: True if option matches bank
        """
        if not bank:
            return True
        # --- Check if bank letter appears at the start of the option (format: "A01 - Program Name")
        return option.startswith(bank.upper()) or option.startswith(bank.lower())

    def _on_search_changed(self, text: str) -> None:
        """Handle search text change."""
        self._current_search_text = text.strip()
        self._populate_combo()

    def _on_category_changed(self, category: str) -> None:
        """Handle category selection change."""
        self._current_category = category if category != "All Categories" else ""
        self._populate_combo()

    def _on_bank_changed(self, bank: str) -> None:
        """Handle bank selection change."""
        self._current_bank = bank if bank != "All Banks" else ""
        self._populate_combo()

    def _populate_combo(self) -> None:
        """Populate the combo box based on current filters."""
        # Block signals during population to prevent spurious valueChanged emissions
        self.combo_box.blockSignals(True)

        # --- Clear existing items and mapping
        self.combo_box.clear()
        self._filtered_to_original.clear()

        # --- Filter options
        filtered_options = []
        for i, option in enumerate(self._full_options):
            # Apply search filter
            if self._current_search_text:
                if not re.search(self._current_search_text, option, re.IGNORECASE):
                    continue

            # --- Apply bank filter
            if self._current_bank:
                if not self._bank_filter_func(option, self._current_bank):
                    continue

            # --- Apply category filter
            if self._current_category:
                if not self._category_filter_func(option, self._current_category):
                    continue

            # --- Option passes all filters
            filtered_options.append(option)
            self._filtered_to_original.append(i)

        # --- Add filtered items to combo box
        for option in filtered_options:
            self.combo_box.addItem(option)

        # --- Restore signals
        self.combo_box.blockSignals(False)

        # --- Log for debugging
        if filtered_options:
            pass  # logging here is way too noisy
            """log.debug(
                f"Populated combo box with {len(filtered_options)} items "
                f"(filtered from {len(self._full_options)} total)"
            )"""

    @Slot(int)
    def _on_combo_index_changed(self, filtered_index: int) -> None:
        """
        Handle combo box index change.

        Emits the original value (not the filtered index) to ensure
        MIDI commands use the correct value.

        :param filtered_index: Index in the filtered combo box
        """
        if 0 <= filtered_index < len(self._filtered_to_original):
            original_index = self._filtered_to_original[filtered_index]
            original_value = self._full_values[original_index]
            self.valueChanged.emit(original_value)
            log.debug(
                f"Combo box changed: filtered_index={filtered_index}, "
                f"original_index={original_index}, value={original_value}"
            )
        else:
            log.warning(
                f"Invalid filtered index {filtered_index} "
                f"(max: {len(self._filtered_to_original) - 1})"
            )

    def setValue(self, value: int) -> None:
        """
        Set the combo box to digital the option with the given value.

        This method finds the original index of the value, then finds
        its position in the filtered list (if any), and sets the combo box index.

        :param value: The value to set
        """
        if value not in self._full_values:
            log.warning(f"Value {value} not found in full values list")
            return

        # --- Find original index
        original_index = self._full_values.index(value)

        # --- Find position in filtered list
        if original_index in self._filtered_to_original:
            filtered_index = self._filtered_to_original.index(original_index)
            self.combo_box.blockSignals(True)
            self.combo_box.setCurrentIndex(filtered_index)
            self.combo_box.blockSignals(False)
        else:
            log.warning(
                f"Value {value} (original_index={original_index}) not in filtered list. "
                f"Clearing filters may help."
            )

    def value(self) -> int:
        """
        Get the currently selected value (original value, not filtered index).

        :return: The original value corresponding to the selected option
        """
        filtered_index = self.combo_box.currentIndex()
        if 0 <= filtered_index < len(self._filtered_to_original):
            original_index = self._filtered_to_original[filtered_index]
            return self._full_values[original_index]
        return 0

    def clearFilters(self) -> None:
        """Clear all filters and show all items."""
        if self.search_box:
            self.search_box.clear()
        if self.category_combo:
            self.category_combo.setCurrentIndex(0)  # --- "All Categories"
        if self.bank_combo:
            self.bank_combo.setCurrentIndex(0)  # --- "All Banks"
        self._current_search_text = ""
        self._current_category = ""
        self._current_bank = ""
        self._populate_combo()

    def setLabelVisible(self, visible: bool) -> None:
        """Show or hide the main label."""
        self.label_widget.setVisible(visible)

    def setEnabled(self, enabled: bool) -> None:
        """Enable or disable the widget."""
        super().setEnabled(enabled)
        self.combo_box.setEnabled(enabled)
        if self.search_box:
            self.search_box.setEnabled(enabled)
        if self.category_combo:
            self.category_combo.setEnabled(enabled)
        if self.bank_combo:
            self.bank_combo.setEnabled(enabled)

    def setVisible(self, visible: bool) -> None:
        """Show or hide the widget."""
        super().setVisible(visible)

    def setLabel(self, label: str) -> None:
        """Set the main label text."""
        self.label_widget.setText(label)

    # --- Compatibility methods for ComboBox interface
    @property
    def options(self) -> List[str]:
        """Get the full options list (for compatibility)."""
        return self._full_options

    @property
    def values(self) -> List[int]:
        """Get the full values list (for compatibility)."""
        return self._full_values
