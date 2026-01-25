"""
AMP section for the digital partial editor.
"""
from typing import Dict

from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital
from jdxi_editor.ui.adsr.spec import ADSRStage, ADSRSpec
from jdxi_editor.ui.editors.param_section import ParameterSectionBase
from jdxi_editor.ui.editors.widget_specs import SliderSpec
from jdxi_editor.ui.widgets.editor.helper import (
    create_adsr_icon,
    create_envelope_group,
    create_layout_with_widgets,
)


class DigitalAmpSection(ParameterSectionBase):
    """Digital Amp Section for JD-Xi Editor"""

    PARAM_SPECS = [
        SliderSpec(Digital.Param.AMP_LEVEL, Digital.Display.Name.AMP_LEVEL),
        SliderSpec(
            Digital.Param.AMP_LEVEL_KEYFOLLOW, Digital.Display.Name.AMP_LEVEL_KEYFOLLOW
        ),
        SliderSpec(Digital.Param.AMP_VELOCITY, Digital.Display.Name.AMP_VELOCITY),
        SliderSpec(
            Digital.Param.LEVEL_AFTERTOUCH, Digital.Display.Name.LEVEL_AFTERTOUCH
        ),
        SliderSpec(
            Digital.Param.CUTOFF_AFTERTOUCH, Digital.Display.Name.CUTOFF_AFTERTOUCH
        ),
        SliderSpec(
            Digital.Param.AMP_PAN, Digital.Display.Name.AMP_PAN
        ),  # Horizontal pan - handled separately
    ]

    ADSR_SPEC: Dict[ADSRStage, ADSRSpec] = {
        ADSRStage.ATTACK: ADSRSpec(ADSRStage.ATTACK, Digital.Param.FILTER_ENV_ATTACK_TIME),
        ADSRStage.DECAY: ADSRSpec(ADSRStage.DECAY, Digital.Param.FILTER_ENV_DECAY_TIME),
        ADSRStage.SUSTAIN: ADSRSpec(ADSRStage.SUSTAIN, Digital.Param.FILTER_ENV_SUSTAIN_LEVEL),
        ADSRStage.RELEASE: ADSRSpec(ADSRStage.RELEASE, Digital.Param.FILTER_ENV_RELEASE_TIME),
        ADSRStage.PEAK: ADSRSpec(ADSRStage.PEAK, Digital.Param.FILTER_ENV_DEPTH),
    }

    """ADSR_SPEC = {
        Digital.Amp.ADSR.ATTACK: Digital.Param.AMP_ENV_ATTACK_TIME,
        Digital.Amp.ADSR.DECAY: Digital.Param.AMP_ENV_DECAY_TIME,
        Digital.Amp.ADSR.SUSTAIN: Digital.Param.AMP_ENV_SUSTAIN_LEVEL,
        Digital.Amp.ADSR.RELEASE: Digital.Param.AMP_ENV_RELEASE_TIME,
    }"""

    BUTTON_SPECS = []  # Digital Amp does not have waveform buttons

    def _create_parameter_widgets(self):
        """Override to handle Pan slider separately (horizontal)"""
        # --- Create all widgets except Pan
        for spec in self.PARAM_SPECS:
            # Skip Pan - it will be created separately as horizontal
            if spec.param == Digital.Param.AMP_PAN:
                continue

            if isinstance(spec, SliderSpec):
                widget = self._create_parameter_slider(
                    spec.param, spec.label, vertical=True
                )
            else:
                continue

            self.controls[spec.param] = widget
            self.control_widgets.append(widget)

        # --- Create Pan slider separately (horizontal)
        self.pan_slider = self._create_parameter_slider(
            Digital.Param.AMP_PAN,
            Digital.Display.Name.AMP_PAN,
            vertical=False,  # Horizontal slider
        )
        self.controls[Digital.Param.AMP_PAN] = self.pan_slider
        # --- Don't add to control_widgets - it will be added separately in _create_tab_widget

    def _create_tab_widget(self):
        """Override to add Pan slider in its own horizontal layout"""

        self.tab_widget = QTabWidget()

        # --- Controls tab
        controls_widget = QWidget()
        controls_layout = QVBoxLayout()

        # --- Add regular vertical sliders
        regular_layout = create_layout_with_widgets(self.control_widgets)
        controls_layout.addLayout(regular_layout)

        # --- Add Pan slider in its own horizontal layout
        pan_layout = create_layout_with_widgets([self.pan_slider])
        controls_layout.addLayout(pan_layout)

        from jdxi_editor.midi.data.parameter.digital.spec import DigitalAmpTab
        
        controls_widget.setLayout(controls_layout)
        self._add_tab(key=DigitalAmpTab.CONTROLS, widget=controls_widget)

        # --- ADSR tab if any
        if self.adsr_widget:
            adsr_group = create_envelope_group(
                "Envelope", adsr_widget=self.adsr_widget, analog=self.analog
            )
            self._add_tab(key=DigitalAmpTab.ADSR, widget=adsr_group)
