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

from decologr import Decologr as log
from PySide6.QtWidgets import (
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.core.synth.type import JDXiSynth
from jdxi_editor.midi.data.address.address import JDXiSysExOffsetSuperNATURALLMB
from jdxi_editor.midi.data.digital.oscillator import DigitalWaveOsc
from jdxi_editor.midi.data.digital.partial import DIGITAL_PARTIAL_NAMES
from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.digital.partial.amp.section import DigitalAmpSection
from jdxi_editor.ui.editors.digital.partial.filter.section import DigitalFilterSection
from jdxi_editor.ui.editors.digital.partial.lfo.lfo import DigitalLFOSection
from jdxi_editor.ui.editors.digital.partial.lfo.mod import DigitalModLFOSection
from jdxi_editor.ui.editors.digital.partial.oscillator.section import (
    DigitalOscillatorSection,
)
from jdxi_editor.ui.editors.synth.partial import PartialPanel


class DigitalPartialPanel(PartialPanel):
    """Editor for a single Digital Synth partial"""

    SYNTH_MAP = {
        1: JDXi.Synth.DIGITAL_SYNTH_1,
        2: JDXi.Synth.DIGITAL_SYNTH_2,
    }

    PARTIAL_ADDRESS_MAP = {
        1: JDXiSysExOffsetSuperNATURALLMB.PARTIAL_1,
        2: JDXiSysExOffsetSuperNATURALLMB.PARTIAL_2,
        3: JDXiSysExOffsetSuperNATURALLMB.PARTIAL_3,
    }

    BIPOLAR_PARAMETERS = {
        Digital.Param.OSC_PITCH_FINE,
        Digital.Param.OSC_PITCH_COARSE,
        Digital.Param.OSC_PITCH_ENV_DEPTH,
        Digital.Param.AMP_PAN,
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

        self.mod_lfo_shape_buttons = {}
        self.lfo_shape_buttons = {}

        self.oscillator_tab = None
        self.filter_tab = None
        self.midi_helper = midi_helper
        self.partial_number = partial_number
        self.preset_type = preset_type
        # Use parent's controls dict so sections and panel share one dict (do not assign new {} here)
        self._resolve_synth_data(synth_number)
        self._resolve_partial_name()
        self._init_state()
        self._build_ui()

        log.parameter(
            "DigitalPartialEditor initialized:", self, scope=self.__class__.__name__
        )

    # ------------------------------------------------------------------
    # Initialization helpers
    # ------------------------------------------------------------------

    def _resolve_synth_data(self, synth_number: int) -> None:
        """resolve synth data"""
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

        log.parameter(
            "Synth address:", self.synth_data.address, scope=self.__class__.__name__
        )

    def _resolve_partial_name(self) -> None:
        try:
            self.part_name = DIGITAL_PARTIAL_NAMES[self.partial_number]
        except IndexError:
            log.error(
                f"[[DigitalPartialPanel] Invalid partial_number: {self.partial_number}"
            )
            self.part_name = "Unknown"

        log.parameter("Partial name:", self.part_name, scope=self.__class__.__name__)

    def _init_state(self) -> None:
        self.updating_from_spinbox = False

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """build ui"""
        main_layout = QVBoxLayout(self)

        container = QWidget()
        container_layout = QVBoxLayout(container)

        self.tab_widget = QTabWidget()
        container_layout.addWidget(self.tab_widget)

        self._register_sections()

        main_layout.addWidget(container)

    def _register_sections(self) -> None:
        """Register sections"""
        log.message(scope=self.__class__.__name__, message=f"[_register_sections]")
        # Correct one
        self._add_tab(
            key=Digital.Tab.OSCILLATOR,
            widget=DigitalOscillatorSection(
                send_midi_parameter=self.send_midi_parameter,
                midi_helper=self.midi_helper,
                address=self.synth_data.address,
            ),
        )

        self._add_tab(
            key=Digital.Tab.FILTER,
            widget=DigitalFilterSection(
                send_midi_parameter=self.send_midi_parameter,
                midi_helper=self.midi_helper,
                address=self.synth_data.address,
            ),
        )

        self._add_tab(
            key=Digital.Tab.AMP,
            widget=DigitalAmpSection(
                send_midi_parameter=self.send_midi_parameter,
                midi_helper=self.midi_helper,
                address=self.synth_data.address,
            ),
        )

        self._add_tab(
            key=Digital.Tab.LFO,
            widget=DigitalLFOSection(
                send_midi_parameter=self.send_midi_parameter,
                midi_helper=self.midi_helper,
                address=self.synth_data.address,
            ),
        )

        self._add_tab(
            key=Digital.Tab.MODLFO,
            widget=DigitalModLFOSection(
                on_parameter_changed=self._on_parameter_changed,
                send_midi_parameter=self.send_midi_parameter,
                midi_helper=self.midi_helper,
                address=self.synth_data.address,
            ),
        )

    @property
    def lfo_depth_controls(self) -> dict:
        """
        Get a dictionary of LFO depth controls filtered from the main controls dictionary.
        This provides compatibility with the base class's _update_partial_lfo_depth method.

        :return: dict mapping LFO depth parameters to their control widgets
        """
        lfo_depth_params = {
            Digital.Param.LFO_PITCH_DEPTH,
            Digital.Param.LFO_FILTER_DEPTH,
            Digital.Param.LFO_AMP_DEPTH,
            Digital.Param.LFO_PAN_DEPTH,
            Digital.Param.MOD_LFO_PITCH_DEPTH,
            Digital.Param.MOD_LFO_FILTER_DEPTH,
            Digital.Param.MOD_LFO_AMP_DEPTH,
        }
        return {
            param: self.controls[param]
            for param in lfo_depth_params
            if param in self.controls
        }

    # ------------------------------------------------------------------
    # Behavior
    # ------------------------------------------------------------------

    def update_filter_controls_state(self, mode: int) -> None:
        """update filter controls state"""
        enabled = mode != 0  # BYPASS == 0

        params = (
            Digital.Param.FILTER_CUTOFF,
            Digital.Param.FILTER_RESONANCE,
            Digital.Param.FILTER_CUTOFF_KEYFOLLOW,
            Digital.Param.FILTER_ENV_VELOCITY_SENSITIVITY,
            Digital.Param.FILTER_ENV_DEPTH,
            Digital.Param.FILTER_SLOPE,
        )

        for param in params:
            widget = self.controls.get(param)
            if widget:
                widget.setEnabled(enabled)

        if self.filter_tab.adsr_widget:
            self.filter_tab.adsr_widget.setEnabled(enabled)

    def _on_waveform_selected(self, waveform: DigitalWaveOsc) -> None:
        """on waveform selected (harmonised Theme API)"""
        for btn in self.oscillator_tab.widgets.waveform_buttons.values():
            btn.setChecked(False)
            JDXi.UI.Theme.apply_button_rect(btn, analog=False)

        selected = self.oscillator_tab.widgets.waveform_buttons.get(waveform)
        if selected:
            selected.setChecked(True)
            JDXi.UI.Theme.apply_button_active(selected, analog=False)

        if not self.send_midi_parameter(Digital.Param.OSC_WAVEFORM, waveform.value):
            log.warning(
                scope=self.__class__.__name__,
                message=f"Failed to set waveform: {waveform.name}",
            )

    # ------------------------------------------------------------------

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.preset_type} partial {self.partial_number}"

    __repr__ = __str__
