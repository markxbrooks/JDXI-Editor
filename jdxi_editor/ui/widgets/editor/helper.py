"""
Helpers to create HBox and VBoxes
"""

import qtawesome as qta
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLayout,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.digital.filter import DigitalFilterMode
from jdxi_editor.ui.image.utils import base64_to_pixmap
from jdxi_editor.ui.image.waveform import generate_waveform_icon
from jdxi_editor.ui.style.dimensions import Dimensions


def create_filter_button(icon_type: str, mode: DigitalFilterMode) -> QPushButton:
    """create filter button"""
    btn = QPushButton(mode.display_name)
    btn.setCheckable(True)
    icon_base64 = generate_waveform_icon(icon_type, JDXi.UI.Style.WHITE, 2.0)
    btn.setIcon(QIcon(base64_to_pixmap(icon_base64)))
    btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)
    btn.setFixedSize(
        JDXi.UI.Dimensions.WAVEFORM_ICON.WIDTH,
        JDXi.UI.Dimensions.WAVEFORM_ICON.HEIGHT,
    )
    return btn


def create_group(title: str, layout_or_widget) -> QGroupBox:
    """Helper for QGroupBox creation with a layout or single widget."""
    from PySide6.QtWidgets import QLayout

    group = QGroupBox(title)
    if isinstance(layout_or_widget, list):
        group.setLayout(create_layout_with_widgets(layout_or_widget))
    elif isinstance(layout_or_widget, QLayout):
        # --- If it's already a layout, use it directly
        group.setLayout(layout_or_widget)
    else:
        # --- If it's a widget, wrap it in a layout
        layout = create_layout_with_widgets([layout_or_widget])
        group.setLayout(layout)
    return group


def create_group_from_definition(
    key: "GroupBoxDefinitionMixin",
    layout_or_widget,
    set_attr: object = None,
    attr_name: str = None,
) -> QGroupBox:
    """
    Create a QGroupBox using GroupBoxDefinitionMixin pattern.
    
    :param key: GroupBoxDefinitionMixin enum value (e.g., Digital.GroupBox.PULSE_WIDTH)
    :param layout_or_widget: Layout, widget, or list of widgets to add to the group
    :param set_attr: Optional object to set attribute on (e.g., self)
    :param attr_name: Optional custom attribute name (defaults to key.attr_name)
    :return: Created QGroupBox
    """
    group = create_group(key.label, layout_or_widget)
    
    # Set attribute if provided
    if set_attr is not None:
        attr = attr_name if attr_name else key.attr_name
        setattr(set_attr, attr, group)
    
    return group


def create_icon_from_qta(icon_name: str) -> QIcon:
    """create qta icon"""
    return qta.icon(icon_name, color=JDXi.UI.Style.WHITE, icon_size=0.7)


def create_button_with_icon(
    icon_name: str,
    icon: QIcon,
    button_dimensions: Dimensions,
    icon_dimensions: Dimensions,
):
    """create button with icon"""
    btn = QPushButton(icon_name)
    btn.setCheckable(True)
    btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)
    # Add icon
    btn.setIcon(icon)
    btn.setIconSize(QSize(icon_dimensions.WIDTH, icon_dimensions.HEIGHT))
    btn.setFixedSize(
        button_dimensions.WIDTH,
        button_dimensions.HEIGHT,
    )
    btn.setCheckable(True)
    btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)
    return btn


def create_widget_with_layout(inner_layout: QHBoxLayout) -> QWidget:
    """create widget with given inner layout"""
    widget = QWidget()
    widget.setLayout(inner_layout)
    return widget


def create_layout_with_widgets(
    widgets: list,
    vertical: bool = False,
    top_stretch: bool = True,
    bottom_stretch: bool = True,
) -> QHBoxLayout:
    """create a row from a list of widgets (centered with stretches)"""
    layout = create_layout(vertical=vertical)
    if top_stretch:
        layout.addStretch()
    for widget in widgets:
        layout.addWidget(widget)
    if bottom_stretch:
        layout.addStretch()
    return layout


