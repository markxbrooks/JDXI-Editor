"""
LFO section of the digital partial editor.
"""

from typing import Callable

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QTabWidget,
    QWidget,
)

from decologr import Decologr as log
from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.digital.lfo import DigitalLFOShape
from jdxi_editor.midi.data.parameter.digital.name import DigitalDisplayName
from jdxi_editor.midi.data.parameter.digital.option import DigitalDisplayOptions
from jdxi_editor.midi.data.parameter.digital.partial import (
    DigitalPartialParam,
)
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import (
    create_button_with_icon,
    create_icon_from_qta,
    create_layout_with_widgets,
)
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget


class BaseLFOSection(SectionBaseWidget):
    """LFO section for the digital partial editor."""

    def __init__(
        self,
        icon_type=IconType.ADSR,
        analog=False
    ):
        """
        Initialize the DigitalLFOSection

        :param icon_type: Type of icon e.g
        :param analog: bool
        """
        self.lfo_shape_buttons = {}  # Dictionary to store LFO shape buttons

        super().__init__(icon_type=icon_type, analog=analog)

    def setup_ui(self):
        """Set up the UI for the LFO section."""
        layout = self.get_layout()
        shape_row_layout = self._create_shape_row_layout()
        switch_row_layout = self._create_switch_row_layout()
        tab_widget = self._create_tab_widget()
        layout.addLayout(shape_row_layout)
        layout.addLayout(switch_row_layout)
        layout.addWidget(tab_widget)
        layout.addStretch()

    def _create_tab_widget(self) -> QTabWidget:
        """Create tab widget for Rate/Fade and Depths"""
        lfo_controls_tab_widget = QTabWidget()

        rate_fade_widget = self._create_rate_fade_controls()

        rate_fade_icon = JDXi.UI.IconRegistry.get_icon(
            JDXi.UI.IconRegistry.CLOCK, color=JDXi.UI.Style.GREY
        )
        lfo_controls_tab_widget.addTab(
            rate_fade_widget, rate_fade_icon, "Rate and Fade"
        )
        depths_widget = self._create_depths_controls()

        depths_icon = JDXi.UI.IconRegistry.get_icon(
            JDXi.UI.IconRegistry.WAVEFORM, color=JDXi.UI.Style.GREY
        )
        lfo_controls_tab_widget.addTab(depths_widget, depths_icon, "Depths")
        return lfo_controls_tab_widget

    def _create_shape_row_layout(self) -> QHBoxLayout:
        pass

    def _create_switch_row_layout(self) -> QHBoxLayout:
        pass

    def _create_depths_controls(self) -> QWidget:
        pass
