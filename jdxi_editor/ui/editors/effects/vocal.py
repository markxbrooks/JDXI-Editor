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

from picomidi.sysex.parameter.address import AddressParameter
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
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
from jdxi_editor.ui.widgets.group import WidgetGroups
from jdxi_editor.ui.widgets.layout import WidgetLayoutSpec
from jdxi_editor.ui.widgets.spec import ComboBoxSpec, SliderSpec, SwitchSpec


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

    def _build_widgets_from_spec(self, spec: WidgetLayoutSpec) -> WidgetGroups:
        """Build WidgetGroups from a layout spec (same paradigm as Arpeggiator/Effects)."""
        return WidgetGroups(
            switches=self._build_switches(spec.switches),
            sliders=self._build_sliders(spec.sliders),
            combos=self._build_combo_boxes(spec.combos),
        )

    def _build_common_layout_spec(self) -> WidgetLayoutSpec:
        """Build layout spec for Common tab."""
        combos = [
            ComboBoxSpec(
                ProgramCommonParam.VOCAL_EFFECT,
                "Vocal Effect",
                ["OFF", "VOCODER", "AUTO - PITCH"],
                [0, 1, 2],
            ),
        ]
        sliders = [
            SliderSpec(ProgramCommonParam.PROGRAM_TEMPO, "Tempo", vertical=False),
            SliderSpec(
                ProgramCommonParam.VOCAL_EFFECT_NUMBER, "Effect Number", vertical=False
            ),
            SliderSpec(ProgramCommonParam.PROGRAM_LEVEL, "Level", vertical=False),
        ]
        switches = [
            SwitchSpec(VocalFXParam.VOCODER_SWITCH, "Effect Part:", ["OFF", "ON"]),
            SwitchSpec(
                ProgramCommonParam.AUTO_NOTE_SWITCH, "Auto Note:", ["OFF", "ON"]
            ),
        ]
        return WidgetLayoutSpec(switches=switches, sliders=sliders, combos=combos)

    def _create_common_section(self) -> QWidget:
        """Create Common tab (spec-driven)."""
        spec = self._build_common_layout_spec()
        groups = self._build_widgets_from_spec(spec)

        common_section = QWidget()
        layout = QVBoxLayout()
        common_section.setLayout(layout)

        icon_row_container = QHBoxLayout()
        icon_hlayout = JDXi.UI.Icon.create_generic_musical_icon_row()
        transfer_layout_items(icon_hlayout, icon_row_container)
        layout.addLayout(icon_row_container)

        form_widget = QWidget()
        form_layout = QFormLayout()
        form_widget.setLayout(form_layout)
        for w in groups.combos + groups.sliders + groups.switches:
            form_layout.addRow(w)
        layout.addWidget(form_widget)
        layout.addStretch()
        return common_section

    def _build_vocal_effect_layout_spec(self) -> WidgetLayoutSpec:
        """Build layout spec for Vocal FX tab (Vocoder settings)."""
        switches = [
            SwitchSpec(VocalFXParam.VOCODER_SWITCH, "Vocoder:", ["OFF", "ON"]),
        ]
        combos = [
            ComboBoxSpec(
                VocalFXParam.VOCODER_ENVELOPE,
                "Envelope",
                [env.display_name for env in VocoderEnvelope],
                [env.value for env in VocoderEnvelope],
            ),
            ComboBoxSpec(
                VocalFXParam.VOCODER_MIC_HPF,
                "HPF",
                [freq.display_name for freq in VocoderHPF],
                [freq.value for freq in VocoderHPF],
            ),
        ]
        sliders = [
            SliderSpec(VocalFXParam.VOCODER_LEVEL, "Level", vertical=False),
            SliderSpec(
                VocalFXParam.VOCODER_MIC_SENS, "Mic Sensitivity", vertical=False
            ),
            SliderSpec(VocalFXParam.VOCODER_SYNTH_LEVEL, "Synth Level", vertical=False),
            SliderSpec(VocalFXParam.VOCODER_MIC_MIX, "Mic Mix", vertical=False),
        ]
        return WidgetLayoutSpec(switches=switches, sliders=sliders, combos=combos)

    def _create_vocal_effect_section(self) -> QWidget:
        """Create Vocal FX tab (spec-driven)."""
        spec = self._build_vocal_effect_layout_spec()
        groups = self._build_widgets_from_spec(spec)

        vocal_effect_section = QWidget()
        layout = QVBoxLayout()
        vocal_effect_section.setLayout(layout)

        icon_row_container = QHBoxLayout()
        icon_hlayout = JDXi.UI.Icon.create_adsr_icons_row()
        transfer_layout_items(icon_hlayout, icon_row_container)
        layout.addLayout(icon_row_container)

        # Vocoder switch at top
        for w in groups.switches:
            layout.addWidget(w)

        vocoder_group = QGroupBox("Vocoder Settings")
        vocoder_form = QFormLayout()
        vocoder_group.setLayout(vocoder_form)
        for w in groups.combos + groups.sliders:
            vocoder_form.addRow(w)
        layout.addWidget(vocoder_group)
        JDXi.UI.Theme.apply_adsr_style(widget=vocoder_group)
        layout.addStretch()
        return vocal_effect_section

    def _build_mixer_layout_spec(self) -> WidgetLayoutSpec:
        """Build layout spec for Mixer tab."""
        combos = [
            ComboBoxSpec(
                VocalFXParam.OUTPUT_ASSIGN,
                "Output",
                [output.display_name for output in VocalOutputAssign],
                [output.value for output in VocalOutputAssign],
            ),
        ]
        sliders = [
            SliderSpec(VocalFXParam.LEVEL, "Level", vertical=False),
            SliderSpec(VocalFXParam.PAN, "Pan", vertical=False),
            SliderSpec(VocalFXParam.DELAY_SEND_LEVEL, "Delay Send", vertical=False),
            SliderSpec(VocalFXParam.REVERB_SEND_LEVEL, "Reverb Send", vertical=False),
        ]
        return WidgetLayoutSpec(switches=[], sliders=sliders, combos=combos)

    def _create_mixer_section(self) -> QWidget:
        """Create Mixer tab (spec-driven)."""
        spec = self._build_mixer_layout_spec()
        groups = self._build_widgets_from_spec(spec)

        mixer_section = QWidget()
        layout = QVBoxLayout()
        mixer_section.setLayout(layout)

        icon_row_container = QHBoxLayout()
        icon_hlayout = JDXi.UI.Icon.create_adsr_icons_row()
        transfer_layout_items(icon_hlayout, icon_row_container)
        layout.addLayout(icon_row_container)

        form_widget = QWidget()
        form_layout = QFormLayout()
        form_widget.setLayout(form_layout)
        for w in groups.combos + groups.sliders + groups.switches:
            form_layout.addRow(w)
        layout.addWidget(form_widget)
        layout.addStretch()
        return mixer_section

    def _build_auto_pitch_layout_spec(self) -> WidgetLayoutSpec:
        """Build layout spec for Auto Pitch tab."""
        switches = [
            SwitchSpec(
                VocalFXParam.AUTO_PITCH_SWITCH,
                "Auto Pitch",
                [switch.display_name for switch in VocalFxSwitch],
            ),
            SwitchSpec(
                VocalFXParam.AUTO_PITCH_OCTAVE,
                "Octave",
                [rng.name for rng in VocalOctaveRange],
            ),
        ]
        combos = [
            ComboBoxSpec(
                VocalFXParam.AUTO_PITCH_TYPE,
                "Pitch Type",
                [pitch_type.display_name for pitch_type in VocalAutoPitchType],
                [pitch_type.value for pitch_type in VocalAutoPitchType],
            ),
            ComboBoxSpec(
                VocalFXParam.AUTO_PITCH_SCALE,
                "Scale",
                ["CHROMATIC", "Maj(Min)"],
                [0, 1],
            ),
            ComboBoxSpec(
                VocalFXParam.AUTO_PITCH_KEY,
                "Key",
                [key.display_name for key in VocalAutoPitchKey],
                [key.value for key in VocalAutoPitchKey],
            ),
            ComboBoxSpec(
                VocalFXParam.AUTO_PITCH_NOTE,
                "Note",
                [note.display_name for note in VocalAutoPitchNote],
                [note.value for note in VocalAutoPitchNote],
            ),
        ]
        sliders = [
            SliderSpec(VocalFXParam.AUTO_PITCH_GENDER, "Gender", vertical=False),
            SliderSpec(VocalFXParam.AUTO_PITCH_BALANCE, "D/W Balance", vertical=False),
        ]
        return WidgetLayoutSpec(switches=switches, sliders=sliders, combos=combos)

    def _create_auto_pitch_section(self) -> QWidget:
        """Create Auto Pitch tab (spec-driven)."""
        spec = self._build_auto_pitch_layout_spec()
        groups = self._build_widgets_from_spec(spec)

        auto_pitch_section = QWidget()
        self.auto_pitch_group = auto_pitch_section  # Store reference
        layout = QVBoxLayout()
        auto_pitch_section.setLayout(layout)

        icon_row_container = QHBoxLayout()
        icon_hlayout = JDXi.UI.Icon.create_adsr_icons_row()
        transfer_layout_items(icon_hlayout, icon_row_container)
        layout.addLayout(icon_row_container)

        form_widget = QWidget()
        form_layout = QFormLayout()
        form_widget.setLayout(form_layout)
        for w in groups.combos + groups.sliders + groups.switches:
            form_layout.addRow(w)
        layout.addWidget(form_widget)
        layout.addStretch()
        return auto_pitch_section