def create_left_aligned_row(widget_list: list) -> QHBoxLayout:
    """
    Create a left-aligned horizontal layout (stretch only on the right).

    Useful for rows where widgets should be left-aligned rather than centered.

    :param widget_list: List of widgets to add to the layout
    :return: QHBoxLayout with widgets left-aligned
    """
    row = QHBoxLayout()
    for widget in widget_list:
        row.addWidget(widget)
    row.addStretch()  # Only add stretch on the right for left alignment
    return row


def create_layout_with_inner_layouts(
    inner_layouts: list, vertical: bool = True
) -> QVBoxLayout:
    """create layout with a list of inner layouts"""
    layout = create_layout(vertical=vertical)
    for inner_layout in inner_layouts:
        layout.addLayout(inner_layout)
    layout.addStretch()
    return layout


def create_layout(vertical: bool = True) -> QVBoxLayout | QHBoxLayout:
    """create Group and a layout"""
    layout = QVBoxLayout() if vertical else QHBoxLayout()
    return layout


def create_group_with_layout(
    label: str = None,
    child_layout: QHBoxLayout | QVBoxLayout | QGridLayout | QFormLayout = None,
    vertical: bool = True,
    style_sheet: str = None,
) -> tuple[QGroupBox, QLayout]:
    """create Group and a layout"""
    group = QGroupBox(label) if label is not None else QGroupBox()
    if child_layout is None:
        child_layout = create_layout(vertical=vertical)
    group.setLayout(child_layout)
    if style_sheet is not None:
        group.setStyleSheet(style_sheet)
    return group, child_layout


def create_layout_with_inner_layout_and_widgets(
    inner_layout: QHBoxLayout | QVBoxLayout | None = None,
    widgets: list = None,
    vertical: bool = True,
) -> QVBoxLayout:
    """create vbox layout with horizontal layout and widgets below it"""
    if inner_layout is None:
        inner_layout = create_layout(vertical=vertical)
    layout = create_layout(vertical=vertical)
    layout.addLayout(inner_layout)
    if widgets:
        for widget in widgets:
            layout.addWidget(
                widget
            )  # Add widgets to vertical layout, not horizontal layout
    layout.addStretch()
    return layout


def create_icon_label_with_pixmap(pixmap: QPixmap) -> QLabel:
    """create icon label"""
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
        icon_pixmap = qta.icon(icon, color=JDXi.UI.Style.GREY).pixmap(
            JDXi.UI.Dimensions.ICON.WIDTH, JDXi.UI.Dimensions.ICON.HEIGHT
        )
        icon_label = create_icon_label_with_pixmap(icon_pixmap)
        icons_hlayout.addWidget(icon_label)
    return icons_hlayout


def create_adsr_icon_pixmap() -> QPixmap:
    """Generate the ADSR waveform pixmap"""
    icon_base64 = generate_waveform_icon(
        waveform="adsr", foreground_color=JDXi.UI.Style.WHITE, icon_scale=2.0
    )
    pixmap = base64_to_pixmap(icon_base64)
    return pixmap


def create_adsr_icon_label() -> QLabel:
    """Generate the ADSR waveform icon (centered)"""
    pixmap = create_adsr_icon_pixmap()
    return create_icon_label_with_pixmap(pixmap)


def create_adsr_icon() -> QIcon:
    """create adsr icon"""
    return QIcon(create_adsr_icon_pixmap())


def create_centered_adsr_icon_layout() -> QHBoxLayout:
    """Create a centered ADSR icon layout (for consistent centering in envelope groups)"""
    icon_label = create_adsr_icon_label()
    return create_layout_with_widgets([icon_label])


def create_group_adsr_with_hlayout(
    name: str, hlayout: QHBoxLayout, analog: bool = False
) -> QGroupBox:
    """create ADSR Group with an hlayout (harmonized for Digital and Analog)"""
    controls_group = QGroupBox(name)
    controls_group.setLayout(hlayout)
    if analog:

        JDXi.UI.Theme.apply_adsr_style(controls_group, analog=True)
    else:
        controls_group.setStyleSheet(JDXi.UI.Style.ADSR)
    return controls_group


