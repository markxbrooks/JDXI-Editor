"""
Analog Filter Section
"""

from typing import Callable, Dict, Optional, Union

import qtawesome as qta
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

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.analog.filter import AnalogFilterType
from jdxi_editor.midi.data.parameter.analog.address import AnalogParam
from jdxi_editor.midi.data.parameter.analog.spec import JDXiMidiAnalog as Analog
from jdxi_editor.ui.adsr.spec import ADSRSpec, ADSRStage
from jdxi_editor.ui.editors.widget_specs import SliderSpec, FilterSpec
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import create_layout_with_widgets
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget
from jdxi_editor.ui.widgets.filter.analog_filter import AnalogFilterWidget


class AnalogFilterSection(SectionBaseWidget):
    """Analog Filter Section"""

    ADSR_SPEC: Dict[ADSRStage, ADSRSpec] = {
        ADSRStage.ATTACK: ADSRSpec(ADSRStage.ATTACK, Analog.Param.FILTER_ENV_ATTACK_TIME),
        ADSRStage.DECAY: ADSRSpec(ADSRStage.DECAY, Analog.Param.FILTER_ENV_DECAY_TIME),
        ADSRStage.SUSTAIN: ADSRSpec(ADSRStage.SUSTAIN, Analog.Param.FILTER_ENV_SUSTAIN_LEVEL),
        ADSRStage.RELEASE: ADSRSpec(ADSRStage.RELEASE, Analog.Param.FILTER_ENV_RELEASE_TIME),
        ADSRStage.PEAK: ADSRSpec(ADSRStage.PEAK, Analog.Param.FILTER_ENV_DEPTH),
    }

    SLIDER_GROUPS = {
        "filter": [
            SliderSpec(AnalogParam.FILTER_RESONANCE, "Resonance", vertical=True),
            SliderSpec(AnalogParam.FILTER_CUTOFF_KEYFOLLOW, "KeyFollow", vertical=True),
            SliderSpec(AnalogParam.FILTER_ENV_VELOCITY_SENSITIVITY, "Velocity", vertical=True),
        ],
    }
    
    FILTER_SPEC: Dict[AnalogFilterType, Dict[str, Any]] = {
        AnalogFilterType.BYPASS: {
            "param": None,  # No parameter adjustments for bypass
            "icon": JDXi.UI.Icon.POWER,  # Power/off icon
            "label": "Bypass",
        },
        AnalogFilterType.LPF: {
            "param": Analog.Param.FILTER_CUTOFF_FREQUENCY,  # Key parameter for low-pass filter
            "icon": JDXi.UI.Icon.FILTER,  # Filter icon
            "label": "Low Pass",
        },
    }

    def __init__(
        self,
        controls: dict[AddressParameter, QWidget],
        address: RolandSysExAddress,
        on_filter_mode_changed: Callable = None,
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize the AnalogFilterSection

        :param controls: dict[AddressParameter, QWidget] controls to add to
        :param address: RolandSysExAddress
        :param on_filter_mode_changed: Optional callback for filter mode changes
        """
        self.tab_widget: QTabWidget | None = None
        self.filter_resonance: QWidget | None = None
        self.filter_mode_buttons: dict = {}  # Dictionary to store filter mode buttons
        self._on_filter_mode_changed: Callable = on_filter_mode_changed

        # Get midi_helper from parent if available
        midi_helper = None
        if parent and hasattr(parent, 'midi_helper'):
            midi_helper = parent.midi_helper
        
        super().__init__(icons_row_type=IconType.ADSR, analog=True, midi_helper=midi_helper)
        # Set attributes after super().__init__() to avoid them being overwritten
        self.controls: Dict[Union[Analog.Param], QWidget] = controls or {}
        self.address = address

        self.build_widgets()
        self.setup_ui()

    def build_widgets(self):
        """build widgets"""
        self.filter_controls_group = self._create_filter_controls_group()
        self._create_adsr_group()
        self._create_tab_widget()

    def setup_ui(self):
        """Setup the UI (standardized method name matching Digital Filter)"""
        layout = self.get_layout()
        JDXi.UI.Theme.apply_tabs_style(self.tab_widget, analog=True)

        # --- Filter Selection Buttons ---
        filter_row = self._create_filter_controls_row()
        if filter_row:
            layout.addLayout(filter_row)
        layout.addWidget(self.tab_widget)

        layout.addSpacing(JDXi.UI.Style.SPACING)
        layout.addStretch()

    def _create_tab_widget(self):
        """create tab widget"""
        self.tab_widget = QTabWidget()
        # --- Filter Controls ---
        self._add_tab(key=Analog.Filter.Tab.CONTROLS, widget=self.filter_controls_group)
        # --- Filter ADSR ---
        self._add_tab(key=Analog.Filter.Tab.ADSR, widget=self.adsr_group)

    def _create_filter_controls_row_new(self) -> QHBoxLayout:
        """Create the filter controls row with buttons for each filter mode."""
        self.filter_label = QLabel("Filter")
        
        layout = QHBoxLayout()
        layout.addWidget(self.filter_label)
    
        # Create buttons dynamically based on the FilterSpec configurations
        for filter_mode, spec in FILTER_SPECS.items():
            button = QPushButton()
            button.setIcon(spec.icon)
            button.setText(spec.name)
            button.setToolTip(spec.description)
            button.clicked.connect(
                lambda _, mode=filter_mode: self._on_filter_mode_changed(mode)
            )
            self.filter_mode_buttons[filter_mode] = button
            layout.addWidget(button)
    
        return layout
        
    def _on_filter_mode_changed_new(self, filter_mode: AnalogFilterType):
        """Handle changes to the filter mode."""
        spec = FILTER_SPECS[filter_mode]
        print(f"Switching to {spec.name} mode.")
        if spec.param:
            # Update the corresponding parameter in the UI or MIDI message handling
            self.midi_helper.send_param_change(spec.param)

    def _create_filter_controls_row(self) -> QHBoxLayout:
        """Filter controls row with individual buttons"""
        # --- Add label - store as instance attribute to prevent garbage collection
        self.filter_label = QLabel("Filter")

        # --- Create buttons for each filter mode
        filter_modes = [
            AnalogFilterType.BYPASS,
            AnalogFilterType.LPF,
        ]

        # --- Map filter modes to icon names
        filter_icon_map = {
            AnalogFilterType.BYPASS: JDXi.UI.Icon.POWER,  # Power/off icon for bypass
            AnalogFilterType.LPF: JDXi.UI.Icon.FILTER,  # Filter icon for LPF
        }

        self.filter_mode_control_button_widgets = [self.filter_label]
        for filter_mode in filter_modes:
            btn = QPushButton(filter_mode.name)
            btn.setCheckable(True)
            # --- Add icon
            icon_name = filter_icon_map.get(filter_mode, JDXi.UI.Icon.FILTER)
            icon = qta.icon(
                icon_name,
                color=JDXi.UI.Style.WHITE,
                icon_size=JDXi.UI.Dimensions.ICON.SIZE_SMALL,
            )
            btn.setIcon(icon)
            btn.setIconSize(QSize(20, 20))
            JDXi.UI.Theme.apply_button_rect_analog(btn)
            btn.setFixedSize(
                JDXi.UI.Dimensions.WAVEFORM_ICON.WIDTH,
                JDXi.UI.Dimensions.WAVEFORM_ICON.HEIGHT,
            )
            btn.clicked.connect(
                lambda checked, mode=filter_mode: self._on_filter_mode_selected(mode)
            )
            self.filter_mode_buttons[filter_mode] = btn
            self.filter_mode_control_button_widgets.append(btn)

        # --- Store the layout as instance attribute to prevent garbage collection
        self.filter_controls_row_layout = create_layout_with_widgets(self.filter_mode_control_button_widgets, vertical=False)
        return self.filter_controls_row_layout

    def _on_filter_mode_selected(self, filter_mode):
        """
        Handle filter mode button clicks

        :param filter_mode: Analog.Filter.FilterType enum value
        """
        # --- Reset all buttons to default style
        for btn in self.filter_mode_buttons.values():
            btn.setChecked(False)
            JDXi.UI.Theme.apply_button_rect_analog(btn)

        # --- Apply active style to the selected filter mode button
        selected_btn = self.filter_mode_buttons.get(filter_mode)
        if selected_btn:
            selected_btn.setChecked(True)
            JDXi.UI.Theme.apply_button_analog_active(selected_btn)

        # --- Send MIDI message via SysEx (analog synth uses SysEx, not control changes)
        if self.midi_helper and self.address:
            sysex_message = self.sysex_composer.compose_message(
                address=self.address,
                param=Analog.Param.FILTER_MODE_SWITCH,
                value=filter_mode.value,
            )
            if sysex_message:
                self.midi_helper.send_midi_message(sysex_message)

        # --- Update filter controls state
        if self._on_filter_mode_changed:
            self._on_filter_mode_changed(filter_mode.value)

    def _create_filter_controls_group(self) -> QGroupBox:
        """Controls Group - standardized order: FilterWidget, Resonance, KeyFollow, Velocity (harmonized with Digital)"""
        self.filter_widget = AnalogFilterWidget(
            cutoff_param=Analog.Param.FILTER_CUTOFF,
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
        # (self.filter_resonance, self.filter_cutoff_keyfollow, self.filter_env_velocity_sens) = self._build_sliders(self.SLIDER_GROUPS["filter"])
        # --- Standardized order: FilterWidget first, then Resonance, KeyFollow, Velocity
        controls_layout = create_layout_with_widgets(
            [
                self.filter_widget,
                self.filter_resonance,
                self.filter_cutoff_keyfollow,
                self.filter_env_velocity_sens,
            ]
        )
        # --- Use harmonized helper function (matching Digital Filter pattern)
        from jdxi_editor.ui.widgets.editor.helper import create_group_adsr_with_hlayout

        return create_group_adsr_with_hlayout(
            name="Controls", hlayout=controls_layout, analog=True
        )
