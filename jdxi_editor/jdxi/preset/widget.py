"""Preset Widget to be used by All Editors"""

from typing import Optional

from PySide6.QtWidgets import QWidget, QGroupBox, QVBoxLayout, QHBoxLayout

from jdxi_editor.jdxi.style import JDXiStyle


class InstrumentPresetWidget(QWidget):
    """InstrumentPresetWidget"""

    def __init__(
            self,
            parent: Optional[QWidget] = None,
    ):
        """
        InstrumentPresetWidget

        :param parent: QWidget
        """
        super().__init__(parent)
        self.group: QGroupBox | None = None
        self.layout: QVBoxLayout | None = None
        self.instrument_presets: QWidget | None = None
        self.widget: QWidget | None = None
        self.hlayout: QHBoxLayout | None = None

    def add_image_group(self, group: QGroupBox):
        """ add image group"""
        group.setMinimumWidth(JDXiStyle.INSTRUMENT_IMAGE_WIDTH)
        self.hlayout.addWidget(group)

    def add_preset_group(self, group: QGroupBox):
        """add groupbox for instruments"""
        self.hlayout.addWidget(group)

    def setup(self):
        """ set up the widget"""
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addStretch()

    def setup_header_layout(self) -> None:
        """ Top layout with title and image ---"""
        self.hlayout = QHBoxLayout()
        self.hlayout.addStretch()
        self.setLayout(self.hlayout)

    def finalize_header(self):
        """Pad both sides by symmetry, supposedly."""
        self.hlayout.addStretch()
