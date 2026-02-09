from dataclasses import dataclass
from typing import Callable, Any

from PySide6.QtWidgets import QWidget

from jdxi_editor.midi.conversion.value import ValueTransform
from jdxi_editor.midi.data.parameter.digital import DigitalPartialParam
from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital


@dataclass(frozen=True)
class ParamBinding:
    transform: ValueTransform
    resolver: Callable[[Any, int], QWidget]  # (self, partial_no) -> control


ADSR_BINDINGS: dict[DigitalPartialParam, ParamBinding] = {
    Digital.Param.AMP_ENV_ATTACK_TIME: ParamBinding(
        ValueTransform.MS,
        lambda s, p: s.partial_editors[p].amp_tab.adsr_widget.attack_control,
    ),
    Digital.Param.AMP_ENV_SUSTAIN_LEVEL: ParamBinding(
        ValueTransform.FRACTION,
        lambda s, p: s.partial_editors[p].amp_tab.adsr_widget.sustain_control,
    ),
    Digital.Param.FILTER_ENV_RELEASE_TIME: ParamBinding(
        ValueTransform.MS,
        lambda s, p: s.partial_editors[p].filter_tab.adsr_widget.release_control,
    ),
}
