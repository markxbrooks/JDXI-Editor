"""
Analog Filter Section
"""

from typing import Callable

import qtawesome as qta
from decologr import Decologr as log
from picomidi.sysex.parameter.address import AddressParameter
from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QWidget,
)

from jdxi_editor.jdxi.style import JDXiStyle, JDXiThemeManager
from jdxi_editor.jdxi.style.icons import IconRegistry
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.ui.image.utils import base64_to_pixmap
from jdxi_editor.ui.image.waveform import generate_waveform_icon
from PySide6.QtGui import QIcon
from jdxi_editor.midi.data.analog.filter import AnalogFilterType
from jdxi_editor.midi.data.parameter.analog import AnalogParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.widgets.adsr.adsr import ADSR
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import create_hlayout_with_widgets
from jdxi_editor.ui.widgets.filter.analog_filter import AnalogFilterWidget
from jdxi_editor.ui.windows.jdxi.dimensions import JDXiDimensions


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
        self.filter_mode_buttons = {}  # Dictionary to store filter mode buttons

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
        controls_icon = qta.icon("mdi.tune", color=JDXiStyle.GREY)
        self.analog_filter_tab_widget.addTab(
            self._create_filter_controls_group(), controls_icon, "Controls"
        )
        # --- Filter ADSR ---
        adsr_icon_base64 = generate_waveform_icon("adsr", "#FFFFFF", 1.0)
        adsr_icon = QIcon(base64_to_pixmap(adsr_icon_base64))
        self.analog_filter_tab_widget.addTab(
            self._create_filter_adsr_env_group(), adsr_icon, "ADSR"
        )
        layout.addSpacing(JDXiStyle.SPACING)
        layout.addStretch()

    def _create_filter_controls_row(self) -> QHBoxLayout:
        """Filter controls row with individual buttons"""
        filter_row = QHBoxLayout()
        filter_row.addStretch()
        
        # Add label
        filter_label = QLabel("Filter")
        filter_row.addWidget(filter_label)
        
        # Create buttons for each filter mode
        filter_modes = [
            AnalogFilterType.BYPASS,
            AnalogFilterType.LPF,
        ]
        
        # Map filter modes to icon names
        filter_icon_map = {
            AnalogFilterType.BYPASS: "mdi.power",  # Power/off icon for bypass
            AnalogFilterType.LPF: "ri.filter-3-fill",  # Filter icon for LPF
        }
        
        for filter_mode in filter_modes:
            btn = QPushButton(filter_mode.name)
            btn.setCheckable(True)
            # Add icon
            icon_name = filter_icon_map.get(filter_mode, "ri.filter-3-fill")
            icon = qta.icon(icon_name, color=JDXiStyle.WHITE, icon_size=JDXiDimensions.ICON_SIZE_SMALL)
            btn.setIcon(icon)
            btn.setIconSize(QSize(20, 20))
            JDXiThemeManager.apply_button_rect_analog(btn)
            btn.setFixedSize(JDXiDimensions.WAVEFORM_ICON_WIDTH, JDXiDimensions.WAVEFORM_ICON_HEIGHT)
            btn.clicked.connect(lambda checked, mode=filter_mode: self._on_filter_mode_selected(mode))
            self.filter_mode_buttons[filter_mode] = btn
            filter_row.addWidget(btn)
        
        filter_row.addStretch()
        return filter_row

    def _on_filter_mode_selected(self, filter_mode: AnalogFilterType):
        """
        Handle filter mode button clicks
        
        :param filter_mode: AnalogFilterType enum value
        """
        # Reset all buttons to default style
        for btn in self.filter_mode_buttons.values():
            btn.setChecked(False)
            JDXiThemeManager.apply_button_rect_analog(btn)
        
        # Apply active style to the selected filter mode button
        selected_btn = self.filter_mode_buttons.get(filter_mode)
        if selected_btn:
            selected_btn.setChecked(True)
            JDXiThemeManager.apply_button_analog_active(selected_btn)
        
        # Send MIDI message via SysEx (analog synth uses SysEx, not control changes)
        if self.midi_helper and self.address:
            from jdxi_editor.midi.sysex.composer import JDXiSysExComposer
            sysex_composer = JDXiSysExComposer()
            sysex_message = sysex_composer.compose_message(
                address=self.address,
                param=AnalogParam.FILTER_MODE_SWITCH,
                value=filter_mode.value,
            )
            if sysex_message:
                self.midi_helper.send_midi_message(sysex_message)
        
        # Update filter controls state
        self._on_filter_mode_changed(filter_mode.value)

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
        controls_layout = create_hlayout_with_widgets([self.filter_resonance,
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
        env_layout = create_hlayout_with_widgets([self.filter_adsr_widget])
        env_group.setLayout(env_layout)
        return env_group
