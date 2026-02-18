"""
Analog Filter Section
"""

from enum import IntEnum, Enum, auto
from typing import Callable, Dict

from decologr import Decologr as log
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import JDXiSysExAddress
from jdxi_editor.midi.data.analog.filter import AnalogFilterType
from jdxi_editor.midi.data.parameter.analog.spec import JDXiMidiAnalog as Analog
from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.adsr.spec import ADSRSpec, ADSRStage
from jdxi_editor.ui.editors.base.filter.definition import FilterDefinition
from jdxi_editor.ui.editors.base.filter.spec import FilterLayoutSpec
from jdxi_editor.ui.editors.base.filter.widget import FilterWidgets
from jdxi_editor.ui.editors.base.layout.spec import FilterFeature
from jdxi_editor.ui.widgets.editor.helper import (
    create_group_adsr_with_hlayout,
    create_icon_from_name,
    create_layout_with_widgets,
    set_button_style_and_dimensions,
)
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget
from jdxi_editor.ui.widgets.filter.filter import FilterWidget
from jdxi_editor.ui.widgets.spec import FilterSpec, FilterWidgetSpec, SliderSpec


class FilterComponent(Enum):
    """Filter Components"""
    MODE_BUTTONS = auto()
    FILTER_CUTOFF = auto()
    FILTER_RESONANCE = auto()
    FILTER_DEPTH = auto()
    FILTER_CUTOFF_KEYFOLLOW = auto()
    FILTER_DEPTH_VELOCITY_SENS = auto()
    ADSR = auto()
    ADSR_DEPTH = auto()


class FilterWidgetFactory:
    def __init__(self):
        pass

    @staticmethod
    def create(
        spec, midi_helper, create_slider, create_switch, controls, address, analog
    ) -> QWidget:
        # spec is FilterWidgetSpec (cutoff_param, slope_param)
        return FilterWidget(
            cutoff_param=spec.cutoff_param,
            slope_param=spec.slope_param,
            midi_helper=midi_helper,
            create_parameter_slider=create_slider,
            create_parameter_switch=create_switch,
            controls=controls,
            address=address,
            analog=analog,
        )


