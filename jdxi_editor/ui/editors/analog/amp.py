"""
Amp section of the JD-Xi editor

This section contains the controls for the amp section of the JD-Xi editor.
"""

from typing import Callable, Dict

from PySide6.QtWidgets import (
    QTabWidget,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.parameter.analog.name import AnalogDisplayName
from jdxi_editor.midi.data.parameter.analog.spec import JDXiMidiAnalog as Analog
from jdxi_editor.ui.adsr.spec import ADSRSpec, ADSRStage
from jdxi_editor.ui.editors.widget_specs import SliderSpec
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import (
    create_adsr_icon,
    create_envelope_group,
    create_layout_with_widgets,
)
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget


class AnalogAmpSection(SectionBaseWidget):
    """Amp section of the JD-Xi editor"""

    PARAM_SPECS = [
        SliderSpec(Analog.Param.AMP_LEVEL, Analog.Display.Name.AMP_LEVEL),
        SliderSpec(
            Analog.Param.AMP_LEVEL_KEYFOLLOW, Analog.Display.Name.AMP_LEVEL_KEYFOLLOW
        ),
        SliderSpec(Analog.Param.AMP_LEVEL_VELOCITY_SENSITIVITY, Analog.Display.Name.AMP_LEVEL_VELOCITY_SENSITIVITY),
    ]
    ADSR_SPEC: Dict[ADSRStage, ADSRSpec] = {
        ADSRStage.ATTACK: ADSRSpec(ADSRStage.ATTACK, Analog.Param.AMP_ENV_ATTACK_TIME),
        ADSRStage.DECAY: ADSRSpec(ADSRStage.DECAY, Analog.Param.AMP_ENV_DECAY_TIME),
        ADSRStage.SUSTAIN: ADSRSpec(ADSRStage.SUSTAIN, Analog.Param.AMP_ENV_SUSTAIN_LEVEL),
        ADSRStage.RELEASE: ADSRSpec(ADSRStage.RELEASE, Analog.Param.AMP_ENV_RELEASE_TIME),
    }

    def __init__(
        self,
        midi_helper,
        address,
        controls: dict,
        create_parameter_slider: Callable,
    ):
        self.midi_helper = midi_helper
        self.address = address
        self._create_parameter_slider = create_parameter_slider

        # Dynamic widgets storage
        self.amp_sliders = {}
        self.amp_adsr_group = None
        self.amp_env_adsr_widget = None
        self.tab_widget = None
        self.layout = None

        super().__init__(icons_row_type=IconType.ADSR, analog=True)
        # Set controls after super().__init__() to avoid it being overwritten
        self.controls = controls or {}

        self.build_widgets()
        self.setup_ui()

    # ------------------------------------------------------------------
    # Build Widgets
    # ------------------------------------------------------------------
    def build_widgets(self):
        """Build all amp widgets"""
        self.tab_widget = QTabWidget()
        self._create_sliders()
        self._create_adsr_group()

    def _create_sliders(self):
        """Create sliders for Level, KeyFollow, and Velocity Sensitivity"""
        for entry in self.PARAM_SPECS:
            slider = self._create_parameter_slider(
                entry.param, entry.label, vertical=entry.vertical
            )
            self.amp_sliders[entry.param] = slider
            self.controls[entry.param] = slider

    def _create_adsr_group(self):
        """Create amp ADSR envelope using standardized helper"""
        from jdxi_editor.ui.widgets.adsr.adsr import ADSR

        # --- Extract parameters from ADSRSpec objects
        def get_param(spec_or_param):
            """Extract parameter from ADSRSpec or return parameter directly"""
            if isinstance(spec_or_param, ADSRSpec):
                return spec_or_param.param
            return spec_or_param

        attack_spec = self.ADSR_SPEC.get(ADSRStage.ATTACK)
        decay_spec = self.ADSR_SPEC.get(ADSRStage.DECAY)
        sustain_spec = self.ADSR_SPEC.get(ADSRStage.SUSTAIN)
        release_spec = self.ADSR_SPEC.get(ADSRStage.RELEASE)

        attack_param = get_param(attack_spec) if attack_spec else None
        decay_param = get_param(decay_spec) if decay_spec else None
        sustain_param = get_param(sustain_spec) if sustain_spec else None
        release_param = get_param(release_spec) if release_spec else None

        self.amp_env_adsr_widget = ADSR(
            attack_param=attack_param,
            decay_param=decay_param,
            sustain_param=sustain_param,
            release_param=release_param,
            midi_helper=self.midi_helper,
            create_parameter_slider=self._create_parameter_slider,
            address=self.address,
            controls=self.controls,
            analog=True,
        )
        self.amp_adsr_group = create_envelope_group(
            name="Envelope",
            adsr_widget=self.amp_env_adsr_widget,
            analog=True,
        )

    # ------------------------------------------------------------------
    # Setup UI
    # ------------------------------------------------------------------
    def setup_ui(self):
        """Setup the UI for the analog amp section"""
        self.layout = self.create_layout()

        # --- Level Controls Tab
        controls_layout = create_layout_with_widgets(
            list(self.amp_sliders.values())
        )
        level_controls_widget = QWidget()
        level_controls_widget.setLayout(controls_layout)

        self._add_tab(key=Analog.Amp.Tab.CONTROLS, widget=level_controls_widget)

        # --- ADSR Tab
        self._add_tab(key=Analog.Amp.Tab.ADSR, widget=self.amp_adsr_group)

        JDXi.UI.Theme.apply_tabs_style(self.tab_widget, analog=True)

        # --- Add tab widget to main layout
        self.layout.addWidget(self.tab_widget)
        self.layout.addStretch()
