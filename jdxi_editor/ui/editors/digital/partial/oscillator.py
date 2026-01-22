"""
Digital Oscillator Section for the JDXI Editor
"""

from typing import Callable

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QTabWidget,
    QVBoxLayout,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.digital.oscillator import DigitalOscWave, WaveformIconType
from jdxi_editor.midi.data.parameter.digital.name import DigitalDisplayName
from jdxi_editor.midi.data.parameter.digital.option import DigitalDisplayOptions
from jdxi_editor.midi.data.parameter.digital.partial import DigitalPartialParam
from jdxi_editor.midi.data.pcm.waves import PCM_WAVES_CATEGORIZED
from jdxi_editor.ui.editors.digital.partial.pwm import PWMWidget
from jdxi_editor.ui.editors.param_section import ParameterSectionBase
from jdxi_editor.ui.editors.widget_specs import SliderSpec
from jdxi_editor.ui.image.utils import base64_to_pixmap
from jdxi_editor.ui.image.waveform import generate_waveform_icon
from jdxi_editor.ui.widgets.combo_box.searchable_filterable import (
    SearchableFilterableComboBox,
)
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import (
    create_layout_with_widgets,
    create_widget_with_layout,
)
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget
from jdxi_editor.ui.widgets.pitch.envelope import PitchEnvelopeWidget



class DigitalOscillatorSection(ParameterSectionBase):
    """Digital Oscillator Section for JD-Xi Editor (spec-driven)."""

    # --- Sliders
    PARAM_SPECS = [
        SliderSpec(DigitalPartialParam.OSC_PITCH, DigitalDisplayName.OSC_PITCH),
        SliderSpec(DigitalPartialParam.OSC_DETUNE, DigitalDisplayName.OSC_DETUNE),
        SliderSpec(DigitalPartialParam.SUPER_SAW_DETUNE, DigitalDisplayName.SUPER_SAW_DETUNE),
    ]

    # --- Waveform buttons
    BUTTON_SPECS = [
        SliderSpec(DigitalOscWave.SAW, "Saw", icon_name=WaveformIconType.UPSAW),
        SliderSpec(DigitalOscWave.SQUARE, "Square", icon_name=WaveformIconType.SQUARE),
        SliderSpec(DigitalOscWave.PW_SQUARE, "PW Square", icon_name=WaveformIconType.PWSQU),
        SliderSpec(DigitalOscWave.TRIANGLE, "Triangle", icon_name=WaveformIconType.TRIANGLE),
        SliderSpec(DigitalOscWave.SINE, "Sine", icon_name=WaveformIconType.SINE),
        SliderSpec(DigitalOscWave.NOISE, "Noise", icon_name=WaveformIconType.NOISE),
        SliderSpec(DigitalOscWave.SUPER_SAW, "Super Saw", icon_name=WaveformIconType.SPSAW),
        SliderSpec(DigitalOscWave.PCM, "PCM", icon_name=WaveformIconType.PCM),
    ]

    # --- Enable rules for dependent widgets
    BUTTON_ENABLE_RULES = {
        DigitalOscWave.PW_SQUARE: ["pwm_widget", "pw_shift_slider"],
        DigitalOscWave.PCM: ["pcm_wave_gain", "pcm_wave_number"],
        DigitalOscWave.SUPER_SAW: ["super_saw_detune"],
    }

    # --- Optional ADSR can be added if Oscillator has one (Digital usually has pitch envelope)
    ADSR_SPEC = None

    def _initialize_button_states(self):
        """Override to skip initialization until after all widgets are created"""
        # Don't initialize button states during __init__ - widgets may not exist yet
        # This will be called manually after all widgets are created
        pass
    
    def setup_ui(self):
        """Override to initialize button states after all widgets are created"""
        super().setup_ui()
        # Now that all widgets are created, initialize button states
        if self.BUTTON_SPECS:
            first_param = self.BUTTON_SPECS[0].param
            self._on_button_selected(first_param)

    def _create_buttons(self):
        """Override to create waveform buttons with custom icon generation"""
        self.wave_buttons = {}
        self.wave_layout_widgets = []

        for spec in self.BUTTON_SPECS:
            wave = spec.param
            icon_type = spec.icon_name  # This is a WaveformIconType enum
            
            # Generate icon from waveform type
            icon_base64 = generate_waveform_icon(icon_type, JDXi.UI.Style.WHITE, 1.0)
            # Use QPushButton directly since WaveformButton expects Waveform enum, not DigitalOscWave
            from PySide6.QtWidgets import QPushButton
            btn = QPushButton(spec.label)  # Use label from spec
            btn.setCheckable(True)
            
            # Set icon
            pixmap = base64_to_pixmap(icon_base64)
            if pixmap and not pixmap.isNull():
                btn.setIcon(QIcon(pixmap))
                btn.setIconSize(QSize(20, 20))
            
            btn.setFixedSize(
                JDXi.UI.Dimensions.WAVEFORM_ICON.WIDTH,
                JDXi.UI.Dimensions.WAVEFORM_ICON.HEIGHT,
            )
            btn.clicked.connect(lambda _, w=wave: self._on_button_selected(w))
            btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)

            self.wave_buttons[wave] = btn
            self.button_widgets[wave] = btn
            self.controls[DigitalPartialParam.OSC_WAVE] = btn
            self.wave_layout_widgets.append(btn)
    
    def _create_button_row_layout(self):
        """Override to create waveform button row layout"""
        from PySide6.QtWidgets import QHBoxLayout
        
        top_row = QHBoxLayout()
        top_row.addStretch()
        top_row.addLayout(create_layout_with_widgets(self.wave_layout_widgets))
        # TODO: Add wave variation switch if needed
        top_row.addStretch()
        return top_row
    
    def _on_button_selected(self, button_param):
        """Override to handle waveform button selection with correct MIDI parameter"""
        # Reset all buttons
        for btn in self.button_widgets.values():
            btn.setChecked(False)
            btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)
        
        # Set selected button
        selected_btn = self.button_widgets[button_param]
        selected_btn.setChecked(True)
        selected_btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT_ACTIVE)
        
        # Update enabled states
        self._update_button_enabled_states(button_param)
        
        # Send MIDI parameter - button_param is a DigitalOscWave enum
        if self.send_midi_parameter:
            self.send_midi_parameter(DigitalPartialParam.OSC_WAVE, button_param.value)
    
    def _update_button_enabled_states(self, button_param):
        """Override to enable/disable widgets based on selected waveform.
        
        This is called after all widgets are created (in setup_ui), so widgets
        should exist. We still check for None as a safety measure.
        """
        # Disable all first
        for attrs in self.BUTTON_ENABLE_RULES.values():
            for attr in attrs:
                widget = getattr(self, attr, None)
                if widget is not None:
                    widget.setEnabled(False)
        # Enable per selected button
        for attr in self.BUTTON_ENABLE_RULES.get(button_param, []):
            widget = getattr(self, attr, None)
            if widget is not None:
                widget.setEnabled(True)
