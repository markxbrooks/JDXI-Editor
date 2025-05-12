"""
VocalFXEditor Module

This module defines the `VocalFXEditor` class, a PySide6-based editor for controlling
the Vocal FX section of the Roland JD-Xi synthesizer. It provides a graphical interface
for adjusting various vocal effects such as vocoder settings, auto-pitch parameters,
and mixer controls.

Features:
- Scrollable UI with multiple tabs for organizing vocal effect settings.
- Support for vocoder controls, including envelope, mic sensitivity, and synthesis levels.
- Auto-pitch settings with selectable pitch type, scale, key, and gender adjustment.
- Mixer section for controlling levels, panning, reverb, and delay send levels.
- MIDI integration for real-time parameter control using `MIDIHelper`.
- Dynamic instrument image loading to visually represent the effect in use.

Dependencies:
- PySide6 for UI components.
- `MIDIHelper` for sending MIDI messages to the JD-Xi.
- `VocalFXParameter` for managing effect-specific MIDI parameters.

"""

from typing import Optional, Dict
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QScrollArea,
    QTabWidget,
)
from PySide6.QtCore import Qt

from jdxi_editor.midi.data.address.address import (
    RolandSysExAddress,
    ZERO_BYTE,
    AddressMemoryAreaMSB,
    AddressOffsetTemporaryToneUMB,
    AddressOffsetProgramLMB,
)
from jdxi_editor.midi.data.parameter.program.common import AddressParameterProgramCommon
from jdxi_editor.midi.data.parameter.synth import AddressParameter
from jdxi_editor.midi.io import MidiIOHelper
from jdxi_editor.jdxi.preset.helper import JDXiPresetHelper
from jdxi_editor.ui.editors.synth.simple import BasicEditor
from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.midi.data.vocal_effects.vocal import (
    VocalAutoPitchType,
    VocalOutputAssign,
    VocalAutoPitchKey,
    VocalAutoPitchNote,
    VocoderEnvelope,
    VocoderHPF,
    VocalOctaveRange,
    VocalFxSwitch,
)
from jdxi_editor.midi.data.parameter.vocal_fx import AddressParameterVocalFX
from jdxi_editor.ui.widgets.display.digital import DigitalTitle


