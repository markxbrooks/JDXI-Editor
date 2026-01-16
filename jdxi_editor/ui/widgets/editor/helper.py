"""
Helpers to create HBox and VBoxes
"""

import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QGroupBox, QPushButton, QWidget

from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.ui.image.utils import base64_to_pixmap
from jdxi_editor.ui.image.waveform import generate_waveform_icon
from jdxi_editor.ui.windows.jdxi.dimensions import JDXiDimensions


def create_hlayout_with_widgets(widget_list: list) -> QHBoxLayout:
    """create a row from a list of widgets (centered with stretches)"""
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

def create_layout(vertical: bool = True) -> QLayout:
    """create Group and a layout"""
    layout = QVBoxLayout() if vertical else QHBoxLayout()
    return layout

def create_group_with_layout(group_name: str = None, inner_layout: QLayout = None, vertical: bool = True) -> tuple(QGroupBox, QLayout):
    """create Group and a layout"""
    group = QGroupBox(group_name) if group_name is not None else QGroupBox()
    if inner_layout is None:
        inner_layout = create_layout(vertical=vertical)
    group.setLayout(inner_layout)
    return group, inner_layout
    

def create_vlayout_with_hlayout_and_widgets(inner_layout: QHBoxLayout, widgets: list = None) -> QVBoxLayout:
    """create vbox layout with horizontal layout and widgets below it"""
    vlayout = QVBoxLayout()
    vlayout.addLayout(inner_layout)
    if widgets:
        for widget in widgets:
            vlayout.addWidget(widget)  # Add widgets to vertical layout, not horizontal layout
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
    """Generate the ADSR waveform icon (centered)"""
    icon_base64 = generate_waveform_icon(waveform="adsr", foreground_color=JDXiStyle.WHITE, icon_scale=2.0)
    pixmap = base64_to_pixmap(icon_base64)
    return create_icon_label_with_pixmap(pixmap)
    
    
def create_adsr_icon() -> QIcon:
    """create adsr icon"""
    adsr_icon_base64 = generate_waveform_icon("adsr", "#FFFFFF", 1.0)
    return QIcon(base64_to_pixmap(adsr_icon_base64))


def create_centered_adsr_icon_layout() -> QHBoxLayout:
    """Create a centered ADSR icon layout (for consistent centering in envelope groups)"""
    icon_label = create_adsr_icon_label()
    return create_hlayout_with_widgets([icon_label])


def create_group_adsr_with_hlayout(name: str, hlayout: QHBoxLayout, analog: bool = False) -> QGroupBox:
    """create ADSR Group with an hlayout (harmonized for Digital and Analog)"""
    controls_group = QGroupBox(name)
    controls_group.setLayout(hlayout)
    if analog:
        from jdxi_editor.jdxi.style.theme_manager import JDXiThemeManager
        JDXiThemeManager.apply_adsr_style(controls_group, analog=True)
    else:
        controls_group.setStyleSheet(JDXiStyle.ADSR)
    return controls_group


def create_envelope_group(name: str = "Envelope", icon_layout: QHBoxLayout = None, adsr_widget: QWidget = None, analog: bool = False) -> QGroupBox:
    """
    Create a standardized envelope group with icon and ADSR widget.
    
    The icon is centered horizontally using stretches in an HBoxLayout,
    and the ADSR widget is placed below it in a VBoxLayout.
    
    :param name: Group box title (default: "Envelope")
    :param icon_layout: Optional icon layout (if None, creates centered ADSR icon)
    :param adsr_widget: ADSR widget to add below the icon
    :param analog: Whether to apply analog styling
    :return: QGroupBox with envelope layout
    """
    env_group = QGroupBox(name)
    env_group.setProperty("adsr", True)
    
    if icon_layout is None:
        icon_layout = create_centered_adsr_icon_layout()
    
    # Create vertical layout: icon layout on top (centered), ADSR widget below
    env_layout = QVBoxLayout()
    env_layout.addLayout(icon_layout)  # Centered icon at top
    if adsr_widget:
        env_layout.addWidget(adsr_widget)  # ADSR widget below icon
    env_layout.addStretch()  # Stretch at bottom for spacing
    
    env_group.setLayout(env_layout)
    
    if analog:
        from jdxi_editor.jdxi.style.theme_manager import JDXiThemeManager
        JDXiThemeManager.apply_adsr_style(env_group, analog=True)
    else:
        env_group.setStyleSheet(JDXiStyle.ADSR)
    
    return env_group


def create_button_with_tooltip(tooltip: str) -> QPushButton:
    """create button with tooltip"""
    button = QPushButton()
    button.setFixedSize(30, 30)
    button.setCheckable(True)
    button.setStyleSheet(JDXiStyle.BUTTON_ROUND)
    button.setToolTip(tooltip)
    return button
