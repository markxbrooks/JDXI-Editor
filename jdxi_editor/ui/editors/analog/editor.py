"""
Module: analog_synth_editor
===========================

This module defines the `AnalogSynthEditor` class, which provides a PySide6-based
user interface for editing analog synthesizer parameters in the Roland JD-Xi synthesizer.
It extends the `SynthEditor` base class and integrates MIDI communication for real-time
parameter adjustments and preset management.

Key Features:
-------------
- Provides a graphical editor for modifying analog synth parameters, including
  oscillator, filter, amp, LFO, and envelope settings.
- Supports MIDI communication to send and receive real-time parameter changes.
- Allows selection of different analog synth presets from a dropdown menu.
- Displays an instrument image that updates based on the selected preset.
- Includes a scrollable layout for managing a variety of parameter controls.
- Implements bipolar parameter handling for proper UI representation.
- Supports waveform selection with custom buttons and icons.
- Provides a "Send Read Request to Synth" button to retrieve current synth settings.
- Enables MIDI-triggered updates via incoming program changes and parameter adjustments.

Dependencies:
-------------
- PySide6 (for UI components and event handling)
- MIDIHelper (for handling MIDI communication)
- PresetHandler (for managing synth presets)
- Various custom enums and helper classes (Analog.Parameter, AnalogCommonParameter, etc.)

Usage:
------
The `AnalogSynthEditor` class can be instantiated as part of a larger PySide6 application.
It requires a `MIDIHelper` instance for proper communication with the synthesizer.

Example:
--------
    midi_helper = MIDIHelper()
    preset_helper = PresetHandler()
    editor = AnalogSynthEditor(midi_helper, preset_helper)
    editor.show()

"""

from typing import TYPE_CHECKING, Dict, Optional, Union

from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QWidget,
)

from jdxi_editor.midi.data.parameter.analog.spec import JDXiMidiAnalog as Analog
from jdxi_editor.ui.editors.base.editor import BaseSynthEditor

if TYPE_CHECKING:
    from jdxi_editor.ui.preset.helper import JDXiPresetHelper

from decologr import Decologr as log

from jdxi_editor.core.synth.type import JDXiSynth
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.analog.amp import AnalogAmpSection
from jdxi_editor.ui.editors.analog.common import AnalogCommonSection
from jdxi_editor.ui.editors.analog.filter import AnalogFilterSection
from jdxi_editor.ui.editors.analog.lfo import AnalogLFOSection
from jdxi_editor.ui.editors.analog.oscillator import AnalogOscillatorSection


