"""
Digital Partial Editor Module

This module defines the `DigitalPartialEditor` class, a specialized editor for managing a single
digital partial in a synthesizer. It extends the `PartialEditor` class, providing a structured UI
to control and modify parameters related to oscillators, filters, amplifiers, and modulation sources.

Classes:
    - DigitalPartialEditor: A `QWidget` subclass that allows users to modify digital synthesis
      parameters using a tabbed interface with various control sections.

Features:
    - Supports editing a single partial within a digital synth part.
    - Provides categorized parameter sections: Oscillator, Filter, Amp, LFO, and Mod LFO.
    - Integrates with `MIDIHelper` for real-time MIDI parameter updates.
    - Uses icons for waveform selection, filter controls, and modulation settings.
    - Stores UI controls for easy access and interaction.

Usage:
    ```python
    from PySide6.QtWidgets import QApplication
    from midi_helper import MIDIHelper

    app = QApplication([])
    midi_helper = MIDIHelper()
    editor = DigitalPartialEditor(midi_helper=midi_helper)
    editor.show()
    app.exec()
    ```

Dependencies:
    - PySide6 (for UI components)
    - MIDIHelper (for MIDI communication)
    - DigitalParameter, DigitalCommonParameter (for parameter management)
    - WaveformButton (for waveform selection UI)
    - QIcons generated from waveform base64 data
"""

import logging
from typing import Dict, Union

import qtawesome as qta
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTabWidget,
)

from jdxi_editor.midi.data.editor.data import DigitalSynthData
from jdxi_editor.midi.data.parameter.digital.partial import DigitalPartialParameter
from jdxi_editor.midi.data.digital import DigitalOscWave, DIGITAL_PARTIAL_NAMES
from jdxi_editor.midi.data.parameter.digital.common import DigitalCommonParameter
from jdxi_editor.midi.data.constants.sysex import TEMPORARY_DIGITAL_SYNTH_1_AREA, TEMPORARY_DIGITAL_SYNTH_2_AREA
from jdxi_editor.midi.sysex.parsers import get_partial_address
from jdxi_editor.ui.editors.digital.partial.amp import DigitalAmpSection
from jdxi_editor.ui.editors.digital.partial.filter import DigitalFilterSection
from jdxi_editor.ui.editors.digital.partial.lfo import DigitalLFOSection
from jdxi_editor.ui.editors.digital.partial.mod_lfo import DigitalModLFOSection
from jdxi_editor.ui.editors.digital.partial.oscillator import DigitalOscillatorSection
from jdxi_editor.ui.editors.synth.partial import PartialEditor
from jdxi_editor.ui.style import JDXIStyle


class DigitalPartialEditor(PartialEditor):
    """Editor for address single partial"""

    def __init__(self, midi_helper=None, synth_number=1, partial_number=1, parent=None):
        super().__init__(parent)
        self.bipolar_parameters = [
            DigitalPartialParameter.OSC_DETUNE,
            DigitalPartialParameter.OSC_PITCH,
            DigitalPartialParameter.OSC_PITCH_ENV_DEPTH,
            DigitalPartialParameter.AMP_PAN,
        ]
        self.midi_helper = midi_helper
        self.partial_number = partial_number
        self.synth_data = DigitalSynthData(synth_number=synth_number, partial_number=partial_number)
        data = self.synth_data
        self.area = data.area
        self.part = data.part
        self.group = data.group
        if 0 <= partial_number < len(DIGITAL_PARTIAL_NAMES):
            self.part_name = DIGITAL_PARTIAL_NAMES[partial_number]
        else:
            logging.error(
                f"Invalid partial_num: {partial_number}. Using default value."
            )
            self.part_name = "Unknown"  # Provide a fallback value


        # Store parameter controls for easy access
        self.controls: Dict[
            Union[DigitalPartialParameter, DigitalCommonParameter], QWidget
        ] = {}

        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Create container widget for the tabs
        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)
        self.tab_widget = QTabWidget()
        container_layout.addWidget(self.tab_widget)
        # Add sections in address vertical layout
        self.oscillator_tab = DigitalOscillatorSection(
            self._create_parameter_slider,
            self._create_parameter_switch,
            self._create_parameter_combo_box,
            self.send_midi_parameter,
            self.partial_number,
            self.midi_helper,
            self.controls,
            self.part,
        )
        self.tab_widget.addTab(
            self.oscillator_tab,
            qta.icon("mdi.triangle-wave", color="#666666"),
            "Oscillator",
        )
        self.filter_tab = DigitalFilterSection(
            self._create_parameter_slider,
            self._create_parameter_switch,
            self.partial_number,
            self.midi_helper,
            self.controls,
            self.part,
        )
        self.tab_widget.addTab(
            self.filter_tab, qta.icon("ri.filter-3-fill", color="#666666"), "Filter"
        )
        self.amp_tab = DigitalAmpSection(
            self._create_parameter_slider,
            self.partial_number,
            self.midi_helper,
            self.controls,
            self.part,
        )
        self.tab_widget.addTab(
            self.amp_tab, qta.icon(
                "mdi.amplifier",
                color="#666666"),
            "Amplifier"
        )
        self.lfo_tab = DigitalLFOSection(
            self._create_parameter_slider,
            self._create_parameter_switch,
            self.controls
        )
        self.tab_widget.addTab(
            self.lfo_tab, qta.icon("mdi.sine-wave", color="#666666"), "LFO"
        )
        self.mod_lfo_tab = DigitalModLFOSection(
            self._create_parameter_slider,
            self._create_parameter_switch,
            self._on_parameter_changed,
            self.controls,
        )
        self.tab_widget.addTab(
            self.mod_lfo_tab, qta.icon("mdi.waveform", color="#666666"), "Mod LFO"
        )

        # Add container to scroll area
        main_layout.addWidget(container)
        self.updating_from_spinbox = False

    def update_filter_controls_state(self, mode: int):
        """Update filter controls enabled state based on mode"""
        enabled = mode != 0  # Enable if not BYPASS
        for param in [
            DigitalPartialParameter.FILTER_CUTOFF,
            DigitalPartialParameter.FILTER_RESONANCE,
            DigitalPartialParameter.FILTER_CUTOFF_KEYFOLLOW,
            DigitalPartialParameter.FILTER_ENV_VELOCITY_SENSITIVITY,
            DigitalPartialParameter.FILTER_ENV_DEPTH,
            DigitalPartialParameter.FILTER_SLOPE,
        ]:
            if param in self.controls:
                self.filter_tab.controls[param].setEnabled(enabled)
            self.filter_tab.filter_adsr_widget.setEnabled(enabled)

    def _on_waveform_selected(self, waveform: DigitalOscWave):
        """Handle waveform button clicks"""
        # Reset all buttons to default style
        for btn in self.oscillator_tab.wave_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet(JDXIStyle.BUTTON_RECT)

        # Apply active style to the selected waveform button
        selected_btn = self.oscillator_tab.wave_buttons.get(waveform)
        if selected_btn:
            selected_btn.setChecked(True)
            selected_btn.setStyleSheet(JDXIStyle.BUTTON_RECT_ACTIVE)

        # Send MIDI message
        if not self.send_midi_parameter(
            DigitalPartialParameter.OSC_WAVE, waveform.value
        ):
            logging.warning(f"Failed to set waveform to {waveform.name}")
