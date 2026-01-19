"""
User Programs Widget Module

This module defines the `UserProgramsWidget` class, a widget for managing
user programs in a sortable, searchable table with database integration.

Classes:
    UserProgramsWidget(QWidget)
        A widget for displaying and managing user programs.
"""

from typing import Callable, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from decologr import Decologr as log
from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.program.program import JDXiProgram
from jdxi_editor.ui.editors.helpers.program import calculate_midi_values
from jdxi_editor.ui.widgets.delegates.play_button import PlayButtonDelegate
from jdxi_editor.ui.widgets.editor.helper import transfer_layout_items


class UserProgramsWidget(QWidget):
    """Widget for managing user programs in a database table."""

    # Signal emitted when a program is selected/loaded
    program_loaded = Signal(JDXiProgram)

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        channel: int = 16,  # Default PROGRAM channel (0-based)
        parent: Optional[QWidget] = None,
        on_program_loaded: Optional[Callable[[JDXiProgram], None]] = None,
    ):
        """
        Initialize the UserProgramsWidget.

        :param midi_helper: Optional[MidiIOHelper] for MIDI communication
        :param channel: int MIDI channel (0-based, default 16 for PROGRAM)
        :param parent: Optional[QWidget] parent widget
        :param on_program_loaded: Optional callback when program is loaded
        """
        super().__init__(parent)
        self.midi_helper = midi_helper
        self.channel = channel
        self.on_program_loaded_callback = on_program_loaded

        # UI components
        self.user_programs_search_box: Optional[QLineEdit] = None
        self.user_programs_table: Optional[QTableWidget] = None
        self.save_user_programs_button: Optional[QPushButton] = None

        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the user programs UI."""
        layout = QVBoxLayout(self)

        # Add icon row at the top (transfer items to avoid "already has a parent" errors)
        icon_row_container = QHBoxLayout()
        icon_row = JDXi.UI.IconRegistry.create_generic_musical_icon_row()

        transfer_layout_items(icon_row, icon_row_container)
        layout.addLayout(icon_row_container)

        # Search box
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.user_programs_search_box = QLineEdit()
        self.user_programs_search_box.setPlaceholderText(
            "Search by ID, name, genre, or tone..."
        )
        self.user_programs_search_box.textChanged.connect(
            lambda text: self.populate_table(text)
        )
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.user_programs_search_box)
        layout.addLayout(search_layout)

        # Create table
        self.user_programs_table = QTableWidget()
        self.user_programs_table.setColumnCount(12)
        self.user_programs_table.setHorizontalHeaderLabels(
            [
                "ID",
                "Name",
                "Genre",
                "Bank",
                "PC",
                "MSB",
                "LSB",
                "Digital 1",
                "Digital 2",
                "Analog",
                "Drums",
                "Play",
            ]
        )

        # Apply custom styling
        self.user_programs_table.setStyleSheet(self._get_table_style())

        # Enable sorting
        self.user_programs_table.setSortingEnabled(True)

        # Set column widths
        header = self.user_programs_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Name
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Genre
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Bank
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # PC
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # MSB
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # LSB
        header.setSectionResizeMode(
            7, QHeaderView.ResizeMode.ResizeToContents
        )  # Digital 1
        header.setSectionResizeMode(
            8, QHeaderView.ResizeMode.ResizeToContents
        )  # Digital 2
        header.setSectionResizeMode(
            9, QHeaderView.ResizeMode.ResizeToContents
        )  # Analog
        header.setSectionResizeMode(
            10, QHeaderView.ResizeMode.ResizeToContents
        )  # Drums
        header.setSectionResizeMode(11, QHeaderView.ResizeMode.ResizeToContents)  # Play

        # Set up Play button delegate for column 11
        play_button_delegate = PlayButtonDelegate(
            self.user_programs_table, play_callback=self._play_user_program
        )
        self.user_programs_table.setItemDelegateForColumn(11, play_button_delegate)

        # Connect double-click to load program
        self.user_programs_table.itemDoubleClicked.connect(
            self._on_user_program_selected
        )

        # Connect single-click to load program (alternative)
        self.user_programs_table.itemSelectionChanged.connect(
            self._on_user_program_selection_changed
        )

        layout.addWidget(self.user_programs_table)

        # Add save button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.save_user_programs_button = QPushButton(
            JDXi.UI.IconRegistry.get_icon(
                JDXi.UI.IconRegistry.FLOPPY_DISK, color=JDXi.UI.Style.FOREGROUND
            ),
            "Save Changes",
        )
        self.save_user_programs_button.clicked.connect(self.save_changes)
        button_layout.addWidget(self.save_user_programs_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Populate table (with error handling)
        try:
            log.message("🔨 Calling populate_table()...")
            self.populate_table()
            log.message("✅ Table populated successfully")
        except Exception as e:
            log.error(f"❌ Error populating user programs table: {e}")
            import traceback

            log.error(traceback.format_exc())
            # Table will be empty but widget will still be visible

    def _get_table_style(self) -> str:
        """
        Get custom styling for tables with rounded corners and charcoal embossed cells.

        :return: str CSS style string
        """
        return JDXi.UI.Style.DATABASE_TABLE_STYLE

    def populate_table(self, search_text: str = "") -> None:
        """
        Populate the user programs table from SQLite database.

        :param search_text: Optional search text to filter programs
        """
        if not self.user_programs_table:
            log.warning("User programs table not initialized")
            return

        try:
            from jdxi_editor.ui.programs.database import get_database

            # Get all user programs from database
            db = get_database()
            all_programs = db.get_all_programs()
        except Exception as e:
            log.error(f"Error getting programs from database: {e}")
            all_programs = []

        # Filter by search text if provided
        if search_text:
            search_lower = search_text.lower()
            all_programs = [
                p
                for p in all_programs
                if (
                    search_lower in p.id.lower()
                    or search_lower in p.name.lower()
                    or (p.genre and search_lower in p.genre.lower())
                    or (p.digital_1 and search_lower in p.digital_1.lower())
                    or (p.digital_2 and search_lower in p.digital_2.lower())
                    or (p.analog and search_lower in p.analog.lower())
                    or (p.drums and search_lower in p.drums.lower())
                )
            ]

        # Clear table
        try:
            self.user_programs_table.setRowCount(0)
        except Exception as e:
            log.error(f"Error clearing user programs table: {e}")
            return

        # Populate table
        for program in all_programs:
            row = self.user_programs_table.rowCount()
            self.user_programs_table.insertRow(row)

            # Extract bank letter from ID
            bank_letter = program.id[0] if program.id else ""

            # Create items
            self.user_programs_table.setItem(row, 0, QTableWidgetItem(program.id or ""))
            # Make Name column editable (column 1)
            name_item = QTableWidgetItem(program.name or "")
            name_item.setFlags(name_item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.user_programs_table.setItem(row, 1, name_item)
            # Make Genre column editable (column 2)
            genre_item = QTableWidgetItem(program.genre or "")
            genre_item.setFlags(genre_item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.user_programs_table.setItem(row, 2, genre_item)
            self.user_programs_table.setItem(row, 3, QTableWidgetItem(bank_letter))
            self.user_programs_table.setItem(
                row,
                4,
                QTableWidgetItem(str(program.pc) if program.pc is not None else ""),
            )
            self.user_programs_table.setItem(
                row,
                5,
                QTableWidgetItem(str(program.msb) if program.msb is not None else ""),
            )
            self.user_programs_table.setItem(
                row,
                6,
                QTableWidgetItem(str(program.lsb) if program.lsb is not None else ""),
            )
            self.user_programs_table.setItem(
                row, 7, QTableWidgetItem(program.digital_1 or "")
            )
            self.user_programs_table.setItem(
                row, 8, QTableWidgetItem(program.digital_2 or "")
            )
            self.user_programs_table.setItem(
                row, 9, QTableWidgetItem(program.analog or "")
            )
            self.user_programs_table.setItem(
                row, 10, QTableWidgetItem(program.drums or "")
            )

            # Store program object in item data for easy access
            for col in range(11):
                item = self.user_programs_table.item(row, col)
                if item:
                    item.setData(Qt.ItemDataRole.UserRole, program)

        log.message(
            f"✅ Populated user programs table with {len(all_programs)} programs"
        )

    def save_changes(self) -> None:
        """Save changes made to the user programs table (e.g., genre edits) to the database."""
        if not self.user_programs_table:
            log.warning("User programs table not initialized")
            return

        from jdxi_editor.midi.io.input_handler import add_or_replace_program_and_save
        from jdxi_editor.ui.programs.database import get_database

        db = get_database()
        saved_count = 0
        error_count = 0

        # Iterate through all rows in the table
        for row in range(self.user_programs_table.rowCount()):
            # Get the program object from the first column's user data
            id_item = self.user_programs_table.item(row, 0)
            if not id_item:
                continue

            program = id_item.data(Qt.ItemDataRole.UserRole)
            if not program or not isinstance(program, JDXiProgram):
                continue

            # Get the updated name from the table (column 1)
            name_item = self.user_programs_table.item(row, 1)
            new_name = name_item.text().strip() if name_item else (program.name or "")

            # Get the updated genre from the table (column 2)
            genre_item = self.user_programs_table.item(row, 2)
            new_genre = (
                genre_item.text().strip() if genre_item else (program.genre or "")
            )

            # Check if name or genre has changed
            name_changed = new_name != (program.name or "")
            genre_changed = new_genre != (program.genre or "")

            if name_changed or genre_changed:
                # Create updated program object
                updated_program = JDXiProgram(
                    id=program.id,
                    name=new_name if new_name else None,
                    genre=new_genre if new_genre else None,
                    pc=program.pc,
                    msb=program.msb,
                    lsb=program.lsb,
                    tempo=program.tempo,
                    measure_length=program.measure_length,
                    scale=program.scale,
                    analog=program.analog,
                    digital_1=program.digital_1,
                    digital_2=program.digital_2,
                    drums=program.drums,
                )

                # Save to database
                if add_or_replace_program_and_save(updated_program):
                    saved_count += 1
                    changes = []
                    if name_changed:
                        changes.append(f"name: '{program.name}' -> '{new_name}'")
                    if genre_changed:
                        changes.append(f"genre: '{program.genre}' -> '{new_genre}'")
                    log.message(f"✅ Updated {program.id}: {', '.join(changes)}")
                    # Update the stored program object in item data
                    for col in range(11):
                        item = self.user_programs_table.item(row, col)
                        if item:
                            item.setData(Qt.ItemDataRole.UserRole, updated_program)
                else:
                    error_count += 1
                    log.error(f"❌ Failed to save update for {program.id}")

        # Show summary message
        if saved_count > 0:
            log.message(f"✅ Saved {saved_count} program update(s)")
            if error_count > 0:
                log.warning(f"⚠️ {error_count} program(s) failed to save")
        else:
            if error_count > 0:
                log.error(f"❌ Failed to save {error_count} program(s)")
            else:
                log.message("ℹ️ No changes to save")

    def _on_user_program_selected(self, item: QTableWidgetItem) -> None:
        """
        Handle double-click on a program in the user programs table.
        Loads the program via MIDI Program Change.

        :param item: The table item that was double-clicked
        """
        self._load_program_from_table(item.row())

    def _on_user_program_selection_changed(self) -> None:
        """
        Handle selection change in the user programs table.
        Loads the program via MIDI Program Change when a row is selected.
        """
        selected_rows = self.user_programs_table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self._load_program_from_table(row)

    def _play_user_program(self, index) -> None:
        """
        Callback for Play button delegate - loads and plays the program.

        :param index: QModelIndex from the delegate
        """
        row = index.row()
        log.message(f"🎹 Play button clicked for row {row}")
        self._load_program_from_table(row)

    def _load_program_from_table(self, row: int) -> None:
        """
        Load a program from the table and send MIDI Program Change.

        :param row: Row index in the table
        """
        if (
            not self.user_programs_table
            or row < 0
            or row >= self.user_programs_table.rowCount()
        ):
            return

        # Get program from first column's user data
        item = self.user_programs_table.item(row, 0)
        if not item:
            return

        program = item.data(Qt.ItemDataRole.UserRole)
        if not program or not isinstance(program, JDXiProgram):
            return

        # Get program ID and extract bank/number
        program_id = program.id
        if not program_id or len(program_id) < 3:
            log.warning(f"Invalid program ID: {program_id}")
            return

        bank_letter = program_id[0]
        try:
            bank_number = int(program_id[1:3])
        except ValueError:
            log.warning(f"Invalid program number in ID: {program_id}")
            return

        log.message(f"🎹 Loading program from table: {program_id} - {program.name}")

        # Calculate MIDI values
        try:
            msb, lsb, pc = calculate_midi_values(bank_letter, bank_number)
        except (ValueError, TypeError) as e:
            log.error(f"Error calculating MIDI values for {program_id}: {e}")
            return

        # Send MIDI Program Change
        if self.midi_helper:
            log.message(f"Sending Program Change: MSB={msb}, LSB={lsb}, PC={pc}")
            self.midi_helper.send_bank_select_and_program_change(
                self.channel, msb, lsb, pc
            )

        # Emit signal and call callback
        self.program_loaded.emit(program)
        if self.on_program_loaded_callback:
            self.on_program_loaded_callback(program)
