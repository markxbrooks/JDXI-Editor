"""
Analog Filter Section
"""

from typing import Callable

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox
from PySide6.QtCore import Qt
import qtawesome as qta

from jdxi_editor.ui.widgets.filter.analog_filter import AnalogFilterWidget
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.parameter import AddressParameter
from jdxi_editor.midi.data.parameter.analog import AddressParameterAnalog
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.jdxi.style import JDXiStyle
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
            controls: dict[AddressParameter, QWidget],
            address: RolandSysExAddress,
    ):
        super().__init__()
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
        self.filter_resonance = None
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_switch = create_parameter_switch
        self._on_filter_mode_changed = on_filter_mode_changed
        self.send_control_change = send_control_change
        self.midi_helper = midi_helper
        self.address = address
        self.controls = controls
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
            icon_pixmap = qta.icon(icon, color="#666666").pixmap(JDXiStyle.ICON_PIXMAP_SIZE,
                                                                 JDXiStyle.ICON_PIXMAP_SIZE)
            adsr_icon_label.setPixmap(icon_pixmap)
            adsr_icon_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            adsr_icon_row_layout.addWidget(adsr_icon_label)
        layout.addLayout(adsr_icon_row_layout)

        # Filter Controls
        filter_row = QHBoxLayout()
        filter_row.addStretch(1)
        self.filter_mode_switch = self._create_parameter_switch(
            AddressParameterAnalog.FILTER_MODE_SWITCH, "Filter", ["BYPASS", "LPF"]
        )
        self.filter_mode_switch.valueChanged.connect(
            lambda v: self._on_filter_mode_changed(v)
        )
        filter_row.addWidget(self.filter_mode_switch)
        filter_row.addStretch(1)
        layout.addLayout(filter_row)
        # Controls Group
        controls_group = QGroupBox("Controls")
        layout.addWidget(controls_group)
        controls_layout = QHBoxLayout()
        controls_group.setLayout(controls_layout)
        controls_layout.addStretch()
        self.filter_widget = AnalogFilterWidget(cutoff_param=AddressParameterAnalog.FILTER_CUTOFF,
                                                midi_helper=self.midi_helper,
                                                create_parameter_slider=self._create_parameter_slider,
                                                controls=self.controls,
                                                address=self.address)

        self.filter_resonance = self._create_parameter_slider(
            AddressParameterAnalog.FILTER_RESONANCE, "Resonance", vertical=True
        )
        self.filter_cutoff_keyfollow = self._create_parameter_slider(
            AddressParameterAnalog.FILTER_CUTOFF_KEYFOLLOW, "Keyfollow", vertical=True
        )
        self.filter_env_velocity_sens = self._create_parameter_slider(
            AddressParameterAnalog.FILTER_ENV_VELOCITY_SENSITIVITY,
            "Env. Velocity Sens.", vertical=True
        )

        controls_layout.addWidget(self.filter_resonance)
        controls_layout.addWidget(self.filter_cutoff_keyfollow)
        controls_layout.addWidget(self.filter_widget)
        # layout.addWidget(self.filter_env_depth)
        controls_layout.addWidget(self.filter_env_velocity_sens)
        layout.addSpacing(JDXiStyle.SPACING)
        controls_layout.addStretch()
        controls_group.setStyleSheet(JDXiStyle.ADSR_ANALOG)

        # ADSR Widget
        self.filter_adsr_widget = ADSR(
            attack_param=AddressParameterAnalog.FILTER_ENV_ATTACK_TIME,
            decay_param=AddressParameterAnalog.FILTER_ENV_DECAY_TIME,
            sustain_param=AddressParameterAnalog.FILTER_ENV_SUSTAIN_LEVEL,
            release_param=AddressParameterAnalog.FILTER_ENV_RELEASE_TIME,
            peak_param=AddressParameterAnalog.FILTER_ENV_DEPTH,
            midi_helper=self.midi_helper,
            create_parameter_slider=self._create_parameter_slider,
            controls=self.controls,
            address=self.address,
        )
        self.filter_adsr_widget.setStyleSheet(JDXiStyle.ADSR_ANALOG)

        env_group = QGroupBox("Envelope")
        env_group.setProperty("adsr", True)
        env_layout = QHBoxLayout()
        env_layout.addWidget(self.filter_adsr_widget)
        env_group.setLayout(env_layout)
        layout.addWidget(env_group)

        layout.addStretch()
