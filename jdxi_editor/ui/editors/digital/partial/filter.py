"""
Digital Filter Section for the JDXI Editor
"""

from decologr import Decologr as log
from jdxi_editor.midi.data.digital.filter import DigitalFilterMode
from jdxi_editor.midi.data.parameter.digital.name import DigitalDisplayName
from jdxi_editor.midi.data.parameter.digital.partial import DigitalPartialParam
from jdxi_editor.ui.editors.param_section import ParameterSectionBase
from jdxi_editor.ui.editors.widget_specs import SliderSpec
from jdxi_editor.midi.data.digital.oscillator import WaveformIconType


class DigitalFilterSection(ParameterSectionBase):
    """Digital Filter Section for JD-Xi Digital Partial"""

    # --- Filter sliders
    PARAM_SPECS = [
        SliderSpec(DigitalPartialParam.FILTER_CUTOFF, DigitalDisplayName.FILTER_CUTOFF),
        SliderSpec(DigitalPartialParam.FILTER_RESONANCE, DigitalDisplayName.FILTER_RESONANCE),
        SliderSpec(DigitalPartialParam.FILTER_CUTOFF_KEYFOLLOW, DigitalDisplayName.FILTER_CUTOFF_KEYFOLLOW),
        SliderSpec(DigitalPartialParam.FILTER_ENV_VELOCITY_SENSITIVITY, DigitalDisplayName.FILTER_ENV_VELOCITY_SENSITIVITY),
        SliderSpec(DigitalPartialParam.FILTER_ENV_DEPTH, DigitalDisplayName.FILTER_ENV_DEPTH),
        SliderSpec(DigitalPartialParam.FILTER_SLOPE, DigitalDisplayName.FILTER_SLOPE),
    ]
    
    # Log PARAM_SPECS at class definition time
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
        # Other modes: all sliders are enabled (default)
    }

    ADSR_SPEC = {
        "attack": DigitalPartialParam.FILTER_ENV_ATTACK_TIME,
        "decay": DigitalPartialParam.FILTER_ENV_DECAY_TIME,
        "sustain": DigitalPartialParam.FILTER_ENV_SUSTAIN_LEVEL,
        "release": DigitalPartialParam.FILTER_ENV_RELEASE_TIME,
        "peak": DigitalPartialParam.FILTER_ENV_DEPTH,
    }
    
    # Log ADSR_SPEC at class definition time
    if _log_param_specs:
        peak_param = ADSR_SPEC.get("peak")
        if peak_param:
            peak_name = getattr(peak_param, 'name', str(peak_param))
            log.message(f"🎯 DigitalFilterSection: ADSR_SPEC peak param: {peak_param} (name: {peak_name})")
            if peak_name == 'FILTER_ENV_DEPTH':
                log.message(f"✅ ADSR_SPEC peak is FILTER_ENV_DEPTH")
        else:
            log.warning(f"⚠️ DigitalFilterSection: No peak param in ADSR_SPEC!")
        log.message(f"📋 ADSR_SPEC keys: {list(ADSR_SPEC.keys())}")
