"""
Amp section of the JD-Xi editor

This section contains the controls for the amp section of the JD-Xi editor.
"""

from typing import Callable

import qtawesome as qta
from picomidi.sysex.parameter.address import AddressParameter
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.jdxi.style import JDXiStyle, JDXiThemeManager
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.parameter.analog import AnalogParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.widgets.adsr.adsr import ADSR


class AnalogAmpSection(QWidget):
    """Amp section of the JD-Xi editor"""

    def __init__(
        self,
        midi_helper: MidiIOHelper,
        address: RolandSysExAddress,
        controls: dict[AddressParameter, QWidget],
        create_parameter_slider: Callable,
        generate_waveform_icon: Callable,
        base64_to_pixmap: Callable,
    ):
        super().__init__()
        """
        Initialize the Amp section of the JD-Xi editor

        :param midi_helper: MidiIOHelper
        :param address: RolandSysExAddress
        :param create_parameter_slider: Callable
        :param generate_waveform_icon: Callable
        :param base64_to_pixmap: Callable
        """
        self.midi_helper = midi_helper
        self.address = address
        self.controls = controls
        self._create_parameter_slider = create_parameter_slider
        self.generate_waveform_icon = generate_waveform_icon
        self.base64_to_pixmap = base64_to_pixmap
        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        main_rows_vlayout = QVBoxLayout()
        main_rows_vlayout.setSpacing(5)
        main_rows_vlayout.setContentsMargins(5, 15, 5, 5)
        self.setLayout(main_rows_vlayout)
        JDXiThemeManager.apply_adsr_style(self, analog=True)

        # --- Add spiffy icons ---
        icons_hlayout = self._create_icons_layout()
        main_rows_vlayout.addLayout(icons_hlayout)

        self.analog_amp_tab_widget = QTabWidget()
        JDXiThemeManager.apply_tabs_style(self.analog_amp_tab_widget, analog=True)
        main_rows_vlayout.addWidget(self.analog_amp_tab_widget)
        # --- Add Analog Amp Level controls ---
        amp_controls_layout = self._create_analog_amp_level_controls()
        amp_controls_widget = QWidget()
        amp_controls_widget.setLayout(amp_controls_layout)
        self.analog_amp_tab_widget.addTab(amp_controls_widget, "Controls")

        # --- Add Analog Amp ADSR controls ---
        amp_adsr_group = self._create_analog_amp_adsr_group()
        self.analog_amp_tab_widget.addTab(amp_adsr_group, "ADSR")

        #  --- Add spacing ---
        main_rows_vlayout.addSpacing(10)

        main_rows_vlayout.addStretch()

    def _create_analog_amp_level_controls(self) -> QHBoxLayout:
        """Level controls"""
        level_controls_row_layout = QHBoxLayout()

        self.amp_level = self._create_parameter_slider(
            AnalogParam.AMP_LEVEL, "Level", vertical=True
        )
        self.amp_level_keyfollow = self._create_parameter_slider(
            AnalogParam.AMP_LEVEL_KEYFOLLOW, "Keyfollow", vertical=True
        )
        self.amp_level_velocity_sensitivity = self._create_parameter_slider(
            AnalogParam.AMP_LEVEL_VELOCITY_SENSITIVITY,
            "Velocity Sensitivity",
            vertical=True,
        )

        level_controls_row_layout.addStretch()
        level_controls_row_layout.addWidget(self.amp_level)
        level_controls_row_layout.addWidget(self.amp_level_keyfollow)
        level_controls_row_layout.addWidget(self.amp_level_velocity_sensitivity)
        level_controls_row_layout.addStretch()
        return level_controls_row_layout

    def _create_icons_layout(self) -> QHBoxLayout:
        # Icon row
        icons_hlayout = QHBoxLayout()
        for icon in [
            "mdi.volume-variant-off",
            "mdi6.volume-minus",
            "mdi.amplifier",
            "mdi6.volume-plus",
            "mdi.waveform",
        ]:
            icon_label = QLabel()
            icon_pixmap = qta.icon(icon, color="#666666").pixmap(30, 30)
            icon_label.setPixmap(icon_pixmap)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            icons_hlayout.addWidget(icon_label)
        return icons_hlayout

    def _create_analog_amp_adsr_group(self) -> QGroupBox:
        """Amp Envelope"""
        env_group = QGroupBox("Envelope")
        env_group.setProperty("adsr", True)
        amp_env_adsr_vlayout = QVBoxLayout()
        env_group.setLayout(amp_env_adsr_vlayout)

        # ADSR Icon
        icon_base64 = self.generate_waveform_icon("adsr", "#FFFFFF", 2.0)
        pixmap = self.base64_to_pixmap(icon_base64)
        icon_label = QLabel()
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        icons_hlayout = QHBoxLayout()
        icons_hlayout.addWidget(icon_label)
        amp_env_adsr_vlayout.addLayout(icons_hlayout)

        # ADSR Widget
        self.amp_env_adsr_widget = ADSR(
            attack_param=AnalogParam.AMP_ENV_ATTACK_TIME,
            decay_param=AnalogParam.AMP_ENV_DECAY_TIME,
            sustain_param=AnalogParam.AMP_ENV_SUSTAIN_LEVEL,
            release_param=AnalogParam.AMP_ENV_RELEASE_TIME,
            midi_helper=self.midi_helper,
            create_parameter_slider=self._create_parameter_slider,
            address=self.address,
            controls=self.controls,
        )
        JDXiThemeManager.apply_adsr_style(self.amp_env_adsr_widget, analog=True)
        amp_env_adsr_vlayout.addWidget(self.amp_env_adsr_widget)
        return env_group
