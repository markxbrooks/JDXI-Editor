"""
Analog LFO Section
"""

from typing import Callable, Dict

import qtawesome as qta
from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.jdxi.style import JDXiStyle, JDXiThemeManager
from jdxi_editor.jdxi.style.icons import IconRegistry
from jdxi_editor.midi.data.parameter.analog import AnalogParam
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.windows.jdxi.dimensions import JDXiDimensions


class AnalogLFOSection(SectionBaseWidget):
    """Analog LFO Section (responsive layout version)"""

    def __init__(
        self,
        create_parameter_slider: Callable,
        create_parameter_switch: Callable,
        create_parameter_combo_box: Callable,
        on_lfo_shape_changed: Callable,
        lfo_shape_buttons: Dict[int, QPushButton],
    ):
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_switch = create_parameter_switch
        self._create_parameter_combo_box = create_parameter_combo_box
        self._on_lfo_shape_changed = on_lfo_shape_changed
        self.lfo_shape_buttons = lfo_shape_buttons
        
        super().__init__(icon_type=IconType.ADSR, analog=True)
        self.setup_ui()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------
    def setup_ui(self):
        """Setup the UI with tabbed organization (standardized method name matching Digital LFO)"""
        main_rows_vlayout = self.get_layout()

        # Shape row (centered)
        shape_row_layout = self._create_shape_row()
        # Center the shape row
        centered_shape_widget = QWidget()
        centered_shape_layout = QHBoxLayout(centered_shape_widget)
        centered_shape_layout.addStretch()
        centered_shape_layout.addLayout(shape_row_layout)
        centered_shape_layout.addStretch()
        main_rows_vlayout.addWidget(centered_shape_widget)

        # Tempo Sync controls
        sync_row_layout = self._create_tempo_sync_controls()
        main_rows_vlayout.addLayout(sync_row_layout)

        # Create tab widget for organizing controls
        self.lfo_controls_tab_widget = QTabWidget()
        JDXiThemeManager.apply_tabs_style(self.lfo_controls_tab_widget, analog=True)
        main_rows_vlayout.addWidget(self.lfo_controls_tab_widget)

        # --- Fade and Rate Controls Tab ---
        fade_rate_controls_row_layout = self._create_lfo_fade_rate_controls_row_layout()
        fade_rate_controls_row_widget = QWidget()
        fade_rate_controls_row_widget.setMinimumHeight(
            JDXiDimensions.EDITOR_MINIMUM_HEIGHT
        )
        fade_rate_controls_row_widget.setLayout(fade_rate_controls_row_layout)
        fade_rate_icon = IconRegistry.get_icon(IconRegistry.CLOCK, color=JDXiStyle.GREY)
        self.lfo_controls_tab_widget.addTab(
            fade_rate_controls_row_widget, fade_rate_icon, "Fade and Rate Controls"
        )

        # --- Depth Controls Tab ---
        depth_controls_row_layout = self._create_lfo_depth_controls()
        depth_controls_row_widget = QWidget()
        depth_controls_row_widget.setMinimumHeight(JDXiDimensions.EDITOR_MINIMUM_HEIGHT)
        depth_controls_row_widget.setLayout(depth_controls_row_layout)
        depth_icon = IconRegistry.get_icon(IconRegistry.WAVEFORM, color=JDXiStyle.GREY)
        self.lfo_controls_tab_widget.addTab(depth_controls_row_widget, depth_icon, "Depth Controls")
        
        main_rows_vlayout.addStretch()

    # ------------------------------------------------------------------
    # Shape Controls
    # ------------------------------------------------------------------
    def _create_shape_row(self) -> QHBoxLayout:
        shape_layout = QHBoxLayout()
        shape_layout.setSpacing(JDXiDimensions.ANALOG.SPACING)

        shape_layout.addWidget(QLabel("Shape"))

        shapes = [
            ("TRI", "mdi.triangle-wave", 0),
            ("SIN", "mdi.sine-wave", 1),
            ("SAW", "mdi.sawtooth-wave", 2),
            ("SQR", "mdi.square-wave", 3),
            ("S&H", "mdi.waveform", 4),
            ("RND", "mdi.wave", 5),
        ]

        button_group = QButtonGroup(self)
        button_group.setExclusive(True)

        for label, icon_name, value in shapes:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setProperty("value", value)
            # Use qta.icon directly with icon_size parameter (like the old implementation)
            icon = qta.icon(icon_name, color=JDXiStyle.WHITE, icon_size=0.7)
            btn.setIcon(icon)
            btn.setIconSize(QSize(20, 20))  # Set explicit icon size for proper display
            JDXiThemeManager.apply_button_rect_analog(btn)

            # Use same dimensions as oscillator waveform buttons for consistency
            btn.setFixedSize(JDXiDimensions.WAVEFORM_ICON_WIDTH, JDXiDimensions.WAVEFORM_ICON_HEIGHT)

            btn.clicked.connect(lambda _, v=value: self._on_lfo_shape_changed(v))

            button_group.addButton(btn)
            self.lfo_shape_buttons[value] = btn
            shape_layout.addWidget(btn)

        return shape_layout

    # ------------------------------------------------------------------
    # Depth Controls
    # ------------------------------------------------------------------
    def _create_lfo_depth_controls(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(JDXiDimensions.ANALOG.SPACING)

        controls = [
            (AnalogParam.LFO_PITCH_DEPTH, "Pitch Depth"),
            (AnalogParam.LFO_PITCH_MODULATION_CONTROL, "Pitch Modulation"),
            (AnalogParam.LFO_FILTER_DEPTH, "Filter Depth"),
            (AnalogParam.LFO_FILTER_MODULATION_CONTROL, "Filter Modulation"),
            (AnalogParam.LFO_AMP_DEPTH, "Amp Depth"),
            (AnalogParam.LFO_AMP_MODULATION_CONTROL, "Amp Modulation"),
        ]

        for address, label in controls:
            control = self._create_parameter_slider(address, label, vertical=True)
            control.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            layout.addWidget(control)

        return layout

    # ------------------------------------------------------------------
    # Rate / Fade Controls
    # ------------------------------------------------------------------
    def _create_lfo_fade_rate_controls_row_layout(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(JDXiDimensions.ANALOG.SPACING)

        controls = [
            (AnalogParam.LFO_RATE, "Rate"),
            (AnalogParam.LFO_RATE_MODULATION_CONTROL, "Rate Modulation"),
            (AnalogParam.LFO_FADE_TIME, "Fade Time"),
        ]

        for address, label in controls:
            control = self._create_parameter_slider(address, label, vertical=True)
            control.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            layout.addWidget(control)

        return layout

    # ------------------------------------------------------------------
    # Sync Controls
    # ------------------------------------------------------------------
    def _create_tempo_sync_controls(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(JDXiDimensions.ANALOG.SPACING)

        layout.addStretch()

        self.lfo_sync_switch = self._create_parameter_switch(
            AnalogParam.LFO_TEMPO_SYNC_SWITCH,
            "Tempo Sync",
            ["OFF", "ON"],
        )
        layout.addWidget(self.lfo_sync_switch)

        self.lfo_sync_note = self._create_parameter_combo_box(
            AnalogParam.LFO_TEMPO_SYNC_NOTE,
            "Sync Note",
            options=["1/1", "1/2", "1/4", "1/8", "1/16"],
        )
        layout.addWidget(self.lfo_sync_note)

        self.key_trigger_switch = self._create_parameter_switch(
            AnalogParam.LFO_KEY_TRIGGER,
            "Key Trigger",
            ["OFF", "ON"],
        )
        layout.addWidget(self.key_trigger_switch)

        layout.addStretch()
        return layout


class AnalogLFOSectionOld(QWidget):
    """Analog LFO Section"""

    def __init__(
        self,
        create_parameter_slider: Callable,
        create_parameter_switch: Callable,
        create_parameter_combo_box: Callable,
        on_lfo_shape_changed: Callable,
        lfo_shape_buttons: dict,
    ):
        super().__init__()
        """
        Initialize the AnalogLFOSection

        :param create_parameter_slider: Callable
        :param create_parameter_switch: Callable
        :param create_parameter_combo_box: Callable
        :param on_lfo_shape_changed: Callable
        :param lfo_shape_buttons: dict
        """
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_switch = create_parameter_switch
        self._create_parameter_combo_box = create_parameter_combo_box
        self._on_lfo_shape_changed = on_lfo_shape_changed
        self.lfo_shape_buttons = lfo_shape_buttons
        JDXiThemeManager.apply_adsr_style(self, analog=True)
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI (standardized method name matching Digital LFO)"""
        main_rows_vlayout = QVBoxLayout()
        self.setLayout(main_rows_vlayout)

        # Shape row
        shape_row_layout = QHBoxLayout()
        shape_row_layout.addStretch()
        shape_row_layout.addWidget(QLabel("Shape"))
        lfo_shapes = [
            ("TRI", "mdi.triangle-wave", 0),
            ("SIN", "mdi.sine-wave", 1),
            ("SAW", "mdi.sawtooth-wave", 2),
            ("SQR", "mdi.square-wave", 3),
            ("S&H", "mdi.waveform", 4),
            ("RND", "mdi.wave", 5),
        ]

        for name, icon_name, value in lfo_shapes:
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setProperty("value", value)
            btn.setIcon(qta.icon(icon_name, color=JDXiStyle.WHITE, icon_size=0.7))
            JDXiThemeManager.apply_button_rect_analog(btn)
            btn.setIconSize(QSize(20, 20))
            btn.setFixedSize(60, 30)
            btn.setToolTip(name)
            btn.clicked.connect(lambda checked, v=value: self._on_lfo_shape_changed(v))
            self.lfo_shape_buttons[value] = btn
            shape_row_layout.addWidget(btn)
            shape_row_layout.addStretch()

        # main_rows_vlayout.addStretch()
        main_rows_vlayout.addLayout(shape_row_layout)

        # --- Add Tempo Sync Controls ---
        sync_row_layout = self._create_tempo_sync_controls()

        main_rows_vlayout.addLayout(sync_row_layout)

        self.lfo_controls_tab_widget = QTabWidget()
        JDXiThemeManager.apply_tabs_style(self.lfo_controls_tab_widget, analog=True)
        main_rows_vlayout.addWidget(self.lfo_controls_tab_widget)

        # ---LFO Rate and Fade Time ---
        fade_rate_controls_row_layout = self._create_lfo_fade_rate_controls_row_layout()
        fade_rate_controls_row_widget = QWidget()
        fade_rate_controls_row_widget.setMinimumHeight(
            JDXiDimensions.EDITOR_MINIMUM_HEIGHT
        )
        fade_rate_controls_row_widget.setLayout(fade_rate_controls_row_layout)

        self.lfo_controls_tab_widget.addTab(
            fade_rate_controls_row_widget, "Fade and Rate Controls"
        )

        # --- Depth controls ---
        depth_controls_row_layout = self._create_lfo_depth_controls()
        depth_controls_row_widget = QWidget()
        depth_controls_row_widget.setMinimumHeight(JDXiDimensions.EDITOR_MINIMUM_HEIGHT)
        depth_controls_row_widget.setLayout(depth_controls_row_layout)
        depth_icon = IconRegistry.get_icon(IconRegistry.WAVEFORM, color=JDXiStyle.GREY)
        self.lfo_controls_tab_widget.addTab(depth_controls_row_widget, depth_icon, "Depth Controls")
        main_rows_vlayout.addStretch()

    def _create_lfo_depth_controls(self) -> QHBoxLayout:
        depth_controls_row_layout = QHBoxLayout()
        self.lfo_pitch = self._create_parameter_slider(
            AnalogParam.LFO_PITCH_DEPTH, "Pitch Depth", vertical=True
        )
        self.lfo_pitch_modulation = self._create_parameter_slider(
            AnalogParam.LFO_PITCH_MODULATION_CONTROL, "Pitch Modulation", vertical=True
        )
        self.lfo_filter = self._create_parameter_slider(
            AnalogParam.LFO_FILTER_DEPTH, "Filter Depth", vertical=True
        )
        self.lfo_filter_modulation = self._create_parameter_slider(
            AnalogParam.LFO_FILTER_MODULATION_CONTROL,
            "Filter Modulation",
            vertical=True,
        )
        self.lfo_amp = self._create_parameter_slider(
            AnalogParam.LFO_AMP_DEPTH, "Amp Depth", vertical=True
        )
        self.lfo_amp_modulation = self._create_parameter_slider(
            AnalogParam.LFO_AMP_MODULATION_CONTROL, "AMP Modulation", vertical=True
        )

        # depth_controls_row_layout.addStretch()
        depth_controls_row_layout.addWidget(self.lfo_pitch)
        depth_controls_row_layout.addWidget(self.lfo_pitch_modulation)
        depth_controls_row_layout.addWidget(self.lfo_filter)
        depth_controls_row_layout.addWidget(self.lfo_filter_modulation)
        depth_controls_row_layout.addWidget(self.lfo_amp)
        depth_controls_row_layout.addWidget(self.lfo_amp_modulation)
        # depth_controls_row_layout.addStretch()
        return depth_controls_row_layout

    def _create_lfo_fade_rate_controls_row_layout(self) -> QHBoxLayout:
        """create lfo fate rate layout"""
        self.lfo_rate = self._create_parameter_slider(
            AnalogParam.LFO_RATE, "Rate", vertical=True
        )
        self.lfo_rate_modulation = self._create_parameter_slider(
            AnalogParam.LFO_RATE_MODULATION_CONTROL, "Rate Modulation", vertical=True
        )
        self.lfo_fade = self._create_parameter_slider(
            AnalogParam.LFO_FADE_TIME, "Fade Time", vertical=True
        )

        fade_rate_controls_row_layout = QHBoxLayout()

        # Add all controls to layout
        # fade_rate_controls_row_layout.addStretch()
        fade_rate_controls_row_layout.addWidget(self.lfo_rate)
        fade_rate_controls_row_layout.addWidget(self.lfo_rate_modulation)
        fade_rate_controls_row_layout.addWidget(self.lfo_fade)
        # fade_rate_controls_row_layout.addStretch()
        return fade_rate_controls_row_layout

    def _create_tempo_sync_controls(self) -> QHBoxLayout:
        # Tempo Sync controls
        sync_row_layout = QHBoxLayout()
        # sync_row_layout.addStretch()
        self.lfo_sync_switch = self._create_parameter_switch(
            AnalogParam.LFO_TEMPO_SYNC_SWITCH, "Tempo Sync", ["OFF", "ON"]
        )
        sync_row_layout.addWidget(self.lfo_sync_switch)
        self.lfo_sync_note = self._create_parameter_combo_box(
            AnalogParam.LFO_TEMPO_SYNC_NOTE,
            "Sync Note",
            options=["1/1", "1/2", "1/4", "1/8", "1/16"],
        )
        sync_row_layout.addWidget(self.lfo_sync_note)
        # Key Trigger switch
        self.key_trigger_switch = self._create_parameter_switch(
            AnalogParam.LFO_KEY_TRIGGER, "Key Trigger", ["OFF", "ON"]
        )
        sync_row_layout.addWidget(self.key_trigger_switch)
        # sync_row_layout.addStretch()
        return sync_row_layout
