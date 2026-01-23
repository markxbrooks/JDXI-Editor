"""
Analog Filter Section
"""

from typing import Callable

import qtawesome as qta
from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.analog.filter import AnalogFilterType
from jdxi_editor.midi.data.parameter.analog.address import AnalogParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import (
    create_adsr_icon,
    create_envelope_group,
    create_layout_with_widgets,
)
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget
from jdxi_editor.ui.widgets.filter.analog_filter import AnalogFilterWidget
from picomidi.sysex.parameter.address import AddressParameter


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
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI (standardized method name matching Digital Filter)"""
        layout = self.get_layout()

        self.analog_filter_tab_widget = QTabWidget()
        JDXi.UI.ThemeManager.apply_tabs_style(
            self.analog_filter_tab_widget, analog=True
        )

        # --- Filter Selection Buttons ---
        filter_row = self._create_filter_controls_row()
        layout.addLayout(filter_row)
        layout.addWidget(self.analog_filter_tab_widget)
        # --- Filter Controls ---
        controls_icon = JDXi.UI.IconRegistry.get_icon(
            JDXi.UI.IconRegistry.TUNE, color=JDXi.UI.Style.GREY
        )
        self.analog_filter_tab_widget.addTab(
            self._create_filter_controls_group(), controls_icon, "Controls"
        )
        # --- Filter ADSR ---
        adsr_icon = create_adsr_icon()
        self.analog_filter_tab_widget.addTab(
            self._create_filter_adsr_env_group(), adsr_icon, "ADSR"
        )
        layout.addSpacing(JDXi.UI.Style.SPACING)
        layout.addStretch()

    def _create_filter_controls_row(self) -> QHBoxLayout:
        """Filter controls row with individual buttons"""
        # Add label
        filter_label = QLabel("Filter")

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

        widgets = [filter_label]
        for filter_mode in filter_modes:
            btn = QPushButton(filter_mode.name)
            btn.setCheckable(True)
            # Add icon
            icon_name = filter_icon_map.get(filter_mode, "ri.filter-3-fill")
            icon = qta.icon(
                icon_name,
                color=JDXi.UI.Style.WHITE,
                icon_size=JDXi.UI.Dimensions.ICON.SIZE_SMALL,
            )
            btn.setIcon(icon)
            btn.setIconSize(QSize(20, 20))
            JDXi.UI.ThemeManager.apply_button_rect_analog(btn)
            btn.setFixedSize(
                JDXi.UI.Dimensions.WAVEFORM_ICON.WIDTH,
                JDXi.UI.Dimensions.WAVEFORM_ICON.HEIGHT,
            )
            btn.clicked.connect(
                lambda checked, mode=filter_mode: self._on_filter_mode_selected(mode)
            )
            self.filter_mode_buttons[filter_mode] = btn
            widgets.append(btn)

        return create_layout_with_widgets(widgets, vertical=False)

    def _on_filter_mode_selected(self, filter_mode: AnalogFilterType):
        """
        Handle filter mode button clicks

        :param filter_mode: AnalogFilterType enum value
        """
        # Reset all buttons to default style
        for btn in self.filter_mode_buttons.values():
            btn.setChecked(False)
            JDXi.UI.ThemeManager.apply_button_rect_analog(btn)

        # Apply active style to the selected filter mode button
        selected_btn = self.filter_mode_buttons.get(filter_mode)
        if selected_btn:
            selected_btn.setChecked(True)
            JDXi.UI.ThemeManager.apply_button_analog_active(selected_btn)

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
        """Controls Group - standardized order: FilterWidget, Resonance, KeyFollow, Velocity (harmonized with Digital)"""
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
            AnalogParam.FILTER_CUTOFF_KEYFOLLOW, "KeyFollow", vertical=True
        )
        self.filter_env_velocity_sens = self._create_parameter_slider(
            AnalogParam.FILTER_ENV_VELOCITY_SENSITIVITY,
            "Velocity",
            vertical=True,
        )
        # Standardized order: FilterWidget first, then Resonance, KeyFollow, Velocity
        controls_layout = create_layout_with_widgets(
            [
                self.filter_widget,
                self.filter_resonance,
                self.filter_cutoff_keyfollow,
                self.filter_env_velocity_sens,
            ]
        )
        # Use harmonized helper function (matching Digital Filter pattern)
        from jdxi_editor.ui.widgets.editor.helper import create_group_adsr_with_hlayout

        return create_group_adsr_with_hlayout(
            name="Controls", hlayout=controls_layout, analog=True
        )

    def _create_filter_adsr_env_group(self) -> QGroupBox:
        """Create filter ADSR group (harmonized with Digital Filter, includes centered icon)"""
        from jdxi_editor.ui.widgets.adsr.adsr import ADSR
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
        # Use standardized envelope group helper (centers icon automatically)
        return create_envelope_group(
            name="Envelope", adsr_widget=self.filter_adsr_widget, analog=True
        )
