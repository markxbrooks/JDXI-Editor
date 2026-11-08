"""
This module provides convenience functions for creating PySide6 UI components
such as checkboxes, buttons, button boxes, and row layouts.

These functions simplify the creation and configuration of commonly used
Qt widgets, allowing for consistent layout structures and streamlined
UI initialization.
"""

from typing import Callable, TypeVar, Optional

import qtawesome as qta
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontInfo, QPixmap
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialogButtonBox,
                               QDoubleSpinBox, QFileDialog, QFormLayout,
                               QGroupBox, QHBoxLayout, QLabel, QLineEdit,
                               QPushButton, QScrollArea, QSpinBox, QTabWidget,
                               QVBoxLayout, QWidget, QLayout)

from picoui.dimensions import Dimensions
from picoui.helpers import (create_layout_with_items, create_row_with_widgets,
                            group_with_layout)
from picoui.icons import IconRegistry
from picoui.specs.widgets import (ButtonSpec, CheckBoxSpec, ComboBoxSpec,
                                  DoubleSpinBoxSpec, FileSelectionMode, FileSelectionSpec,
                                  GroupBoxSpec, LabelSpec, LineEditSpec,
                                  LogoSpec, SpinBoxSpec, TabSpec,
                                  wayland_safe_file_dialog_options, BaseSpinBoxSpec)
TSpinBox = TypeVar("TSpinBox", QSpinBox, QDoubleSpinBox)

TSpinBoxSpec = TypeVar("TSpinBoxSpec", SpinBoxSpec, DoubleSpinBoxSpec)


def _attach_form_label(widget: QWidget, label: str) -> None:
    """Optional UI metadata for QFormLayout helpers; not part of Qt public API."""
    if label:
        setattr(widget, "_form_label", label)


def add_form_row_for_spec_widget(layout: QFormLayout, widget: QWidget) -> None:
    """Add ``widget`` to a :class:`~PySide6.QtWidgets.QFormLayout` using ``_form_label`` when set.

    Spec-built controls should set ``_form_label`` via :func:`_attach_form_label`.
    Checkboxes span the form (label is the checkbox text).
    """
    if isinstance(widget, QCheckBox):
        layout.addRow(widget)
        return
    label = getattr(widget, "_form_label", None)
    layout.addRow(label or "", widget)


def double_spinbox_from_spec(spec: DoubleSpinBoxSpec) -> QDoubleSpinBox:
    """create_double_spinbox_from_spec plus DoubleSpinBoxSpec.suffix (PicoUI omits it)."""
    spin = create_double_spinbox_from_spec(spec)
    if spec.suffix:
        spin.setSuffix(spec.suffix)
    return spin


def create_layout_and_widget(margins: tuple, spacing: int) -> tuple[QLayout, QWidget]:
    """create layout and widget"""
    widget = QWidget()
    layout = create_layout_with_items(parent=widget, vertical=False, margins=margins, spacing=spacing)
    return layout, widget


def create_widget_with_items(items: list, margins: tuple, spacing: int) -> QWidget:
    """Create a widget with items"""
    widget = QWidget()
    layout = create_layout_with_items(parent=widget,
                                      items=items,
                                      end_stretch=True)
    layout.setContentsMargins(*margins)
    layout.setSpacing(spacing)
    return widget


def create_scroll_area(resizable: bool = True,
                       policy_horizontal: Qt.ScrollBarPolicy = Qt.ScrollBarPolicy.ScrollBarAsNeeded,
                       policy_vertical: Qt.ScrollBarPolicy = Qt.ScrollBarPolicy.ScrollBarAsNeeded) -> QScrollArea:
    """Create a scrollable area for the entire content"""
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(resizable)
    scroll_area.setHorizontalScrollBarPolicy(policy_horizontal)
    scroll_area.setVerticalScrollBarPolicy(policy_vertical)
    return scroll_area


def create_button_box(
    label: str = "OK", parent: QWidget = None, dimensions: Dimensions = Dimensions(150, 250, 341, 32)
) -> tuple[QDialogButtonBox, QPushButton]:
    """create button box"""
    button_box = QtWidgets.QDialogButtonBox(parent)
    button_box.setGeometry(QtCore.QRect(*dimensions))
    button_box.setOrientation(QtCore.Qt.Horizontal)
    button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
    button_box.setObjectName("button_box")
    # Add Reset to Defaults button
    reset_button = button_box.addButton(label, QtWidgets.QDialogButtonBox.ActionRole)
    return button_box, reset_button


def create_row(
    icon_name: str,
    label_text: str,
    widget: QWidget,
) -> QLayout:
    """create row layout"""
    icon = QLabel()
    icon.setPixmap(IconRegistry.get_icon(icon_name))
    label = QLabel(label_text)
    layout_widgets = [
        icon,
        label,
        widget
    ]
    layout = create_layout_with_items(layout_widgets)
    return layout


def create_checkbox(label: Optional[str] = None, value: bool = False,
                    layout_direction: QtCore.Qt.LayoutDirection = QtCore.Qt.RightToLeft) -> QCheckBox:
    """Create a checkbox from label and value, or from a CheckBoxSpec."""
    check_box = QCheckBox(label or "")
    check_box.setLayoutDirection(layout_direction)
    check_box.setChecked(bool(value))
    return check_box


