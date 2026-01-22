"""
Digital Filter Section for the JDXI Editor
"""

from decologr import Decologr as log
from jdxi_editor.midi.data.digital.filter import DigitalFilterMode
from jdxi_editor.midi.data.parameter.digital.name import DigitalDisplayName
from jdxi_editor.midi.data.parameter.digital.partial import DigitalPartialParam
from jdxi_editor.ui.adsr.type import ADSRType
from jdxi_editor.ui.editors.param_section import ParameterSectionBase
from jdxi_editor.ui.editors.widget_specs import SliderSpec
from jdxi_editor.midi.data.digital.oscillator import WaveformIconType
from PySide6.QtWidgets import QWidget, QTabWidget
from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.ui.widgets.filter.filter import FilterWidget
from jdxi_editor.ui.widgets.editor.helper import create_layout_with_widgets, create_envelope_group, create_adsr_icon


class DigitalFilterSection(ParameterSectionBase):
    """Digital Filter Section for JD-Xi Digital Partial"""

    # --- Filter sliders
    # Note: FILTER_CUTOFF and FILTER_SLOPE are handled by FilterWidget (includes plot)
    PARAM_SPECS = [
        SliderSpec(DigitalPartialParam.FILTER_RESONANCE, DigitalDisplayName.FILTER_RESONANCE),
        SliderSpec(DigitalPartialParam.FILTER_CUTOFF_KEYFOLLOW, DigitalDisplayName.FILTER_CUTOFF_KEYFOLLOW),
        SliderSpec(DigitalPartialParam.FILTER_ENV_VELOCITY_SENSITIVITY, DigitalDisplayName.FILTER_ENV_VELOCITY_SENSITIVITY),
        SliderSpec(DigitalPartialParam.FILTER_ENV_DEPTH, DigitalDisplayName.FILTER_ENV_DEPTH),
    ]
    
    # --- Log PARAM_SPECS at class definition time
    _log_param_specs = True
    if _log_param_specs:
        filter_env_depth_spec = next((s for s in PARAM_SPECS if hasattr(s.param, 'name') and s.param.name == 'FILTER_ENV_DEPTH'), None)
        if filter_env_depth_spec:
            log.message(f"🎯 DigitalFilterSection: FILTER_ENV_DEPTH found in PARAM_SPECS: {filter_env_depth_spec.param}, label: {filter_env_depth_spec.label}")
        else:
            log.warning(f"⚠️ DigitalFilterSection: FILTER_ENV_DEPTH NOT found in PARAM_SPECS!")
        log.message(f"📋 DigitalFilterSection PARAM_SPECS count: {len(PARAM_SPECS)}")
        log.message(f"📋 PARAM_SPECS params: {[getattr(s.param, 'name', str(s.param)) for s in PARAM_SPECS]}")

    # --- Filter mode buttons
    BUTTON_SPECS = [
        SliderSpec(DigitalFilterMode.BYPASS, "Bypass", icon_name=WaveformIconType.BYPASS_FILTER),
        SliderSpec(DigitalFilterMode.LPF, "LPF", icon_name=WaveformIconType.LPF_FILTER),
        SliderSpec(DigitalFilterMode.HPF, "HPF", icon_name=WaveformIconType.HPF_FILTER),
        SliderSpec(DigitalFilterMode.BPF, "BPF", icon_name=WaveformIconType.BPF_FILTER),
        SliderSpec(DigitalFilterMode.PKG, "PKG", icon_name=WaveformIconType.LPF_FILTER),
        SliderSpec(DigitalFilterMode.LPF2, "LPF2", icon_name=WaveformIconType.LPF_FILTER),
        SliderSpec(DigitalFilterMode.LPF3, "LPF3", icon_name=WaveformIconType.LPF_FILTER),
        SliderSpec(DigitalFilterMode.LPF4, "LPF4", icon_name=WaveformIconType.LPF_FILTER),
    ]

    BUTTON_ENABLE_RULES = {
        DigitalFilterMode.BYPASS: [],  # disables everything
        # --- Other modes: all sliders are enabled (default)
    }

    ADSR_SPEC = {
        ADSRType.ATTACK: DigitalPartialParam.FILTER_ENV_ATTACK_TIME,
        ADSRType.DECAY: DigitalPartialParam.FILTER_ENV_DECAY_TIME,
        ADSRType.SUSTAIN: DigitalPartialParam.FILTER_ENV_SUSTAIN_LEVEL,
        ADSRType.RELEASE: DigitalPartialParam.FILTER_ENV_RELEASE_TIME,
        ADSRType.PEAK: DigitalPartialParam.FILTER_ENV_DEPTH,
    }
    
    # --- Log ADSR_SPEC at class definition time
    if _log_param_specs:
        peak_param = ADSR_SPEC.get(ADSRType.PEAK)
        if peak_param:
            peak_name = getattr(peak_param, 'name', str(peak_param))
            log.message(f"🎯 DigitalFilterSection: ADSR_SPEC peak param: {peak_param} (name: {peak_name})")
            if peak_name == 'FILTER_ENV_DEPTH':
                log.message(f"✅ ADSR_SPEC peak is FILTER_ENV_DEPTH")
        else:
            log.warning(f"⚠️ DigitalFilterSection: No peak param in ADSR_SPEC!")
        log.message(f"📋 ADSR_SPEC keys: {list(ADSR_SPEC.keys())}")
    
    def build_widgets(self):
        """Override to create FilterWidget with plot"""
        # Create FilterWidget first (includes cutoff and slope with plot)
        self.filter_widget = FilterWidget(
            cutoff_param=DigitalPartialParam.FILTER_CUTOFF,
            slope_param=DigitalPartialParam.FILTER_SLOPE,
            midi_helper=self.midi_helper,
            create_parameter_slider=self._create_parameter_slider,
            create_parameter_switch=self._create_parameter_switch,
            controls=self.controls,
            address=self.address,
        )
        # Store filter widget controls
        self.controls[DigitalPartialParam.FILTER_CUTOFF] = self.filter_widget.cutoff_param_control
        if hasattr(self.filter_widget, 'slope_param_control'):
            self.controls[DigitalPartialParam.FILTER_SLOPE] = self.filter_widget.slope_param_control
        
        # Call parent to create other widgets from PARAM_SPECS
        super().build_widgets()
    
    def _create_tab_widget(self):
        """Override to add FilterWidget to Controls tab"""
        self.tab_widget = QTabWidget()

        # Controls tab - include FilterWidget first, then other controls
        controls_widget = QWidget()
        # FilterWidget includes cutoff and slope with plot
        # Other controls from PARAM_SPECS (resonance, keyfollow, velocity, depth)
        all_control_widgets = [self.filter_widget] + self.control_widgets
        controls_layout = create_layout_with_widgets(all_control_widgets)
        controls_widget.setLayout(controls_layout)
        self.tab_widget.addTab(
            controls_widget, 
            JDXi.UI.IconRegistry.get_icon(JDXi.UI.IconRegistry.TUNE, JDXi.UI.Style.GREY), 
            "Controls"
        )

        # ADSR tab
        if self.adsr_widget:
            adsr_group = create_envelope_group("Envelope", adsr_widget=self.adsr_widget, analog=self.analog)
            self.tab_widget.addTab(adsr_group, create_adsr_icon(), "ADSR")
    
    def _on_button_selected(self, button_param):
        """Override to update filter mode in FilterWidget plot and enable/disable plot"""
        # Call parent to handle button selection
        super()._on_button_selected(button_param)
        
        # Update filter mode in FilterWidget plot
        if hasattr(self, 'filter_widget') and self.filter_widget and hasattr(self.filter_widget, 'plot'):
            # Map DigitalFilterMode to filter mode string
            filter_mode_map = {
                DigitalFilterMode.BYPASS: "bypass",
                DigitalFilterMode.LPF: "lpf",
                DigitalFilterMode.HPF: "hpf",
                DigitalFilterMode.BPF: "bpf",
                DigitalFilterMode.PKG: "lpf",  # PKG uses LPF-style plot
                DigitalFilterMode.LPF2: "lpf",
                DigitalFilterMode.LPF3: "lpf",
                DigitalFilterMode.LPF4: "lpf",
            }
            filter_mode_str = filter_mode_map.get(button_param, "lpf")
            self.filter_widget.filter_mode = filter_mode_str
            if hasattr(self.filter_widget.plot, 'set_filter_mode'):
                self.filter_widget.plot.set_filter_mode(filter_mode_str)
            
            # Disable plot display when bypass is selected
            is_bypass = button_param == DigitalFilterMode.BYPASS
            self.filter_widget.plot.enabled = not is_bypass
            self.filter_widget.plot.update()  # Trigger redraw