class VocalFXEditor(BasicEditor):
    """Vocal Effects Window Class"""

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        preset_helper: JDXiPresetHelper = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(midi_helper=midi_helper, parent=parent)
        self.setWindowTitle("Vocal FX")
        self.preset_helper = preset_helper
        self.address = RolandSysExAddress(
            AddressMemoryAreaMSB.TEMPORARY_PROGRAM,
            AddressOffsetTemporaryToneUMB.COMMON,
            AddressOffsetProgramLMB.VOCAL_EFFECT,
            ZERO_BYTE,
        )
        self.setStyleSheet(JDXiStyle.EDITOR + JDXiStyle.TABS)

        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        self.controls: Dict[AddressParameter, QWidget] = {}

        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Create container widget for scroll area
        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)

        # self.title_label = QLabel("Vocal Effects")
        self.title_label = DigitalTitle()
        self.title_label.setText("Vocal Effects")
        self.title_label.setStyleSheet(JDXiStyle.INSTRUMENT_TITLE_LABEL)
        title_layout = QHBoxLayout()
        title_layout.addWidget(self.title_label)
        container_layout.addLayout(title_layout)
        # Image display
        self.image_label = QLabel()
        self.image_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )  # Center align the image
        self.default_image = "vocal_fx.png"
        self.instrument_icon_folder = "vocal_fx"
        container_layout.addWidget(self.image_label)
        self.update_instrument_image()
        title_layout.addWidget(self.image_label)
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self._create_common_section(), "Common")
        self.tab_widget.addTab(self._create_vocal_effect_section(), "Vocal FX")
        self.tab_widget.addTab(self._create_mixer_section(), "Mixer")
        self.tab_widget.addTab(self._create_auto_pitch_section(), "Auto Pitch")

        # Add sections to container
        container_layout.addWidget(self.tab_widget)

        # Add container to scroll area
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def _create_common_section(self) -> QWidget:
        """
        _create_common_section
        :return: QWidget
        """
        common_section = QWidget()
        layout = QVBoxLayout()
        common_section.setLayout(layout)
        self.program_tempo = self._create_parameter_slider(
            AddressParameterProgramCommon.PROGRAM_TEMPO, "Tempo"
        )
        layout.addWidget(self.program_tempo)

        vocal_effect_switch_row = QHBoxLayout()
        self.vocal_effect_type = self._create_parameter_combo_box(
            AddressParameterProgramCommon.VOCAL_EFFECT,
            "Vocal Effect",
            ["OFF", "VOCODER", "AUTO - PITCH"],
            [0, 1, 2],
        )

        vocal_effect_switch_row.addWidget(self.vocal_effect_type)
        layout.addLayout(vocal_effect_switch_row)

        self.vocal_effect_number = self._create_parameter_slider(
            AddressParameterProgramCommon.VOCAL_EFFECT_NUMBER, "Effect Number"
        )
        layout.addWidget(self.vocal_effect_number)

        self.program_level = self._create_parameter_slider(
            AddressParameterProgramCommon.PROGRAM_LEVEL, "Level"
        )
        layout.addWidget(self.program_level)

        # Add Effect Part switch
        effect_part_switch_row = QHBoxLayout()
        self.effect_part_switch = self._create_parameter_switch(
            AddressParameterVocalFX.VOCODER_SWITCH, "Effect Part:", ["OFF", "ON"]
        )
        effect_part_switch_row.addWidget(self.effect_part_switch)
        layout.addLayout(effect_part_switch_row)  # Add at bottom

        # Add Auto Note switch
        auto_note_switch_row = QHBoxLayout()
        self.auto_note_switch = self._create_parameter_switch(
            AddressParameterProgramCommon.AUTO_NOTE_SWITCH, "Auto Note:", ["OFF", "ON"]
        )
        auto_note_switch_row.addWidget(self.auto_note_switch)
        layout.addLayout(auto_note_switch_row)  # Add at bottom

        return common_section

    def _create_vocal_effect_section(self) -> QWidget:
        """Create general vocal effect controls section"""
        vocal_effect_section = QWidget()
        layout = QVBoxLayout()
        vocal_effect_section.setLayout(layout)

        # Add vocoder switch
        switch_row = QHBoxLayout()
        self.vocoder_switch = self._create_parameter_switch(
            AddressParameterVocalFX.VOCODER_SWITCH, "Vocoder:", ["OFF", "ON"]
        )
        switch_row.addWidget(self.vocoder_switch)
        layout.addLayout(switch_row)  # Add at top

        # Add Vocoder controls
        vocoder_group = QGroupBox("Vocoder Settings")
        vocoder_layout = QVBoxLayout()
        vocoder_group.setLayout(vocoder_layout)

        # Envelope Type
        env_row = QHBoxLayout()
        env_row.addWidget(QLabel("Envelope"))
        self.vocoder_env = self._create_parameter_combo_box(
            AddressParameterVocalFX.VOCODER_ENVELOPE,
            "Envelope",
            [env.display_name for env in VocoderEnvelope],
            [env.value for env in VocoderEnvelope],
        )
        env_row.addWidget(self.vocoder_env)
        vocoder_layout.addLayout(env_row)

        # Level controls
        levels_row_layout = QHBoxLayout()
        self.vocoder_level = self._create_parameter_slider(
            AddressParameterVocalFX.VOCODER_LEVEL, "Level", 1
        )

        self.vocoder_mic_sens = self._create_parameter_slider(
            AddressParameterVocalFX.VOCODER_MIC_SENS, "Mic Sensitivity", 1
        )

        self.vocoder_synth_level = self._create_parameter_slider(
            AddressParameterVocalFX.VOCODER_SYNTH_LEVEL, "Synth Level", 1
        )

        self.vocoder_mic_mix = self._create_parameter_slider(
            AddressParameterVocalFX.VOCODER_MIC_MIX, "Mic Mix", 1
        )

        self.vocoder_hpf = self._create_parameter_combo_box(
            AddressParameterVocalFX.VOCODER_MIC_HPF,
            "HPF",
            [freq.display_name for freq in VocoderHPF],
            [freq.value for freq in VocoderHPF],
        )

        # HPF Frequency
        hpf_row = QHBoxLayout()
        hpf_row.addWidget(self.vocoder_hpf)

        # Add all controls
        levels_row_layout.addWidget(self.vocoder_level)
        levels_row_layout.addWidget(self.vocoder_mic_sens)
        levels_row_layout.addWidget(self.vocoder_synth_level)
        levels_row_layout.addWidget(self.vocoder_mic_mix)
        vocoder_layout.addLayout(levels_row_layout)
        vocoder_layout.addLayout(hpf_row)

        layout.addWidget(vocoder_group)
        vocoder_group.setStyleSheet(JDXiStyle.ADSR)
        return vocal_effect_section

    def _create_mixer_section(self) -> QWidget:
        """
        _create_mixer_section
        :return: QWidget
        """
        mixer_section = QWidget()
        layout = QVBoxLayout()
        mixer_section.setLayout(layout)

        # Level and Pan
        self.level = self._create_parameter_slider(
            AddressParameterVocalFX.LEVEL,
            "Level",
        )
        self.pan = self._create_parameter_slider(
            AddressParameterVocalFX.PAN, "Pan"
        )  # Center at 0

        # Send Levels
        self.delay_send_level_slider = self._create_parameter_slider(
            AddressParameterVocalFX.DELAY_SEND_LEVEL, "Delay Send"
        )
        self.reverb_send_level_slider = self._create_parameter_slider(
            AddressParameterVocalFX.REVERB_SEND_LEVEL, "Reverb Send"
        )

        # Output Assign
        output_row = QHBoxLayout()
        output_row.addWidget(QLabel("Output"))
        self.output_assign = self._create_parameter_combo_box(
            AddressParameterVocalFX.OUTPUT_ASSIGN,
            "Output",
            [output.display_name for output in VocalOutputAssign],
            [output.value for output in VocalOutputAssign],
        )
        output_row.addWidget(self.output_assign)
        layout.addLayout(output_row)

        layout.addWidget(self.level)
        layout.addWidget(self.pan)
        layout.addWidget(self.delay_send_level_slider)
        layout.addWidget(self.reverb_send_level_slider)

        return mixer_section

    def _create_auto_pitch_section(self):
        """
        _create_auto_pitch_section
        :return: QWidget
        """
        auto_pitch_section = QWidget()
        self.auto_pitch_group = auto_pitch_section  # Store reference
        layout = QVBoxLayout()
        auto_pitch_section.setLayout(layout)

        self.pitch_switch = self._create_parameter_switch(
            AddressParameterVocalFX.AUTO_PITCH_SWITCH,
            "Auto Pitch",
            [switch.display_name for switch in VocalFxSwitch],
        )

        # Type selector
        type_row = QHBoxLayout()
        self.auto_pitch_type = self._create_parameter_combo_box(
            AddressParameterVocalFX.AUTO_PITCH_TYPE,
            "Pitch Type",
            [pitch_type.display_name for pitch_type in VocalAutoPitchType],
            [pitch_type.value for pitch_type in VocalAutoPitchType],
        )
        type_row.addWidget(self.auto_pitch_type)

        # Scale selector
        scale_row = QHBoxLayout()
        self.pitch_scale = self._create_parameter_combo_box(
            AddressParameterVocalFX.AUTO_PITCH_SCALE,
            "Scale",
            ["CHROMATIC", "Maj(Min)"],
            [0, 1],
        )
        scale_row.addWidget(self.pitch_scale)

        # Key selector
        key_row = QHBoxLayout()
        self.pitch_key = self._create_parameter_combo_box(
            AddressParameterVocalFX.AUTO_PITCH_KEY,
            "Key",
            [key.display_name for key in VocalAutoPitchKey],
            [key.value for key in VocalAutoPitchKey],
        )
        key_row.addWidget(self.pitch_key)

        # Note selector
        note_row = QHBoxLayout()
        self.pitch_note = self._create_parameter_combo_box(
            AddressParameterVocalFX.AUTO_PITCH_NOTE,
            "Note",
            [note.display_name for note in VocalAutoPitchNote],
            [note.value for note in VocalAutoPitchNote],
        )
        note_row.addWidget(self.pitch_note)

        # Gender and Octave controls
        self.gender = self._create_parameter_slider(
            AddressParameterVocalFX.AUTO_PITCH_GENDER, "Gender"
        )

        self.octave = self._create_parameter_switch(
            AddressParameterVocalFX.AUTO_PITCH_OCTAVE,
            "Octave",
            [range.name for range in VocalOctaveRange],
        )

        # Dry/Wet Balance
        self.auto_pitch_balance = self._create_parameter_slider(
            AddressParameterVocalFX.AUTO_PITCH_BALANCE, "D/W Balance"
        )

        # Add all controls to layout
        layout.addWidget(self.pitch_switch)
        layout.addLayout(type_row)
        layout.addLayout(scale_row)
        layout.addLayout(key_row)
        layout.addLayout(note_row)
        layout.addWidget(self.gender)
        layout.addWidget(self.octave)
        layout.addWidget(self.auto_pitch_balance)

        return auto_pitch_section
