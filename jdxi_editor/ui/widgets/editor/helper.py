"""
Helpers to create HBox and VBoxes
"""

import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QGroupBox, QPushButton

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


def create_adsr_icon_label() -> QLabel:
    """Generate the ADSR waveform icon"""
    icon_base64 = generate_waveform_icon(waveform="adsr", foreground_color=JDXiStyle.WHITE, icon_scale=2.0)
    pixmap = base64_to_pixmap(icon_base64)
    icon_label = create_icon_label_with_pixmap(pixmap)
    return icon_label


def create_centered_adsr_icon_label() -> QLabel:
    """ADSR Icon"""
    icon_pixmap = base64_to_pixmap(
        generate_waveform_icon(
            waveform="adsr", foreground_color=JDXiStyle.WHITE, icon_scale=2.0
        )
    )
    icon_label = create_icon_label_with_pixmap(icon_pixmap)
    return icon_label


def create_group_adsr_with_hlayout(name: str, hlayout: QHBoxLayout) -> QGroupBox:
    """create ADSR Group with an hlayout"""
    controls_group = QGroupBox(name)
    controls_group.setLayout(hlayout)
    controls_group.setStyleSheet(JDXiStyle.ADSR)
    return controls_group


def create_button_with_tooltip(tooltip: str) -> QPushButton:
    """create button with tooltip"""
    button = QPushButton()
    button.setFixedSize(30, 30)
    button.setCheckable(True)
    button.setStyleSheet(JDXiStyle.BUTTON_ROUND)
    button.setToolTip(tooltip)
    return button
