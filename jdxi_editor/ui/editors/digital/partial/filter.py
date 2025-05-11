"""
Digital Filter Section for the JDXI Editor
"""
from typing import Callable

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox
from PySide6.QtCore import Qt
import qtawesome as qta

from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.parameter.digital.partial import (
    AddressParameterDigitalPartial,
)
from jdxi_editor.midi.io import MidiIOHelper
from jdxi_editor.ui.image.utils import base64_to_pixmap
from jdxi_editor.ui.image.waveform import generate_waveform_icon
from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.ui.widgets.adsr.adsr import ADSR


class DigitalFilterSection(QWidget):
    """Filter section for the digital partial editor."""

    def __init__(
        self,
        create_parameter_slider: Callable,
        create_parameter_switch: Callable,
        partial_number: int,
        midi_helper: MidiIOHelper,
        controls: dict,
        address: RolandSysExAddress,
    ):
        super().__init__()
        """
        Initialize the DigitalFilterSection
        :param create_parameter_slider: Callable
        :param create_parameter_switch: Callable
        :param partial_number: int
        :param midi_helper: MidiIOHelper
        :param controls: dict
        :param address: RolandSysExAddress
        """
        self.partial_number = partial_number
        self.midi_helper = midi_helper
        self.controls = controls
        self.address = address
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_switch = create_parameter_switch

        self.setup_ui()

    def setup_ui(self):
        """Set up the UI for the filter section."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Icons
        icon_hlayout = QHBoxLayout()
        for icon in ["mdi.sine-wave", "ri.filter-3-fill", "mdi.waveform"]:
            icon_label = QLabel()
            icon_pixmap = qta.icon(icon, color="#666666").pixmap(30, 30)
            icon_label.setPixmap(icon_pixmap)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            icon_hlayout.addWidget(icon_label)
        layout.addLayout(icon_hlayout)

        # Filter mode and slope
        type_row = QHBoxLayout()
        self.filter_mode_switch = self._create_parameter_switch(
            AddressParameterDigitalPartial.FILTER_MODE_SWITCH,
            "Mode",
            ["BYPASS", "LPF", "HPF", "BPF", "PKG", "LPF2", "LPF3", "LPF4"],
        )
        self.filter_mode_switch.valueChanged.connect(self._on_filter_mode_changed)
        type_row.addWidget(self.filter_mode_switch)

        self.filter_slope_switch = self._create_parameter_switch(
            AddressParameterDigitalPartial.FILTER_SLOPE, "Slope", ["-12dB", "-24dB"]
        )
        type_row.addWidget(self.filter_slope_switch)
        layout.addLayout(type_row)

        # Controls Group
        controls_group = QGroupBox("Controls")
        controls_layout = QVBoxLayout()
        controls_group.setLayout(controls_layout)
        controls_layout.addWidget(
            self._create_parameter_slider(
                AddressParameterDigitalPartial.FILTER_CUTOFF, "Cutoff (Hz /10)"
            )
        )
        controls_layout.addWidget(
            self._create_parameter_slider(
                AddressParameterDigitalPartial.FILTER_RESONANCE, "Resonance"
            )
        )
        controls_layout.addWidget(
            self._create_parameter_slider(
                AddressParameterDigitalPartial.FILTER_CUTOFF_KEYFOLLOW, "KeyFollow"
            )
        )
        controls_layout.addWidget(
            self._create_parameter_slider(
                AddressParameterDigitalPartial.FILTER_ENV_VELOCITY_SENSITIVITY,
                "Velocity",
            )
        )
        layout.addWidget(controls_group)

        # Filter Envelope
        env_group = QGroupBox("Envelope")
        env_group.setProperty("adsr", True)
        env_layout = QVBoxLayout()
        env_group.setLayout(env_layout)

        # ADSR Icon
        icon_label = QLabel()
        icon_pixmap = base64_to_pixmap(generate_waveform_icon("adsr", "#FFFFFF", 2.0))
        icon_label.setPixmap(icon_pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        env_layout.addWidget(icon_label)

        # ADSR Widget
        (
            group_address,
            _,
        ) = AddressParameterDigitalPartial.AMP_ENV_ATTACK_TIME.get_address_for_partial(
            self.partial_number
        )
        self.filter_adsr_widget = ADSR(
            attack_param=AddressParameterDigitalPartial.FILTER_ENV_ATTACK_TIME,
            decay_param=AddressParameterDigitalPartial.FILTER_ENV_DECAY_TIME,
            sustain_param=AddressParameterDigitalPartial.FILTER_ENV_SUSTAIN_LEVEL,
            release_param=AddressParameterDigitalPartial.FILTER_ENV_RELEASE_TIME,
            midi_helper=self.midi_helper,
            address=self.address,
        )
        self.filter_adsr_widget.setStyleSheet(JDXiStyle.ADSR)
        env_layout.addWidget(self.filter_adsr_widget)

        # Envelope Depth
        env_layout.addWidget(
            self._create_parameter_slider(
                AddressParameterDigitalPartial.FILTER_ENV_DEPTH, "Depth"
            )
        )
        layout.addWidget(env_group)

    def _on_filter_mode_changed(self, mode: int):
        """Handle filter mode changes"""
        self.update_filter_controls_state(mode)

    def update_filter_controls_state(self, mode: int):
        """Update filter controls enabled state based on mode"""
        enabled = mode != 0  # Enable if not BYPASS
        for param in [
            AddressParameterDigitalPartial.FILTER_CUTOFF,
            AddressParameterDigitalPartial.FILTER_RESONANCE,
            AddressParameterDigitalPartial.FILTER_CUTOFF_KEYFOLLOW,
            AddressParameterDigitalPartial.FILTER_ENV_VELOCITY_SENSITIVITY,
            AddressParameterDigitalPartial.FILTER_ENV_DEPTH,
            AddressParameterDigitalPartial.FILTER_SLOPE,
        ]:
            if param in self.controls:
                self.controls[param].setEnabled(enabled)
            self.filter_adsr_widget.setEnabled(enabled)
