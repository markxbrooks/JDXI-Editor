"""
Amp section of the JD-Xi editor

This section contains the controls for the amp section of the JD-Xi editor.
"""

from typing import Dict

from jdxi_editor.midi.data.parameter.analog.spec import JDXiMidiAnalog as Analog
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.adsr.spec import ADSRSpec, ADSRStage
from jdxi_editor.ui.editors.base.amp.section import BaseAmpSection
from jdxi_editor.ui.editors.digital.partial.amp.spec import AmpLayoutSpec
from jdxi_editor.ui.widgets.spec import SliderSpec


class AnalogAmpSection(BaseAmpSection):
    """Amp section of the JD-Xi editor"""

    SYNTH_SPEC = Analog

    def __init__(
            self,
            address,
            send_midi_parameter=None,
            midi_helper: MidiIOHelper = None,
    ):
        # Build layout spec (including ADSR mapping) before base init so widgets/ADSR
        # can be constructed correctly in BaseAmpSection.build_widgets().
        self.spec: AmpLayoutSpec = self._build_layout_spec()
        self.spec_adsr = self.spec.adsr
        # Bridge newer AmpLayoutSpec.adsr into the shared spec_adsr field used by
        # SectionBaseWidget / BaseAmpSection ADSR helpers.
        # This ensures self.adsr_widget is created for the Analog amp section.
        from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget

        # Instance-level override; fall back to empty dict if adsr is missing.
        self.spec_adsr = getattr(self.spec, "adsr", None) or {}
        super().__init__(
            analog=True,
            address=address,
            send_midi_parameter=send_midi_parameter,
            midi_helper=midi_helper,
        )
        self.setup_ui()

    def _build_layout_spec(self) -> AmpLayoutSpec:
        """build Analog Oscillator Layout Spec"""
        S = self.SYNTH_SPEC
        controls = [
            SliderSpec(
                S.Param.AMP_LEVEL,
                S.Param.AMP_LEVEL.display_name,
                vertical=True,
            ),
            SliderSpec(
                S.Param.AMP_LEVEL_KEYFOLLOW,
                S.Param.AMP_LEVEL_KEYFOLLOW.display_name,
                vertical=True,
            ),
            SliderSpec(
                S.Param.AMP_LEVEL_VELOCITY_SENSITIVITY,
                S.Param.AMP_LEVEL_VELOCITY_SENSITIVITY.display_name,
                vertical=True,
            ),
        ]
        adsr: Dict[ADSRStage, ADSRSpec] = {
            ADSRStage.ATTACK: ADSRSpec(ADSRStage.ATTACK, Analog.Param.AMP_ENV_ATTACK_TIME),
            ADSRStage.DECAY: ADSRSpec(ADSRStage.DECAY, Analog.Param.AMP_ENV_DECAY_TIME),
            ADSRStage.SUSTAIN: ADSRSpec(
                ADSRStage.SUSTAIN, Analog.Param.AMP_ENV_SUSTAIN_LEVEL
            ),
            ADSRStage.RELEASE: ADSRSpec(
                ADSRStage.RELEASE, Analog.Param.AMP_ENV_RELEASE_TIME
            ),
        }
        return AmpLayoutSpec(controls=controls, adsr=adsr)
