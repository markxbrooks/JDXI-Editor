from jdxi_editor.midi.conversion.adsr import ParamBinding
from jdxi_editor.midi.conversion.value import ValueTransform
from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital

PWM_BINDINGS = {
    Digital.Param.OSC_PULSE_WIDTH: ParamBinding(
        ValueTransform.FRACTION,
        lambda s, p: s.partial_editors[p].oscillator_tab.pwm_widget.pulse_width_control,
    ),
    Digital.Param.OSC_PULSE_WIDTH_MOD_DEPTH: ParamBinding(
        ValueTransform.FRACTION,
        lambda s, p: s.partial_editors[p].oscillator_tab.pwm_widget.mod_depth_control,
    ),
}


def resolve_pwm(s, p, param):
    osc = s.partial_editors[p].oscillator_tab
    if hasattr(osc, "controls") and param in osc.controls:
        return osc.controls[param]
    if hasattr(osc, "pwm_widget"):
        if param == Digital.Param.OSC_PULSE_WIDTH:
            return osc.pwm_widget.pulse_width_control
        if param == Digital.Param.OSC_PULSE_WIDTH_MOD_DEPTH:
            return osc.pwm_widget.mod_depth_control
