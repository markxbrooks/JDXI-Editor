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

from typing import Dict, Optional, Union

from PySide6.QtWidgets import (
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from decologr import Decologr as log
from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import AddressOffsetSuperNATURALLMB
from jdxi_editor.midi.data.digital.oscillator import DigitalOscWave
from jdxi_editor.midi.data.digital.partial import DIGITAL_PARTIAL_NAMES
from jdxi_editor.midi.data.parameter.digital import DigitalCommonParam
from jdxi_editor.midi.data.parameter.digital.partial import DigitalPartialParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.synth.type import JDXiSynth
from jdxi_editor.ui.editors.digital.partial.amp import DigitalAmpSection
from jdxi_editor.ui.editors.digital.partial.filter import DigitalFilterSection
from jdxi_editor.ui.editors.digital.partial.lfo.lfo import DigitalLFOSection
from jdxi_editor.ui.editors.digital.partial.lfo.mod import DigitalModLFOSection
from jdxi_editor.ui.editors.digital.partial.oscillator import DigitalOscillatorSection
from jdxi_editor.ui.editors.synth.partial import PartialEditor


class DigitalPartialEditor(PartialEditor):
    """Editor for a single Digital Synth partial"""

    SYNTH_MAP = {
        1: JDXiSynth.DIGITAL_SYNTH_1,
        2: JDXiSynth.DIGITAL_SYNTH_2,
    }

    PARTIAL_ADDRESS_MAP = {
        1: AddressOffsetSuperNATURALLMB.PARTIAL_1,
        2: AddressOffsetSuperNATURALLMB.PARTIAL_2,
        3: AddressOffsetSuperNATURALLMB.PARTIAL_3,
    }

    BIPOLAR_PARAMETERS = {
        DigitalPartialParam.OSC_DETUNE,
        DigitalPartialParam.OSC_PITCH,
        DigitalPartialParam.OSC_PITCH_ENV_DEPTH,
        DigitalPartialParam.AMP_PAN,
    }

    def __init__(
        self,
        midi_helper: MidiIOHelper | None = None,
        synth_number: int = 1,
        partial_number: int = 1,
        preset_type: JDXiSynth | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.filter_tab = None
        self.midi_helper = midi_helper
        self.partial_number = partial_number
        self.preset_type = preset_type
        self.controls: dict[
            DigitalPartialParam | DigitalCommonParam, QWidget
        ] = {}

        self._resolve_synth_data(synth_number)
        self._resolve_partial_name()
        self._init_state()
        self._build_ui()

        log.parameter("DigitalPartialEditor initialized:", self)

    # ------------------------------------------------------------------
    # Initialization helpers
    # ------------------------------------------------------------------

    def _resolve_synth_data(self, synth_number: int) -> None:
        try:
            synth_type = self.SYNTH_MAP[synth_number]
        except KeyError:
            raise ValueError(
                f"Invalid synth_number: {synth_number}. Must be {list(self.SYNTH_MAP)}"
            )

        self._init_synth_data(
            synth_type=synth_type,
            partial_number=self.partial_number,
        )

        log.parameter("Synth address:", self.synth_data.address)

    def _resolve_partial_name(self) -> None:
        try:
            self.part_name = DIGITAL_PARTIAL_NAMES[self.partial_number]
        except IndexError:
            log.error(f"Invalid partial_number: {self.partial_number}")
            self.part_name = "Unknown"

        log.parameter("Partial name:", self.part_name)

    def _init_state(self) -> None:
        self.updating_from_spinbox = False

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)

        container = QWidget()
        container_layout = QVBoxLayout(container)

        self.tab_widget = QTabWidget()
        container_layout.addWidget(self.tab_widget)

        self._register_sections()

        main_layout.addWidget(container)

    def _register_sections(self) -> None:
        self._add_tab(
            key="oscillator",
            widget=DigitalOscillatorSection(
                create_parameter_slider=self._create_parameter_slider,
                create_parameter_switch=self._create_parameter_switch,
                create_parameter_combo_box=self._create_parameter_combo_box,
                send_midi_parameter=self.send_midi_parameter,
                midi_helper=self.midi_helper,
                controls=self.controls,
                address=self.synth_data.address,
            ),
            icon=JDXi.UI.IconRegistry.TRIANGLE_WAVE,
            label="Oscillator",
        )

        self._add_tab(
            key="filter",
            widget=DigitalFilterSection(
                create_parameter_slider=self._create_parameter_slider,
                create_parameter_switch=self._create_parameter_switch,
                create_parameter_combo_box=self._create_parameter_combo_box,
                send_midi_parameter=self.send_midi_parameter,
                midi_helper=self.midi_helper,
                controls=self.controls,
                address=self.synth_data.address,
            ),
            icon=JDXi.UI.IconRegistry.FILTER,
            label="Filter",
        )

        self._add_tab(
            key="amp",
            widget=DigitalAmpSection(
                create_parameter_slider=self._create_parameter_slider,
                create_parameter_switch=self._create_parameter_switch,
                create_parameter_combo_box=self._create_parameter_combo_box,
                send_midi_parameter=self.send_midi_parameter,
                midi_helper=self.midi_helper,
                controls=self.controls,
                address=self.synth_data.address,
            ),
            icon=JDXi.UI.IconRegistry.AMPLIFIER,
            label="Amp",
        )

        self._add_tab(
            key="lfo",
            widget=DigitalLFOSection(
                self._create_parameter_slider,
                self._create_parameter_switch,
                self._create_parameter_combo_box,
                self.controls,
                self.send_midi_parameter,
            ),
            icon=JDXi.UI.IconRegistry.SINE_WAVE,
            label="LFO",
        )

        self._add_tab(
            key="mod_lfo",
            widget=DigitalModLFOSection(
                create_parameter_slider=self._create_parameter_slider,
                create_parameter_combo_box=self._create_parameter_combo_box,
                create_parameter_switch=self._create_parameter_switch,
                on_parameter_changed=self._on_parameter_changed,
                controls=self.controls,
                send_midi_parameter=self.send_midi_parameter,
            ),
            icon=JDXi.UI.IconRegistry.WAVEFORM,
            label="Mod LFO",
        )

    def _add_tab(self, *, key: str, widget: QWidget, icon, label: str) -> None:
        self.tab_widget.addTab(
            widget,
            JDXi.UI.IconRegistry.get_icon(icon, color=JDXi.UI.Style.GREY),
            label,
        )
        setattr(self, f"{key}_tab", widget)

    # ------------------------------------------------------------------
    # Behavior
    # ------------------------------------------------------------------

    def update_filter_controls_state(self, mode: int) -> None:
        enabled = mode != 0  # BYPASS == 0

        params = (
            DigitalPartialParam.FILTER_CUTOFF,
            DigitalPartialParam.FILTER_RESONANCE,
            DigitalPartialParam.FILTER_CUTOFF_KEYFOLLOW,
            DigitalPartialParam.FILTER_ENV_VELOCITY_SENSITIVITY,
            DigitalPartialParam.FILTER_ENV_DEPTH,
            DigitalPartialParam.FILTER_SLOPE,
        )

        for param in params:
            widget = self.controls.get(param)
            if widget:
                widget.setEnabled(enabled)

        self.filter_tab.filter_adsr_widget.setEnabled(enabled)

    def _on_waveform_selected(self, waveform: DigitalOscWave) -> None:
        for btn in self.oscillator_tab.wave_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)

        selected = self.oscillator_tab.wave_buttons.get(waveform)
        if selected:
            selected.setChecked(True)
            selected.setStyleSheet(JDXi.UI.Style.BUTTON_RECT_ACTIVE)

        if not self.send_midi_parameter(
            DigitalPartialParam.OSC_WAVE, waveform.value
        ):
            log.warning(f"Failed to set waveform: {waveform.name}")

    # ------------------------------------------------------------------

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.preset_type} partial {self.partial_number}"

    __repr__ = __str__
