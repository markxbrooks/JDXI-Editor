"""
Arpeggio Editor Module

This module defines the `ArpeggioEditor` class, a specialized editor for configuring arpeggiator
settings within a synthesizer. It extends the `SynthEditor` class, providing a user-friendly
interface to control various arpeggiator parameters.

Classes:
    - ArpeggioEditor: A `QWidget` subclass that allows users to modify arpeggiator parameters
      such as style, grid, duration, velocity, accent, swing, octave range, and motif.

Features:
    - Provides an intuitive UI with labeled controls and dropdown menus for parameter selection.
    - Includes a toggle switch to enable or disable the arpeggiator.
    - Displays an instrument image for better user engagement.
    - Uses MIDI integration to send real-time parameter changes to the synthesizer.
    - Supports dynamic visualization and interaction through sliders and combo boxes.

Usage:
    ```python
    from PySide6.QtWidgets import QApplication
    from midi_helper import MIDIHelper

    app = QApplication([])
    midi_helper = MIDIHelper()
    editor = ArpeggioEditor(midi_helper=midi_helper)
    editor.show()
    app.exec()
    ```

Dependencies:
    - PySide6 (for UI components)
    - MIDIHelper (for MIDI communication)
    - ArpeggioParameter (for managing parameter addresses and value ranges)
    - Slider (for smooth control over numerical parameters)

"""

from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from decologr import Decologr as log
from picomidi.sysex.parameter.address import AddressParameter
from PySide6.QtGui import QShowEvent

from jdxi_editor.midi.data.address.address import JDXiSysExAddress

if TYPE_CHECKING:
    from jdxi_editor.ui.windows.jdxi.instrument import JDXiInstrument

from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
)

from jdxi_editor.midi.data.arpeggio.arpeggio import (
    ArpeggioDuration,
    ArpeggioOctaveRange,
    ArpeggioSwitch,
)
from jdxi_editor.midi.data.arpeggio.data import (
    ARPEGGIO_GRID,
    ARPEGGIO_MOTIF,
    ARPEGGIO_STYLE,
)
from jdxi_editor.midi.data.parameter.arpeggio import ArpeggioParam
from jdxi_editor.midi.data.parameter.program.zone import ProgramZoneParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.sysex.request.midi_requests import MidiRequests
from jdxi_editor.midi.sysex.sections import SysExSection
from jdxi_editor.ui.common import JDXi, QVBoxLayout, QWidget
from jdxi_editor.ui.editors.address.factory import create_arp_address
from jdxi_editor.ui.editors.synth.simple import BasicEditor
from jdxi_editor.ui.preset.helper import JDXiPresetHelper
from jdxi_editor.ui.widgets.editor.base import EditorBaseWidget
from jdxi_editor.ui.widgets.editor.helper import transfer_layout_items
from jdxi_editor.ui.widgets.editor.simple_editor_helper import SimpleEditorHelper
from jdxi_editor.ui.widgets.group import WidgetGroups
from jdxi_editor.ui.widgets.layout import WidgetLayoutSpec
from jdxi_editor.ui.widgets.spec import ComboBoxSpec, SliderSpec, SwitchSpec


