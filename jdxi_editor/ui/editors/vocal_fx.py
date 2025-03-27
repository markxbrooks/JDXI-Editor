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
import logging
from typing import Optional
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QScrollArea,
    QPushButton,
    QTabWidget,
)
from PySide6.QtCore import Qt

from jdxi_editor.midi.data.parameter.program.common import ProgramCommonParameter
from jdxi_editor.midi.io import MidiIOHelper
from jdxi_editor.midi.message.roland import RolandSysEx
from jdxi_editor.ui.editors.synth import SynthEditor
from jdxi_editor.ui.style import Style
from jdxi_editor.midi.data.constants.vocal_fx import (
    VOCAL_FX_AREA,
    VOCAL_FX_PART,
    VOCAL_FX_GROUP,
    VocalFxSwitch,
    AutoPitchType,
    OutputAssign,
    AutoPitchKey,
    AutoPitchNote,
    VocoderEnvelope,
    VocoderHPF,
)
from jdxi_editor.midi.data.parameter.vocal_fx import VocalFXParameter


class VocalFXEditor(SynthEditor):
    """Vocal Effects Window Class"""

    def __init__(
        self, midi_helper: Optional[MidiIOHelper] = None, parent: Optional[QWidget] = None
    ):
        super().__init__(midi_helper, parent)
        self.setWindowTitle("Vocal FX")
        self.setMinimumHeight(700)
        self.setMinimumWidth(500)
        self.area = VOCAL_FX_AREA
        self.part = VOCAL_FX_PART
        self.group = VOCAL_FX_GROUP
        self.setStyleSheet(Style.JDXI_EDITOR + Style.JDXI_TABS)

        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Create container widget for scroll area
        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)

        self.title_label = QLabel("Vocal Effects")
        self.title_label.setStyleSheet(
            """
            font-size: 16px;
            font-weight: bold;
        """
        )
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
        vocal_effect_switch_label = QLabel("Effect Part:")
        vocal_effect_switch_row.addWidget(vocal_effect_switch_label)
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
        effect_part_switch_label = QLabel("Effect Part:")
        self.effect_part_switch = QPushButton("OFF")
        self.effect_part_switch.setCheckable(True)
        self.effect_part_switch.clicked.connect(self._on_effect_part_switch_changed)
        effect_part_switch_row.addWidget(effect_part_switch_label)
        effect_part_switch_row.addWidget(self.effect_part_switch)
        layout.addLayout(effect_part_switch_row)  # Add at bottom

        # Add Auto Note switch
        auto_note_switch_row = QHBoxLayout()
        auto_note_switch_label = QLabel("Auto Note:")
        self.auto_note_switch = QPushButton("OFF")
        self.auto_note_switch.setCheckable(True)
        self.auto_note_switch.clicked.connect(self._on_auto_note_switch_changed)
        auto_note_switch_row.addWidget(auto_note_switch_label)
        auto_note_switch_row.addWidget(self.auto_note_switch)
        layout.addLayout(auto_note_switch_row)  # Add at bottom

        return common_section

    def _create_vocal_effect_section(self):
        """Create general vocal effect controls section"""
        vocal_effect_section = QWidget()
        # group = QGroupBox("Vocal Effect")
        layout = QVBoxLayout()
        vocal_effect_section.setLayout(layout)

        # Add vocoder switch
        switch_row = QHBoxLayout()
        switch_label = QLabel("Vocoder:")
        self.vocoder_switch = QPushButton("OFF")
        self.vocoder_switch.setCheckable(True)
        self.vocoder_switch.clicked.connect(self._on_vocoder_switch_changed)
        switch_row.addWidget(switch_label)
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
            [output.display_name for output in OutputAssign],
            [output.value for output in OutputAssign],
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
                                                          ["OFF", "ON"])

        # Type selector
        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Type"))
        self.auto_pitch_type = self._create_parameter_combo_box(
            VocalFXParameter.AUTO_PITCH_TYPE,
            "Pitch Type",
            [pitch_type.display_name for pitch_type in AutoPitchType],
            [pitch_type.value for pitch_type in AutoPitchType],
        )
        type_row.addWidget(self.auto_pitch_type)

        # Scale selector
        scale_row = QHBoxLayout()
        scale_row.addWidget(QLabel("Scale"))
        self.pitch_scale = self._create_parameter_combo_box(
            VocalFXParameter.AUTO_PITCH_SCALE,
            "Scale",
            ["CHROMATIC", "Maj(Min)"],
            [0, 1],
        )
        scale_row.addWidget(self.pitch_scale)

        # Key selector
        key_row = QHBoxLayout()
        key_row.addWidget(QLabel("Key"))
        self.pitch_key = self._create_parameter_combo_box(
            VocalFXParameter.AUTO_PITCH_KEY,
            "Key",
            [key.display_name for key in AutoPitchKey],
            [key.value for key in AutoPitchKey],
        )
        key_row.addWidget(self.pitch_key)

        # Note selector
        note_row = QHBoxLayout()
        note_row.addWidget(QLabel("Note"))
        self.pitch_note = self._create_parameter_combo_box(
            VocalFXParameter.AUTO_PITCH_NOTE,
            "Note",
            [note.display_name for note in AutoPitchNote],
            [note.value for note in AutoPitchNote],
        )
        note_row.addWidget(self.pitch_note)

        # Gender and Octave controls
        self.gender = self._create_parameter_slider(
            VocalFXParameter.AUTO_PITCH_GENDER, "Gender"
        )

        self.octave = self._create_parameter_switch(VocalFXParameter.AUTO_PITCH_OCTAVE,
                                                    "Octave",
                                                    ["-1", "0", "+1"])

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

    def _on_vocoder_switch_changed(self, checked: bool):
        """Handle vocoder switch change"""
        if self.midi_helper:
            switch = VocalFxSwitch.ON if checked else VocalFxSwitch.OFF
            logging.info(
                f"Sending vocoder switch change: area={VOCAL_FX_AREA:02x}, "
                f"address={VOCAL_FX_PART:02x}, group={VOCAL_FX_GROUP:02x}, "
                f"param={VocalFXParameter.VOCODER_SWITCH.value[0]:02x}, "
                f"value={switch.midi_value:02x}"
            )
            sysex_message = RolandSysEx(area=self.area,
                                        section=self.part,
                                        group=self.group,
                                        param=VocalFXParameter.VOCODER_SWITCH.value[0],
                                        value=switch.midi_value)
            self.midi_helper.send_midi_message(sysex_message)
            self.vocoder_switch.setText(switch.display_name)

    def _on_auto_note_switch_changed(self, checked: bool):
        """Handle vocoder switch change"""
        if self.midi_helper:
            switch = VocalFxSwitch.ON if checked else VocalFxSwitch.OFF
            logging.info(
                f"Sending effect part switch change: area={VOCAL_FX_AREA:02x}, "
                f"address={VOCAL_FX_PART:02x}, group={VOCAL_FX_GROUP:02x}, "
                f"param={VocalFXParameter.VOCODER_SWITCH.value[0]:02x}, "
                f"value={switch.midi_value:02x}"
            )
            sysex_message = RolandSysEx(area=self.area,
                                        section=self.part,
                                        group=self.group,
                                        param=ProgramCommonParameter.AUTO_NOTE_SWITCH.value[0],
                                        value=switch.midi_value)
            self.midi_helper.send_midi_message(sysex_message)
            self.auto_note_switch.setText(switch.display_name)

    def _on_effect_part_switch_changed(self, checked: bool):
        """Handle vocoder switch change"""
        if self.midi_helper:
            switch = VocalFxSwitch.ON if checked else VocalFxSwitch.OFF
            logging.info(
                f"Sending effect part switch change: area={VOCAL_FX_AREA:02x}, "
                f"address={VOCAL_FX_PART:02x}, group={VOCAL_FX_GROUP:02x}, "
                f"param={VocalFXParameter.VOCODER_SWITCH.value[0]:02x}, "
                f"value={switch.midi_value:02x}"
            )
            # Send MIDI message
            sysex_message = RolandSysEx(area=self.area,
                                        section=self.part,
                                        group=self.group,
                                        param=ProgramCommonParameter.VOCAL_EFFECT_PART.value[0],
                                        value=switch.midi_value)
            self.midi_helper.send_midi_message(sysex_message)
            # Update button text
            self.effect_part_switch.setText(switch.display_name)

    def _on_octave_changed(self, value: int):
        """Handle octave change"""
        if self.midi_helper:
            logging.info(
                f"Sending octave change: area={VOCAL_FX_AREA:02x}, "
                f"address={VOCAL_FX_PART:02x}, group={VOCAL_FX_GROUP:02x}, "
                f"param={VocalFXParameter.AUTO_PITCH_OCTAVE.value[0]:02x}, "
                f"value={value:02x}"
            )
            # Send MIDI message
            sysex_message = RolandSysEx(area=self.area,
                                        section=self.part,
                                        group=self.group,
                                        param=VocalFXParameter.AUTO_PITCH_OCTAVE.value[0],
                                        value=value)
            return self.midi_helper.send_midi_message(sysex_message)

    def _on_pitch_note_changed(self, index: int):
        """Handle auto pitch note change"""
        if self.midi_helper:
            note = AutoPitchNote(index)
            logging.info(
                f"Sending auto pitch note change: area={VOCAL_FX_AREA:02x}, "
                f"address={VOCAL_FX_PART:02x}, group={VOCAL_FX_GROUP:02x}, "
                f"param={VocalFXParameter.AUTO_PITCH_NOTE.value[0]:02x}, "
                f"value={note.midi_value:02x}"
            )
            sysex_message = RolandSysEx(area=self.area,
                                        section=self.part,
                                        group=self.group,
                                        param=VocalFXParameter.AUTO_PITCH_NOTE.value[0],
                                        value=note.midi_value)
            return self.midi_helper.send_midi_message(sysex_message)

    def _on_pitch_switch_changed(self, checked: bool):
        """Handle auto pitch switch change"""
        if self.midi_helper:
            switch = VocalFxSwitch.ON if checked else VocalFxSwitch.OFF
            logging.info(
                f"Sending auto pitch switch change: area={VOCAL_FX_AREA:02x}, "
                f"address={VOCAL_FX_PART:02x}, group={VOCAL_FX_GROUP:02x}, "
                f"param={VocalFXParameter.AUTO_PITCH_SWITCH.value[0]:02x}, "
                f"value={switch.midi_value:02x}"
            )
            # Send MIDI message
            sysex_message = RolandSysEx(area=self.area,
                                        section=self.part,
                                        group=self.group,
                                        param=VocalFXParameter.AUTO_PITCH_SWITCH.value[0],
                                        value=switch.midi_value)
            return self.midi_helper.send_midi_message(sysex_message)
