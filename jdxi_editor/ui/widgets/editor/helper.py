"""
Helpers to create HBox and VBoxes
"""

import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel

from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.ui.image.utils import base64_to_pixmap
from jdxi_editor.ui.image.waveform import generate_waveform_icon
from jdxi_editor.ui.windows.jdxi.dimensions import JDXiDimensions


def create_hlayout_with_widgets(widget_list: list) -> QHBoxLayout:
    """create a row from a list of widgets"""
    row = QHBoxLayout()
    row.addStretch()
    for widget in widget_list:
        row.addWidget(widget)
    row.addStretch()
    return row


def create_vlayout_with_hlayouts(inner_layouts: list) -> QVBoxLayout:
    """create vbox layout with widgets"""
    vlayout = QVBoxLayout()
    for inner_layout in inner_layouts:
        vlayout.addLayout(inner_layout)
    vlayout.addStretch()
    return vlayout


def create_vlayout_with_hlayout_and_widgets(inner_layout: QHBoxLayout, widgets: list = None) -> QVBoxLayout:
    """create vbox layout with widgets"""
    vlayout = QVBoxLayout()
    vlayout.addLayout(inner_layout)
    if widgets:
        for widget in widgets:
            inner_layout.addWidget(widget)
    vlayout.addStretch()
    return vlayout


def create_icon_label_with_pixmap(pixmap: QPixmap) -> QLabel:
    """ create icon label"""
    label = QLabel()
    label.setPixmap(pixmap)
    label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
    return label


def create_icons_layout() -> QHBoxLayout:
    """Create icons layout"""
    icons_hlayout = QHBoxLayout()
    for icon in [
        "mdi.volume-variant-off",
        "mdi6.volume-minus",
        "mdi.amplifier",
        "mdi6.volume-plus",
        "mdi.waveform",
    ]:
        icon_pixmap = qta.icon(icon, color=JDXiStyle.GREY).pixmap(JDXiDimensions.ICON_WIDTH,
                                                                  JDXiDimensions.ICON_HEIGHT)
        icon_label = create_icon_label_with_pixmap(icon_pixmap)
        icons_hlayout.addWidget(icon_label)
    return icons_hlayout


def create_adsr_icon() -> QLabel:
    """Generate the ADSR waveform icon"""
    icon_base64 = generate_waveform_icon("adsr", JDXiStyle.WHITE, 2.0)
    pixmap = base64_to_pixmap(icon_base64)
    icon_label = create_icon_label_with_pixmap(pixmap)
    return icon_label
