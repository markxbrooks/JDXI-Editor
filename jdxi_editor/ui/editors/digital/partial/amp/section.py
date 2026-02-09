"""
AMP section for the digital partial editor.


Example Usage:
==============
>>> DigitalAmpSection(send_midi_parameter=send_midi_parameter,
... midi_helper=midi_helper,
... address=synth_data.address
... )
"""

from typing import Dict

from PySide6.QtWidgets import QVBoxLayout, QWidget

from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital
from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital
from jdxi_editor.ui.adsr.spec import ADSRSpec, ADSRStage
from jdxi_editor.ui.editors.base.amp import BaseAmpSection
from jdxi_editor.ui.editors.digital.partial.amp.spec import AmpWidgetSpec
from jdxi_editor.ui.widgets.editor.helper import (
    create_layout_with_widgets,
)
from jdxi_editor.ui.widgets.spec import SliderSpec


class DigitalAmpSection(BaseAmpSection):
    """Digital Amp Section for JD-Xi Editor"""

    SYNTH_SPEC = JDXiMidiDigital

    ADSR_SPEC: Dict[ADSRStage, ADSRSpec] = {
        ADSRStage.ATTACK: ADSRSpec(ADSRStage.ATTACK, Digital.Param.AMP_ENV_ATTACK_TIME),
        ADSRStage.DECAY: ADSRSpec(ADSRStage.DECAY, Digital.Param.AMP_ENV_DECAY_TIME),
        ADSRStage.SUSTAIN: ADSRSpec(
            ADSRStage.SUSTAIN, Digital.Param.AMP_ENV_SUSTAIN_LEVEL
        ),
        ADSRStage.RELEASE: ADSRSpec(
            ADSRStage.RELEASE, Digital.Param.AMP_ENV_RELEASE_TIME
        ),
        # Note: AMP envelope does not have a PEAK/DEPTH parameter like Filter envelope
    }

    def __init__(self, **kwargs):
        self.SLIDER_GROUPS: AmpWidgetSpec = self._build_layout_spec()
        self.widgets: AmpWidgetSpec | None = None
        self.AMP_PARAMETERS = self._build_amp_parameters()
        super().__init__(**kwargs)

    def build_widgets(self):
        """Override to build from SLIDER_GROUPS via _create_parameter_widgets, then base tab/ADSR."""
        self._build_widgets()
        super(BaseAmpSection, self).build_widgets()

    def _build_widgets(self):
        """Override to build from SLIDER_GROUPS; Pan in its own group (horizontal).
        Pop any existing control/pan widgets before adding to avoid duplication."""
        # --- Pop existing control sliders so we don't duplicate
        control_params = [s.param for s in self.SLIDER_GROUPS.controls]
        for param in control_params:
            if param in self.controls:
                w = self.controls.pop(param)
                if w in self.amp_control_widgets:
                    self.amp_control_widgets.remove(w)
        # --- Remove Pan from controls and amp_control_widgets if it was previously added
        pan_specs = self.SLIDER_GROUPS.pan
        if pan_specs and pan_specs[0].param in self.controls:
            pan_widget = self.controls.pop(pan_specs[0].param, None)
            if pan_widget and pan_widget in self.amp_control_widgets:
                self.amp_control_widgets.remove(pan_widget)

        # --- Vertical control sliders
        self.widgets = AmpWidgetSpec(controls=self._build_sliders(self.SLIDER_GROUPS.controls),
                                     pan=self._build_sliders(self.SLIDER_GROUPS.pan))

        for spec, widget in zip(
            self.SLIDER_GROUPS.controls, self.widgets.controls
        ):
            self.controls[spec.param] = widget
            self.amp_control_widgets.append(widget)

        # Register Pan in controls but don't add to amp_control_widgets
        # (it will be added separately below the sliders)
        for spec, widget in zip(
            self.SLIDER_GROUPS.pan, self.widgets.pan
        ):
            self.controls[spec.param] = widget
            # Don't add to amp_control_widgets - it's added separately below

    def _create_controls_widget(self) -> QWidget:
        """Override to add Pan slider in its own horizontal layout"""
        controls_widget = QWidget()
        controls_layout = QVBoxLayout()

        # --- Add regular vertical sliders
        regular_layout = create_layout_with_widgets(self.amp_control_widgets)
        controls_layout.addLayout(regular_layout)

        # --- Add Pan slider in its own horizontal layout
        pan_layout = create_layout_with_widgets(self.widgets.pan)
        controls_layout.addLayout(pan_layout)

        controls_widget.setLayout(controls_layout)
        return controls_widget

    def _build_layout_spec(self) -> AmpWidgetSpec:
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
                S.Param.AMP_VELOCITY,
                S.Param.AMP_VELOCITY.display_name,
                vertical=True,
            ),
            SliderSpec(
                S.Param.LEVEL_AFTERTOUCH,
                S.Param.LEVEL_AFTERTOUCH.display_name,
                vertical=True,
            ),
            SliderSpec(
                S.Param.CUTOFF_AFTERTOUCH,
                S.Param.CUTOFF_AFTERTOUCH.display_name,
                vertical=True,
            ),
        ]
        pan = [
            SliderSpec(
                S.Param.AMP_PAN,
                S.Param.AMP_PAN.display_name,
                vertical=False,
            ),
        ]
        return AmpWidgetSpec(
            controls=controls, pan=pan
        )  # separate place to put the Pan

    def set_pan(self, value: int) -> None:
        self._set_param(self.SYNTH_SPEC.Param.AMP_PAN, value)

