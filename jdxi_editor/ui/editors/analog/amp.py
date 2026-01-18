"""
Amp section of the JD-Xi editor

This section contains the controls for the amp section of the JD-Xi editor.
"""

from typing import Callable

from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QTabWidget,
    QWidget,
)

from jdxi_editor.jdxi.jdxi import JDXi
from jdxi_editor.midi.data.parameter.analog.name import AnalogDisplayName
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.parameter.analog.address import AnalogParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.widgets.adsr.adsr import ADSR
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import (
    create_adsr_icon,
    create_envelope_group,
    create_layout_with_widgets,
)
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget
from picomidi.sysex.parameter.address import AddressParameter


class AnalogAmpSection(SectionBaseWidget):
    """Amp section of the JD-Xi editor"""

    def __init__(
        self,
        midi_helper: MidiIOHelper,
        address: RolandSysExAddress,
        controls: dict[AddressParameter, QWidget],
        create_parameter_slider: Callable,
    ):
        """
        Initialize the Amp section of the JD-Xi editor

        :param midi_helper: MidiIOHelper
        :param address: RolandSysExAddress
        :param create_parameter_slider: Callable
        """
        self.midi_helper = midi_helper
        self.address = address
        self.controls = controls
        self._create_parameter_slider = create_parameter_slider

        super().__init__(icon_type=IconType.ADSR, analog=True)
        self.setup_ui()

    def setup_ui(self):
        """Setup UI (standardized method name matching Digital Amp)"""

        # --- Add Analog Amp Level controls ---
        amp_controls_layout = self._create_analog_amp_level_controls()
        amp_controls_widget = QWidget()
        amp_controls_widget.setLayout(amp_controls_layout)

        # --- Add Analog Amp ADSR controls ---
        amp_adsr_group = self._create_analog_amp_adsr_group()

        self.analog_amp_tab_widget = QTabWidget()
        controls_icon = JDXi.UI.IconRegistry.get_icon(
            JDXi.UI.IconRegistry.TUNE, color=JDXi.UI.Style.GREY
        )
        self.analog_amp_tab_widget.addTab(
            amp_controls_widget, controls_icon, "Controls"
        )
        adsr_icon = create_adsr_icon()
        self.analog_amp_tab_widget.addTab(amp_adsr_group, adsr_icon, "ADSR")
        JDXi.UI.ThemeManager.apply_tabs_style(self.analog_amp_tab_widget, analog=True)

        self.main_rows_layout = self.create_main_rows_layout()
        self.main_rows_layout.addWidget(self.analog_amp_tab_widget)
        self.main_rows_layout.addStretch()

    def _create_analog_amp_level_controls(self) -> QHBoxLayout:
        """Level controls - standardized order: Level, KeyFollow, Velocity"""
        self.amp_level = self._create_parameter_slider(
            AnalogParam.AMP_LEVEL, AnalogDisplayName.AMP_LEVEL, vertical=True
        )
        self.amp_level_keyfollow = self._create_parameter_slider(
            AnalogParam.AMP_LEVEL_KEYFOLLOW, AnalogDisplayName.AMP_LEVEL_KEYFOLLOW, vertical=True
        )
        self.amp_level_velocity_sensitivity = self._create_parameter_slider(
            AnalogParam.AMP_LEVEL_VELOCITY_SENSITIVITY,
            AnalogDisplayName.AMP_LEVEL_VELOCITY_SENSITIVITY,
            vertical=True,
        )
        # Standardized order: Level, KeyFollow, Velocity (matching Filter pattern)
        level_controls_row_layout = create_layout_with_widgets(
            [
                self.amp_level,
                self.amp_level_keyfollow,
                self.amp_level_velocity_sensitivity,
            ]
        )
        return level_controls_row_layout

    def _create_analog_amp_adsr_group(self) -> QGroupBox:
        """Amp Envelope - harmonized with Digital Amp, uses standardized helper"""
        # --- ADSR Widget
        self.amp_env_adsr_widget = ADSR(
            attack_param=AnalogParam.AMP_ENV_ATTACK_TIME,
            decay_param=AnalogParam.AMP_ENV_DECAY_TIME,
            sustain_param=AnalogParam.AMP_ENV_SUSTAIN_LEVEL,
            release_param=AnalogParam.AMP_ENV_RELEASE_TIME,
            midi_helper=self.midi_helper,
            create_parameter_slider=self._create_parameter_slider,
            address=self.address,
            controls=self.controls,
            analog=True,
        )
        # Use standardized envelope group helper (centers icon automatically)
        return create_envelope_group(
            name="Envelope", adsr_widget=self.amp_env_adsr_widget, analog=True
        )
