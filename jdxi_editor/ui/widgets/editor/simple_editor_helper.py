"""
Simple Editor Helper

This module provides helper methods for standardizing the setup of "Simple Editors"
(Effects, Vocal Effects, Arpeggio) that follow a common pattern:
- Title + Image header
- Centered content layout
- Tab widget with multiple sections
- Icon rows in each tab section

Classes:
--------
- `SimpleEditorHelper`: Helper class that provides standardized setup methods
  for simple editors with title/image headers and tabbed content.

Usage Example:
--------------
    # In a simple editor's __init__:

    from jdxi_editor.ui.widgets.editor.simple_editor_helper import SimpleEditorHelper

    class MySimpleEditor(BasicEditor):
        def __init__(self, ...):
            super().__init__(midi_helper=midi_helper, parent=parent)

            # Setup base widget
            self.base_widget = EditorBaseWidget(parent=self, analog=False)
            self.base_widget.setup_scrollable_content()

            # Use helper to setup title/image and tabbed content
            self.editor_helper = SimpleEditorHelper(
                editor=self,
                base_widget=self.base_widget,
                title="My Editor",
                image_folder="my_editor",
                default_image="my_editor.png"
            )

            # Create tabs
            self.tab_widget = self.editor_helper.get_tab_widget()
            self.tab_widget.addTab(self._create_section1(), "Section 1")
            self.tab_widget.addTab(self._create_section2(), "Section 2")

            # Add base widget to editor's layout
            if not hasattr(self, 'main_layout') or self.main_layout is None:
                self.main_layout = QVBoxLayout(self)
                self.setLayout(self.main_layout)
            self.main_layout.addWidget(self.base_widget)

"""

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.ui.widgets.display.digital import DigitalTitle
from jdxi_editor.ui.widgets.editor.base import EditorBaseWidget


class SimpleEditorHelper:
    """
    Helper class for standardizing simple editor setup.

    Provides methods to setup title/image headers and tabbed content
    in a consistent way across Effects, Vocal Effects, and Arpeggio editors.
    """

    def __init__(
        self,
        editor: QWidget,
        base_widget: EditorBaseWidget,
        title: str,
        image_folder: str,
        default_image: str,
    ):
        """
        Initialize the SimpleEditorHelper.

        :param editor: The editor widget (typically a BasicEditor subclass)
        :param base_widget: The EditorBaseWidget instance
        :param title: Title text for the editor
        :param image_folder: Folder name for instrument images
        :param default_image: Default image filename
        """
        self.editor = editor
        self.base_widget = base_widget
        self.title_text = title
        self.image_folder = image_folder
        self.default_image = default_image

        # Store references
        self.title_label: Optional[DigitalTitle] = None
        self.image_label: Optional[QLabel] = None
        self.tab_widget: Optional[QTabWidget] = None
        self.rows_layout: Optional[QVBoxLayout] = None

        # Setup title/image and tabbed content
        self._setup_title_and_image()
        self._setup_tabbed_content()

    def _setup_title_and_image(self) -> None:
        """Setup title label and image label"""
        # Create title label
        self.title_label = DigitalTitle(self.title_text)
        JDXi.UI.Theme.apply_instrument_title_label(self.title_label)

        # Create image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Set image folder and default image on editor
        self.editor.instrument_icon_folder = self.image_folder
        self.editor.default_image = self.default_image

        # Set image_label and preset_image_label on editor so update_instrument_image can access it
        self.editor.image_label = self.image_label
        # BasicEditor expects preset_image_label; keep both in sync
        if (
            not hasattr(self.editor, "preset_image_label")
            or self.editor.preset_image_label is None
        ):
            self.editor.preset_image_label = self.image_label

        # Update image (if editor has update_instrument_image method)
        if hasattr(self.editor, "update_instrument_image"):
            self.editor.update_instrument_image()

    def _setup_tabbed_content(self) -> None:
        """Setup centered content with title/image and tab widget"""
        # Create title group box
        title_group_box = QGroupBox()
        title_group_layout = QHBoxLayout()
        title_group_box.setLayout(title_group_layout)
        title_group_layout.addWidget(self.title_label)
        title_group_layout.addWidget(self.image_label)

        # Create centered content widget
        centered_content = QWidget()
        main_row_hlayout = QHBoxLayout(centered_content)
        main_row_hlayout.addStretch()
        self.rows_layout = QVBoxLayout()
        main_row_hlayout.addLayout(self.rows_layout)
        self.rows_layout.addWidget(title_group_box)

        # Create tab widget
        self.tab_widget = QTabWidget()
        JDXi.UI.Theme.apply_tabs_style(self.tab_widget)
        self.rows_layout.addWidget(self.tab_widget)

        main_row_hlayout.addStretch()

        # Add centered content to base widget
        self.base_widget.add_centered_content(centered_content)

    def get_tab_widget(self) -> QTabWidget:
        """
        Get the tab widget for adding tabs.

        :return: The QTabWidget instance
        """
        return self.tab_widget

    def get_rows_layout(self) -> QVBoxLayout:
        """
        Get the rows layout (contains title group and tab widget).

        :return: The QVBoxLayout instance
        """
        return self.rows_layout

    def get_title_label(self) -> DigitalTitle:
        """
        Get the title label.

        :return: The DigitalTitle instance
        """
        return self.title_label

    def get_image_label(self) -> QLabel:
        """
        Get the image label.

        :return: The QLabel instance for the image
        """
        return self.image_label