class AnalogSynthEditor(BaseSynthEditor):
    """Analog Synth Editor UI."""

    SUB_OSC_TYPE_MAP = {0: 0, 1: 1, 2: 2}
    
    SYNTH_SPEC = Analog

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        preset_helper: Optional["JDXiPresetHelper"] = None,  # type: ignore[name-defined]
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize the AnalogSynthEditor

        :param midi_helper: MidiIOHelper
        :param preset_helper: JDXIPresetHelper
        :param parent: QWidget
        """
        super().__init__(midi_helper=midi_helper, parent=parent)
        self.preset_helper = preset_helper
        self.main_window = parent
        self.analog = True

        # --- Initialize mappings as empty dicts/lists early to prevent AttributeError
        # --- These will be populated after sections are created
        self.adsr_mapping = {}
        self.pitch_env_mapping = {}
        self.pwm_mapping = {}

        self._init_parameter_mappings()
        self._init_synth_data(JDXiSynth.ANALOG_SYNTH)
        self.setup_ui()

        if self.midi_helper:
            self.midi_helper.midi_program_changed.connect(self._handle_program_change)
            self.midi_helper.midi_sysex_json.connect(self._dispatch_sysex_to_area)
            log.message("[AnalogSynthEditor] MIDI signals connected")
        else:
            log.message("[AnalogSynthEditor] MIDI signals not connected")

        self.refresh_shortcut = QShortcut(QKeySequence.StandardKey.Refresh, self)
        self.refresh_shortcut.activated.connect(self.data_request)

        # --- Define mapping dictionaries
        self.filter_switch_map = {0: 0, 1: 1}
        self.osc_waveform_map = {
            0: Analog.Wave.Osc.SAW,
            1: Analog.Wave.Osc.TRI,
            2: Analog.Wave.Osc.PW_SQUARE,
        }
        self._create_sections()
        self.adsr_mapping = {
            Analog.Param.AMP_ENV_ATTACK_TIME: self.amp_section.adsr_widget.attack_control,
            Analog.Param.AMP_ENV_DECAY_TIME: self.amp_section.adsr_widget.decay_control,
            Analog.Param.AMP_ENV_SUSTAIN_LEVEL: self.amp_section.adsr_widget.sustain_control,
            Analog.Param.AMP_ENV_RELEASE_TIME: self.amp_section.adsr_widget.release_control,
            Analog.Param.FILTER_ENV_ATTACK_TIME: self.filter_section.adsr_widget.attack_control,
            Analog.Param.FILTER_ENV_DECAY_TIME: self.filter_section.adsr_widget.decay_control,
            Analog.Param.FILTER_ENV_SUSTAIN_LEVEL: self.filter_section.adsr_widget.sustain_control,
            Analog.Param.FILTER_ENV_RELEASE_TIME: self.filter_section.adsr_widget.release_control,
        }
        self.pitch_env_mapping = {
            Analog.Param.OSC_PITCH_ENV_ATTACK_TIME: self.oscillator_section.pitch_env_widget.attack_control,
            Analog.Param.OSC_PITCH_ENV_DECAY_TIME: self.oscillator_section.pitch_env_widget.decay_control,
            Analog.Param.OSC_PITCH_ENV_DEPTH: self.oscillator_section.pitch_env_widget.depth_control,
        }
        self.pwm_mapping = {
            Analog.Param.OSC_PULSE_WIDTH: self.oscillator_section.pwm_widget.controls[
                Analog.Param.OSC_PULSE_WIDTH
            ],
            Analog.Param.OSC_PULSE_WIDTH_MOD_DEPTH: self.oscillator_section.pwm_widget.controls[
                Analog.Param.OSC_PULSE_WIDTH_MOD_DEPTH
            ],
        }
        # Note: data_request() is called in showEvent() when editor is displayed

    def setup_ui(self):
        """Set up the Analog Synth Editor UI."""
        super().setup_ui()

    def _create_sections(self):
        """Create the sections for the Analog Synth Editor."""
        self.oscillator_section = AnalogOscillatorSection(
            waveform_selected_callback=self._on_waveform_selected,
            wave_buttons=self.wave_buttons,
            midi_helper=self.midi_helper,
            controls=self.controls,
            address=self.address,
        )
        self.filter_section = AnalogFilterSection(
            controls=self.controls,
            address=self.synth_data.address,
            send_midi_parameter=self.send_midi_parameter,
            midi_helper=self.midi_helper,
            on_filter_mode_changed=self._on_filter_mode_changed,
            parent=self,
        )
        self.amp_section = AnalogAmpSection(
            address=self.synth_data.address,
            controls=self.controls,
            parent=self,
        )
        self.lfo_section = AnalogLFOSection(
            on_lfo_shape_changed=self._on_lfo_shape_changed,
            lfo_shape_buttons=self.lfo_shape_buttons,
            send_midi_parameter=self.send_midi_parameter,
            controls=self.controls,
        )
        self.common_section = AnalogCommonSection(
            controls=self.controls,
            send_midi_parameter=self.send_midi_parameter,
            midi_helper=self.midi_helper,
        )
        self.add_tabs()

    def _init_parameter_mappings(self):
        """Initialize MIDI parameter mappings."""
        self.cc_parameters = {
            "Cutoff": Analog.ControlChange.CUTOFF,
            "Resonance": Analog.ControlChange.RESONANCE,
            "Level": Analog.ControlChange.LEVEL,
            "LFO Rate": Analog.ControlChange.LFO_RATE,
        }

        self.nrpn_parameters = {
            "Envelope": Analog.RPN.ENVELOPE.value.msb_lsb,  # --- (0, 124),
            "LFO Shape": Analog.RPN.LFO_SHAPE.value.msb_lsb,  # --- (0, 3),
            "LFO Pitch Depth": Analog.RPN.LFO_PITCH_DEPTH.value.msb_lsb,  # --- (0, 15),
            "LFO Filter Depth": Analog.RPN.LFO_FILTER_DEPTH.value.msb_lsb,  # --- (0, 18),
            "LFO Amp Depth": Analog.RPN.LFO_AMP_DEPTH.value.msb_lsb,  # --- (0, 21),
            "Pulse Width": Analog.RPN.PULSE_WIDTH.value.msb_lsb,  # --- (0, 37),
        }

        # --- Reverse lookup map
        self.nrpn_map = {v: k for k, v in self.nrpn_parameters.items()}

    def update_filter_controls_state(self, mode: int):
        """Update filter controls enabled state (delegate to section, same mechanism as Digital)."""
        log.message(
            f"[AnalogSynthEditor] update_filter_controls_state: mode={mode} "
            f"has filter_section={hasattr(self, 'filter_section')} "
            f"filter_section is not None={getattr(self, 'filter_section', None) is not None}"
        )
        if hasattr(self, "filter_section") and self.filter_section is not None:
            self.filter_section.update_controls_state(mode)
        else:
            log.warning(
                "[AnalogSynthEditor] update_filter_controls_state: no filter_section, skipping"
            )

    def _on_filter_mode_changed(self, mode: int):
        """Handle filter mode changes (callback from filter section when mode button clicked)."""
        log.message(f"[AnalogSynthEditor] _on_filter_mode_changed: mode={mode}")
        self.update_filter_controls_state(mode)
