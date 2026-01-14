"""
Section Base Widget

This module provides the `SectionBaseWidget` class, which provides a common base
for all editor sections. It automatically adds standardized icon rows based on
section type, ensuring consistency across all tabs.

Classes:
--------
- `SectionBaseWidget`: Base widget that automatically adds icon rows to sections.

Features:
---------
- Automatic icon row addition based on section type
- Consistent layout structure
- Theme-aware styling (analog vs regular)
- Easy to subclass for new sections

Usage Example:
--------------
    # In a section's __init__ or setup_ui method:
    
    class MySection(SectionBaseWidget):
        def __init__(self, ...):
            super().__init__(icon_type="adsr", analog=False)
            # Your initialization code
            self.setup_ui()
        
        def setup_ui(self):
            layout = self.get_layout()  # Gets the QVBoxLayout with icon row already added
            # Add your controls to layout
            layout.addWidget(my_widget)

"""

from enum import Enum
from typing import Literal, Optional

from PySide6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout

from jdxi_editor.jdxi.style.icons import IconRegistry
from jdxi_editor.jdxi.style.theme_manager import JDXiThemeManager


class IconType(str, Enum):
    """Icon row types for sections"""
    ADSR = "adsr"  # ADSR/envelope-related sections (Filter, Amp, LFO, etc.)
    OSCILLATOR = "oscillator"  # Oscillator sections
    GENERIC = "generic"  # Common/general sections
    NONE = "none"  # No icon row


class SectionBaseWidget(QWidget):
    """
    Base widget for editor sections that automatically adds icon rows.
    
    This widget standardizes section structure by automatically adding
    appropriate icon rows based on section type, reducing boilerplate
    and ensuring consistency.
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        icon_type: Literal["adsr", "oscillator", "generic", "none"] = "adsr",
        analog: bool = False,
    ):
        """
        Initialize the SectionBaseWidget.

        :param parent: Parent widget
        :param icon_type: Type of icon row to add ("adsr", "oscillator", "generic", or "none")
        :param analog: Whether to apply analog-specific styling
        """
        super().__init__(parent)
        self.analog = analog
        self.icon_type = icon_type
        self._layout: Optional[QVBoxLayout] = None
        self._icon_added = False

    def get_layout(
        self,
        margins: tuple[int, int, int, int] = None,
        spacing: int = None,
    ) -> QVBoxLayout:
        """
        Get or create the main layout for this section.
        
        If the layout doesn't exist, creates it and adds the icon row.
        This should be called at the start of setup_ui() or init_ui().

        :param margins: Optional tuple of (left, top, right, bottom) margins
        :param spacing: Optional spacing between widgets
        :return: The main QVBoxLayout
        """
        if self._layout is None:
            self._layout = QVBoxLayout()
            self.setLayout(self._layout)
            
            # Set margins and spacing if provided
            if margins is not None:
                self._layout.setContentsMargins(*margins)
            if spacing is not None:
                self._layout.setSpacing(spacing)
            
            # Apply styling
            JDXiThemeManager.apply_adsr_style(self, analog=self.analog)
            
            # Add icon row if not disabled
            if self.icon_type != IconType.NONE and not self._icon_added:
                self._add_icon_row()
                self._icon_added = True
        
        return self._layout
        
    def _create_row(widget_list: list):
        """create a row from a list of widgets"""
        row = QHBoxLayout()
        row.addStretch()
        for widget in widget_list:
            row.addWidget(widget)
        row.addStretch()
        return row

    def _add_icon_row(self) -> None:
        """Add the appropriate icon row based on icon_type"""
        if self._layout is None:
            return
        
        if self.icon_type == IconType.ADSR:
            icon_hlayout = IconRegistry.create_adsr_icons_row()
        elif self.icon_type == IconType.OSCILLATOR:
            icon_hlayout = IconRegistry.create_oscillator_icons_row()
        elif self.icon_type == IconType.GENERIC:
            icon_hlayout = IconRegistry.create_generic_musical_icon_row()
        else:
            return  # IconType.NONE or unknown
        
        self._layout.addLayout(icon_hlayout)

    def setup_ui(self) -> None:
        """
        Setup the UI for this section.
        
        Subclasses should override this method and call get_layout()
        at the start to ensure the icon row is added.
        
        Example:
            def setup_ui(self):
                layout = self.get_layout()
                layout.addWidget(my_widget)
        """
        # Default implementation - subclasses should override
        self.get_layout()

    def init_ui(self) -> None:
        """
        Initialize the UI for this section.
        
        Alias for setup_ui() for sections that use init_ui() naming.
        Subclasses can override either setup_ui() or init_ui().
        """
        self.setup_ui()
