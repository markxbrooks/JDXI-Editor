"""
Digital Filter Section for the JDXI Editor
"""

from typing import Callable

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
)

from decologr import Decologr as log
from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.jdxi.style.icons import IconRegistry
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.digital.filter import DigitalFilterMode
from jdxi_editor.midi.data.parameter.digital.partial import DigitalPartialParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.image.utils import base64_to_pixmap
from jdxi_editor.ui.image.waveform import generate_waveform_icon
from jdxi_editor.ui.widgets.adsr.adsr import ADSR
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import (
    create_adsr_icon,
    create_envelope_group,
    create_group_adsr_with_hlayout,
    create_layout_with_widgets,
)
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget
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
        send_midi_parameter: Callable = None,
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
        self.send_midi_parameter = send_midi_parameter
        self.filter_mode_buttons = {}  # Dictionary to store filter mode buttons

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
        controls_icon = IconRegistry.get_icon(IconRegistry.TUNE, color=JDXiStyle.GREY)
        self.digital_filter_tab_widget.addTab(controls_group, controls_icon, "Controls")

        # --- Add ADSR tab
        adsr_group = self._create_filter_adsr_env_group()
        adsr_icon = create_adsr_icon()
        self.digital_filter_tab_widget.addTab(adsr_group, adsr_icon, "ADSR")

        self.main_rows_layout = self.create_main_rows_layout()
        self.main_rows_layout.addLayout(filter_mode_row)
        self.main_rows_layout.addWidget(self.digital_filter_tab_widget)
        self.main_rows_layout.addStretch()

    def _create_filter_controls_row(self) -> QHBoxLayout:
        """Filter mode controls row with individual buttons"""
        # Add label
        mode_label = QLabel("Mode")

        # Create buttons for each filter mode
        filter_modes = [
            DigitalFilterMode.BYPASS,
            DigitalFilterMode.LPF,
            DigitalFilterMode.HPF,
            DigitalFilterMode.BPF,
            DigitalFilterMode.PKG,
            DigitalFilterMode.LPF2,
            DigitalFilterMode.LPF3,
            DigitalFilterMode.LPF4,
        ]

        # Map filter modes to their waveform icon types
        # Use scale 2.0 to make the icon larger and more visible (17*2=34x9*2=18 pixels)
        filter_icon_map = {
            DigitalFilterMode.BYPASS: "bypass_filter",  # Straight horizontal line for bypass (no filtering)
            DigitalFilterMode.LPF: "lpf_filter",
            DigitalFilterMode.HPF: "hpf_filter",
            DigitalFilterMode.BPF: "bpf_filter",  # Band-pass filter icon
            DigitalFilterMode.PKG: "lpf_filter",  # Peaking can use LPF icon
            DigitalFilterMode.LPF2: "lpf_filter",
            DigitalFilterMode.LPF3: "lpf_filter",
            DigitalFilterMode.LPF4: "lpf_filter",
        }

        widgets = [mode_label]
        for filter_mode in filter_modes:
            btn = QPushButton(filter_mode.display_name)
            btn.setCheckable(True)
            # Generate waveform icon for this specific filter mode
            icon_type = filter_icon_map.get(filter_mode, "filter")
            filter_icon_base64 = generate_waveform_icon(icon_type, "#FFFFFF", 2.0)
            filter_icon = QIcon(base64_to_pixmap(filter_icon_base64))
            # Add waveform icon (let Qt handle icon sizing automatically, like oscillator buttons)
            btn.setIcon(filter_icon)
            btn.setStyleSheet(JDXiStyle.BUTTON_RECT)
            btn.setFixedSize(
                JDXiDimensions.WAVEFORM_ICON_WIDTH, JDXiDimensions.WAVEFORM_ICON_HEIGHT
            )
            btn.clicked.connect(
                lambda checked, mode=filter_mode: self._on_filter_mode_selected(mode)
            )
            self.filter_mode_buttons[filter_mode] = btn
            widgets.append(btn)

        return create_layout_with_widgets(widgets, vertical=False)

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
        filter_controls_list = [
            self.filter_widget,
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
            ),
        ]
        controls_layout = create_layout_with_widgets(filter_controls_list)
        controls_group = create_group_adsr_with_hlayout(
            name="Controls", hlayout=controls_layout
        )
        return controls_group

    def _create_filter_adsr_env_group(self) -> QGroupBox:
        """Create filter ADSR group (harmonized with Analog Filter)"""
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
        # Use standardized envelope group helper (centers icon automatically)
        return create_envelope_group(
            name="Envelope", adsr_widget=self.filter_adsr_widget, analog=False
        )

    def _on_filter_mode_selected(self, filter_mode: DigitalFilterMode):
        """
        Handle filter mode button clicks

        :param filter_mode: DigitalFilterMode enum value
        """
        # Reset all buttons to default style
        for btn in self.filter_mode_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet(JDXiStyle.BUTTON_RECT)

        # Apply active style to the selected filter mode button
        selected_btn = self.filter_mode_buttons.get(filter_mode)
        if selected_btn:
            selected_btn.setChecked(True)
            selected_btn.setStyleSheet(JDXiStyle.BUTTON_RECT_ACTIVE)

        # Update filter controls state
        self.update_filter_controls_state(filter_mode.value)

        # Send MIDI message
        if self.send_midi_parameter:
            if not self.send_midi_parameter(
                DigitalPartialParam.FILTER_MODE_SWITCH, filter_mode.value
            ):
                log.warning(f"Failed to set filter mode to {filter_mode.name}")

    def update_filter_controls_state(self, mode: int):
        """Update filter controls enabled state based on mode"""
        enabled = mode != 0  # Enable if not BYPASS

        # Map filter mode value to filter mode string for the plot
        filter_mode_map = {
            0: "bypass",
            1: "lpf",
            2: "hpf",
            3: "bpf",
            4: "lpf",  # PKG uses LPF-style response
            5: "lpf",  # LPF2
            6: "lpf",  # LPF3
            7: "lpf",  # LPF4
        }
        filter_mode_str = filter_mode_map.get(mode, "lpf")

        # Update plot filter mode
        if self.filter_widget and hasattr(self.filter_widget, "plot"):
            self.filter_widget.filter_mode = filter_mode_str
            self.filter_widget.plot.set_filter_mode(filter_mode_str)

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