class ArpeggioEditor(BasicEditor):
    """Arpeggio Editor Window"""

    EDITOR_PARAM = ArpeggioParam

    def __init__(
        self,
        midi_helper: MidiIOHelper,
        preset_helper: Optional[JDXiPresetHelper] = None,
        parent: Optional["JDXiInstrument"] = None,
    ):
        super().__init__(midi_helper=midi_helper, parent=parent)

        """
        Initialize the ArpeggioEditor

        :param midi_helper: MidiIOHelper
        :param preset_helper: JDXIPresetHelper
        :param parent: QWidget
        """
        self.setWindowTitle("Arpeggio Editor")
        self.midi_helper = midi_helper
        self.preset_helper = preset_helper
        self.address = create_arp_address()
        self.partial_number = 0
        self.controls: Dict[AddressParameter, QWidget] = {}
        # Zone name -> switch widget (for Program Zone Arpeggio Switch per zone)
        self.zone_switches: Dict[str, QWidget] = {}

        if parent:
            if parent.current_synth_type:
                if parent.current_synth_type == "Digital 1":
                    self.partial_number = 0
                elif parent.current_synth_type == "Digital 2":
                    self.partial_number = 1
                elif parent.current_synth_type == "Digital 3":
                    self.partial_number = 2
                elif parent.current_synth_type == "Digital 4":
                    self.partial_number = 3

        # --- Use EditorBaseWidget for consistent scrollable layout structure
        self.base_widget = EditorBaseWidget(parent=self, analog=False)
        self.base_widget.setup_scrollable_content()

        # --- Use SimpleEditorHelper for standardized title/image/tab setup
        self.editor_helper = SimpleEditorHelper(
            editor=self,
            base_widget=self.base_widget,
            title="Arpeggiator",
            image_folder="arpeggiator",
            default_image="arpeggiator2.png",
        )

        self.midi_requests = [
            MidiRequests.PROGRAM_CONTROLLER,
            MidiRequests.PROGRAM_ZONE_DIGITAL1,
            MidiRequests.PROGRAM_ZONE_DIGITAL2,
            MidiRequests.PROGRAM_ZONE_ANALOG,
            MidiRequests.PROGRAM_ZONE_DRUMS,
        ]

        self.setup_ui()

        if self.midi_helper:
            self.midi_helper.midi_sysex_json.connect(self._dispatch_sysex_to_area)
            log.message(
                "Arpeggio: Connected to midi_sysex_json signal",
                scope=self.__class__.__name__,
            )

    def setup_ui(self):
        # --- Icons row (standardized across editor tabs) - transfer items to avoid "already has a parent" errors
        icon_row_container = QHBoxLayout()
        icon_hlayout = JDXi.UI.Icon.create_generic_musical_icon_row()
        transfer_layout_items(icon_hlayout, icon_row_container)

        # --- 1) build widgets
        arp_widgets: WidgetGroups = self._build_widgets()
        # --- 2) setup layout
        rows_layout = self.editor_helper.get_rows_layout()
        # Add icon row at top so it is visible
        rows_layout.insertLayout(0, icon_row_container)

        form_layout_widget = QWidget()
        form_layout = QFormLayout()
        form_layout_widget.setLayout(form_layout)
        rows_layout.addWidget(form_layout_widget)
        # --- 3) add widgets
        widgets = arp_widgets.switches + arp_widgets.combos + arp_widgets.sliders
        for widget in widgets:
            form_layout.addRow(widget)
        rows_layout.addStretch()

        # Add base widget to editor's layout
        if not hasattr(self, "main_layout") or self.main_layout is None:
            self.main_layout = QVBoxLayout(self)
            self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.base_widget)

    def showEvent(self, event: QShowEvent) -> None:
        """Request current settings from the instrument when the editor is shown."""
        super().showEvent(event)
        if self.midi_helper:
            log.message(
                "Arpeggio shown - requesting current settings from instrument",
                scope=self.__class__.__name__,
            )
        self.data_request()

    def _dispatch_sysex_to_area(self, json_sysex_data: str) -> None:
        """Parse SysEx JSON and update Arpeggio controls."""
        try:
            import json

            from jdxi_editor.ui.editors.digital.utils import filter_sysex_keys

            sysex_data = json.loads(json_sysex_data)
            temporary_area = sysex_data.get(SysExSection.TEMPORARY_AREA, "")
            synth_tone = sysex_data.get(SysExSection.SYNTH_TONE, "")

            if temporary_area != "TEMPORARY_PROGRAM":
                return

            filtered = filter_sysex_keys(sysex_data)

            # Handle Program Zone (per-zone Arpeggio Switch)
            if synth_tone in (
                "ZONE_DIGITAL_SYNTH_1",
                "ZONE_DIGITAL_SYNTH_2",
                "ZONE_ANALOG",
                "ZONE_DRUM",
            ):
                raw_val = filtered.get("ARPEGGIO_SWITCH")
                if raw_val is not None:
                    switch_widget = self.zone_switches.get(synth_tone)
                    if switch_widget:
                        try:
                            value = (
                                int(raw_val)
                                if not isinstance(raw_val, int)
                                else raw_val
                            )
                            switch_widget.blockSignals(True)
                            if hasattr(switch_widget, "setValue"):
                                switch_widget.setValue(value)
                            elif hasattr(switch_widget, "setChecked"):
                                switch_widget.setChecked(bool(value))
                            switch_widget.blockSignals(False)
                        except Exception:
                            pass
                return

            if synth_tone != "CONTROLLER":
                return

            for param_name, raw_value in filtered.items():
                if param_name in (SysExSection.TEMPORARY_AREA, SysExSection.SYNTH_TONE):
                    continue
                param = ArpeggioParam.get_by_name(param_name)
                if not param:
                    continue
                widget = self.controls.get(param)
                if not widget:
                    continue
                try:
                    value = (
                        int(raw_value) if not isinstance(raw_value, int) else raw_value
                    )
                    display = (
                        param.convert_from_midi(value)
                        if hasattr(param, "convert_from_midi")
                        else value
                    )
                    if hasattr(widget, "combo_box"):
                        # ComboBox: setValue expects raw MIDI value for index lookup
                        widget.blockSignals(True)
                        widget.setValue(value)
                        widget.blockSignals(False)
                    elif hasattr(widget, "setValue"):
                        # Slider or Switch: use display value (sliders) or value (switches)
                        widget.blockSignals(True)
                        widget.setValue(display)
                        widget.blockSignals(False)
                    elif hasattr(widget, "setChecked"):
                        widget.blockSignals(True)
                        widget.setChecked(bool(value))
                        widget.blockSignals(False)
                except Exception:
                    pass
        except Exception:
            pass

    def _build_widgets(self):
        """Build widgets"""
        spec = self._build_layout_spec()
        zone_switches = self._build_zone_switches()
        return WidgetGroups(
            switches=zone_switches + self._build_switches(spec.switches),
            sliders=self._build_sliders(spec.sliders),
            combos=self._build_combo_boxes(spec.combos),
        )

    def _build_zone_switches(self) -> List[QWidget]:
        """Build per-zone Arpeggio Switch controls (enables arpeggiator per zone)."""
        from jdxi_editor.ui.widgets.switch.switch import Switch

        param = ProgramZoneParam.ARPEGGIO_SWITCH
        values = [s.display_name for s in ArpeggioSwitch]
        zone_config: List[Tuple[str, str, JDXiSysExAddress]] = [
            (
                "ZONE_DIGITAL_SYNTH_1",
                "Digital 1",
                JDXiSysExAddress(0x18, 0x00, 0x30, 0x00),
            ),
            (
                "ZONE_DIGITAL_SYNTH_2",
                "Digital 2",
                JDXiSysExAddress(0x18, 0x00, 0x31, 0x00),
            ),
            ("ZONE_ANALOG", "Analog", JDXiSysExAddress(0x18, 0x00, 0x32, 0x00)),
            ("ZONE_DRUM", "Drums", JDXiSysExAddress(0x18, 0x00, 0x33, 0x00)),
        ]
        switches = []
        for zone_name, label, zone_addr in zone_config:
            switch = Switch(
                label=f"{label} Arpeggio",
                values=values,
                tooltip=f"Enable arpeggiator for {label} zone",
            )
            switch.valueChanged.connect(
                lambda v, p=param, addr=zone_addr: self._on_parameter_changed(
                    p, v, addr
                )
            )
            self.zone_switches[zone_name] = switch
            switches.append(switch)
        return switches

    def _build_layout_spec(self):
        P = self.EDITOR_PARAM

        switches = [
            SwitchSpec(
                P.ARPEGGIO_SWITCH,
                P.ARPEGGIO_SWITCH.display_name,
                [switch_setting.display_name for switch_setting in ArpeggioSwitch],
            ),
        ]

        combos = [
            ComboBoxSpec(
                P.ARPEGGIO_STYLE, P.ARPEGGIO_STYLE.display_name, ARPEGGIO_STYLE
            ),
            ComboBoxSpec(
                P.ARPEGGIO_GRID,
                P.ARPEGGIO_GRID.display_name,
                ARPEGGIO_GRID,
            ),
            ComboBoxSpec(
                P.ARPEGGIO_DURATION,
                P.ARPEGGIO_DURATION.display_name,
                [duration.display_name for duration in ArpeggioDuration],
            ),
            ComboBoxSpec(
                P.ARPEGGIO_OCTAVE_RANGE,
                P.ARPEGGIO_OCTAVE_RANGE.display_name,
                [octave.display_name for octave in ArpeggioOctaveRange],
                [octave.midi_value for octave in ArpeggioOctaveRange],
            ),
            ComboBoxSpec(
                P.ARPEGGIO_MOTIF,
                P.ARPEGGIO_MOTIF.display_name,
                ARPEGGIO_MOTIF,
            ),
        ]
        sliders = [
            SliderSpec(
                P.ARPEGGIO_VELOCITY, P.ARPEGGIO_VELOCITY.display_name, vertical=False
            ),
            SliderSpec(
                P.ARPEGGIO_ACCENT_RATE,
                P.ARPEGGIO_ACCENT_RATE.display_name,
                vertical=False,
            ),
        ]

        return WidgetLayoutSpec(switches=switches, sliders=sliders, combos=combos)
