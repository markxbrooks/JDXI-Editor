from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QComboBox,
    QScrollArea,
    QPushButton,
)
from PySide6.QtCore import Qt
import logging
from typing import Optional

from jdxi_manager.midi.io import MIDIHelper
from jdxi_manager.ui.editors.base import BaseEditor
from jdxi_manager.ui.widgets.slider import Slider
from jdxi_manager.ui.widgets.switch.switch import Switch
from jdxi_manager.midi.constants.vocal_fx import (
    VOCAL_FX_AREA,
    VOCAL_FX_PART,
    VOCAL_FX_GROUP,
    VocalFXParameters,
    VocalFxSwitch,
    AutoPitchType,
    OutputAssign,
    AutoPitchKey,
    AutoPitchNote,
    VocoderEnvelope,
    VocoderHPF,
)


class VocalFXEditor(BaseEditor):
    def __init__(
        self, midi_helper: Optional[MIDIHelper] = None, parent: Optional[QWidget] = None
    ):
        super().__init__(midi_helper, parent)
        self.setWindowTitle("Vocal FX")

        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Create container widget for scroll area
        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)

        # Add sections to container
        container_layout.addWidget(self._create_vocal_effect_section())
        container_layout.addWidget(self._create_mixer_section())
        container_layout.addWidget(self._create_auto_pitch_section())

        # Add container to scroll area
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def _create_vocal_effect_section(self):
        """Create general vocal effect controls section"""
        group = QGroupBox("Vocal Effect")
        layout = QVBoxLayout()
        group.setLayout(layout)

        # Add vocoder switch
        switch_row = QHBoxLayout()
        switch_label = QLabel("Vocoder:")
        self.vocoder_switch = QPushButton("OFF")
        self.vocoder_switch.setCheckable(True)
        self.vocoder_switch.clicked.connect(self._on_vocoder_switch_changed)
        switch_row.addWidget(switch_label)
        switch_row.addWidget(self.vocoder_switch)
        layout.addLayout(switch_row)  # Add at top

        """
        # Effect Type selector
        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Type"))
        self.effect_type = QComboBox()
        self.effect_type.addItems(["OFF", "VOCODER", "AUTO-PITCH"])
        self.effect_type.currentIndexChanged.connect(self._on_effect_type_changed)
        type_row.addWidget(self.effect_type)
        layout.addLayout(type_row)
        
        
        # Effect Number and Part
        number_row = QHBoxLayout()
        number_row.addWidget(QLabel("Number"))
        self.effect_number = QComboBox()
        self.effect_number.addItems([str(i) for i in range(1, 22)])  # 1-21
        number_row.addWidget(self.effect_number)
        layout.addLayout(number_row)
        
        part_row = QHBoxLayout()
        part_row.addWidget(QLabel("Part"))
        self.effect_part = QComboBox()
        self.effect_part.addItems(["1", "2"])
        part_row.addWidget(self.effect_part)
        layout.addLayout(part_row)
        
        # Auto Note Switch
        self.auto_note = Switch("Auto Note", ["OFF", "ON"])
        self.auto_note.valueChanged.connect(self._on_auto_note_changed)
        layout.addWidget(self.auto_note)
        """

        # Add Vocoder controls
        vocoder_group = QGroupBox("Vocoder Settings")
        vocoder_layout = QVBoxLayout()
        vocoder_group.setLayout(vocoder_layout)

        # Envelope Type
        env_row = QHBoxLayout()
        env_row.addWidget(QLabel("Envelope"))
        self.vocoder_env = QComboBox()
        self.vocoder_env.addItems([env.display_name for env in VocoderEnvelope])
        self.vocoder_env.currentIndexChanged.connect(self._on_vocoder_env_changed)
        env_row.addWidget(self.vocoder_env)
        vocoder_layout.addLayout(env_row)

        # Level controls
        self.vocoder_level = Slider("Level", 0, 127)
        self.vocoder_level.valueChanged.connect(self._on_vocoder_level_changed)
        self.vocoder_mic_sens = Slider("Mic Sensitivity", 0, 127)
        self.vocoder_mic_sens.valueChanged.connect(self._on_vocoder_mic_sens_changed)
        self.vocoder_synth_level = Slider("Synth Level", 0, 127)
        self.vocoder_synth_level.valueChanged.connect(
            self._on_vocoder_synth_level_changed
        )
        self.vocoder_mic_mix = Slider("Mic Mix", 0, 127)
        self.vocoder_mic_mix.valueChanged.connect(self._on_vocoder_mic_mix_changed)

        # HPF Frequency
        hpf_row = QHBoxLayout()
        hpf_row.addWidget(QLabel("HPF"))
        self.vocoder_hpf = QComboBox()
        self.vocoder_hpf.addItems([freq.display_name for freq in VocoderHPF])
        self.vocoder_hpf.currentIndexChanged.connect(self._on_vocoder_hpf_changed)
        hpf_row.addWidget(self.vocoder_hpf)

        # Add all controls
        vocoder_layout.addWidget(self.vocoder_level)
        vocoder_layout.addWidget(self.vocoder_mic_sens)
        vocoder_layout.addWidget(self.vocoder_synth_level)
        vocoder_layout.addWidget(self.vocoder_mic_mix)
        vocoder_layout.addLayout(hpf_row)

        layout.addWidget(vocoder_group)

        return group

    def _on_effect_type_changed(self, index: int):
        """Handle effect preset_type changes"""
        # Enable/disable sections based on effect preset_type
        is_auto_pitch = index == 2  # AUTO-PITCH
        if hasattr(self, "auto_pitch_group"):
            self.auto_pitch_group.setEnabled(is_auto_pitch)

    def _create_mixer_section(self):
        group = QGroupBox("Mixer")
        layout = QVBoxLayout()
        group.setLayout(layout)

        # Level and Pan
        self.level = Slider("Level", 0, 127)
        self.level.valueChanged.connect(self._on_level_changed)
        self.pan = Slider("Pan", -64, 63)  # Center at 0
        self.pan.valueChanged.connect(self._on_pan_changed)

        # Send Levels
        self.delay_send = Slider("Delay Send", 0, 127)
        self.delay_send.valueChanged.connect(self._on_delay_send_changed)
        self.reverb_send = Slider("Reverb Send", 0, 127)
        self.reverb_send.valueChanged.connect(self._on_reverb_send_changed)

        # Output Assign
        output_row = QHBoxLayout()
        output_row.addWidget(QLabel("Output"))
        self.output_assign = QComboBox()
        self.output_assign.addItems([output.display_name for output in OutputAssign])
        self.output_assign.currentIndexChanged.connect(self._on_output_assign_changed)
        output_row.addWidget(self.output_assign)
        layout.addLayout(output_row)

        layout.addWidget(self.level)
        layout.addWidget(self.pan)
        layout.addWidget(self.delay_send)
        layout.addWidget(self.reverb_send)

        return group

    def _on_level_changed(self, value: int):
        """Handle level change"""
        if self.midi_helper:
            logging.debug(
                f"Sending vocal fx level change: area={VOCAL_FX_AREA:02x}, address={VOCAL_FX_PART:02x}, group={VOCAL_FX_GROUP:02x}, param={VocalFXParameters.LEVEL:02x}, value={value:02x}"
            )
            self.midi_helper.send_parameter(
                area=VOCAL_FX_AREA,
                part=VOCAL_FX_PART,
                group=VOCAL_FX_GROUP,
                param=VocalFXParameters.LEVEL,
                value=value,
            )

    def _on_delay_send_changed(self, value: int):
        """Handle delay send level change"""
        if self.midi_helper:
            logging.debug(
                f"Sending vocal fx delay send change: area={VOCAL_FX_AREA:02x}, address={VOCAL_FX_PART:02x}, group={VOCAL_FX_GROUP:02x}, param={VocalFXParameters.DELAY_SEND:02x}, value={value:02x}"
            )
            self.midi_helper.send_parameter(
                area=VOCAL_FX_AREA,
                part=VOCAL_FX_PART,
                group=VOCAL_FX_GROUP,
                param=VocalFXParameters.DELAY_SEND,
                value=value,
            )

    def _on_reverb_send_changed(self, value: int):
        """Handle reverb send level change"""
        if self.midi_helper:
            logging.debug(
                f"Sending vocal fx reverb send change: area={VOCAL_FX_AREA:02x}, address={VOCAL_FX_PART:02x}, group={VOCAL_FX_GROUP:02x}, param={VocalFXParameters.REVERB_SEND:02x}, value={value:02x}"
            )
            self.midi_helper.send_parameter(
                area=VOCAL_FX_AREA,
                part=VOCAL_FX_PART,
                group=VOCAL_FX_GROUP,
                param=VocalFXParameters.REVERB_SEND,
                value=value,
            )

    def _create_auto_pitch_section(self):
        group = QGroupBox("Auto Pitch")
        self.auto_pitch_group = group  # Store reference
        layout = QVBoxLayout()
        group.setLayout(layout)

        # Auto Pitch Switch
        self.pitch_switch = Switch("Auto Pitch", ["OFF", "ON"])
        self.pitch_switch.valueChanged.connect(self._on_pitch_switch_changed)
        # Type selector
        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Type"))
        self.pitch_type = QComboBox()
        self.pitch_type.addItems(
            [pitch_type.display_name for pitch_type in AutoPitchType]
        )
        self.pitch_type.currentIndexChanged.connect(self._on_pitch_type_changed)
        type_row.addWidget(self.pitch_type)

        # Scale selector
        scale_row = QHBoxLayout()
        scale_row.addWidget(QLabel("Scale"))
        self.pitch_scale = QComboBox()
        self.pitch_scale.addItems(["CHROMATIC", "Maj(Min)"])
        scale_row.addWidget(self.pitch_scale)

        # Key selector
        key_row = QHBoxLayout()
        key_row.addWidget(QLabel("Key"))
        self.pitch_key = QComboBox()
        self.pitch_key.addItems([key.display_name for key in AutoPitchKey])
        self.pitch_key.currentIndexChanged.connect(self._on_pitch_key_changed)
        key_row.addWidget(self.pitch_key)

        # Note selector
        note_row = QHBoxLayout()
        note_row.addWidget(QLabel("Note"))
        self.pitch_note = QComboBox()
        self.pitch_note.addItems([note.display_name for note in AutoPitchNote])
        self.pitch_note.currentIndexChanged.connect(self._on_pitch_note_changed)
        note_row.addWidget(self.pitch_note)

        # Gender and Octave controls
        self.gender = Slider("Gender", -10, 10)
        self.gender.valueChanged.connect(self._on_gender_changed)

        self.octave = Switch("Octave", ["-1", "0", "+1"])
        self.octave.valueChanged.connect(self._on_octave_changed)

        # Dry/Wet Balance
        self.balance = Slider("D/W Balance", 0, 100)
        self.balance.valueChanged.connect(self._on_balance_changed)

        # Add all controls to layout
        layout.addWidget(self.pitch_switch)
        layout.addLayout(type_row)
        layout.addLayout(scale_row)
        layout.addLayout(key_row)
        layout.addLayout(note_row)
        layout.addWidget(self.gender)
        layout.addWidget(self.octave)
        layout.addWidget(self.balance)

        return group

    def _on_vocoder_switch_changed(self, checked: bool):
        """Handle vocoder switch change"""
        if self.midi_helper:
            switch = VocalFxSwitch.ON if checked else VocalFxSwitch.OFF
            logging.debug(
                f"Sending vocoder switch change: area={VOCAL_FX_AREA:02x}, address={VOCAL_FX_PART:02x}, group={VOCAL_FX_GROUP:02x}, param={VocalFXParameters.VOCODER_SWITCH:02x}, value={switch.midi_value:02x}"
            )
            self.midi_helper.send_parameter(
                area=VOCAL_FX_AREA,
                part=VOCAL_FX_PART,
                group=VOCAL_FX_GROUP,
                param=VocalFXParameters.VOCODER_SWITCH,
                value=switch.midi_value,
            )
            # Update button text
            self.vocoder_switch.setText(switch.display_name)

    def _on_auto_note_changed(self, value: int):
        """Handle auto note switch change"""
        if self.midi_helper:
            switch = VocalFxSwitch(value)
            logging.debug(
                f"Sending auto note switch change: area={VOCAL_FX_AREA:02x}, address={VOCAL_FX_PART:02x}, group={VOCAL_FX_GROUP:02x}, param={VocalFXParameters.AUTO_NOTE_SWITCH:02x}, value={switch.midi_value:02x}"
            )
            self.midi_helper.send_parameter(
                area=VOCAL_FX_AREA,
                part=VOCAL_FX_PART,
                group=VOCAL_FX_GROUP,
                param=VocalFXParameters.AUTO_NOTE_SWITCH,
                value=switch.midi_value,
            )

    def _on_pitch_type_changed(self, index: int):
        """Handle auto pitch preset_type change"""
        if self.midi_helper:
            pitch_type = AutoPitchType(index)
            logging.debug(
                f"Sending auto pitch preset_type change: area={VOCAL_FX_AREA:02x}, address={VOCAL_FX_PART:02x}, group={VOCAL_FX_GROUP:02x}, param={VocalFXParameters.AUTO_PITCH_TYPE:02x}, value={pitch_type.midi_value:02x}"
            )
            self.midi_helper.send_parameter(
                area=VOCAL_FX_AREA,
                part=VOCAL_FX_PART,
                group=VOCAL_FX_GROUP,
                param=VocalFXParameters.AUTO_PITCH_TYPE,
                value=pitch_type.midi_value,
            )

    def _on_pan_changed(self, value: int):
        """Handle pan change"""
        if self.midi_helper:
            # Convert from -64/+63 to 0-127 range
            midi_value = value + 64
            logging.debug(
                f"Sending vocal fx pan change: area={VOCAL_FX_AREA:02x}, address={VOCAL_FX_PART:02x}, group={VOCAL_FX_GROUP:02x}, param={VocalFXParameters.PAN:02x}, value={midi_value:02x}"
            )
            self.midi_helper.send_parameter(
                area=VOCAL_FX_AREA,
                part=VOCAL_FX_PART,
                group=VOCAL_FX_GROUP,
                param=VocalFXParameters.PAN,
                value=midi_value,
            )

    def _on_output_assign_changed(self, index: int):
        """Handle output assignment change"""
        if self.midi_helper:
            output = OutputAssign(index)
            logging.debug(
                f"Sending output assign change: area={VOCAL_FX_AREA:02x}, address={VOCAL_FX_PART:02x}, group={VOCAL_FX_GROUP:02x}, param={VocalFXParameters.OUTPUT_ASSIGN:02x}, value={output.midi_value:02x}"
            )
            self.midi_helper.send_parameter(
                area=VOCAL_FX_AREA,
                part=VOCAL_FX_PART,
                group=VOCAL_FX_GROUP,
                param=VocalFXParameters.OUTPUT_ASSIGN,
                value=output.midi_value,
            )

    def _on_pitch_key_changed(self, index: int):
        """Handle auto pitch key change"""
        if self.midi_helper:
            key = AutoPitchKey(index)
            logging.debug(
                f"Sending auto pitch key change: area={VOCAL_FX_AREA:02x}, address={VOCAL_FX_PART:02x}, group={VOCAL_FX_GROUP:02x}, param={VocalFXParameters.KEY:02x}, value={key.midi_value:02x}"
            )
            self.midi_helper.send_parameter(
                area=VOCAL_FX_AREA,
                part=VOCAL_FX_PART,
                group=VOCAL_FX_GROUP,
                param=VocalFXParameters.KEY,
                value=key.midi_value,
            )

    def _on_gender_changed(self, value: int):
        """Handle gender change"""
        if self.midi_helper:
            # Convert from -10/+10 to 0-20 range
            midi_value = value + 10
            logging.debug(
                f"Sending gender change: area={VOCAL_FX_AREA:02x}, address={VOCAL_FX_PART:02x}, group={VOCAL_FX_GROUP:02x}, param={VocalFXParameters.GENDER:02x}, value={midi_value:02x}"
            )
            self.midi_helper.send_parameter(
                area=VOCAL_FX_AREA,
                part=VOCAL_FX_PART,
                group=VOCAL_FX_GROUP,
                param=VocalFXParameters.GENDER,
                value=midi_value,
            )

    def _on_octave_changed(self, value: int):
        """Handle octave change"""
        if self.midi_helper:
            logging.debug(
                f"Sending octave change: area={VOCAL_FX_AREA:02x}, address={VOCAL_FX_PART:02x}, group={VOCAL_FX_GROUP:02x}, param={VocalFXParameters.OCTAVE:02x}, value={value:02x}"
            )
            self.midi_helper.send_parameter(
                area=VOCAL_FX_AREA,
                part=VOCAL_FX_PART,
                group=VOCAL_FX_GROUP,
                param=VocalFXParameters.OCTAVE,
                value=value,
            )

    def _on_balance_changed(self, value: int):
        """Handle balance change"""
        if self.midi_helper:
            logging.debug(
                f"Sending balance change: area={VOCAL_FX_AREA:02x}, address={VOCAL_FX_PART:02x}, group={VOCAL_FX_GROUP:02x}, param={VocalFXParameters.BALANCE:02x}, value={value:02x}"
            )
            self.midi_helper.send_parameter(
                area=VOCAL_FX_AREA,
                part=VOCAL_FX_PART,
                group=VOCAL_FX_GROUP,
                param=VocalFXParameters.BALANCE,
                value=value,
            )

    def _on_pitch_note_changed(self, index: int):
        """Handle auto pitch note change"""
        if self.midi_helper:
            note = AutoPitchNote(index)
            logging.debug(
                f"Sending auto pitch note change: area={VOCAL_FX_AREA:02x}, address={VOCAL_FX_PART:02x}, group={VOCAL_FX_GROUP:02x}, param={VocalFXParameters.NOTE:02x}, value={note.midi_value:02x}"
            )
            self.midi_helper.send_parameter(
                area=VOCAL_FX_AREA,
                part=VOCAL_FX_PART,
                group=VOCAL_FX_GROUP,
                param=VocalFXParameters.NOTE,
                value=note.midi_value,
            )

    def _on_vocoder_env_changed(self, index: int):
        """Handle vocoder envelope change"""
        if self.midi_helper:
            env = VocoderEnvelope(index)
            self.midi_helper.send_parameter(
                area=VOCAL_FX_AREA,
                part=VOCAL_FX_PART,
                group=VOCAL_FX_GROUP,
                param=VocalFXParameters.VOCODER_ENVELOPE,
                value=env.midi_value,
            )

    def _on_vocoder_level_changed(self, value: int):
        """Handle vocoder level change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=VOCAL_FX_AREA,
                part=VOCAL_FX_PART,
                group=VOCAL_FX_GROUP,
                param=VocalFXParameters.VOCODER_LEVEL,
                value=value,
            )

    def _on_vocoder_mic_sens_changed(self, value: int):
        """Handle vocoder mic sensitivity change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=VOCAL_FX_AREA,
                part=VOCAL_FX_PART,
                group=VOCAL_FX_GROUP,
                param=VocalFXParameters.VOCODER_MIC_SENS,
                value=value,
            )

    def _on_vocoder_synth_level_changed(self, value: int):
        """Handle vocoder synth level change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=VOCAL_FX_AREA,
                part=VOCAL_FX_PART,
                group=VOCAL_FX_GROUP,
                param=VocalFXParameters.VOCODER_SYNTH_LEVEL,
                value=value,
            )

    def _on_vocoder_mic_mix_changed(self, value: int):
        """Handle vocoder mic mix level change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=VOCAL_FX_AREA,
                part=VOCAL_FX_PART,
                group=VOCAL_FX_GROUP,
                param=VocalFXParameters.VOCODER_MIC_MIX,
                value=value,
            )

    def _on_vocoder_hpf_changed(self, index: int):
        """Handle vocoder HPF frequency change"""
        if self.midi_helper:
            freq = VocoderHPF(index)
            self.midi_helper.send_parameter(
                area=VOCAL_FX_AREA,
                part=VOCAL_FX_PART,
                group=VOCAL_FX_GROUP,
                param=VocalFXParameters.VOCODER_MIC_HPF,
                value=freq.midi_value,
            )

    def _on_pitch_switch_changed(self, checked: bool):
        """Handle auto pitch switch change"""
        if self.midi_helper:
            switch = VocalFxSwitch.ON if checked else VocalFxSwitch.OFF
            logging.debug(
                f"Sending auto pitch switch change: area={VOCAL_FX_AREA:02x}, address={VOCAL_FX_PART:02x}, group={VOCAL_FX_GROUP:02x}, param={VocalFXParameters.AUTO_NOTE_SWITCH:02x}, value={switch.midi_value:02x}"
            )
            self.midi_helper.send_parameter(
                area=VOCAL_FX_AREA,
                part=VOCAL_FX_PART,
                group=VOCAL_FX_GROUP,
                param=VocalFXParameters.AUTO_NOTE_SWITCH,
                value=switch.midi_value,
            )
