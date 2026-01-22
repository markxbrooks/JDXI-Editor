"""
AMP section for the digital partial editor.
"""

from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from jdxi_editor.midi.data.parameter.digital.name import DigitalDisplayName
from jdxi_editor.midi.data.parameter.digital.partial import (
    DigitalPartialParam,
)
from jdxi_editor.ui.adsr.type import ADSRType
from jdxi_editor.ui.editors.param_section import ParameterSectionBase
from jdxi_editor.ui.editors.widget_specs import SliderSpec


class DigitalAmpSection(ParameterSectionBase):
    """Digital Amp Section for JD-Xi Editor"""

    PARAM_SPECS = [
        SliderSpec(DigitalPartialParam.AMP_LEVEL, DigitalDisplayName.AMP_LEVEL),
        SliderSpec(DigitalPartialParam.AMP_LEVEL_KEYFOLLOW, DigitalDisplayName.AMP_LEVEL_KEYFOLLOW),
        SliderSpec(DigitalPartialParam.AMP_VELOCITY, DigitalDisplayName.AMP_VELOCITY),
        SliderSpec(DigitalPartialParam.LEVEL_AFTERTOUCH, DigitalDisplayName.LEVEL_AFTERTOUCH),
        SliderSpec(DigitalPartialParam.CUTOFF_AFTERTOUCH, DigitalDisplayName.CUTOFF_AFTERTOUCH),
        SliderSpec(DigitalPartialParam.AMP_PAN, DigitalDisplayName.AMP_PAN),  # Horizontal pan - handled separately
    ]

    ADSR_SPEC = {
        ADSRType.ATTACK: DigitalPartialParam.AMP_ENV_ATTACK_TIME,
        ADSRType.DECAY: DigitalPartialParam.AMP_ENV_DECAY_TIME,
        ADSRType.SUSTAIN: DigitalPartialParam.AMP_ENV_SUSTAIN_LEVEL,
        ADSRType.RELEASE: DigitalPartialParam.AMP_ENV_RELEASE_TIME,
    }

    BUTTON_SPECS = []  # Digital Amp does not have waveform buttons

    def _create_parameter_widgets(self):
        """Override to handle Pan slider separately (horizontal)"""
        # Create all widgets except Pan
        for spec in self.PARAM_SPECS:
            # Skip Pan - it will be created separately as horizontal
            if spec.param == DigitalPartialParam.AMP_PAN:
                continue
                
            if isinstance(spec, SliderSpec):
                widget = self._create_parameter_slider(spec.param, spec.label, vertical=True)
            else:
                continue
            
            self.controls[spec.param] = widget
            self.control_widgets.append(widget)
        
        # Create Pan slider separately (horizontal)
        self.pan_slider = self._create_parameter_slider(
            DigitalPartialParam.AMP_PAN,
            DigitalDisplayName.AMP_PAN,
            vertical=False  # Horizontal slider
        )
        self.controls[DigitalPartialParam.AMP_PAN] = self.pan_slider
        # Don't add to control_widgets - it will be added separately in _create_tab_widget

    def _create_tab_widget(self):
        """Override to add Pan slider in its own horizontal layout"""
        from PySide6.QtWidgets import QTabWidget, QVBoxLayout
        from jdxi_editor.core.jdxi import JDXi
        from jdxi_editor.ui.widgets.editor.helper import create_layout_with_widgets, create_envelope_group, create_adsr_icon
        
        self.tab_widget = QTabWidget()

        # Controls tab
        controls_widget = QWidget()
        controls_layout = QVBoxLayout()
        
        # Add regular vertical sliders
        regular_layout = create_layout_with_widgets(self.control_widgets)
        controls_layout.addLayout(regular_layout)
        
        # --- Add Pan slider in its own horizontal layout
        pan_layout = create_layout_with_widgets([self.pan_slider])
        controls_layout.addLayout(pan_layout)
        
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
