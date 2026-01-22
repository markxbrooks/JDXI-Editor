from typing import Callable

from PySide6.QtWidgets import QWidget, QTabWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.digital.filter import DigitalFilterMode
from jdxi_editor.midi.data.parameter.digital.partial import DigitalPartialParam
from jdxi_editor.ui.editors.widget_specs import SliderSpec, SwitchSpec
from jdxi_editor.ui.widgets.adsr.adsr import ADSR
from jdxi_editor.ui.widgets.editor import SectionBaseWidget, IconType
from jdxi_editor.ui.widgets.editor.helper import create_button_with_icon, create_layout_with_widgets, \
    create_envelope_group, create_adsr_icon
from picomidi.sysex.parameter.address import AddressParameter


class ComboBoxSpec:
    pass


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
        create_parameter_slider: Callable,
        create_parameter_switch: Callable = None,
        create_parameter_combo_box: Callable = None,
        send_midi_parameter: Callable = None,
        midi_helper=None,
        controls: dict = None,
        address=None,
        icon_type: str = IconType.NONE,
        analog: bool = False,
    ):
        self.midi_helper = midi_helper
        self.controls = controls or {}
        self.address = address
        self.send_midi_parameter = send_midi_parameter

        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_switch = create_parameter_switch
        self._create_parameter_combo_box = create_parameter_combo_box

        self.tab_widget = None
        self.adsr_widget = None
        self.control_widgets = []
        self.button_widgets = {}

        super().__init__(icon_type=icon_type, analog=analog)

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
                (hasattr(spec.param, 'name') and spec.param.name == 'FILTER_ENV_DEPTH') or 
                (spec.param == DigitalPartialParam.FILTER_ENV_DEPTH)
                for spec in self.PARAM_SPECS
            )
            if filter_env_depth_in_specs:
                log.message(f"✅ FILTER_ENV_DEPTH found in PARAM_SPECS")
            else:
                log.warning(f"⚠️ FILTER_ENV_DEPTH NOT in PARAM_SPECS!")
        
        self._create_parameter_widgets()
        if self.BUTTON_SPECS:
            self._create_buttons()
        if self.ADSR_SPEC:
            self._create_adsr()

    def _create_parameter_widgets(self):
        """Create widgets from PARAM_SPECS declaratively"""
        from decologr import Decologr as log
        from jdxi_editor.midi.data.parameter.digital.partial import DigitalPartialParam
        
        class_name = self.__class__.__name__
        is_filter_section = class_name == "DigitalFilterSection"
        
        if is_filter_section:
            log.message(f"🔧 Creating parameter widgets from {len(self.PARAM_SPECS)} specs")
        
        for spec in self.PARAM_SPECS:
            param_name = getattr(spec.param, 'name', str(spec.param))
            is_filter_env_depth = (hasattr(spec.param, 'name') and 
                                  spec.param.name == 'FILTER_ENV_DEPTH') or \
                                 (spec.param == DigitalPartialParam.FILTER_ENV_DEPTH)
            
            if is_filter_env_depth and is_filter_section:
                log.message(f"🎯 Found FILTER_ENV_DEPTH in PARAM_SPECS: {spec.param}, label: {spec.label}")
            
            if isinstance(spec, SliderSpec):
                widget = self._create_parameter_slider(spec.param, spec.label, vertical=True)
                if is_filter_env_depth and is_filter_section:
                    log.message(f"✅ Created FILTER_ENV_DEPTH slider widget: {widget}, type: {type(widget)}")
            elif isinstance(spec, SwitchSpec):
                widget = self._create_parameter_switch(spec.param, spec.label, spec.options)
            elif isinstance(spec, ComboBoxSpec):
                widget = self._create_parameter_combo_box(spec.param, spec.label, options=spec.options)
            else:
                if is_filter_env_depth and is_filter_section:
                    log.warning(f"⚠️ FILTER_ENV_DEPTH spec is not SliderSpec/SwitchSpec/ComboBoxSpec: {type(spec)}")
                continue
            
            self.controls[spec.param] = widget
            if is_filter_env_depth and is_filter_section:
                log.message(f"📝 Stored FILTER_ENV_DEPTH in controls dict: {spec.param} -> {widget}")
                log.message(f"📊 Controls dict now has {len(self.controls)} entries")
            
            self.control_widgets.append(widget)
            if is_filter_env_depth and is_filter_section:
                log.message(f"📦 Added FILTER_ENV_DEPTH to control_widgets list (total: {len(self.control_widgets)})")

    def _create_buttons(self):
        """Create mode/waveform/shape buttons from BUTTON_SPECS"""
        from PySide6.QtWidgets import QPushButton
        from PySide6.QtGui import QIcon
        from PySide6.QtCore import QSize
        
        for spec in self.BUTTON_SPECS:
            # Handle both SliderSpec (has 'label') and other specs (may have 'name')
            button_label = getattr(spec, 'label', getattr(spec, 'name', 'Button'))
            icon_name_str = getattr(spec, 'icon_name', None)
            
            # Create button
            btn = QPushButton(button_label)
            btn.setCheckable(True)
            btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)
            
            # Create icon if icon_name is provided
            if icon_name_str:
                icon = None
                try:
                    # Try to get the WaveformIconType value (it's a class with string constants)
                    from jdxi_editor.midi.data.digital.oscillator import WaveformIconType
                    # Check if icon_name_str matches a WaveformIconType attribute
                    icon_type_value = getattr(WaveformIconType, icon_name_str, None)
                    if icon_type_value is not None:
                        # Use generate_waveform_icon directly for waveform/filter icons
                        from jdxi_editor.ui.image.waveform import generate_waveform_icon
                        from jdxi_editor.ui.image.utils import base64_to_pixmap
                        icon_base64 = generate_waveform_icon(icon_type_value, JDXi.UI.Style.WHITE, 1.0)
                        pixmap = base64_to_pixmap(icon_base64)
                        if pixmap and not pixmap.isNull():
                            icon = QIcon(pixmap)
                except (AttributeError, KeyError, TypeError):
                    pass
                
                # If not a waveform icon, try registry or QTA
                if icon is None or icon.isNull():
                    try:
                        # Try to get icon from registry (which also uses generate_waveform_icon)
                        icon = JDXi.UI.IconRegistry.get_generated_icon(icon_name_str)
                    except (AttributeError, KeyError):
                        try:
                            # Try to create from QTA icon name
                            from jdxi_editor.ui.widgets.editor.helper import create_icon_from_qta
                            icon = create_icon_from_qta(icon_name_str)
                        except:
                            icon = None
                
                if icon and not icon.isNull():
                    btn.setIcon(icon)
                    btn.setIconSize(QSize(JDXi.UI.Dimensions.LFOIcon.WIDTH, JDXi.UI.Dimensions.LFOIcon.HEIGHT))
            
            btn.setFixedSize(
                JDXi.UI.Dimensions.WAVEFORM_ICON.WIDTH,
                JDXi.UI.Dimensions.WAVEFORM_ICON.HEIGHT,
            )
            
            btn.clicked.connect(lambda _, b=spec.param: self._on_button_selected(b))
            self.button_widgets[spec.param] = btn
            # Only store in controls if it's a parameter enum, not a mode enum (like DigitalFilterMode)
            if not isinstance(spec.param, DigitalFilterMode):
                self.controls[spec.param] = btn
        
        # For compatibility with code that expects filter_mode_buttons (DigitalFilterSection)
        # or wave_buttons (DigitalOscillatorSection), create an alias
        if hasattr(self, 'BUTTON_SPECS') and self.BUTTON_SPECS:
            # Check if this is a filter section by checking the first param type
            first_param = self.BUTTON_SPECS[0].param
            if isinstance(first_param, DigitalFilterMode):
                self.filter_mode_buttons = self.button_widgets

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
        
        attack_key = "attack" if "attack" in self.ADSR_SPEC else ADSRType.ATTACK
        decay_key = "decay" if "decay" in self.ADSR_SPEC else ADSRType.DECAY
        sustain_key = "sustain" if "sustain" in self.ADSR_SPEC else ADSRType.SUSTAIN
        release_key = "release" if "release" in self.ADSR_SPEC else ADSRType.RELEASE
        peak_key = "peak" if "peak" in self.ADSR_SPEC else ADSRType.PEAK
        
        peak_param = self.ADSR_SPEC.get(peak_key) if peak_key else None
        if peak_param:
            peak_name = getattr(peak_param, 'name', str(peak_param))
            if is_filter_section:
                log.message(f"🎯 ADSR peak_param: {peak_param} (name: {peak_name})")
            is_filter_env_depth = (hasattr(peak_param, 'name') and 
                                  peak_param.name == 'FILTER_ENV_DEPTH') or \
                                 (peak_param == DigitalPartialParam.FILTER_ENV_DEPTH)
            if is_filter_env_depth and is_filter_section:
                log.message(f"✅ Peak param is FILTER_ENV_DEPTH")
                # Check if it exists in controls
                if peak_param in self.controls:
                    existing_widget = self.controls[peak_param]
                    log.message(f"📝 FILTER_ENV_DEPTH already in controls: {existing_widget}, type: {type(existing_widget)}")
                else:
                    log.warning(f"⚠️ FILTER_ENV_DEPTH NOT found in controls dict!")
                    log.message(f"📊 Controls dict has {len(self.controls)} entries")
                    log.message(f"📋 Controls keys: {[getattr(k, 'name', str(k)) for k in self.controls.keys()]}")
        else:
            if is_filter_section:
                log.warning(f"⚠️ No peak parameter in ADSR_SPEC")
        
        self.adsr_widget = ADSR(
            attack_param=self.ADSR_SPEC[attack_key],
            decay_param=self.ADSR_SPEC[decay_key],
            sustain_param=self.ADSR_SPEC[sustain_key],
            release_param=self.ADSR_SPEC[release_key],
            peak_param=peak_param,  # Optional peak parameter
            midi_helper=self.midi_helper,
            create_parameter_slider=self._create_parameter_slider,
            controls=self.controls,
            address=self.address,
            analog=self.analog,
        )
        
        if peak_param and is_filter_section:
            peak_name = getattr(peak_param, 'name', str(peak_param))
            log.message(f"✅ ADSR widget created with peak_param: {peak_name}")
            if hasattr(self.adsr_widget, 'peak_control'):
                log.message(f"✅ ADSR widget has peak_control: {self.adsr_widget.peak_control}, type: {type(self.adsr_widget.peak_control)}")
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

    def _create_tab_widget(self):
        """Create tab widget with controls and optional ADSR"""
        self.tab_widget = QTabWidget()

        # Controls tab
        controls_widget = QWidget()
        controls_layout = create_layout_with_widgets(self.control_widgets)
        controls_widget.setLayout(controls_layout)
        self.tab_widget.addTab(controls_widget, JDXi.UI.IconRegistry.get_icon(JDXi.UI.IconRegistry.TUNE, JDXi.UI.Style.GREY), "Controls")

        # ADSR tab
        if self.adsr_widget:
            adsr_group = create_envelope_group("Envelope", adsr_widget=self.adsr_widget, analog=self.analog)
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
                param_value = getattr(button_param, 'value', button_param)
            
            # Ensure we have a valid AddressParameter before sending
            if not isinstance(actual_param, AddressParameter):
                from decologr import Decologr as log
                log.error(f"Cannot send MIDI: {button_param} is not an AddressParameter (got {type(button_param)})")
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
