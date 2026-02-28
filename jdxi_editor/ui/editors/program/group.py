"""
Program Group Widget Module

This module defines the `ProgramGroupWidget` class, a widget for program selection
and loading within the Program Editor.

Classes:
    ProgramGroupWidget(QGroupBox)
        A widget for selecting and loading programs.
"""

from typing import TYPE_CHECKING, Any, Optional

from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget
)

from jdxi_editor.ui.common import JDXi, QVBoxLayout, QWidget
from jdxi_editor.ui.editors.helpers.widgets import create_jdxi_button, create_jdxi_row
from jdxi_editor.ui.style import JDXiUIDimensions, JDXiUIStyle
from jdxi_editor.ui.widgets.editor.helper import transfer_layout_items

if TYPE_CHECKING:
    from jdxi_editor.ui.editors.program.editor import ProgramEditor

from decologr import Decologr as log

from jdxi_editor.log.midi_info import log_midi_info
from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.midi.data.parameter.program.common import ProgramCommonParam
from jdxi_editor.midi.program.program import JDXiProgram
from jdxi_editor.ui.editors.helpers.program import (
    calculate_midi_values,
    get_program_by_id
)
from jdxi_editor.ui.editors.preset.widget import PresetWidget
from jdxi_editor.ui.editors.program.mixer.section import ProgramMixer
from jdxi_editor.ui.widgets.combo_box.searchable_filterable import (
    SearchableFilterableComboBox
)
from jdxi_editor.ui.widgets.digital.title import DigitalTitle
from jdxi_editor.ui.windows.patch.name_editor import PatchNameEditor


