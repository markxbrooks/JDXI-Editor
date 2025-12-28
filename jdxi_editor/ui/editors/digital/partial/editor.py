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

from typing import Dict, Union, Optional

import qtawesome as qta
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTabWidget,
)

from jdxi_editor.log.logger import Logger as log
from jdxi_editor.midi.data.address.address import AddressOffsetSuperNATURALLMB
from jdxi_editor.midi.data.parameter.digital.partial import (
    AddressParameterDigitalPartial,
)
from jdxi_editor.midi.data.digital.oscillator import DigitalOscWave
from jdxi_editor.midi.data.digital.partial import DIGITAL_PARTIAL_NAMES
from jdxi_editor.midi.data.parameter.digital.common import AddressParameterDigitalCommon
from jdxi_editor.jdxi.synth.type import JDXiSynth
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.digital.partial.amp import DigitalAmpSection
from jdxi_editor.ui.editors.digital.partial.filter import DigitalFilterSection
from jdxi_editor.ui.editors.digital.partial.lfo import DigitalLFOSection
from jdxi_editor.ui.editors.digital.partial.mod_lfo import DigitalModLFOSection
from jdxi_editor.ui.editors.digital.partial.oscillator import DigitalOscillatorSection
from jdxi_editor.ui.editors.synth.partial import PartialEditor
from jdxi_editor.jdxi.style import JDXiStyle


class DigitalPartialEditor(PartialEditor):
    """Editor for address single partial"""

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        synth_number: int = 1,
        partial_number: int = 1,
        preset_type: JDXiSynth = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.filter_mode_switch = None
        """
        Initialize the DigitalPartialEditor

        :param midi_helper: MidiIOHelper
        :param synth_number: int
        :param partial_number: int
        :param preset_type: JDXiSynth
        :param parent: QWidget
        """
        self.partial_address_default = AddressOffsetSuperNATURALLMB.PARTIAL_1
        self.partial_address_map = {
            1: AddressOffsetSuperNATURALLMB.PARTIAL_1,
            2: AddressOffsetSuperNATURALLMB.PARTIAL_2,
            3: AddressOffsetSuperNATURALLMB.PARTIAL_3,
        }
        self.bipolar_parameters = [
            AddressParameterDigitalPartial.OSC_DETUNE,
            AddressParameterDigitalPartial.OSC_PITCH,
            AddressParameterDigitalPartial.OSC_PITCH_ENV_DEPTH,
            AddressParameterDigitalPartial.AMP_PAN,
        ]
        self.midi_helper = midi_helper
        self.partial_number = partial_number
        self.preset_type = preset_type
        if synth_number == 1:
            self._init_synth_data(synth_type=JDXiSynth.DIGITAL_SYNTH_1, partial_number=self.partial_number)
        elif synth_number == 2:
            self._init_synth_data(synth_type=JDXiSynth.DIGITAL_SYNTH_2, partial_number=self.partial_number)
            """elif synth_number == 3:
                self._init_synth_data(synth_type=JDXiSynth.DIGITAL_SYNTH_3, partial_number=self.partial_number)"""
        else:
            raise ValueError(f"Invalid synth_number: {synth_number}. Must be 1 or 2.")
        log.parameter("Initializing partial:", self.synth_data.address)
        if 0 <= partial_number < len(DIGITAL_PARTIAL_NAMES):
            self.part_name = DIGITAL_PARTIAL_NAMES[partial_number]
            log.parameter("Partial name:", self.part_name)
        else:
            log.error(f"Invalid partial_num: {partial_number}. Using default value.")
            self.part_name = "Unknown"  # Provide a fallback value
        # Store parameter controls for easy access
        self.controls: Dict[
            Union[AddressParameterDigitalPartial, AddressParameterDigitalCommon],
            QWidget,
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
            self.address,
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
            self.synth_data.address,
        )
        self.tab_widget.addTab(
            self.filter_tab, qta.icon("ri.filter-3-fill", color="#666666"), "Filter"
        )
        self.amp_tab = DigitalAmpSection(
            self._create_parameter_slider,
            self.partial_number,
            self.midi_helper,
            self.controls,
            self.synth_data.address,
        )
        self.tab_widget.addTab(
            self.amp_tab, qta.icon("mdi.amplifier", color="#666666"), "Amp"
        )
        self.lfo_tab = DigitalLFOSection(
            self._create_parameter_slider,
            self._create_parameter_switch,
            self._create_parameter_combo_box,
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
        log.parameter(f"DigitalPartialEditor initialized for",  self)

    def __str__(self):
        return f"{self.__class__.__name__} {self.preset_type} partial: {self.partial_number}"

    def __repr__(self):
        return f"{self.__class__.__name__} {self.preset_type} partial: {self.partial_number}"

    def update_filter_controls_state(self, mode: int):
        """
        Update filter controls enabled state based on mode

        :param mode: int
        """
        enabled = mode != 0  # Enable if not BYPASS
        for param in [
            AddressParameterDigitalPartial.FILTER_CUTOFF,
            AddressParameterDigitalPartial.FILTER_RESONANCE,
            AddressParameterDigitalPartial.FILTER_CUTOFF_KEYFOLLOW,
            AddressParameterDigitalPartial.FILTER_ENV_VELOCITY_SENSITIVITY,
            AddressParameterDigitalPartial.FILTER_ENV_DEPTH,
            AddressParameterDigitalPartial.FILTER_SLOPE,
        ]:
            if param in self.controls:
                self.filter_tab.controls[param].setEnabled(enabled)
            self.filter_tab.filter_adsr_widget.setEnabled(enabled)

    def _on_waveform_selected(self, waveform: DigitalOscWave):
        """
        Handle waveform button clicks

        :param waveform: DigitalOscWave
        """
        # Reset all buttons to default style
        for btn in self.oscillator_tab.wave_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet(JDXiStyle.BUTTON_RECT)

        # Apply active style to the selected waveform button
        selected_btn = self.oscillator_tab.wave_buttons.get(waveform)
        if selected_btn:
            selected_btn.setChecked(True)
            selected_btn.setStyleSheet(JDXiStyle.BUTTON_RECT_ACTIVE)

        # Send MIDI message
        if not self.send_midi_parameter(
            AddressParameterDigitalPartial.OSC_WAVE, waveform.value
        ):
            log.warning(f"Failed to set waveform to {waveform.name}")
