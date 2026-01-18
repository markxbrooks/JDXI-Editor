"""
Editor Base Widget

This module provides the `EditorBaseWidget` class, which provides a common layout
structure for all Editor Windows. Similar to how `InstrumentPresetWidget` provides
common preset/image layout, this widget standardizes the overall editor structure.

Classes:
--------
- `EditorBaseWidget`: Base widget that provides common scrollable layout structure
  for all Editor Windows.

Features:
---------
- Standard scroll area + container layout
- Tab widget creation and management
- Consistent spacing and margins
- Theme-aware styling (analog vs regular)
- Flexible content addition (tabs or direct)

Usage Example:
--------------
    # In an editor's setup_ui() method:

    # Option 1: Using tabs (like AnalogSynthEditor)
    base_widget = EditorBaseWidget(parent=self, analog=True)
    base_widget.setup_scrollable_content()

    # Add preset widget as first tab
    base_widget.add_tab_section("Presets", self.instrument_preset)

    # Add other sections as tabs
    base_widget.add_tab_section("Oscillator", self.oscillator_section)
    base_widget.add_tab_section("Filter", self.filter_section)

    # Option 2: Direct content (like DigitalSynthEditor)
    base_widget = EditorBaseWidget(parent=self)
    base_widget.setup_scrollable_content()

    # Add widgets directly to container
    base_widget.add_content_section(self.partials_panel)
    base_widget.add_content_section(self.instrument_preset)

    # Then add a tab widget for partials
    base_widget.add_tab_section("Partials", self.partial_tab_widget)

    # Option 3: Mixed approach
    base_widget = EditorBaseWidget(parent=self, analog=True)
    base_widget.setup_scrollable_content()

    # Add some content directly
    base_widget.add_content_section(header_widget)

    # Then add tabs
    base_widget.add_tab_section("Section 1", widget1)
    base_widget.add_tab_section("Section 2", widget2)

"""

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QScrollArea,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.jdxi.jdxi import JDXi
from jdxi_editor.jdxi.preset.helper import create_scroll_container