class BaseFilterSection(SectionBaseWidget):
    """Base Filter Section"""

    spec_filter: dict = {}
    FILTER_WIDGET_SPEC: FilterWidgetSpec = None
    SYNTH_SPEC = JDXiMidiDigital
    # Subclasses (e.g. DigitalFilterSection) override these; do not set in __init__
    FILTER_MODE_ENABLED_MAP: dict = {}
    FILTER_PARAMS_LIST: list = []
    FILTER_MODE_MIDI_MAP: dict = {}

    def __init__(
        self,
        definition: FilterDefinition,
        address: JDXiSysExAddress,
        midi_helper: MidiIOHelper,
        send_midi_parameter: Callable | None = None,
        on_filter_mode_changed: Callable | None = None,
        analog: bool = False,
    ):
        """
        Initialize the AnalogFilterSection

        :param controls: dict[AddressParameter, QWidget] controls to add to
        :param address: RolandSysExAddress
        :param on_filter_mode_changed: Optional callback for filter mode changes
        """
        self.defn: FilterDefinition = definition
        self.widgets: FilterWidgets | None = None
        self.tab_widget: QTabWidget | None = None
        self.filter_resonance: QWidget | None = None
        self.filter_mode_buttons: dict = {}  # Dictionary to store filter mode buttons
        self._filter_mode_changed_callback: Callable = on_filter_mode_changed
        self.send_midi_parameter: Callable | None = send_midi_parameter

        super().__init__(
            send_midi_parameter=send_midi_parameter,
            midi_helper=midi_helper,
            address=address,
            analog=analog,
        )
        self.address = address
        # When analog=True, SectionBaseWidget skips _setup_ui(); build layout here so the tab widget is shown
        if getattr(self, "analog", False):
            self.setup_ui()
            if self._get_button_specs():
                self._initialize_button_states()

    def _build_filter_spec(self) -> dict[str, FilterSpec]:
        """build filter spec"""
        raise NotImplementedError("Must be implemented in subclass")

    def build_widgets(self):
        """build widgets"""
        if self._get_button_specs():
            self._create_waveform_buttons()
            if self.analog:
                self.filter_mode_buttons = self.button_widgets
        self.controls_group = self._create_controls_group()
        self._create_adsr_group()
        self._create_tab_widget()
        self.widgets = FilterWidgets(
            filter_widget=self.filter_widget,
            controls_group=self.controls_group,
            adsr_widget=getattr(self, "adsr_widget", None),
            filter_mode_buttons=self.filter_mode_buttons,
            tab_widget=self.tab_widget,
        )

    def setup_ui(self):
        """Setup the UI (standardized method name matching Digital Filter)"""
        layout = self.get_layout()
        JDXi.UI.Theme.apply_tabs_style(self.tab_widget, analog=self.analog)
        if self.button_widgets:
            button_layout = self._create_button_row_layout()
            if button_layout is not None:
                layout.addLayout(button_layout)
        layout.addWidget(self.tab_widget)

        layout.addSpacing(JDXi.UI.Style.SPACING)
        layout.addStretch()
        if self.analog and self._get_button_specs():
            self._initialize_button_states()

    def set_filter_mode(self, mode: IntEnum):
        """Set UI state"""
        for m, btn in self.filter_mode_buttons.items():
            btn.setChecked(m == mode)

        # --- MIDI send
        midi_value = self.defn.mode_to_midi[mode]

        if self.midi_helper:
            msg = self.sysex_composer.compose_message(
                address=self.address,
                param=self.defn.param_mode,
                value=midi_value,
            )
            if msg:
                self.midi_helper.send_midi_message(msg)

        # --- enable state
        self._apply_mode_state(mode)

        # --- notify
        if self._filter_mode_changed_callback:
            self._filter_mode_changed_callback(mode)

    def apply_midi_mode(self, midi_value: int):
        """Called from SysEx dispatcher"""
        mode = self.defn.midi_to_mode.get(midi_value, self.defn.bypass_mode)
        self._apply_mode_state(mode)

    def _apply_mode_state(self, mode: IntEnum):
        enabled = mode != self.defn.bypass_mode

        self.controls_group.setEnabled(enabled)

        if self.adsr_widget:
            self.adsr_widget.setEnabled(enabled)

        if hasattr(self, "filter_widget"):
            self.filter_widget.setEnabled(enabled)
            if hasattr(self.filter_widget, "plot"):
                self.filter_widget.plot.enabled = enabled
                self.filter_widget.plot.set_filter_mode(mode.name)
                self.filter_widget.plot.update()

    def _create_controls_group(self) -> QGroupBox:
        """Create controls group"""
        widget_spec = self.defn.widget_spec

        self.filter_widget = FilterWidgetFactory.create(
            spec=widget_spec,
            midi_helper=self.midi_helper,
            create_slider=self._create_parameter_slider,
            create_switch=self._create_parameter_switch,
            controls=self.controls,
            address=self.address,
            analog=self.analog,
        )

        # defn.sliders may be LayoutSpec (.controls) or dict (e.g. Digital "filter")
        slider_specs = (
            self.defn.sliders.controls
            if hasattr(self.defn.sliders, "controls")
            else self.defn.sliders.get("filter", self.defn.sliders.get("controls", []))
        )
        sliders = self._build_sliders(slider_specs)

        layout = create_layout_with_widgets([self.filter_widget, *sliders])
        return create_group_adsr_with_hlayout("Controls", layout, analog=self.analog)

    def _create_tab_widget(self):
        """Create tab widget. Idempotent: skip if already built (called from build_widgets and from SectionBaseWidget._setup_ui)."""
        if self.tab_widget is not None and self.tab_widget.count() > 0:
            return
        self.tab_widget = QTabWidget()
        self._create_tabs()
        JDXi.UI.Theme.apply_tabs_style(widget=self.tab_widget, analog=self.analog)
        JDXi.UI.Theme.apply_editor_style(widget=self.tab_widget, analog=self.analog)

    def _create_tabs(self):
        """_create_tabs"""
        if FilterFeature.FILTER_CUTOFF in self.spec.features:
            self._add_filter_tab()

        if FilterFeature.ADSR in self.spec.features:
            self._add_adsr_tab()

    def _add_adsr_tab(self):
        """Filter ADSR"""
        self._add_tab(key=self.SYNTH_SPEC.Filter.Tab.ADSR, widget=self.adsr_group)

    def _add_filter_tab(self):
        """Filter Controls"""
        self._add_tab(
            key=self.SYNTH_SPEC.Filter.Tab.CONTROLS, widget=self.controls_group
        )

    def update_controls_state(self, value: int) -> None:
        """
        Update filter controls enabled state based on filter mode value.
        Called when filter mode changes from SysEx data.

        :param value: int - Filter mode value (0=BYPASS, 1=LPF, 2=HPF, etc.)
        :return: None
        """
        # --- Normalize to int (callers may pass enum or wrong type)
        if value is not None and not isinstance(value, int):
            if hasattr(value, "value"):
                value = value.value
            try:
                value = int(value) if isinstance(value, (int, float)) else 0
            except (ValueError, TypeError):
                value = 0
        if value is None:
            value = 0

        try:
            selected_filter_mode = self.FILTER_MODE_ENABLED_MAP.get(value)
            _map_keys = (
                list(self.FILTER_MODE_ENABLED_MAP.keys())
                if self.FILTER_MODE_ENABLED_MAP
                else []
            )
            log.message(
                scope=self.__class__.__name__,
                message=f"update_controls_state: value={value} selected_filter_mode={selected_filter_mode!r} "
                f"FILTER_MODE_ENABLED_MAP keys={_map_keys}",
            )
            if selected_filter_mode is None:
                log.warning(
                    scope=self.__class__.__name__,
                    message=f"Unknown filter mode value: {value}, returning early",
                )
                return

            # --- Enable/disable controls based on filter mode
            is_bypass = selected_filter_mode == self.SYNTH_SPEC.Filter.Mode.BYPASS
            enabled = not is_bypass
            self.controls_group.setEnabled(enabled)
            log.message(
                scope=self.__class__.__name__,
                message=f"Set controls_group.setEnabled({enabled})",
            )
            if self.adsr_widget:
                self.adsr_widget.setEnabled(enabled)
                log.message(
                    scope=self.__class__.__name__,
                    message=f"Set adsr_widget.setEnabled({enabled})",
                )
            if hasattr(self, "filter_widget"):
                self.filter_widget.setEnabled(enabled)
                log.message(
                    scope=self.__class__.__name__,
                    message=f"Set filter_widget.setEnabled({enabled})",
                )
        except Exception as ex:
            log.error(f"Error {ex} occurred updating controls")

    def _on_button_selected(self, button_param):
        """Override to update filter mode in FilterWidget plot and enable/disable Controls sliders and ADSR"""
        # --- Call parent to handle button selection
        super()._on_button_selected(button_param)

        # --- Update enabled state of Controls sliders and filter widget (uses FILTER_MODE_* maps)
        if hasattr(button_param, "value"):
            self.update_controls_state(button_param.value)

        # --- Determine if bypass is selected
        is_bypass = button_param == self.SYNTH_SPEC.Filter.Mode.BYPASS
        enabled = not is_bypass

        # --- Update filter mode in FilterWidget plot
        if (
            hasattr(self, "filter_widget")
            and self.filter_widget
            and hasattr(self.filter_widget, "plot")
        ):
            filter_mode_str = self.FILTER_MODE_MIDI_MAP.get(
                button_param, self.SYNTH_SPEC.Filter.ModeType.LPF
            )
            self.filter_widget.filter_mode = filter_mode_str
            if hasattr(self.filter_widget.plot, "set_filter_mode"):
                self.filter_widget.plot.set_filter_mode(filter_mode_str)

            # --- Disable plot digital when bypass is selected
            self.filter_widget.plot.enabled = enabled
            self.filter_widget.plot.update()  # Trigger redraw

        # --- Enable/disable ADSR widget based on filter mode (like PWM widget)
        if self.adsr_widget:
            self.adsr_widget.setEnabled(enabled)

    def _build_layout_spec(self) -> FilterLayoutSpec:
        """build Analog Oscillator Layout Spec"""
        S = self.SYNTH_SPEC
        controls = [
            SliderSpec(
                S.Param.FILTER_RESONANCE,
                S.Param.FILTER_RESONANCE.display_name,
                vertical=True,
            ),
            SliderSpec(
                S.Param.FILTER_CUTOFF_KEYFOLLOW,
                S.Param.FILTER_CUTOFF_KEYFOLLOW.display_name,
                vertical=True,
            ),
            SliderSpec(
                S.Param.FILTER_ENV_VELOCITY_SENSITIVITY,
                S.Param.FILTER_ENV_VELOCITY_SENSITIVITY.display_name,
                vertical=True,
            ),
        ]
        if hasattr(S.Param, "FILTER_ENV_DEPTH"):
            filter_env_depth = [
                SliderSpec(
                    S.Param.FILTER_ENV_DEPTH,
                    S.Param.FILTER_ENV_DEPTH.display_name,
                    vertical=True,
                )
            ]
            controls = controls + filter_env_depth
        adsr: Dict[ADSRStage, ADSRSpec] = {
            ADSRStage.ATTACK: ADSRSpec(
                ADSRStage.ATTACK, S.Param.FILTER_ENV_ATTACK_TIME
            ),
            ADSRStage.DECAY: ADSRSpec(ADSRStage.DECAY, S.Param.FILTER_ENV_DECAY_TIME),
            ADSRStage.SUSTAIN: ADSRSpec(
                ADSRStage.SUSTAIN, S.Param.FILTER_ENV_SUSTAIN_LEVEL
            ),
            ADSRStage.RELEASE: ADSRSpec(
                ADSRStage.RELEASE, S.Param.FILTER_ENV_RELEASE_TIME
            ),
            ADSRStage.DEPTH: ADSRSpec(ADSRStage.DEPTH, S.Param.FILTER_ENV_DEPTH),
        }
        # Include default features so _create_tabs() adds Controls and ADSR tabs (Digital uses this; Analog overrides)
        features = {FilterFeature.FILTER_CUTOFF, FilterFeature.ADSR}
        feature_tabs = {
            FilterFeature.FILTER_CUTOFF: self._add_filter_tab,
            FilterFeature.ADSR: self._add_adsr_tab,
        }
        return FilterLayoutSpec(controls=controls, adsr=adsr, features=features, feature_tabs=feature_tabs)
