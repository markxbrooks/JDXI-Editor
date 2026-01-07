"""
Digital Filter Section for the JDXI Editor
"""

from typing import Callable

import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.log.logger import Logger as log
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.parameter.digital.partial import DigitalPartialParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.image.utils import base64_to_pixmap
from jdxi_editor.ui.image.waveform import generate_waveform_icon
from jdxi_editor.ui.widgets.adsr.adsr import ADSR
from jdxi_editor.ui.widgets.filter.filter import FilterWidget
from jdxi_editor.ui.windows.jdxi.dimensions import JDXiDimensions


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
        log.parameter(f"initialization complete for", self)

    def setup_ui(self):
        """Set up the UI for the filter section."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(5, 15, 5, 5)
        layout.setSpacing(5)
        self.setStyleSheet(JDXiStyle.ADSR)
        self.setMinimumHeight(JDXiDimensions.EDITOR_MINIMUM_HEIGHT)

        # Icons
        icon_hlayout = self._create_adsr_icons_row()
        layout.addLayout(icon_hlayout)

        # Filter mode and slope
        filter_mode_row = self._create_filter_controls_row()
        layout.addLayout(filter_mode_row)

        # Create tab widget
        self.digital_filter_tab_widget = QTabWidget()
        layout.addWidget(self.digital_filter_tab_widget)

        # Add Controls tab
        controls_group = self._create_filter_controls_group()
        self.digital_filter_tab_widget.addTab(controls_group, "Controls")

        # Add ADSR tab
        adsr_group = self._create_filter_adsr_env_group()
        self.digital_filter_tab_widget.addTab(adsr_group, "ADSR")

        layout.addSpacing(JDXiStyle.SPACING)
        layout.addStretch()

    def _create_adsr_icons_row(self) -> QHBoxLayout:
        """Create ADSR icons row"""
        icon_hlayout = QHBoxLayout()
        for icon in [
            "mdi.triangle-wave",
            "mdi.sine-wave",
            "fa5s.wave-square",
            "mdi.cosine-wave",
            "mdi.triangle-wave",
            "mdi.waveform",
        ]:
            icon_label = QLabel()
            icon_pixmap = qta.icon(icon, color="#666666").pixmap(30, 30)
            icon_label.setPixmap(icon_pixmap)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            icon_hlayout.addWidget(icon_label)
        return icon_hlayout

    def _create_filter_controls_row(self) -> QHBoxLayout:
        """Filter mode controls row"""
        filter_mode_row = QHBoxLayout()
        filter_mode_row.addStretch()
        self.filter_mode_switch = self._create_parameter_switch(
            DigitalPartialParam.FILTER_MODE_SWITCH,
            "Mode",
            ["BYPASS", "LPF", "HPF", "BPF", "PKG", "LPF2", "LPF3", "LPF4"],
        )
        self.filter_mode_switch.valueChanged.connect(self._on_filter_mode_changed)
        filter_mode_row.addWidget(self.filter_mode_switch)
        filter_mode_row.addStretch()
        return filter_mode_row

    def _create_filter_controls_group(self) -> QGroupBox:
        """Create filter controls group"""
        controls_group = QGroupBox("Controls")
        controls_layout = QHBoxLayout()
        controls_layout.addStretch()
        controls_group.setLayout(controls_layout)

        self.filter_widget = FilterWidget(
            cutoff_param=DigitalPartialParam.FILTER_CUTOFF,
            slope_param=DigitalPartialParam.FILTER_SLOPE,
            create_parameter_slider=self._create_parameter_slider,
            create_parameter_switch=self._create_parameter_switch,
            midi_helper=self.midi_helper,
            parent=self,
            controls=self.controls,
            address=self.address,
        )
        controls_group.setStyleSheet(JDXiStyle.ADSR)
        controls_layout.addWidget(self.filter_widget)
        controls_layout.addWidget(
            self._create_parameter_slider(
                DigitalPartialParam.FILTER_RESONANCE, "Resonance", vertical=True
            )
        )
        controls_layout.addWidget(
            self._create_parameter_slider(
                DigitalPartialParam.FILTER_CUTOFF_KEYFOLLOW, "KeyFollow", vertical=True
            )
        )
        controls_layout.addWidget(
            self._create_parameter_slider(
                DigitalPartialParam.FILTER_ENV_VELOCITY_SENSITIVITY,
                "Velocity",
                vertical=True,
            )
        )
        controls_layout.addStretch()
        return controls_group

    def _create_filter_adsr_env_group(self) -> QGroupBox:
        """Create filter ADSR group"""
        env_group = QGroupBox("Envelope")
        env_group.setProperty("adsr", True)
        env_layout = QVBoxLayout()
        env_group.setLayout(env_layout)

        # --- ADSR Icon ---
        icon_label = QLabel()
        icon_pixmap = base64_to_pixmap(
            generate_waveform_icon(
                waveform="adsr", foreground_color="#FFFFFF", icon_scale=2.0
            )
        )
        icon_label.setPixmap(icon_pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        env_layout.addWidget(icon_label)

        # --- ADSR Widget ---
        (
            group_address,
            _,
        ) = DigitalPartialParam.AMP_ENV_ATTACK_TIME.get_address_for_partial(
            partial_number=self.partial_number
        )
        self.filter_adsr_widget = ADSR(
            attack_param=DigitalPartialParam.FILTER_ENV_ATTACK_TIME,
            decay_param=DigitalPartialParam.FILTER_ENV_DECAY_TIME,
            sustain_param=DigitalPartialParam.FILTER_ENV_SUSTAIN_LEVEL,
            release_param=DigitalPartialParam.FILTER_ENV_RELEASE_TIME,
            peak_param=DigitalPartialParam.FILTER_ENV_DEPTH,
            create_parameter_slider=self._create_parameter_slider,
            midi_helper=self.midi_helper,
            controls=self.controls,
            address=self.address,
        )
        self.filter_adsr_widget.setStyleSheet(JDXiStyle.ADSR)
        env_layout.addWidget(self.filter_adsr_widget)
        return env_group

    def _on_filter_mode_changed(self, mode: int):
        """Handle filter mode changes"""
        self.update_filter_controls_state(mode)

    def update_filter_controls_state(self, mode: int):
        """Update filter controls enabled state based on mode"""
        enabled = mode != 0  # Enable if not BYPASS
        for param in [
            DigitalPartialParam.FILTER_CUTOFF,
            DigitalPartialParam.FILTER_RESONANCE,
            DigitalPartialParam.FILTER_CUTOFF_KEYFOLLOW,
            DigitalPartialParam.FILTER_ENV_VELOCITY_SENSITIVITY,
            DigitalPartialParam.FILTER_ENV_DEPTH,
            DigitalPartialParam.FILTER_SLOPE,
        ]:
            if param in self.controls:
                self.controls[param].setEnabled(enabled)
            self.filter_adsr_widget.setEnabled(enabled)
            self.filter_widget.setEnabled(enabled)
