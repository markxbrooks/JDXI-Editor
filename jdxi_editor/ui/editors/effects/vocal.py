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

from decologr import Decologr as log
from picomidi.sysex.parameter.address import AddressParameter
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QStackedWidget,
    QVBoxLayout,
)

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
from jdxi_editor.midi.sysex.request.midi_requests import MidiRequests
from jdxi_editor.midi.sysex.sections import SysExSection
from jdxi_editor.ui.common import JDXi, QVBoxLayout, QWidget
from jdxi_editor.ui.editors.address.factory import create_vocal_fx_address
from jdxi_editor.ui.editors.synth.simple import BasicEditor
from jdxi_editor.ui.preset.helper import JDXiPresetHelper
from jdxi_editor.ui.widgets.editor.base import EditorBaseWidget
from jdxi_editor.ui.widgets.editor.helper import transfer_layout_items
from jdxi_editor.ui.widgets.editor.simple_editor_helper import SimpleEditorHelper
from jdxi_editor.ui.editors.effects.data import VocalEffectsData
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

        # Get tab widget from helper and add tabs (Phase 3: polymorphic layout)
        self.tab_widget = self.editor_helper.get_tab_widget()
        common_icon = JDXi.UI.Icon.get_icon(
            JDXi.UI.Icon.COG_OUTLINE, color=JDXi.UI.Style.GREY
        )
        self.tab_widget.addTab(self._create_common_section(), common_icon, "Common")
        vocal_fx_icon = JDXi.UI.Icon.get_icon(
            JDXi.UI.Icon.MICROPHONE, color=JDXi.UI.Style.GREY
        )
        self.tab_widget.addTab(
            self._create_vocal_effect_stack_section(),
            vocal_fx_icon,
            "Vocoder & Auto Pitch",
        )
        mixer_icon = JDXi.UI.Icon.get_icon(
            JDXi.UI.Icon.EQUALIZER, color=JDXi.UI.Style.GREY
        )
        self.tab_widget.addTab(self._create_mixer_section(), mixer_icon, "Mixer")

        # Connect Vocal Effect combo to switch stack page
        vocal_effect_ctrl = self.controls.get(ProgramCommonParam.VOCAL_EFFECT)
        if vocal_effect_ctrl and hasattr(vocal_effect_ctrl, "combo_box"):
            vocal_effect_ctrl.combo_box.currentIndexChanged.connect(
                self._update_vocal_effect_stack
            )
            self._update_vocal_effect_stack(
                vocal_effect_ctrl.combo_box.currentIndex()
            )

        # Add base widget to editor's layout
        if not hasattr(self, "main_layout") or self.main_layout is None:
            self.main_layout = QVBoxLayout(self)
            self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.base_widget)

        self._apply_vocal_effect_tooltips()

        self.midi_requests = [
            MidiRequests.PROGRAM_COMMON,
            MidiRequests.PROGRAM_VOCAL_EFFECT,
        ]

        if self.midi_helper:
            self.midi_helper.midi_sysex_json.connect(self._dispatch_sysex_to_area)
            log.message(
                "🎛️: Connected to midi_sysex_json signal",
                scope=self.__class__.__name__,
            )

    def showEvent(self, event: QShowEvent) -> None:
        """Request current settings from the instrument when the editor is shown."""
        super().showEvent(event)
        if self.midi_helper:
            log.message(
                "🎛️ shown - requesting current settings from instrument",
                scope=self.__class__.__name__,
            )
        self.data_request()

    def _dispatch_sysex_to_area(self, json_sysex_data: str) -> None:
        """Parse SysEx JSON and update Vocal FX controls."""
        try:
            import json

            from jdxi_editor.ui.editors.digital.utils import filter_sysex_keys

            sysex_data = json.loads(json_sysex_data)
            temporary_area = sysex_data.get(SysExSection.TEMPORARY_AREA, "")
            synth_tone = sysex_data.get(SysExSection.SYNTH_TONE, "")

            if temporary_area != "TEMPORARY_PROGRAM":
                return
            if synth_tone not in ("COMMON", "VOCAL_EFFECT"):
                return

            filtered = filter_sysex_keys(sysex_data)
            applied, failed = [], []

            for param_name, raw_value in filtered.items():
                if param_name in (SysExSection.TEMPORARY_AREA, SysExSection.SYNTH_TONE):
                    continue
                param = ProgramCommonParam.get_by_name(param_name) or VocalFXParam.get_by_name(
                    param_name
                )
                if not param:
                    continue
                widget = self.controls.get(param)
                if not widget:
                    failed.append(param_name)
                    continue
                try:
                    value = int(raw_value) if not isinstance(raw_value, int) else raw_value
                    display = (
                        param.convert_from_midi(value)
                        if hasattr(param, "convert_from_midi")
                        else value
                    )
                    if hasattr(widget, "setValue"):
                        widget.blockSignals(True)
                        widget.setValue(display)
                        widget.blockSignals(False)
                    elif hasattr(widget, "combo_box"):
                        widget.combo_box.blockSignals(True)
                        values = getattr(widget, "values", None)
                        if values and value in values:
                            widget.combo_box.setCurrentIndex(values.index(value))
                        else:
                            widget.combo_box.setCurrentIndex(value)
                        widget.combo_box.blockSignals(False)
                    elif hasattr(widget, "setChecked"):
                        widget.blockSignals(True)
                        widget.setChecked(bool(value))
                        widget.blockSignals(False)
                    else:
                        failed.append(param_name)
                        continue
                    applied.append(param_name)
                except Exception:
                    failed.append(param_name)

            if applied:
                log.message(
                    f"Vocal FX: applied {len(applied)} params",
                    scope=self.__class__.__name__,
                    silent=True,
                )
        except Exception as ex:
            log.error(
                f"Vocal FX dispatch error: {ex}",
                scope=self.__class__.__name__,
            )

    def _apply_vocal_effect_tooltips(self) -> None:
        """Set tooltips for vocal effect controls from VocalEffectsData."""
        for param, widget in self.controls.items():
            if widget and hasattr(param, "name"):
                tip = VocalEffectsData.vocal_effect_tooltips.get(param.name)
                if tip:
                    widget.setToolTip(tip)

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
            SwitchSpec(
                ProgramCommonParam.VOCAL_EFFECT_PART,
                "Effect Part:",
                ["Part 1", "Part 2"],
            ),
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

    def _update_vocal_effect_stack(self, index: int) -> None:
        """Switch Vocoder & Auto Pitch stack to the page for the selected effect type."""
        try:
            if hasattr(self, "vocal_effect_stack"):
                self.vocal_effect_stack.setCurrentIndex(index)
        except Exception as ex:
            log.error(
                f"Error switching Vocal Effect stack: {ex}",
                scope=self.__class__.__name__,
            )

    def _create_vocal_effect_stack_section(self) -> QWidget:
        """Create Vocoder & Auto Pitch tab with QStackedWidget (OFF/VOCODER/AUTO-PITCH)."""
        self.vocal_effect_stack = QStackedWidget()

        # Page 0: OFF (Vocal Effect disabled — no additional params)
        off_page = QWidget()
        off_layout = QVBoxLayout(off_page)
        off_label = QLabel("Vocal Effect is OFF. Select VOCODER or AUTO-PITCH in Common to configure.")
        off_label.setWordWrap(True)
        off_layout.addWidget(off_label)
        off_layout.addStretch()
        self.vocal_effect_stack.addWidget(off_page)

        # Page 1: Vocoder
        self.vocal_effect_stack.addWidget(self._create_vocal_effect_section())

        # Page 2: Auto Pitch
        self.vocal_effect_stack.addWidget(self._create_auto_pitch_section())

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(self.vocal_effect_stack)
        return container

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
            SliderSpec(
                VocalFXParam.AUTO_PITCH_BALANCE,
                "Balance [dry→wet]",
                vertical=False,
            ),
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
