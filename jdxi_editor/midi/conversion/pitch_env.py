from jdxi_editor.midi.conversion.adsr import ParamBinding
from jdxi_editor.midi.conversion.value import ValueTransform
from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital

PITCH_ENV_BINDINGS = {
    Digital.Param.OSC_PITCH_ENV_ATTACK_TIME: ParamBinding(
        ValueTransform.PITCH_ENV_TIME,
        lambda s, p: s.partial_editors[
            p
        ].oscillator_tab.widgets.pitch_env_widget.attack_control,
    ),
    Digital.Param.OSC_PITCH_ENV_DEPTH: ParamBinding(
        ValueTransform.FRACTION,
        lambda s, p: s.partial_editors[
            p
        ].oscillator_tab.widgets.pitch_env_widget.depth_control,
    ),
}
