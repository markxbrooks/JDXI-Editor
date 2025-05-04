"""
Analog Filter Section
"""


from typing import Callable

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox
from PySide6.QtCore import Qt
import qtawesome as qta

from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.parameter.analog import AddressParameterAnalog
from jdxi_editor.midi.io import MidiIOHelper
from jdxi_editor.jdxi.style import JDXIStyle
from jdxi_editor.ui.widgets.adsr.adsr import ADSR


class AnalogFilterSection(QWidget):
    """Analog Filter Section"""
    def __init__(
        self,
        create_parameter_slider: Callable,
        create_parameter_switch: Callable,
        on_filter_mode_changed: Callable,
        send_control_change: Callable,
        midi_helper: MidiIOHelper,
        address: RolandSysExAddress
    ):
        super().__init__()
        """
        Initialize the AnalogFilterSection
        :param create_parameter_slider: Callable
        :param create_parameter_switch: Callable
        :param on_filter_mode_changed: Callable
        :param send_control_change: Callable
        :param midi_helper: MidiIOHelper
        :param address: RolandSysExAddress
        """
        self.filter_resonance = None
        self.create_parameter_slider = create_parameter_slider
        self.create_parameter_switch = create_parameter_switch
        self._on_filter_mode_changed = on_filter_mode_changed
        self.send_control_change = send_control_change
        self.midi_helper = midi_helper
        self.address = address
        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # ADSR Icon Row
        adsr_icon_row_layout = QHBoxLayout()
        for icon in [
            "mdi.triangle-wave",
            "mdi.sine-wave",
            "fa5s.wave-square",
            "mdi.cosine-wave",
            "mdi.triangle-wave",
            "mdi.waveform",
        ]:
            adsr_icon_label = QLabel()
            icon_pixmap = qta.icon(icon, color="#666666").pixmap(30, 30)
            adsr_icon_label.setPixmap(icon_pixmap)
            adsr_icon_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            adsr_icon_row_layout.addWidget(adsr_icon_label)
        layout.addLayout(adsr_icon_row_layout)

        # Filter Controls
        self.filter_mode_switch = self.create_parameter_switch(
            AddressParameterAnalog.FILTER_MODE_SWITCH, "Filter", ["BYPASS", "LPF"]
        )
        self.filter_mode_switch.valueChanged.connect(
            lambda v: self._on_filter_mode_changed(v)
        )
        self.filter_cutoff = self.create_parameter_slider(
            AddressParameterAnalog.FILTER_CUTOFF, "Cutoff"
        )
        self.filter_resonance = self.create_parameter_slider(
            AddressParameterAnalog.FILTER_RESONANCE, "Resonance"
        )
        self.filter_cutoff_keyfollow = self.create_parameter_slider(
            AddressParameterAnalog.FILTER_CUTOFF_KEYFOLLOW, "Keyfollow"
        )

        layout.addWidget(self.filter_mode_switch)
        layout.addWidget(self.filter_cutoff)
        layout.addWidget(self.filter_resonance)
        layout.addWidget(self.filter_cutoff_keyfollow)

        # Connect filter controls
        self.filter_resonance.valueChanged.connect(
            lambda v: self.send_control_change(
                AddressParameterAnalog.FILTER_RESONANCE.lsb, v
            )
        )

        # Envelope Controls
        self.filter_env_depth = self.create_parameter_slider(
            AddressParameterAnalog.FILTER_ENV_DEPTH, "Depth"
        )
        self.filter_env_velocity_sens = self.create_parameter_slider(
            AddressParameterAnalog.FILTER_ENV_VELOCITY_SENSITIVITY, "Env. Velocity Sens."
        )

        layout.addWidget(self.filter_env_depth)
        layout.addWidget(self.filter_env_velocity_sens)
        layout.addSpacing(10)

        # ADSR Widget
        self.filter_adsr_widget = ADSR(
            attack_param=AddressParameterAnalog.FILTER_ENV_ATTACK_TIME,
            decay_param=AddressParameterAnalog.FILTER_ENV_DECAY_TIME,
            sustain_param=AddressParameterAnalog.FILTER_ENV_SUSTAIN_LEVEL,
            release_param=AddressParameterAnalog.FILTER_ENV_RELEASE_TIME,
            midi_helper=self.midi_helper,
            address=self.address
        )
        self.filter_adsr_widget.setStyleSheet(JDXIStyle.ADSR_ANALOG)
        env_group = QGroupBox("Envelope")
        env_group.setProperty("adsr", True)
        env_layout = QHBoxLayout()
        env_layout.addWidget(self.filter_adsr_widget)
        env_group.setLayout(env_layout)
        layout.addWidget(env_group)

        layout.addStretch()