def create_checkbox_from_spec(spec: CheckBoxSpec) -> QCheckBox:
    """Create a checkbox from a CheckBoxSpec."""
    check_box = create_checkbox(label=spec.label, value=spec.checked_state)
    if spec.tooltip:
        check_box.setToolTip(spec.tooltip)
    if spec.icon is not None:
        check_box.setIcon(spec.icon)
    if spec.slot is not None:
        check_box.stateChanged.connect(spec.slot)
    return check_box


def create_button(label: Optional[str] = None,
                  tooltip: Optional[str] = None,
                  spec: Optional[ButtonSpec] = None) -> QPushButton:
    """Create a button from label/tooltip or from a ButtonSpec."""
    if spec is not None:
        label = spec.label or ""
        tooltip = spec.tooltip or ""
    button = QPushButton(label or "")
    if tooltip:
        button.setToolTip(tooltip)
    if spec is not None:
        if spec.icon:
            button.setIcon(qta.icon(spec.icon))
        button.setEnabled(spec.enabled)
        if spec.slot is not None:
            button.clicked.connect(spec.slot)
        if spec.default is not None:
            button.setDefault(spec.default)
    return button


def create_button_from_spec(spec: ButtonSpec) -> QPushButton:
    """Create a button from a ButtonSpec."""
    return create_button(spec=spec)


def create_label_from_spec(
    spec: LabelSpec, parent: QtWidgets.QWidget | None = None
) -> QLabel:
    """Create a QLabel from a LabelSpec."""
    label = QLabel(spec.label or "", parent)
    if spec.object_name:
        label.setObjectName(spec.object_name)
    if spec.dimensions is not None:
        label.setFixedSize(*spec.dimensions.to_tuple())
    if spec.style is not None:
        style = spec.style
        if "background" not in style.lower():
            style = f"background: transparent; {style}"
        label.setStyleSheet(style)
    if spec.alignment is not None:
        label.setAlignment(spec.alignment)
    if spec.word_wrap:
        label.setWordWrap(True)
    if spec.tooltip:
        label.setToolTip(spec.tooltip)
    if spec.icon:
        pixmap = IconRegistry.get_icon(spec.icon)
        if pixmap is not None:
            label.setPixmap(pixmap)
    if spec.slot is not None:
        label.mousePressEvent = lambda event, slot=spec.slot: slot()
    return label


def create_group_with_items(
    label: str, items: list, vertical: bool = False
) -> QGroupBox:
    """create group with widgets"""
    layout = create_layout_with_items(items=items, vertical=vertical)
    group, _ = group_with_layout(label=label, layout=layout)
    return group


def create_double_spinbox_from_spec(spin_spec: DoubleSpinBoxSpec) -> QDoubleSpinBox:
    """create double spin from spec"""
    double_spinbox = QDoubleSpinBox()
    double_spinbox.setRange(
        spin_spec.min_val, spin_spec.max_val
    )
    double_spinbox.setDecimals(spin_spec.decimals)
    result = _configure_spinbox(double_spinbox, spin_spec)
    _attach_form_label(result, spin_spec.label)
    return result


def _configure_spinbox(spinbox: TSpinBox, spin_spec: BaseSpinBoxSpec) -> TSpinBox:
    """configure spinbox"""
    spinbox.setSingleStep(spin_spec.step)
    if spin_spec.value is not None:
        spinbox.setValue(spin_spec.value)
    spinbox.setToolTip(spin_spec.tooltip)
    spinbox.setSuffix(spin_spec.suffix)
    if spin_spec.slot is not None:
        spinbox.valueChanged.connect(spin_spec.slot)
    return spinbox


def create_spinbox_from_spec(spin_spec: TSpinBoxSpec) -> QSpinBox:
    """create double spin from spec"""
    spinbox = QSpinBox()
    spinbox.setRange(
        int(spin_spec.min_val), int(spin_spec.max_val)
    )
    result = _configure_spinbox(spinbox, spin_spec)
    _attach_form_label(result, spin_spec.label)
    return result


def create_combo_box(
    all_items_label: str = None,
    items: list = None,
    slot: Callable = None,
    spec: ComboBoxSpec = None,
    sort_items: bool = True
) -> QComboBox:
    """Create a combo box from arguments or from a ComboBoxSpec."""
    if spec is not None:
        items = spec.items or []
        slot = spec.slot
        combo = QComboBox()
        combo.addItems(items)
        if spec.tooltip:
            combo.setToolTip(spec.tooltip)
        if slot is not None:
            combo.currentTextChanged.connect(slot)
        if spec.current_index is not None:
            combo.setCurrentIndex(spec.current_index)
        _attach_form_label(combo, spec.label)
        return combo
    combo = QComboBox()
    if all_items_label is not None:
        combo.addItem(all_items_label)
    if items is not None:
        if sort_items:
            items = sorted(items)
        combo.addItems(items)
    if slot is not None:
        combo.currentTextChanged.connect(slot)
    return combo


