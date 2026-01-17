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

from jdxi_editor.jdxi.jdxi import JDXi
from jdxi_editor.midi.data.parameter.analog.address import AnalogParam
from jdxi_editor.midi.data.parameter.analog.name import AnalogDisplayName
from jdxi_editor.midi.data.parameter.analog.option import AnalogDisplayOptions
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import create_layout_with_widgets
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget


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
        self.display_names = AnalogDisplayName

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
        JDXi.ThemeManager.apply_tabs_style(self.lfo_controls_tab_widget, analog=True)
        main_rows_vlayout.addWidget(self.lfo_controls_tab_widget)

        # --- Fade and Rate Controls Tab ---
        fade_rate_controls_row_layout = self._create_lfo_fade_rate_controls_row_layout()
        fade_rate_controls_row_widget = QWidget()
        fade_rate_controls_row_widget.setMinimumHeight(
            JDXi.Dimensions.EDITOR.MINIMUM_HEIGHT
        )
        fade_rate_controls_row_widget.setLayout(fade_rate_controls_row_layout)
        fade_rate_icon = JDXi.IconRegistry.get_icon(
            JDXi.IconRegistry.CLOCK, color=JDXi.Style.GREY
        )
        self.lfo_controls_tab_widget.addTab(
            fade_rate_controls_row_widget, fade_rate_icon, "Fade and Rate Controls"
        )

        # --- Depth Controls Tab ---
        depth_controls_row_layout = self._create_lfo_depth_controls()
        depth_controls_row_widget = QWidget()
        depth_controls_row_widget.setMinimumHeight(
            JDXi.Dimensions.EDITOR.MINIMUM_HEIGHT
        )
        depth_controls_row_widget.setLayout(depth_controls_row_layout)
        depth_icon = JDXi.IconRegistry.get_icon(
            JDXi.IconRegistry.WAVEFORM, color=JDXi.Style.GREY
        )
        self.lfo_controls_tab_widget.addTab(
            depth_controls_row_widget, depth_icon, "Depth Controls"
        )

        main_rows_vlayout.addStretch()

    # ------------------------------------------------------------------
    # Shape Controls
    # ------------------------------------------------------------------
    def _create_shape_row(self) -> QHBoxLayout:
        shape_layout = QHBoxLayout()
        shape_layout.setSpacing(JDXi.Dimensions.ANALOG.SPACING)

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
            icon = qta.icon(icon_name, color=JDXi.Style.WHITE, icon_size=0.7)
            btn.setIcon(icon)
            btn.setIconSize(QSize(20, 20))  # Set explicit icon size for proper display
            JDXi.ThemeManager.apply_button_rect_analog(btn)

            # Use same dimensions as oscillator waveform buttons for consistency
            btn.setFixedSize(
                JDXi.Dimensions.WAVEFORM_ICON.WIDTH,
                JDXi.Dimensions.WAVEFORM_ICON.HEIGHT,
            )

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
        layout.setSpacing(JDXi.Dimensions.ANALOG.SPACING)

        controls = [
            (AnalogParam.LFO_PITCH_DEPTH, AnalogDisplayName.LFO_PITCH_DEPTH),
            (
                AnalogParam.LFO_PITCH_MODULATION_CONTROL,
                AnalogDisplayName.LFO_PITCH_MODULATION_CONTROL,
            ),
            (AnalogParam.LFO_FILTER_DEPTH, AnalogDisplayName.LFO_FILTER_DEPTH),
            (
                AnalogParam.LFO_FILTER_MODULATION_CONTROL,
                AnalogDisplayName.LFO_FILTER_MODULATION_CONTROL,
            ),
            (AnalogParam.LFO_AMP_DEPTH, AnalogDisplayName.LFO_AMP_DEPTH),
            (
                AnalogParam.LFO_AMP_MODULATION_CONTROL,
                AnalogDisplayName.LFO_AMP_MODULATION_CONTROL,
            ),
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
        layout.setSpacing(JDXi.Dimensions.ANALOG.SPACING)

        controls = [
            (AnalogParam.LFO_RATE, AnalogDisplayName.LFO_RATE),
            (
                AnalogParam.LFO_RATE_MODULATION_CONTROL,
                AnalogDisplayName.LFO_RATE_MODULATION_CONTROL,
            ),
            (AnalogParam.LFO_FADE_TIME, AnalogDisplayName.LFO_FADE_TIME),
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
        layout.setSpacing(JDXi.Dimensions.ANALOG.SPACING)

        layout.addStretch()

        self.lfo_sync_switch = self._create_parameter_switch(
            AnalogParam.LFO_TEMPO_SYNC_SWITCH,
            AnalogDisplayName.LFO_TEMPO_SYNC_SWITCH,
            AnalogDisplayOptions.LFO_TEMPO_SYNC_SWITCH,
        )
        layout.addWidget(self.lfo_sync_switch)

        self.lfo_sync_note = self._create_parameter_combo_box(
            AnalogParam.LFO_TEMPO_SYNC_NOTE,
            AnalogDisplayName.LFO_TEMPO_SYNC_NOTE,
            options=AnalogDisplayOptions.LFO_TEMPO_SYNC_NOTE,
        )
        layout.addWidget(self.lfo_sync_note)

        self.key_trigger_switch = self._create_parameter_switch(
            AnalogParam.LFO_KEY_TRIGGER,
            AnalogDisplayName.LFO_KEY_TRIGGER,
            AnalogDisplayOptions.LFO_KEY_TRIGGER,
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
        JDXi.ThemeManager.apply_adsr_style(self, analog=True)
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
            btn.setIcon(qta.icon(icon_name, color=JDXi.Style.WHITE, icon_size=0.7))
            JDXi.ThemeManager.apply_button_rect_analog(btn)
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
        sync_row_layout = self._create_lfo_sync_controls()

        main_rows_vlayout.addLayout(sync_row_layout)

        self.lfo_controls_tab_widget = QTabWidget()
        JDXi.ThemeManager.apply_tabs_style(self.lfo_controls_tab_widget, analog=True)
        main_rows_vlayout.addWidget(self.lfo_controls_tab_widget)

        # ---LFO Rate and Fade Time ---
        fade_rate_controls_row_layout = self._create_lfo_timing_controls()
        timing_controls_row_widget = QWidget()
        timing_controls_row_widget.setMinimumHeight(
            JDXi.Dimensions.EDITOR.MINIMUM_HEIGHT
        )
        timing_controls_row_widget.setLayout(fade_rate_controls_row_layout)

        self.lfo_controls_tab_widget.addTab(
            timing_controls_row_widget, "Timing Controls"
        )

        # --- Modulation Controls ---
        destination_modulation_controls_row_layout = (
            self._create_lfo_destination_modulation_controls()
        )
        modulation_controls_row_widget = QWidget()
        modulation_controls_row_widget.setMinimumHeight(
            JDXi.Dimensions.EDITOR.MINIMUM_HEIGHT
        )
        modulation_controls_row_widget.setLayout(
            destination_modulation_controls_row_layout
        )
        depth_icon = JDXi.IconRegistry.get_icon(
            JDXi.IconRegistry.WAVEFORM, color=JDXi.Style.GREY
        )
        self.lfo_controls_tab_widget.addTab(
            modulation_controls_row_widget,
            depth_icon,
            "Destination Modulation Controls",
        )
        main_rows_vlayout.addStretch()

    def _create_lfo_destination_modulation_controls(self) -> QHBoxLayout:
        self.lfo_pitch = self._create_parameter_slider(
            AnalogParam.LFO_PITCH_DEPTH,
            AnalogDisplayName.LFO_PITCH_DEPTH,
            vertical=True,
        )
        self.lfo_pitch_modulation = self._create_parameter_slider(
            AnalogParam.LFO_PITCH_MODULATION_CONTROL,
            AnalogDisplayName.LFO_PITCH_MODULATION_CONTROL,
            vertical=True,
        )
        self.lfo_filter = self._create_parameter_slider(
            AnalogParam.LFO_FILTER_DEPTH,
            AnalogDisplayName.LFO_FILTER_DEPTH,
            vertical=True,
        )
        self.lfo_filter_modulation = self._create_parameter_slider(
            AnalogParam.LFO_FILTER_MODULATION_CONTROL,
            AnalogDisplayName.LFO_FILTER_MODULATION_CONTROL,
            vertical=True,
        )
        self.lfo_amp = self._create_parameter_slider(
            AnalogParam.LFO_AMP_DEPTH, AnalogDisplayName.LFO_AMP_DEPTH, vertical=True
        )
        self.lfo_amp_modulation = self._create_parameter_slider(
            AnalogParam.LFO_AMP_MODULATION_CONTROL,
            AnalogDisplayName.LFO_AMP_MODULATION_CONTROL,
            vertical=True,
        )

        mod_controls_row_layout = create_layout_with_widgets(
            [
                self.lfo_pitch,
                self.lfo_pitch_modulation,
                self.lfo_filter,
                self.lfo_filter_modulation,
                self.lfo_amp,
                self.lfo_amp_modulation,
            ]
        )
        return mod_controls_row_layout

    def _create_lfo_timing_controls(self) -> QHBoxLayout:
        """create lfo fate rate layout"""
        self.lfo_rate = self._create_parameter_slider(
            AnalogParam.LFO_RATE, AnalogDisplayName.LFO_RATE, vertical=True
        )
        self.lfo_rate_modulation = self._create_parameter_slider(
            AnalogParam.LFO_RATE_MODULATION_CONTROL,
            AnalogDisplayName.LFO_RATE_MODULATION_CONTROL,
            vertical=True,
        )
        self.lfo_fade = self._create_parameter_slider(
            AnalogParam.LFO_FADE_TIME, AnalogDisplayName.LFO_FADE_TIME, vertical=True
        )

        fade_rate_controls_row_layout = QHBoxLayout()
        fade_rate_controls_row_layout.addWidget(self.lfo_rate)
        fade_rate_controls_row_layout.addWidget(self.lfo_rate_modulation)
        fade_rate_controls_row_layout.addWidget(self.lfo_fade)
        return fade_rate_controls_row_layout

    def _create_lfo_sync_controls(self) -> QHBoxLayout:
        """LFO Sync controls"""
        # --- LFO Sync Switch
        self.lfo_sync_switch = self._create_parameter_switch(
            AnalogParam.LFO_TEMPO_SYNC_SWITCH,
            AnalogDisplayName.LFO_TEMPO_SYNC_SWITCH,
            AnalogDisplayOptions.LFO_TEMPO_SYNC_SWITCH,
        )
        # --- LFO Sync Note
        self.lfo_sync_note = self._create_parameter_combo_box(
            AnalogParam.LFO_TEMPO_SYNC_NOTE,
            AnalogDisplayName.LFO_TEMPO_SYNC_NOTE,
            options=AnalogDisplayOptions.LFO_TEMPO_SYNC_NOTE,
        )
        # Key Trigger switch
        self.key_trigger_switch = self._create_parameter_switch(
            AnalogParam.LFO_KEY_TRIGGER,
            AnalogDisplayName.LFO_KEY_TRIGGER,
            AnalogDisplayOptions.LFO_KEY_TRIGGER,
        )

        sync_row_layout = create_layout_with_widgets(
            widget_list=[
                self.lfo_sync_switch,
                self.lfo_sync_note,
                self.key_trigger_switch,
            ],
            vertical=False,
        )
        return sync_row_layout
