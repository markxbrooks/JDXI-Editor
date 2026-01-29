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

from typing import Dict, Optional

from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.parameter.program.common import ProgramCommonParam
from jdxi_editor.midi.data.parameter.vocal_fx import VocalFXParam
from jdxi_editor.midi.data.vocal_effects.vocal import (
    VocalAutoPitchKey,
    VocalAutoPitchNote,
    VocalAutoPitchType,
    VocalFxSwitch,
    VocalOctaveRange,
    VocalOutputAssign,
    VocoderEnvelope,
    VocoderHPF,
)
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.address.factory import create_vocal_fx_address
from jdxi_editor.ui.editors.synth.simple import BasicEditor
from jdxi_editor.ui.preset.helper import JDXiPresetHelper
from jdxi_editor.ui.widgets.editor.base import EditorBaseWidget
from jdxi_editor.ui.widgets.editor.helper import transfer_layout_items
from jdxi_editor.ui.widgets.editor.simple_editor_helper import SimpleEditorHelper
from picomidi.sysex.parameter.address import AddressParameter


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
        self.address = create_vocal_fx_address()

        JDXi.UI.Theme.apply_editor_style(self)

        # Use EditorBaseWidget for consistent scrollable layout structure
        self.base_widget = EditorBaseWidget(parent=self, analog=False)
        self.base_widget.setup_scrollable_content()

        # Use SimpleEditorHelper for standardized title/image/tab setup
        self.editor_helper = SimpleEditorHelper(
            editor=self,
            base_widget=self.base_widget,
            title="Vocal Effects",
            image_folder="vocal_fx",
            default_image="vocal_fx.png",
        )

        self.controls: Dict[AddressParameter, QWidget] = {}

        # Get tab widget from helper and add tabs
        self.tab_widget = self.editor_helper.get_tab_widget()
        common_icon = JDXi.UI.Icon.get_icon(
            JDXi.UI.Icon.COG_OUTLINE, color=JDXi.UI.Style.GREY
        )
        self.tab_widget.addTab(self._create_common_section(), common_icon, "Common")
        vocal_fx_icon = JDXi.UI.Icon.get_icon(
            JDXi.UI.Icon.MICROPHONE, color=JDXi.UI.Style.GREY
        )
        self.tab_widget.addTab(
            self._create_vocal_effect_section(), vocal_fx_icon, "Vocal FX"
        )
        mixer_icon = JDXi.UI.Icon.get_icon(
            JDXi.UI.Icon.EQUALIZER, color=JDXi.UI.Style.GREY
        )
        self.tab_widget.addTab(self._create_mixer_section(), mixer_icon, "Mixer")
        auto_pitch_icon = JDXi.UI.Icon.get_icon(
            JDXi.UI.Icon.MUSIC_NOTE, color=JDXi.UI.Style.GREY
        )
        self.tab_widget.addTab(
            self._create_auto_pitch_section(), auto_pitch_icon, "Auto Pitch"
        )

        # Add base widget to editor's layout
        if not hasattr(self, "main_layout") or self.main_layout is None:
            self.main_layout = QVBoxLayout(self)
            self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.base_widget)

    def _create_common_section(self) -> QWidget:
        """
        _create_common_section

        :return: QWidget
        """
        common_section = QWidget()
        layout = QVBoxLayout()
        common_section.setLayout(layout)

        # Icons row (standardized across editor tabs) - transfer items to avoid "already has a parent" errors
        icon_row_container = QHBoxLayout()
        icon_hlayout = JDXi.UI.Icon.create_generic_musical_icon_row()

        transfer_layout_items(icon_hlayout, icon_row_container)
        layout.addLayout(icon_row_container)

        self.program_tempo = self._create_parameter_slider(
            ProgramCommonParam.PROGRAM_TEMPO, "Tempo"
        )
        layout.addWidget(self.program_tempo)

        vocal_effect_switch_row = QHBoxLayout()
        self.vocal_effect_type = self._create_parameter_combo_box(
            ProgramCommonParam.VOCAL_EFFECT,
            "Vocal Effect",
            ["OFF", "VOCODER", "AUTO - PITCH"],
            [0, 1, 2],
        )

        vocal_effect_switch_row.addWidget(self.vocal_effect_type)
        layout.addLayout(vocal_effect_switch_row)

        self.vocal_effect_number = self._create_parameter_slider(
            ProgramCommonParam.VOCAL_EFFECT_NUMBER, "Effect Number"
        )
        layout.addWidget(self.vocal_effect_number)

        self.program_level = self._create_parameter_slider(
            ProgramCommonParam.PROGRAM_LEVEL, "Level"
        )
        layout.addWidget(self.program_level)

        # Add Effect Part switch
        effect_part_switch_row = QHBoxLayout()
        self.effect_part_switch = self._create_parameter_switch(
            VocalFXParam.VOCODER_SWITCH, "Effect Part:", ["OFF", "ON"]
        )
        effect_part_switch_row.addWidget(self.effect_part_switch)
        layout.addLayout(effect_part_switch_row)  # Add at bottom

        # Add Auto Note switch
        auto_note_switch_row = QHBoxLayout()
        self.auto_note_switch = self._create_parameter_switch(
            ProgramCommonParam.AUTO_NOTE_SWITCH, "Auto Note:", ["OFF", "ON"]
        )
        auto_note_switch_row.addWidget(self.auto_note_switch)
        layout.addLayout(auto_note_switch_row)  # Add at bottom

        layout.addStretch()
        return common_section

    def _create_vocal_effect_section(self) -> QWidget:
        """Create general vocal effect controls section"""
        vocal_effect_section = QWidget()
        layout = QVBoxLayout()
        vocal_effect_section.setLayout(layout)

        # Icons row (standardized across editor tabs) - transfer items to avoid "already has a parent" errors
        icon_row_container = QHBoxLayout()
        icon_hlayout = JDXi.UI.Icon.create_adsr_icons_row()

        transfer_layout_items(icon_hlayout, icon_row_container)
        layout.addLayout(icon_row_container)

        # Add vocoder switch
        switch_row = QHBoxLayout()
        self.vocoder_switch = self._create_parameter_switch(
            VocalFXParam.VOCODER_SWITCH, "Vocoder:", ["OFF", "ON"]
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
            VocalFXParam.VOCODER_ENVELOPE,
            "Envelope",
            [env.display_name for env in VocoderEnvelope],
            [env.value for env in VocoderEnvelope],
        )
        env_row.addWidget(self.vocoder_env)
        vocoder_layout.addLayout(env_row)

        # Level controls
        levels_row_layout = QHBoxLayout()
        self.vocoder_level = self._create_parameter_slider(
            VocalFXParam.VOCODER_LEVEL, "Level", 1
        )

        self.vocoder_mic_sens = self._create_parameter_slider(
            VocalFXParam.VOCODER_MIC_SENS, "Mic Sensitivity", 1
        )

        self.vocoder_synth_level = self._create_parameter_slider(
            VocalFXParam.VOCODER_SYNTH_LEVEL, "Synth Level", 1
        )

        self.vocoder_mic_mix = self._create_parameter_slider(
            VocalFXParam.VOCODER_MIC_MIX, "Mic Mix", 1
        )

        self.vocoder_hpf = self._create_parameter_combo_box(
            VocalFXParam.VOCODER_MIC_HPF,
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
        JDXi.UI.Theme.apply_adsr_style(widget=vocoder_group)
        layout.addStretch()
        return vocal_effect_section

    def _create_mixer_section(self) -> QWidget:
        """
        _create_mixer_section

        :return: QWidget
        """
        mixer_section = QWidget()
        layout = QVBoxLayout()
        mixer_section.setLayout(layout)

        # Icons row (standardized across editor tabs) - transfer items to avoid "already has a parent" errors
        icon_row_container = QHBoxLayout()
        icon_hlayout = JDXi.UI.Icon.create_adsr_icons_row()

        transfer_layout_items(icon_hlayout, icon_row_container)
        layout.addLayout(icon_row_container)

        # Level and Pan
        self.level = self._create_parameter_slider(
            VocalFXParam.LEVEL,
            "Level",
        )
        self.pan = self._create_parameter_slider(VocalFXParam.PAN, "Pan")  # Center at 0

        # Send Levels
        self.delay_send_level_slider = self._create_parameter_slider(
            VocalFXParam.DELAY_SEND_LEVEL, "Delay Send"
        )
        self.reverb_send_level_slider = self._create_parameter_slider(
            VocalFXParam.REVERB_SEND_LEVEL, "Reverb Send"
        )

        # Output Assign
        output_row = QHBoxLayout()
        output_row.addWidget(QLabel("Output"))
        self.output_assign = self._create_parameter_combo_box(
            VocalFXParam.OUTPUT_ASSIGN,
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

        layout.addStretch()
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

        # Icons row (standardized across editor tabs) - transfer items to avoid "already has a parent" errors
        icon_row_container = QHBoxLayout()
        icon_hlayout = JDXi.UI.Icon.create_adsr_icons_row()

        transfer_layout_items(icon_hlayout, icon_row_container)
        layout.addLayout(icon_row_container)

        self.pitch_switch = self._create_parameter_switch(
            VocalFXParam.AUTO_PITCH_SWITCH,
            "Auto Pitch",
            [switch.display_name for switch in VocalFxSwitch],
        )

        # Type selector
        type_row = QHBoxLayout()
        self.auto_pitch_type = self._create_parameter_combo_box(
            VocalFXParam.AUTO_PITCH_TYPE,
            "Pitch Type",
            [pitch_type.display_name for pitch_type in VocalAutoPitchType],
            [pitch_type.value for pitch_type in VocalAutoPitchType],
        )
        type_row.addWidget(self.auto_pitch_type)

        # Scale selector
        scale_row = QHBoxLayout()
        self.pitch_scale = self._create_parameter_combo_box(
            VocalFXParam.AUTO_PITCH_SCALE,
            "Scale",
            ["CHROMATIC", "Maj(Min)"],
            [0, 1],
        )
        scale_row.addWidget(self.pitch_scale)

        # Key selector
        key_row = QHBoxLayout()
        self.pitch_key = self._create_parameter_combo_box(
            VocalFXParam.AUTO_PITCH_KEY,
            "Key",
            [key.display_name for key in VocalAutoPitchKey],
            [key.value for key in VocalAutoPitchKey],
        )
        key_row.addWidget(self.pitch_key)

        # Note selector
        note_row = QHBoxLayout()
        self.pitch_note = self._create_parameter_combo_box(
            VocalFXParam.AUTO_PITCH_NOTE,
            "Note",
            [note.display_name for note in VocalAutoPitchNote],
            [note.value for note in VocalAutoPitchNote],
        )
        note_row.addWidget(self.pitch_note)

        # Gender and Octave controls
        self.gender = self._create_parameter_slider(
            VocalFXParam.AUTO_PITCH_GENDER, "Gender"
        )

        self.octave = self._create_parameter_switch(
            VocalFXParam.AUTO_PITCH_OCTAVE,
            "Octave",
            [range.name for range in VocalOctaveRange],
        )

        # Dry/Wet Balance
        self.auto_pitch_balance = self._create_parameter_slider(
            VocalFXParam.AUTO_PITCH_BALANCE, "D/W Balance"
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

        layout.addStretch()
        return auto_pitch_section