def create_envelope_group(
    name: str = "Envelope",
    icon_layout: QHBoxLayout = None,
    adsr_widget: QWidget = None,
    analog: bool = False,
) -> QGroupBox:
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

    # --- Create vertical layout: icon layout on top (centered), ADSR widget below
    env_layout = QVBoxLayout()
    env_layout.addLayout(icon_layout)  # Centered icon at top
    if adsr_widget:
        env_layout.addWidget(adsr_widget)  # ADSR widget below icon
    env_layout.addStretch()  # --- Stretch at bottom for spacing

    env_group.setLayout(env_layout)

    if analog:

        JDXi.UI.Theme.apply_adsr_style(env_group, analog=True)
    else:
        env_group.setStyleSheet(JDXi.UI.Style.ADSR)

    return env_group


def create_button_with_tooltip(tooltip: str) -> QPushButton:
    """create button with tooltip"""
    button = QPushButton()
    button.setFixedSize(30, 30)
    button.setCheckable(True)
    button.setStyleSheet(JDXi.UI.Style.BUTTON_ROUND)
    button.setToolTip(tooltip)
    return button


def create_scrolled_area_with_layout() -> tuple[QScrollArea, QVBoxLayout]:
    """create scrolled area with layout"""
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    scroll_area.setSizePolicy(
        QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
    )
    scrolled_widget = QWidget()
    scrolled_layout = QVBoxLayout(scrolled_widget)
    scroll_area.setWidget(scrolled_widget)
    return scroll_area, scrolled_layout


def create_form_layout_with_widgets(widget_list: list) -> QFormLayout:
    """create form layout with widgets"""
    layout = QFormLayout()
    for widget in widget_list:
        layout.addRow(widget)
    return layout


def create_group_and_grid_layout(group_name: str) -> tuple[QGroupBox, QGridLayout]:
    """A named group box with grid layout"""
    group = QGroupBox(group_name)
    layout = QGridLayout()
    group.setLayout(layout)
    return group, layout


def create_group_with_form_layout(
    widgets: list, label: str = None
) -> tuple[QGroupBox, QFormLayout]:
    """
    Create a group box with form layout and add widgets in one call.

    This combines create_group_with_layout() and create_form_layout_with_widgets()
    for convenience when creating form-based groups.

    :param widgets: List of widgets to add as rows to the form layout
    :param label: Optional name for the group box
    :return: Tuple of (QGroupBox, QFormLayout)
    """
    form_layout = create_form_layout_with_widgets(widgets)
    group, _ = create_group_with_layout(label, child_layout=form_layout)
    return group, form_layout


def create_scroll_area() -> QScrollArea:
    """setup scroll area"""
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    return scroll


def create_scroll_container() -> tuple[QWidget, QVBoxLayout]:
    """create scroll container"""
    container = QWidget()
    container_layout = QVBoxLayout(container)
    return container, container_layout


def transfer_layout_items(source_layout: QLayout, target_layout: QHBoxLayout | QVBoxLayout) -> None:
    """
    Transfer all items from a source layout to a target layout.

    This is useful for avoiding "already has a parent" errors when reusing layouts.
    All widgets, spacer items, and nested layouts are transferred to the target.

    :param source_layout: The layout to take items from
    :param target_layout: The layout to add items to
    """
    while source_layout.count() > 0:
        item = source_layout.takeAt(0)
        if item.widget():
            target_layout.addWidget(item.widget())
        elif item.spacerItem():
            target_layout.addItem(item.spacerItem())
        elif item.layout():
            target_layout.addLayout(item.layout())


def create_group_with_widgets(label: str, widgets: list, vertical: bool = False) -> QGroupBox:
    """create group with widgets"""
    pw_layout = create_layout_with_widgets(widgets=widgets, vertical=vertical)
    pw_group, _ = create_group_with_layout(label=label,
                                           child_layout=pw_layout)
    return pw_group