def create_combo_row(
    label: str = "", all_items_label: Optional[str] = None, items: Optional[list] = None, slot=None, sort_items: bool = True
) -> tuple[QHBoxLayout, QComboBox]:
    """create a combo row"""
    label_widget = QLabel(label)
    combo = create_combo_box(all_items_label, items, slot, sort_items=sort_items)
    widgets = [label_widget, combo]
    row = create_row_with_widgets(widgets)
    return row, combo


def create_line_edit_from_spec(spec: LineEditSpec) -> QLineEdit:
    """create line edit"""
    line_edit = create_line_edit(style_sheet=spec.style_sheet, placeholder=spec.placeholder, slot=spec.slot)
    return line_edit


def create_line_edit(style_sheet: str, placeholder: str, slot: Optional[Callable] = None) -> QLineEdit:
    """create line edit"""
    line_edit = QLineEdit()
    if style_sheet:
        line_edit.setStyleSheet(style_sheet)
    line_edit.setPlaceholderText(placeholder)
    line_edit.textChanged.connect(slot)
    return line_edit


def get_file_path_from_spec(
    parent: QWidget, spec: FileSelectionSpec, start_dir: str = ""
) -> str | None:
    """Open a file dialog from a FileSelectionSpec; returns selected path or None."""
    opts = wayland_safe_file_dialog_options()
    kw: dict = {}
    if opts is not None:
        kw["options"] = opts
    # FileSelectionSpec normalises mode="save" to FileSelectionMode.SAVE (a plain
    # Enum, never equal to the string), so accept either
    if spec.mode in (FileSelectionMode.SAVE, FileSelectionMode.SAVE.value):
        path, _ = QFileDialog.getSaveFileName(
            parent,
            spec.caption,
            start_dir or spec.default_name,
            spec.filter,
            **kw,
        )
    else:
        path, _ = QFileDialog.getOpenFileName(
            parent,
            spec.caption,
            start_dir,
            spec.filter,
            **kw,
        )
    return path if path else None

def create_icon(icon_name: str):
    """create icon"""
    icon_label = QLabel()
    icon_label.setPixmap(qta.icon(icon_name).pixmap(16, 16))
    return icon_label

def create_icon_label(icon_name, text):
    """Create a label widget with an icons and text"""
    widget = QWidget()

    icon_label = create_icon(icon_name)
    text_label = QLabel(text)

    layout = create_layout_with_items(items=[icon_label, text_label], vertical=False, parent=widget, spacing=4, margins=(0,0,0,0), end_stretch=True)
    return widget


def add_tab_from_spec(parent: QWidget, tab_widget: QTabWidget, spec: TabSpec):
    """add tab from spec"""
    widget = getattr(parent, spec.widget_attr)
    if widget is not None:
        tab_widget.addTab(
            widget,
            IconRegistry.get_icon(spec.icon),
            spec.name,
        )


def create_logo_label_from_spec(spec: LogoSpec) -> QLabel:
    """Create a centered logo label from a :class:`~picoui.specs.widgets.LogoSpec`."""
    label = QLabel()
    label.setAlignment(spec.alignment)
    if spec.path:
        transform = Qt.TransformationMode.SmoothTransformation
        if not spec.smooth:
            transform = Qt.TransformationMode.FastTransformation
        pixmap = QPixmap(spec.path).scaled(
            *spec.size.to_tuple(),
            Qt.AspectRatioMode.KeepAspectRatio,
            transform,
        )
        label.setPixmap(pixmap)
    return label


def create_group_box_from_spec(
    spec: GroupBoxSpec,
) -> tuple[QGroupBox, QVBoxLayout]:
    """Create a titled group box and its centered vertical layout."""
    group_box = QGroupBox(spec.title)
    group_box.setAlignment(spec.alignment)
    for font_name in spec.title_fonts:
        font = QFont(font_name, spec.title_size)
        font.setBold(True)
        if QFontInfo(font).family() == font_name:
            group_box.setFont(font)
            break
    group_box.setStyleSheet(
        "QGroupBox {"
        f"color: {spec.foreground_color};"
        "font-weight: bold;"
        "}"
        "QGroupBox::title {"
        f"color: {spec.foreground_color};"
        "subcontrol-origin: margin;"
        "}"
    )
    group_layout = QVBoxLayout()
    group_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    group_box.setLayout(group_layout)
    return group_box, group_layout


def apply_splash_subtitle_style(label: QLabel, config: "SplashScreenConfig") -> None:
    """Apply splash theme foreground and subtitle typography to *label*."""
    from picoui.splash.config import SplashScreenConfig

    if not isinstance(config, SplashScreenConfig):
        raise TypeError("config must be a SplashScreenConfig")
    label.setMinimumHeight(80)
    label.setFixedSize(config.dimensions.width - 25, 80)
    label.setStyleSheet(
        "QLabel{"
        "background: transparent;"
        f"color: {config.foreground_color};"
        f"font-family: '{config.theme.subtitle_font}';"
        f"font-size: {config.theme.subtitle_size}px;"
        "}"
    )