class ProgramGroup(QGroupBox):
    """Program Widget"""

    def __init__(self, title: str = None, parent: Optional["ProgramEditor"] = None):
        super().__init__("Load a program")
        self.mixer_widget: Optional[ProgramMixer] = None
        self.parent = parent
        self.preset: PresetWidget = PresetWidget(parent=self)
        self.program_name = ""
        self.channel = (
            MidiChannel.PROGRAM  # Default MIDI channel: 16 for programs, 0-based
        )
        # Program controls group
        program_layout = QVBoxLayout()
        program_vlayout = QVBoxLayout()

        self.setLayout(program_layout)

        self.file_label = DigitalTitle("No file loaded")
        program_layout.addWidget(self.file_label)

        # program and presets tab widget (nested inside group box)
        self.program_preset_tab_widget = QTabWidget()
        self.program_preset_tab_widget.setMinimumHeight(
            300
        )  # Ensure tab widget is visible
        program_widget = QWidget()
        program_widget.setLayout(program_vlayout)

        # Add icon row at the top of Programs tab (transfer items to avoid "already has a parent" errors)
        icon_row_container = QHBoxLayout()
        icon_row = JDXi.UI.Icon.create_generic_musical_icon_row()

        transfer_layout_items(icon_row, icon_row_container)
        program_vlayout.addLayout(icon_row_container)

        program_layout.addWidget(self.program_preset_tab_widget)
        programs_icon = JDXi.UI.Icon.get_icon(
            "mdi.music-box-multiple", color=JDXi.UI.Style.GREY
        )
        if programs_icon is None:
            programs_icon = JDXi.UI.Icon.get_icon(
                JDXi.UI.Icon.MUSIC, color=JDXi.UI.Style.GREY
            )
        self.program_preset_tab_widget.addTab(program_widget, programs_icon, "Programs")
        log.message(
            f"📑Created nested tab widget, added 'Programs' tab (total tabs: {self.program_preset_tab_widget.count()})",
            scope=self.__class__.__name__
)

        # Edit Program Name (round button + icon + label, centered)
        edit_name_row = QHBoxLayout()
        edit_name_row.addStretch()
        self._add_round_action_button(
            JDXi.UI.Icon.SETTINGS,
            "Edit Program Name",
            self.edit_program_name,
            edit_name_row,
            name="edit_program_name"
)
        edit_name_row.addStretch()
        program_vlayout.addLayout(edit_name_row)

        # Create SearchableFilterableComboBox for program selection with bank and genre filtering
        # Initialize with empty data - will be populated by populate_programs()
        self.program_number_combo_box = SearchableFilterableComboBox(
            label="Program",
            options=[],
            values=[],
            categories=[],
            banks=["A", "B", "C", "D", "E", "F", "G", "H"],
            show_label=True,
            show_search=True,
            show_category=True,
            show_bank=True,
            search_placeholder="Search programs...",
            category_label="Genre:",
            bank_label="Bank:"
)
        program_vlayout.addWidget(self.program_number_combo_box)

        # Store reference to actual program list for use in filtering
        self._program_list_data = []
        # Load Program (round button + icon + label, centered)
        load_program_row = QHBoxLayout()
        load_program_row.addStretch()
        self.preset.load_button = self._add_round_action_button(
            JDXi.UI.Icon.FOLDER_NOTCH_OPEN,
            "Load Program",
            self.load_program,
            load_program_row,
            name=None
)
        load_program_row.addStretch()
        program_vlayout.addLayout(load_program_row)

    def _add_round_action_button(
        self,
        icon_enum: Any,
        text: str,
        slot: Any,
        layout: QHBoxLayout,
        *,
        name: Optional[str] = None,
        checkable: bool = False
) -> QPushButton:
        """Create a round button with icon + text label (same style as Transport)."""
        btn = create_jdxi_button("")
        btn.setCheckable(checkable)
        if slot is not None:
            btn.clicked.connect(slot)
        if name:
            setattr(self, f"{name}_button", btn)
        layout.addWidget(btn)
        pixmap = JDXi.UI.Icon.get_icon_pixmap(
            icon_enum, color=JDXi.UI.Style.FOREGROUND, size=20
        )
        label_row, _ = create_jdxi_row(text, icon_pixmap=pixmap)
        layout.addWidget(label_row)
        return btn

    def edit_program_name(self):
        """
        edit_tone_name

        :return: None
        """
        program_name_dialog = PatchNameEditor(current_name=self.program_name)
        if program_name_dialog.exec():  # If the user clicks Save
            sysex_string = program_name_dialog.get_sysex_string()
            log.message(f"SysEx string: {sysex_string}", scope=self.__class__.__name__)
            self.parent.send_tone_name(ProgramCommonParam, sysex_string)
            self.parent.data_request()

    def load_program(self):
        """Load the selected program based on bank and number."""
        # Get program name from combo box
        program_name = self.program_number_combo_box.combo_box.currentText()
        # Extract program ID from format "A01 - Program Name"
        program_id = (
            program_name[:3] if " - " in program_name else program_name.split()[0]
        )
        bank_letter = program_id[0] if len(program_id) >= 1 else ""
        bank_number = int(program_id[1:3]) if len(program_id) >= 3 else 0
        log.parameter("combo box bank_letter", bank_letter)
        log.parameter("combo box bank_number", bank_number)
        if bank_letter in ["A", "B", "C", "D"]:
            program_details = get_program_by_id(program_id)
            self.update_current_synths(program_details)
            self.set_current_program_name(program_details.name)
        msb, lsb, pc = calculate_midi_values(bank_letter, bank_number)
        log.message("Calculated msb, lsb, pc :", scope=self.__class__.__name__)
        log.parameter("[msb]", msb, scope=self.__class__.__name__)
        log.parameter("[lsb]", lsb, scope=self.__class__.__name__)
        log.parameter("[pc]", pc, scope=self.__class__.__name__)
        log_midi_info(msb, lsb, pc)
        self.parent.midi_helper.send_bank_select_and_program_change(
            self.channel, msb, lsb, pc
        )
        self.parent.data_request()

    def update_current_synths(self, program_details: JDXiProgram) -> None:
        """Update the current synth label.
        Delegates to parent's update_current_synths method.

        :param program_details: JDXiProgram
        :return: None
        """
        if self.parent and hasattr(self.parent, "update_current_synths"):
            self.parent.update_current_synths(program_details)

    def set_current_program_name(
        self, program_name: str, synth_type: str = None
    ) -> None:
        """
        Set the current program name in the file label

        :param program_name: str
        :param synth_type: str (optional), discarded for now
        :return: None
        """
        self.program_name = program_name or "Untitled Program"
        if self.file_label:
            self.file_label.setText(program_name)
        else:
            log.message("File label not initialized.", scope=self.__class__.__name__)
        if self.mixer_widget:
            self.mixer_widget.update_program_name(program_name)
