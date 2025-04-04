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

import os
from typing import Optional, Dict
from PySide6.QtGui import QPixmap
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

from jdxi_editor.midi.data.parameter.program.common import ProgramCommonParameter
from jdxi_editor.midi.data.parameter.synth import SynthParameter
from jdxi_editor.midi.io import MidiIOHelper
from jdxi_editor.ui.editors.synth.editor import SynthEditor
from jdxi_editor.ui.style import Style
from jdxi_editor.midi.data.constants.vocal import (
    VOCAL_FX_AREA,
    VOCAL_FX_PART,
    VOCAL_FX_GROUP,
)
from jdxi_editor.midi.data.vocal_effects.vocal import VocalAutoPitchType, VocalOutputAssign, VocalAutoPitchKey, \
    VocalAutoPitchNote, \
    VocoderEnvelope, VocoderHPF, VocalOctaveRange, VocalFxSwitch
from jdxi_editor.midi.data.parameter.vocal_fx import VocalFXParameter
from jdxi_editor.ui.widgets.display.digital import DigitalTitle


class VocalFXEditor(SynthEditor):
    """Vocal Effects Window Class"""

    def __init__(
        self, midi_helper: Optional[MidiIOHelper] = None, parent: Optional[QWidget] = None
    ):
        super().__init__(midi_helper, parent)
        self.setWindowTitle("Vocal FX")
        self.setMinimumHeight(750)
        self.setMinimumWidth(650)
        self.area = VOCAL_FX_AREA
        self.part = VOCAL_FX_PART
        self.group = VOCAL_FX_GROUP
        self.setStyleSheet(Style.JDXI_EDITOR + Style.JDXI_TABS)

        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        self.controls: Dict[
            SynthParameter, QWidget
        ] = {}

        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Create container widget for scroll area
        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)

        #self.title_label = QLabel("Vocal Effects")
        self.title_label = DigitalTitle()
        self.title_label.setText("Vocal Effects")
        self.title_label.setStyleSheet(Style.JDXI_INSTRUMENT_TITLE_LABEL)
        title_layout = QHBoxLayout()
        title_layout.addWidget(self.title_label)
        container_layout.addLayout(title_layout)
        # Image display
        self.image_label = QLabel()
        self.image_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )  # Center align the image
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

    def update_instrument_image(self):
        image_loaded = False

        def load_and_set_image(image_path):
            """Helper function to load and set the image on the label."""
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                scaled_pixmap = pixmap.scaledToHeight(
                    200, Qt.TransformationMode.SmoothTransformation
                )  # Resize to 250px height
                self.image_label.setPixmap(scaled_pixmap)
                return True
            return False

        # Define paths
        default_image_path = os.path.join("resources", "vocal_fx", "vocal_fx.png")

        if not image_loaded:
            if not load_and_set_image(default_image_path):
                self.image_label.clear()  # Clear label if default image is also missing

    def _create_common_section(self):
        common_section = QWidget()
        layout = QVBoxLayout()
        common_section.setLayout(layout)
        self.program_tempo = self._create_parameter_slider(
            ProgramCommonParameter.PROGRAM_TEMPO, "Tempo"
        )
        layout.addWidget(self.program_tempo)

        vocal_effect_switch_row = QHBoxLayout()
        self.vocal_effect_type = self._create_parameter_combo_box(
            ProgramCommonParameter.VOCAL_EFFECT,
            "Vocal Effect",
            ["OFF", "VOCODER", "AUTO - PITCH"],
            [0, 1, 2],
        )

        vocal_effect_switch_row.addWidget(self.vocal_effect_type)
        layout.addLayout(vocal_effect_switch_row)

        self.vocal_effect_number = self._create_parameter_slider(
            ProgramCommonParameter.VOCAL_EFFECT_NUMBER, "Effect Number"
        )
        layout.addWidget(self.vocal_effect_number)

        self.program_level = self._create_parameter_slider(
            ProgramCommonParameter.PROGRAM_LEVEL, "Level"
        )
        layout.addWidget(self.program_level)

        # Add Effect Part switch
        effect_part_switch_row = QHBoxLayout()
        self.effect_part_switch = self._create_parameter_switch(VocalFXParameter.VOCODER_SWITCH,
                                                                "Effect Part:",
                                                                ["OFF", "ON"])
        effect_part_switch_row.addWidget(self.effect_part_switch)
        layout.addLayout(effect_part_switch_row)  # Add at bottom

        # Add Auto Note switch
        auto_note_switch_row = QHBoxLayout()
        self.auto_note_switch = self._create_parameter_switch(ProgramCommonParameter.AUTO_NOTE_SWITCH,
                                                              "Auto Note:",
                                                              ["OFF", "ON"])
        auto_note_switch_row.addWidget(self.auto_note_switch)
        layout.addLayout(auto_note_switch_row)  # Add at bottom

        return common_section

    def _create_vocal_effect_section(self):
        """Create general vocal effect controls section"""
        vocal_effect_section = QWidget()
        layout = QVBoxLayout()
        vocal_effect_section.setLayout(layout)

        # Add vocoder switch
        switch_row = QHBoxLayout()
        self.vocoder_switch = self._create_parameter_switch(VocalFXParameter.VOCODER_SWITCH,
                                                            "Vocoder:",
                                                            ["OFF", "ON"]
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
            VocalFXParameter.VOCODER_ENVELOPE,
            "Envelope",
            [env.display_name for env in VocoderEnvelope],
            [env.value for env in VocoderEnvelope],
        )
        env_row.addWidget(self.vocoder_env)
        vocoder_layout.addLayout(env_row)

        # Level controls
        levels_row_layout = QHBoxLayout()
        self.vocoder_level = self._create_parameter_slider(
            VocalFXParameter.VOCODER_LEVEL, "Level", 1
        )

        self.vocoder_mic_sens = self._create_parameter_slider(
            VocalFXParameter.VOCODER_MIC_SENS, "Mic Sensitivity", 1
        )

        self.vocoder_synth_level = self._create_parameter_slider(
            VocalFXParameter.VOCODER_SYNTH_LEVEL, "Synth Level", 1
        )

        self.vocoder_mic_mix = self._create_parameter_slider(
            VocalFXParameter.VOCODER_MIC_MIX, "Mic Mix", 1
        )

        self.vocoder_hpf = self._create_parameter_combo_box(
            VocalFXParameter.VOCODER_MIC_HPF,
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
        vocoder_group.setStyleSheet(Style.JDXI_ADSR)
        return vocal_effect_section

    def _create_mixer_section(self):
        # group = QGroupBox("Mixer")
        mixer_section = QWidget()
        layout = QVBoxLayout()
        mixer_section.setLayout(layout)

        # Level and Pan
        self.level = self._create_parameter_slider(
            VocalFXParameter.LEVEL,
            "Level",
        )
        self.pan = self._create_parameter_slider(
            VocalFXParameter.PAN, "Pan"
        )  # Center at 0

        # Send Levels
        self.delay_send_level_slider = self._create_parameter_slider(
            VocalFXParameter.DELAY_SEND_LEVEL, "Delay Send"
        )
        self.reverb_send_level_slider = self._create_parameter_slider(
            VocalFXParameter.REVERB_SEND_LEVEL, "Reverb Send"
        )

        # Output Assign
        output_row = QHBoxLayout()
        output_row.addWidget(QLabel("Output"))
        self.output_assign = self._create_parameter_combo_box(
            VocalFXParameter.OUTPUT_ASSIGN,
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
        # group = QGroupBox("Auto Pitch")
        auto_pitch_section = QWidget()
        self.auto_pitch_group = auto_pitch_section  # Store reference
        layout = QVBoxLayout()
        auto_pitch_section.setLayout(layout)

        self.pitch_switch = self._create_parameter_switch(VocalFXParameter.AUTO_PITCH_SWITCH,
                                                          "Auto Pitch",
                                                          [switch.display_name for switch in VocalFxSwitch])

        # Type selector
        type_row = QHBoxLayout()
        self.auto_pitch_type = self._create_parameter_combo_box(
            VocalFXParameter.AUTO_PITCH_TYPE,
            "Pitch Type",
            [pitch_type.display_name for pitch_type in VocalAutoPitchType],
            [pitch_type.value for pitch_type in VocalAutoPitchType],
        )
        type_row.addWidget(self.auto_pitch_type)

        # Scale selector
        scale_row = QHBoxLayout()
        self.pitch_scale = self._create_parameter_combo_box(
            VocalFXParameter.AUTO_PITCH_SCALE,
            "Scale",
            ["CHROMATIC", "Maj(Min)"],
            [0, 1],
        )
        scale_row.addWidget(self.pitch_scale)

        # Key selector
        key_row = QHBoxLayout()
        self.pitch_key = self._create_parameter_combo_box(
            VocalFXParameter.AUTO_PITCH_KEY,
            "Key",
            [key.display_name for key in VocalAutoPitchKey],
            [key.value for key in VocalAutoPitchKey],
        )
        key_row.addWidget(self.pitch_key)

        # Note selector
        note_row = QHBoxLayout()
        self.pitch_note = self._create_parameter_combo_box(
            VocalFXParameter.AUTO_PITCH_NOTE,
            "Note",
            [note.display_name for note in VocalAutoPitchNote],
            [note.value for note in VocalAutoPitchNote],
        )
        note_row.addWidget(self.pitch_note)

        # Gender and Octave controls
        self.gender = self._create_parameter_slider(
            VocalFXParameter.AUTO_PITCH_GENDER, "Gender"
        )

        self.octave = self._create_parameter_switch(VocalFXParameter.AUTO_PITCH_OCTAVE,
                                                    "Octave",
                                                    [range.name for range in VocalOctaveRange])

        # Dry/Wet Balance
        self.auto_pitch_balance = self._create_parameter_slider(
            VocalFXParameter.AUTO_PITCH_BALANCE, "D/W Balance"
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
