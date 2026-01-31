"""
Analog Filter Section
"""

from typing import Callable, Dict, Optional, Union

from picomidi.sysex.parameter.address import AddressParameter
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
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import (
    create_group_adsr_with_hlayout,
    create_icon_from_name,
    create_layout_with_widgets,
    set_button_style_and_dimensions,
)
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget
from jdxi_editor.ui.widgets.filter.analog_filter import AnalogFilterWidget


class BaseFilterSection(SectionBaseWidget):
    """Base Filter Section"""

    FILTER_SPECS: dict = {}

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
        self._filter_mode_changed_callback: Callable = on_filter_mode_changed

        # Get midi_helper from parent if available
        midi_helper = None
        if parent and hasattr(parent, 'midi_helper'):
            midi_helper = parent.midi_helper
        
        super().__init__(icons_row_type=IconType.ADSR, analog=True, midi_helper=midi_helper)
        # Set attributes after super().__init__() to avoid them being overwritten
        self.controls: Dict[Union[Analog.Param], QWidget] = controls or {}
        self.address = address

    def build_widgets(self):
        """build widgets"""
        self.controls_group = self._create_controls_group()
        self._create_adsr_group()
        self._create_tab_widget()

    def setup_ui(self):
        """Setup the UI (standardized method name matching Digital Filter)"""
        layout = self.get_layout()
        JDXi.UI.Theme.apply_tabs_style(self.tab_widget, analog=True)

        # --- Filter Selection Buttons ---
        self.filter_row = filter_row = self._create_filter_controls_row()
        if filter_row:
            layout.addLayout(filter_row)
        layout.addWidget(self.tab_widget)

        layout.addSpacing(JDXi.UI.Style.SPACING)
        layout.addStretch()

    def _create_tab_widget(self):
        """create tab widget"""
        self.tab_widget = QTabWidget()
        # --- Filter Controls ---
        self._add_tab(key=Analog.Filter.Tab.CONTROLS, widget=self.controls_group)
        # --- Filter ADSR ---
        self._add_tab(key=Analog.Filter.Tab.ADSR, widget=self.adsr_group)

    def _create_filter_controls_row(self) -> QHBoxLayout:
        """Create the filter controls row with buttons for each filter mode."""
        self.filter_label = QLabel("Filter")

        self.filter_mode_control_button_widgets: list[QWidget] = [self.filter_label]
        # Create buttons dynamically based on the FilterSpec configurations
        for filter_mode, spec in self.FILTER_SPECS.items():
            button = QPushButton()
            icon = create_icon_from_name(spec.icon)
            button.setIcon(icon)
            button.setText(spec.name)
            button.setToolTip(spec.description)
            set_button_style_and_dimensions(button, JDXi.UI.Dimensions.WaveformIcon)
            button.clicked.connect(
                lambda checked, mode=filter_mode: self._on_filter_mode_selected(mode)
            )
            self.filter_mode_buttons[filter_mode] = button
            self.filter_mode_control_button_widgets.append(button)
        filter_row = create_layout_with_widgets(self.filter_mode_control_button_widgets, vertical=False)
        return filter_row
        
    def _on_filter_mode_selected(self, filter_mode: AnalogFilterType):
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

        # --- Notify parent so it can update filter controls enabled state
        if self._filter_mode_changed_callback:
            self._filter_mode_changed_callback(filter_mode.value)

    def _create_controls_group(self) -> QGroupBox:
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
        controls_layout = create_layout_with_widgets(
            [
                self.filter_widget,
                self.filter_resonance,
                self.filter_cutoff_keyfollow,
                self.filter_env_velocity_sens,
            ]
        )
        return create_group_adsr_with_hlayout(
            name="Controls", hlayout=controls_layout, analog=True
        )
