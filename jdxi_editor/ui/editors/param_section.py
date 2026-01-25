from typing import Callable, Literal, Dict, Union

from PySide6.QtWidgets import QTabWidget, QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.digital.filter import DigitalFilterMode
from jdxi_editor.midi.data.parameter.digital.partial import DigitalPartialParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.adsr.spec import ADSRStage
from jdxi_editor.ui.editors.widget_specs import SliderSpec, SwitchSpec, ComboBoxSpec
from jdxi_editor.ui.adsr.spec import ADSRSpec
from jdxi_editor.ui.widgets.adsr.adsr import ADSR
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import (
    create_adsr_icon,
    create_envelope_group,
    create_layout_with_widgets,
)
from jdxi_editor.midi.data.parameter.digital.spec import TabDefinitionMixin
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget
from picomidi.sysex.parameter.address import AddressParameter


class ParameterSectionBase(SectionBaseWidget):
    """
    Generalized section for Digital/Analog editor.

    Handles:
      - Parameter sliders, switches, combos (from specs)
      - Optional ADSR/envelope
      - Optional waveform/mode buttons
      - Tabs (Controls / ADSR / Custom)
      - MIDI parameter sending
    """

    PARAM_SPECS: list = []  # list of SliderSpec / SwitchSpec / ComboBoxSpec
    ADSR_SPEC: dict | None = None  # optional envelope parameters
    BUTTON_SPECS: list = []  # optional waveform/mode/shape buttons
    BUTTON_ENABLE_RULES: dict = {}  # optional rules for enabling controls per button

    def __init__(
        self,
        *,
        send_midi_parameter: Callable = None,
        midi_helper: MidiIOHelper = None,
        controls: dict = None,
        address: RolandSysExAddress = None,
        icons_row_type: Literal[
            IconType.ADSR, IconType.OSCILLATOR, IconType.GENERIC, IconType.NONE
        ] = IconType.OSCILLATOR,
        analog: bool = False,
    ):
        self.midi_helper = midi_helper
        self.address = address
        self.send_midi_parameter = send_midi_parameter

        self.tab_widget = None
        self.adsr_widget = None
        self.control_widgets = []
        self.button_widgets = {}

        super().__init__(icons_row_type=icons_row_type, analog=analog)
        # Set controls after super().__init__() to avoid it being overwritten
        self.controls: Dict[Union[DigitalPartialParam], QWidget] = controls or {}

        self.build_widgets()
        self.setup_ui()
        if self.BUTTON_SPECS:
            self._initialize_button_states()

    # -------------------------------
    # Build Widgets
    # -------------------------------
    def build_widgets(self):
        """Build sliders, switches, combo boxes, buttons, and ADSR"""
        from decologr import Decologr as log
        from jdxi_editor.midi.data.parameter.digital.partial import DigitalPartialParam

        class_name = self.__class__.__name__
        is_filter_section = class_name == "DigitalFilterSection"

        if is_filter_section:
            log.message(f"🔧 {class_name}.build_widgets() called")
            log.message(f"📋 PARAM_SPECS count: {len(self.PARAM_SPECS)}")
            log.message(f"📋 ADSR_SPEC: {self.ADSR_SPEC if self.ADSR_SPEC else 'None'}")

            # Check if FILTER_ENV_DEPTH is in PARAM_SPECS
            filter_env_depth_in_specs = any(
                (hasattr(spec.param, "name") and spec.param.name == "FILTER_ENV_DEPTH")
                or (spec.param == DigitalPartialParam.FILTER_ENV_DEPTH)
                for spec in self.PARAM_SPECS
            )
            if filter_env_depth_in_specs:
                log.message(f"✅ FILTER_ENV_DEPTH found in PARAM_SPECS")
            else:
                log.warning(f"⚠️ FILTER_ENV_DEPTH NOT in PARAM_SPECS!")

        self._create_parameter_widgets()
        if self.BUTTON_SPECS:
            self._create_waveform_buttons()
        if self.ADSR_SPEC:
            self._create_adsr()

    def _create_parameter_widgets(self):
        """Create widgets from PARAM_SPECS declaratively"""
        from decologr import Decologr as log
        from jdxi_editor.midi.data.parameter.digital.partial import DigitalPartialParam

        class_name = self.__class__.__name__
        is_filter_section = class_name == "DigitalFilterSection"

        if is_filter_section:
            log.message(
                f"🔧 Creating parameter widgets from {len(self.PARAM_SPECS)} specs"
            )

        for spec in self.PARAM_SPECS:
            param_name = getattr(spec.param, "name", str(spec.param))
            is_filter_env_depth = (
                hasattr(spec.param, "name") and spec.param.name == "FILTER_ENV_DEPTH"
            ) or (spec.param == DigitalPartialParam.FILTER_ENV_DEPTH)

            if is_filter_env_depth and is_filter_section:
                log.message(
                    f"🎯 Found FILTER_ENV_DEPTH in PARAM_SPECS: {spec.param}, label: {spec.label}"
                )

            if isinstance(spec, SliderSpec):
                widget = self._create_parameter_slider(
                    spec.param, spec.label, vertical=True
                )
                if is_filter_env_depth and is_filter_section:
                    log.message(
                        f"✅ Created FILTER_ENV_DEPTH slider widget: {widget}, type: {type(widget)}"
                    )
            elif isinstance(spec, SwitchSpec):
                widget = self._create_parameter_switch(
                    spec.param, spec.label, spec.options
                )
            elif isinstance(spec, ComboBoxSpec):
                widget = self._create_parameter_combo_box(
                    spec.param, spec.label, options=spec.options
                )
            else:
                if is_filter_env_depth and is_filter_section:
                    log.warning(
                        f"⚠️ FILTER_ENV_DEPTH spec is not SliderSpec/SwitchSpec/ComboBoxSpec: {type(spec)}"
                    )
                continue

            self.controls[spec.param] = widget
            if is_filter_env_depth and is_filter_section:
                log.message(
                    f"📝 Stored FILTER_ENV_DEPTH in controls dict: {spec.param} -> {widget}"
                )
                log.message(f"📊 Controls dict now has {len(self.controls)} entries")

            self.control_widgets.append(widget)
            if is_filter_env_depth and is_filter_section:
                log.message(
                    f"📦 Added FILTER_ENV_DEPTH to control_widgets list (total: {len(self.control_widgets)})"
                )

    def _create_adsr(self):
        """Create ADSR widget from ADSR_SPEC"""
        from decologr import Decologr as log
        from jdxi_editor.midi.data.parameter.digital.partial import DigitalPartialParam

        class_name = self.__class__.__name__
        is_filter_section = class_name == "DigitalFilterSection"

        if is_filter_section:
            log.message(f"🔧 Creating ADSR widget from ADSR_SPEC")
            log.message(f"📋 ADSR_SPEC keys: {list(self.ADSR_SPEC.keys())}")

        # Handle both string keys and ADSRType enum keys
        from jdxi_editor.ui.adsr.type import ADSRType

        attack_key = ADSRStage.ATTACK  #if "attack" in self.ADSR_SPEC else ADSRType.ATTACK
        decay_key = ADSRStage.DECAY # if "decay" in self.ADSR_SPEC else ADSRType.DECAY
        sustain_key = ADSRStage.SUSTAIN # if "sustain" in self.ADSR_SPEC else ADSRType.SUSTAIN
        release_key = ADSRStage.RELEASE # "release" in self.ADSR_SPEC else ADSRType.RELEASE
        peak_key = ADSRStage.PEAK #  if "peak" in self.ADSR_SPEC else ADSRType.PEAK

        # Extract parameters from ADSR_SPEC (handles both ADSRSpec objects and direct parameters)
        def get_param(spec_or_param):
            """Extract parameter from ADSRSpec or return parameter directly"""
            if isinstance(spec_or_param, ADSRSpec):
                return spec_or_param.param
            return spec_or_param

        attack_spec = self.ADSR_SPEC.get(attack_key)
        decay_spec = self.ADSR_SPEC.get(decay_key)
        sustain_spec = self.ADSR_SPEC.get(sustain_key)
        release_spec = self.ADSR_SPEC.get(release_key)
        peak_spec = self.ADSR_SPEC.get(peak_key) if peak_key else None

        attack_param = get_param(attack_spec) if attack_spec else None
        decay_param = get_param(decay_spec) if decay_spec else None
        sustain_param = get_param(sustain_spec) if sustain_spec else None
        release_param = get_param(release_spec) if release_spec else None
        peak_param = get_param(peak_spec) if peak_spec else None

        if peak_param:
            peak_name = getattr(peak_param, "name", str(peak_param))
            if is_filter_section:
                log.message(f"🎯 ADSR peak_param: {peak_param} (name: {peak_name})")
            is_filter_env_depth = (
                hasattr(peak_param, "name") and peak_param.name == "FILTER_ENV_DEPTH"
            ) or (peak_param == DigitalPartialParam.FILTER_ENV_DEPTH)
            if is_filter_env_depth and is_filter_section:
                log.message(f"✅ Peak param is FILTER_ENV_DEPTH")
                # Check if it exists in controls
                if peak_param in self.controls:
                    existing_widget = self.controls[peak_param]
                    log.message(
                        f"📝 FILTER_ENV_DEPTH already in controls: {existing_widget}, type: {type(existing_widget)}"
                    )
                else:
                    log.warning(f"⚠️ FILTER_ENV_DEPTH NOT found in controls dict!")
                    log.message(f"📊 Controls dict has {len(self.controls)} entries")
                    log.message(
                        f"📋 Controls keys: {[getattr(k, 'name', str(k)) for k in self.controls.keys()]}"
                    )
        else:
            if is_filter_section:
                log.warning(f"⚠️ No peak parameter in ADSR_SPEC")

        self.adsr_widget = ADSR(
            attack_param=attack_param,
            decay_param=decay_param,
            sustain_param=sustain_param,
            release_param=release_param,
            peak_param=peak_param,  # Optional peak parameter
            midi_helper=self.midi_helper,
            create_parameter_slider=self._create_parameter_slider,
            controls=self.controls,
            address=self.address,
            analog=self.analog,
        )

        if peak_param and is_filter_section:
            peak_name = getattr(peak_param, "name", str(peak_param))
            log.message(f"✅ ADSR widget created with peak_param: {peak_name}")
            if hasattr(self.adsr_widget, "peak_control"):
                log.message(
                    f"✅ ADSR widget has peak_control: {self.adsr_widget.peak_control}, type: {type(self.adsr_widget.peak_control)}"
                )
            else:
                log.warning(f"⚠️ ADSR widget does NOT have peak_control attribute")

    # -------------------------------
    # Layout & Tabs
    # -------------------------------
    def setup_ui(self):
        """Assemble section UI"""
        layout = self.create_layout()
        if self.button_widgets:
            button_layout = self._create_button_row_layout()
            if button_layout is not None:
                layout.addLayout(button_layout)
        self._create_tab_widget()
        layout.addWidget(self.tab_widget)
        layout.addStretch()

    def _add_tab(
        self,
        *,
        key: TabDefinitionMixin,
        widget: QWidget,
    ) -> None:
        """Add a tab using TabDefinitionMixin pattern"""
        from jdxi_editor.midi.data.digital.oscillator import WaveformType
        
        # Handle both regular icons and generated waveform icons
        waveform_type_values = {
            WaveformType.ADSR,
            WaveformType.UPSAW,
            WaveformType.SQUARE,
            WaveformType.PWSQU,
            WaveformType.TRIANGLE,
            WaveformType.SINE,
            WaveformType.SAW,
            WaveformType.SPSAW,
            WaveformType.PCM,
            WaveformType.NOISE,
            WaveformType.LPF_FILTER,
            WaveformType.HPF_FILTER,
            WaveformType.BYPASS_FILTER,
            WaveformType.BPF_FILTER,
            WaveformType.FILTER_SINE,
        }
        
        # Handle icon - could be a string (qtawesome icon name) or WaveformType value
        if isinstance(key.icon, str) and key.icon in waveform_type_values:
            # Use generated icon for waveform types
            icon = JDXi.UI.Icon.get_generated_icon(key.icon)
        elif isinstance(key.icon, str) and key.icon.startswith("mdi."):
            # Direct qtawesome icon name (e.g., "mdi.numeric-1-circle-outline")
            icon = JDXi.UI.Icon.get_icon(key.icon, color=JDXi.UI.Style.GREY)
        else:
            # Use regular icon from registry
            icon = JDXi.UI.Icon.get_icon(key.icon, color=JDXi.UI.Style.GREY)
        
        self.tab_widget.addTab(
            widget,
            icon,
            key.label,
        )
        setattr(self, key.attr_name, widget)

    def _create_tab_widget(self):
        """Create tab widget with controls and optional ADSR"""
        self.tab_widget = QTabWidget()

        # Controls tab
        controls_widget = QWidget()
        controls_layout = create_layout_with_widgets(self.control_widgets)
        controls_widget.setLayout(controls_layout)
        self.tab_widget.addTab(
            controls_widget,
            JDXi.UI.Icon.get_icon(JDXi.UI.Icon.TUNE, JDXi.UI.Style.GREY),
            "Controls",
        )

        # ADSR tab
        if self.adsr_widget:
            adsr_group = create_envelope_group(
                "Envelope", adsr_widget=self.adsr_widget, analog=self.analog
            )
            self.tab_widget.addTab(adsr_group, create_adsr_icon(), "ADSR")

    # -------------------------------
    # Button Logic
    # -------------------------------
    def _on_button_selected(self, button_param):
        """Handle button selection & enabling dependent widgets"""
        for btn in self.button_widgets.values():
            btn.setChecked(False)
            btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)
        selected_btn = self.button_widgets[button_param]
        selected_btn.setChecked(True)
        selected_btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT_ACTIVE)
        self._update_button_enabled_states(button_param)
        if self.send_midi_parameter:
            # Map filter mode enums to their corresponding parameter
            if isinstance(button_param, DigitalFilterMode):
                # Filter mode buttons map to FILTER_MODE_SWITCH parameter
                actual_param = DigitalPartialParam.FILTER_MODE_SWITCH
                param_value = button_param.value
            else:
                # For other button types (like waveform), use the param directly
                actual_param = button_param
                param_value = getattr(button_param, "value", button_param)

            # Ensure we have a valid AddressParameter before sending
            if not isinstance(actual_param, AddressParameter):
                from decologr import Decologr as log

                log.error(
                    f"Cannot send MIDI: {button_param} is not an AddressParameter (got {type(button_param)})"
                )
                return

            self.send_midi_parameter(actual_param, param_value)

    def _update_button_enabled_states(self, button_param):
        """Enable/disable controls based on BUTTON_ENABLE_RULES"""
        # Disable all first
        for attrs in self.BUTTON_ENABLE_RULES.values():
            for attr in attrs:
                getattr(self, attr, None).setEnabled(False)
        # Enable per selected button
        for attr in self.BUTTON_ENABLE_RULES.get(button_param, []):
            getattr(self, attr, None).setEnabled(True)

    def _initialize_button_states(self):
        """Set initial button state (first in BUTTON_SPECS)"""
        if self.BUTTON_SPECS:
            first_param = self.BUTTON_SPECS[0].param
            self._on_button_selected(first_param)

    def _create_button_row_layout(self):
        """Create layout for button row. Override in subclasses."""
        if not self.button_widgets:
            return None
        from PySide6.QtWidgets import QHBoxLayout

        from jdxi_editor.ui.widgets.editor.helper import create_layout_with_widgets

        layout = QHBoxLayout()
        layout.addStretch()
        layout.addLayout(create_layout_with_widgets(list(self.button_widgets.values())))
        layout.addStretch()
        return layout