class EditorBaseWidget(QWidget):
    """
    Base widget that provides common layout structure for all Editor Windows.

    This widget standardizes the scrollable content area and tab structure
    used across all editors, reducing boilerplate and ensuring consistency.
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        analog: bool = False,
    ):
        """
        Initialize the EditorBaseWidget.

        :param parent: Parent widget (typically the editor window)
        :param analog: Whether to apply analog-specific styling
        """
        super().__init__(parent)
        self.analog = analog
        self.scroll_area: Optional[QScrollArea] = None
        self.container: Optional[QWidget] = None
        self.container_layout: Optional[QVBoxLayout] = None
        self.tab_widget: Optional[QTabWidget] = None
        self.main_layout: Optional[QVBoxLayout] = None
        self.centered_wrapper: Optional[QWidget] = (
            None  # Wrapper widget with HBoxLayout for centering
        )

    def setup_main_layout(self) -> QVBoxLayout:
        """
        Set up the main vertical layout for the widget.

        :return: The main layout
        """
        if self.main_layout is None:
            self.main_layout = QVBoxLayout(self)
            self.main_layout.setContentsMargins(0, 0, 0, 0)
            self.main_layout.setSpacing(0)
            self.setLayout(self.main_layout)
            # Ensure the widget itself expands
            self.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
            )
        return self.main_layout

    def setup_scrollable_content(
        self,
        spacing: int = 5,
        margins: tuple[int, int, int, int] = (5, 5, 5, 5),
    ) -> tuple[QScrollArea, QWidget, QVBoxLayout]:
        """
        Set up the standard scrollable content area.

        Creates a scroll area with a container widget and layout, following
        the common pattern used across all editors. The container is wrapped
        in an HBoxLayout with stretches on both sides for horizontal centering.

        :param spacing: Spacing for the container layout
        :param margins: Contents margins (left, top, right, bottom) for container layout
        :return: Tuple of (scroll_area, container, container_layout)
        """
        # Set up main layout if not already done
        main_layout = self.setup_main_layout()

        # Create scroll area with hidden scrollbars
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_area.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        main_layout.addWidget(self.scroll_area)

        # Create container and layout
        self.container, self.container_layout = create_scroll_container()
        self.container_layout.setSpacing(spacing)
        self.container_layout.setContentsMargins(*margins)

        # Wrap container in HBoxLayout with stretches for horizontal centering
        self.centered_wrapper = QWidget()
        wrapper_layout = QHBoxLayout(self.centered_wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(0)
        wrapper_layout.addStretch()  # Left stretch for centering
        wrapper_layout.addWidget(self.container)  # Container in middle
        wrapper_layout.addStretch()  # Right stretch for centering

        self.scroll_area.setWidget(self.centered_wrapper)

        return self.scroll_area, self.container, self.container_layout

    def create_tab_widget(self) -> QTabWidget:
        """
        Create and style a tab widget for organizing content.

        :return: The created and styled QTabWidget
        """
        if self.tab_widget is None:
            self.tab_widget = QTabWidget()
            JDXi.UI.ThemeManager.apply_tabs_style(self.tab_widget, analog=self.analog)

            # Ensure container layout exists
            if self.container_layout is None:
                self.setup_scrollable_content()

            # Add tab widget to container
            self.container_layout.addWidget(self.tab_widget)

        return self.tab_widget

    def add_tab_section(self, title: str, widget: QWidget) -> int:
        """
        Add a widget as a tab section.

        :param title: Tab title
        :param widget: Widget to add as tab content
        :return: Index of the added tab
        """
        tab_widget = self.create_tab_widget()
        return tab_widget.addTab(widget, title)

    def add_content_section(self, widget: QWidget) -> None:
        """
        Add a widget directly to the container layout (not as a tab).

        :param widget: Widget to add
        """
        if self.container_layout is None:
            self.setup_scrollable_content()

        self.container_layout.addWidget(widget)

    def add_stretch(self) -> None:
        """
        Add stretch to the container layout for spacing.

        Useful for vertical centering or pushing content to top.
        """
        if self.container_layout is None:
            self.setup_scrollable_content()

        self.container_layout.addStretch()

    def insert_content_section(self, index: int, widget: QWidget) -> None:
        """
        Insert a widget at a specific position in the container layout.

        :param index: Position to insert at
        :param widget: Widget to insert
        """
        if self.container_layout is None:
            self.setup_scrollable_content()

        self.container_layout.insertWidget(index, widget)

    def add_centered_content(self, widget: QWidget) -> None:
        """
        Add a widget centered horizontally in the container.

        This method wraps the widget in a horizontal layout with stretch
        on both sides, creating a centered appearance. Useful for editors
        that use centered layouts (like Arpeggiator and Effects editors).

        :param widget: Widget to add centered
        """
        if self.container_layout is None:
            self.setup_scrollable_content()

        # Create a container widget for centering
        centered_container = QWidget()
        centered_layout = QHBoxLayout(centered_container)
        centered_layout.setContentsMargins(0, 0, 0, 0)
        centered_layout.setSpacing(0)

        # Add stretch, widget, stretch for horizontal centering
        centered_layout.addStretch()
        centered_layout.addWidget(widget)
        centered_layout.addStretch()

        # Add the centered container to the main container layout
        self.container_layout.addWidget(centered_container)

    def get_scroll_area(self) -> Optional[QScrollArea]:
        """
        Get the scroll area widget.

        :return: The scroll area, or None if not yet created
        """
        return self.scroll_area

    def get_container(self) -> Optional[QWidget]:
        """
        Get the container widget.

        :return: The container widget, or None if not yet created
        """
        return self.container

    def get_container_layout(self) -> Optional[QVBoxLayout]:
        """
        Get the container layout.

        :return: The container layout, or None if not yet created
        """
        return self.container_layout

    def get_tab_widget(self) -> Optional[QTabWidget]:
        """
        Get the tab widget.

        :return: The tab widget, or None if not yet created
        """
        return self.tab_widget
