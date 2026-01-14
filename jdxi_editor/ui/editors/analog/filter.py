"""
Analog Filter Section
"""

from typing import Callable


from picomidi.sysex.parameter.address import AddressParameter
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QTabWidget,
    QWidget,
)

from jdxi_editor.jdxi.style import JDXiStyle, JDXiThemeManager
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.parameter.analog import AnalogParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.widgets.adsr.adsr import ADSR
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import create_hrow_layout
from jdxi_editor.ui.widgets.filter.analog_filter import AnalogFilterWidget


class AnalogFilterSection(SectionBaseWidget):
    """Analog Filter Section"""

    def __init__(
        self,
        create_parameter_slider: Callable,
        create_parameter_switch: Callable,
        on_filter_mode_changed: Callable,
        send_control_change: Callable,
        midi_helper: MidiIOHelper,
        controls: dict[AddressParameter, QWidget],
        address: RolandSysExAddress,
    ):
        """
        Initialize the AnalogFilterSection

        :param create_parameter_slider: Callable
        :param create_parameter_switch: Callable
        :param on_filter_mode_changed: Callable
        :param send_control_change: Callable
        :param midi_helper: MidiIOHelper Midi Helper
        :param controls: dict[AddressParameter, QWidget] controls to add to
        :param address: RolandSysExAddress
        """
        self.analog_filter_tab_widget: QTabWidget | None = None
        self.filter_resonance = None
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_switch = create_parameter_switch
        self._on_filter_mode_changed = on_filter_mode_changed
        self.send_control_change = send_control_change
        self.midi_helper = midi_helper
        self.address = address
        self.controls = controls

        super().__init__(icon_type=IconType.ADSR, analog=True)
        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        layout = self.get_layout()

        self.analog_filter_tab_widget = QTabWidget()
        JDXiThemeManager.apply_tabs_style(self.analog_filter_tab_widget, analog=True)

        # --- Filter Selection Buttons ---
        filter_row = self._create_filter_controls_row()
        layout.addLayout(filter_row)
        layout.addWidget(self.analog_filter_tab_widget)
        # --- Filter Controls ---
        self.analog_filter_tab_widget.addTab(
            self._create_filter_controls_group(), "Controls"
        )
        # --- Filter ADSR ---
        self.analog_filter_tab_widget.addTab(
            self._create_filter_adsr_env_group(), "ADSR"
        )
        layout.addSpacing(JDXiStyle.SPACING)
        layout.addStretch()

    def _create_filter_controls_row(self) -> QHBoxLayout:
        """Filter controls"""
        self.filter_mode_switch = self._create_parameter_switch(
            AnalogParam.FILTER_MODE_SWITCH, "Filter", ["BYPASS", "LPF"]
        )
        self.filter_mode_switch.valueChanged.connect(
            lambda v: self._on_filter_mode_changed(v)
        )
        filter_row = create_hrow_layout([self.filter_mode_switch])
        return filter_row

    def _create_filter_controls_group(self) -> QGroupBox:
        """Controls Group"""
        controls_group = QGroupBox("Controls")
        self.filter_widget = AnalogFilterWidget(
            cutoff_param=AnalogParam.FILTER_CUTOFF,
            midi_helper=self.midi_helper,
            create_parameter_slider=self._create_parameter_slider,
            controls=self.controls,
            address=self.address,
        )
        self.filter_resonance = self._create_parameter_slider(
            AnalogParam.FILTER_RESONANCE, "Resonance", vertical=True
        )
        self.filter_cutoff_keyfollow = self._create_parameter_slider(
            AnalogParam.FILTER_CUTOFF_KEYFOLLOW, "Keyfollow", vertical=True
        )
        self.filter_env_velocity_sens = self._create_parameter_slider(
            AnalogParam.FILTER_ENV_VELOCITY_SENSITIVITY,
            "Env. Velocity Sens.",
            vertical=True,
        )
        controls_layout = create_hrow_layout([self.filter_resonance,
                                                   self.filter_cutoff_keyfollow,
                                                   self.filter_widget,
                                                   self.filter_env_velocity_sens])

        controls_group.setLayout(controls_layout)
        JDXiThemeManager.apply_adsr_style(controls_group, analog=True)
        return controls_group

    def _create_filter_adsr_env_group(self) -> QGroupBox:
        """ADSR Widget"""
        self.filter_adsr_widget = ADSR(
            attack_param=AnalogParam.FILTER_ENV_ATTACK_TIME,
            decay_param=AnalogParam.FILTER_ENV_DECAY_TIME,
            sustain_param=AnalogParam.FILTER_ENV_SUSTAIN_LEVEL,
            release_param=AnalogParam.FILTER_ENV_RELEASE_TIME,
            peak_param=AnalogParam.FILTER_ENV_DEPTH,
            midi_helper=self.midi_helper,
            create_parameter_slider=self._create_parameter_slider,
            controls=self.controls,
            address=self.address,
            analog=True,
        )
        env_group = QGroupBox("Envelope")
        env_group.setProperty("adsr", True)
        env_layout = create_hrow_layout([self.filter_adsr_widget])
        env_group.setLayout(env_layout)
        return env_group
