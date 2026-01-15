"""
Digital Filter Section for the JDXI Editor
"""

from typing import Callable

from decologr import Decologr as log
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QTabWidget,
    QVBoxLayout,
)

from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.parameter.digital.partial import DigitalPartialParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.image.utils import base64_to_pixmap
from jdxi_editor.ui.image.waveform import generate_waveform_icon
from jdxi_editor.ui.widgets.adsr.adsr import ADSR
from jdxi_editor.ui.widgets.editor.helper import create_hlayout_with_widgets, create_icon_label_with_pixmap
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.filter.filter import FilterWidget
from jdxi_editor.ui.windows.jdxi.dimensions import JDXiDimensions


class DigitalFilterSection(SectionBaseWidget):
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

        super().__init__(icon_type=IconType.ADSR, analog=False)
        self.setup_ui()
        log.parameter(f"initialization complete for", self)

    def setup_ui(self):
        """Set up the UI for the filter section."""
        self.setMinimumHeight(JDXiDimensions.EDITOR_MINIMUM_HEIGHT)

        # --- Filter mode and slope
        filter_mode_row = self._create_filter_controls_row()

        # --- Create tab widget
        self.digital_filter_tab_widget = QTabWidget()

        # --- Add Controls tab
        controls_group = self._create_filter_controls_group()
        self.digital_filter_tab_widget.addTab(controls_group, "Controls")

        # --- Add ADSR tab
        adsr_group = self._create_filter_adsr_env_group()
        self.digital_filter_tab_widget.addTab(adsr_group, "ADSR")

        self.main_rows_layout = self.create_main_rows_layout()
        self.main_rows_layout.addWidget(self.digital_filter_tab_widget)
        self.main_rows_layout.addLayout(filter_mode_row)
        self.main_rows_layout.addStretch()

    def _create_filter_controls_row(self) -> QHBoxLayout:
        """Filter mode controls row"""
        self.filter_mode_switch = self._create_parameter_switch(
            DigitalPartialParam.FILTER_MODE_SWITCH,
            "Mode",
            ["BYPASS", "LPF", "HPF", "BPF", "PKG", "LPF2", "LPF3", "LPF4"],
        )
        self.filter_mode_switch.valueChanged.connect(self._on_filter_mode_changed)
        filter_mode_row = create_hlayout_with_widgets([self.filter_mode_switch])
        return filter_mode_row

    def _create_filter_controls_group(self) -> QGroupBox:
        """Create filter controls group"""
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
        filter_controls_list = [self.filter_widget,
                                self._create_parameter_slider(
                                    DigitalPartialParam.FILTER_RESONANCE, "Resonance", vertical=True
                                ),
                                self._create_parameter_slider(
                                    DigitalPartialParam.FILTER_CUTOFF_KEYFOLLOW, "KeyFollow", vertical=True
                                ),
                                self._create_parameter_slider(
                                    DigitalPartialParam.FILTER_ENV_VELOCITY_SENSITIVITY,
                                    "Velocity",
                                    vertical=True,
                                )
                                ]
        controls_layout = create_hlayout_with_widgets(filter_controls_list)
        controls_group = QGroupBox("Controls")
        controls_group.setLayout(controls_layout)
        controls_group.setStyleSheet(JDXiStyle.ADSR)
        return controls_group

    def _create_filter_adsr_env_group(self) -> QGroupBox:
        """Create filter ADSR group"""
        env_group = QGroupBox("Envelope")
        env_group.setProperty("adsr", True)
        env_layout = QVBoxLayout()
        env_group.setLayout(env_layout)

        # --- ADSR Icon ---
        icon_pixmap = base64_to_pixmap(
            generate_waveform_icon(
                waveform="adsr", foreground_color="#FFFFFF", icon_scale=2.0
            )
        )
        icon_label = create_icon_label_with_pixmap(icon_pixmap)
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
