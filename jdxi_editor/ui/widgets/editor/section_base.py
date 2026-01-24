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

from typing import Any, Callable, Literal, Optional

from PySide6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.ui.editors.widget_specs import SliderSpec
from jdxi_editor.ui.widgets.editor.helper import transfer_layout_items
from jdxi_editor.ui.widgets.editor.icon_type import IconType


class SectionBaseWidget(QWidget):
    """
    Base widget for editor sections that automatically adds icon rows.

    This widget standardizes section structure by automatically adding
    appropriate icon rows based on section type, reducing boilerplate
    and ensuring consistency.
    """

    WAVEFORM_SPECS: list[SliderSpec] = []
    SLIDER_GROUPS: dict[str, list[SliderSpec]] = {}
    BUTTON_ENABLE_RULES: dict[Any, list[str]] = {}
    ENVELOPE_WIDGET_FACTORIES: list[Callable] = []

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        icon_type: Literal[
            IconType.ADSR, IconType.OSCILLATOR, IconType.GENERIC, IconType.NONE
        ] = "adsr",
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

        self.button_widgets: dict[Any, QPushButton] = {}
        self.slider_widgets: dict[Any, QWidget] = {}

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
                # Margins class now has __iter__, so it can be unpacked directly
                # Also handles tuples/lists for backward compatibility
                self._layout.setContentsMargins(*margins)
            if spacing is not None:
                self._layout.setSpacing(spacing)

            # Apply styling
            JDXi.UI.Theme.apply_adsr_style(self, analog=self.analog)

            # Add icon row if not disabled
            if self.icon_type != IconType.NONE and not self._icon_added:
                self._add_icon_row()
                self._icon_added = True

        return self._layout

    def _add_centered_row(self, *widgets: QWidget) -> None:
        """add centered row"""
        row = QHBoxLayout()
        row.addStretch()
        for w in widgets:
            row.addWidget(w)
        row.addStretch()
        self.get_layout().addLayout(row)

    def _add_icon_row(self) -> None:
        """Add the appropriate icon row based on icon_type"""
        if self._layout is None:
            return

        # Create a container layout to avoid "already has a parent" errors
        icon_row_container = QHBoxLayout()

        if self.icon_type == IconType.ADSR:
            icon_hlayout = JDXi.UI.Icon.create_adsr_icons_row()
        elif self.icon_type == IconType.OSCILLATOR:
            icon_hlayout = JDXi.UI.Icon.create_oscillator_icons_row()
        elif self.icon_type == IconType.GENERIC:
            icon_hlayout = JDXi.UI.Icon.create_generic_musical_icon_row()
        else:
            return  # IconType.NONE or unknown

        # Transfer all items from icon_hlayout to icon_row_container

        transfer_layout_items(icon_hlayout, icon_row_container)

        self._layout.addLayout(icon_row_container)

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

    def create_layout(self):
        """create main rows layout"""
        layout = self.get_layout(
            margins=JDXi.UI.Dimensions.EDITOR_DIGITAL.MARGINS,
            spacing=JDXi.UI.Dimensions.EDITOR_DIGITAL.SPACING,
        )
        layout.addSpacing(JDXi.UI.Dimensions.EDITOR_DIGITAL.SPACING)
        return layout

    def _build_sliders(self, specs: list["SliderSpec"]):
        return [
            self._create_parameter_slider(
                spec.param,
                spec.label,
                vertical=spec.vertical,
            )
            for spec in specs
        ]

    def _build_combo_boxes(self, specs: list["ComboBoxSpec"]):
        return [
            self._create_parameter_combo_box(spec.param, spec.label, spec.options, spec.values)
            for spec in specs
        ]

    def _build_switches(self, specs: list["SwitchSpec"]):
        return [
            self._create_parameter_switch(spec.param, spec.label, spec.options)
            for spec in specs
        ]

    def _create_parameter_slider(self, param, label, vertical) -> QWidget:
        pass

    def _create_parameter_switch(self, param, label, options) -> QWidget:
        pass

    def _create_parameter_combo_box(self, param, label, options, values):
        pass
