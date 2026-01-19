"""
Playlist Widget Module

This module defines the `PlaylistWidget` class, a widget for managing
playlists in a sortable, editable table with database integration.

Classes:
    PlaylistWidget(QWidget)
        A widget for displaying and managing playlists.
"""

from typing import Callable, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from decologr import Decologr as log
from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.ui.widgets.editor.helper import transfer_layout_items


class PlaylistWidget(QWidget):
    """Widget for managing playlists in a database table."""

    # Signal emitted when a playlist is created, deleted, or updated
    playlist_changed = Signal()

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        on_playlist_changed: Optional[Callable[[], None]] = None,
    ):
        """
        Initialize the PlaylistWidget.

        :param parent: Optional[QWidget] parent widget
        :param on_playlist_changed: Optional callback when playlist changes (for refreshing editor combo)
        """
        super().__init__(parent)
        self.on_playlist_changed_callback = on_playlist_changed

        # UI components
        self.create_playlist_button: Optional[QPushButton] = None
        self.delete_playlist_button: Optional[QPushButton] = None
        self.refresh_playlist_button: Optional[QPushButton] = None
        self.playlist_table: Optional[QTableWidget] = None

        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the playlist UI."""
        layout = QVBoxLayout(self)

        # Add icon row at the top (transfer items to avoid "already has a parent" errors)
        icon_row_container = QHBoxLayout()
        icon_row = JDXi.UI.IconRegistry.create_generic_musical_icon_row()

        transfer_layout_items(icon_row, icon_row_container)
        layout.addLayout(icon_row_container)

        # Button layout for create/delete actions
        button_layout = QHBoxLayout()
        self.create_playlist_button = QPushButton(
            JDXi.UI.IconRegistry.get_icon(
                JDXi.UI.IconRegistry.PLUS_CIRCLE, color=JDXi.UI.Style.FOREGROUND
            ),
            "New Playlist",
        )
        self.create_playlist_button.clicked.connect(self.create_new_playlist)
        button_layout.addWidget(self.create_playlist_button)

        self.delete_playlist_button = QPushButton(
            JDXi.UI.IconRegistry.get_icon(
                JDXi.UI.IconRegistry.TRASH_FILL, color=JDXi.UI.Style.FOREGROUND
            ),
            "Delete Playlist",
        )
        self.delete_playlist_button.clicked.connect(self.delete_selected_playlist)
        button_layout.addWidget(self.delete_playlist_button)

        self.refresh_playlist_button = QPushButton(
            JDXi.UI.IconRegistry.get_icon(
                JDXi.UI.IconRegistry.REFRESH, color=JDXi.UI.Style.FOREGROUND
            ),
            "Refresh Playlist",
        )
        self.refresh_playlist_button.clicked.connect(self.refresh_playlists)
        button_layout.addWidget(self.refresh_playlist_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Create playlist table
        self.playlist_table = QTableWidget()
        self.playlist_table.setColumnCount(4)
        self.playlist_table.setHorizontalHeaderLabels(
            ["ID", "Name", "Description", "Programs"]
        )

        # Apply custom styling
        self.playlist_table.setStyleSheet(self._get_table_style())

        # Enable sorting
        self.playlist_table.setSortingEnabled(True)

        # Set column widths
        header = self.playlist_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Name
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Description
        header.setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )  # Programs

        # Connect item changed to save edits
        self.playlist_table.itemChanged.connect(self._on_playlist_item_changed)

        # Connect double-click to edit playlist
        self.playlist_table.itemDoubleClicked.connect(self._on_playlist_selected)

        layout.addWidget(self.playlist_table)

        # Populate table (with error handling)
        try:
            log.message("🔨 Calling populate_table()...")
            self.populate_table()
            log.message("✅ Playlist table populated successfully")
        except Exception as e:
            log.error(f"❌ Error populating playlist table: {e}")
            import traceback

            log.error(traceback.format_exc())

    def _get_table_style(self) -> str:
        """
        Get custom styling for tables with rounded corners and charcoal embossed cells.

        :return: str CSS style string
        """
        return JDXi.UI.Style.DATABASE_TABLE_STYLE

    def populate_table(self) -> None:
        """Populate the playlist table from SQLite database."""
        if not self.playlist_table:
            log.warning("Playlist table not initialized")
            return

        try:
            from jdxi_editor.ui.programs.database import get_database

            # Get all playlists from database
            db = get_database()
            all_playlists = db.get_all_playlists()
        except Exception as e:
            log.error(f"Error getting playlists from database: {e}")
            import traceback

            log.error(traceback.format_exc())
            all_playlists = []

        # Disable sorting while populating to prevent data misalignment
        was_sorting_enabled = self.playlist_table.isSortingEnabled()
        self.playlist_table.setSortingEnabled(False)

        try:
            # Clear table
            self.playlist_table.setRowCount(0)

            # Populate table
            for playlist in all_playlists:
                row = self.playlist_table.rowCount()
                self.playlist_table.insertRow(row)

                # Create items
                id_item = QTableWidgetItem(str(playlist["id"]))
                id_item.setFlags(
                    id_item.flags() & ~Qt.ItemFlag.ItemIsEditable
                )  # ID not editable
                # Set data role for proper sorting (as integer)
                id_item.setData(Qt.ItemDataRole.DisplayRole, playlist["id"])
                id_item.setData(Qt.ItemDataRole.UserRole, playlist)
                self.playlist_table.setItem(row, 0, id_item)

                # Name column - editable
                name_item = QTableWidgetItem(playlist["name"] or "")
                name_item.setFlags(name_item.flags() | Qt.ItemFlag.ItemIsEditable)
                name_item.setData(Qt.ItemDataRole.UserRole, playlist)
                self.playlist_table.setItem(row, 1, name_item)

                # Description column - editable
                desc_item = QTableWidgetItem(playlist["description"] or "")
                desc_item.setFlags(desc_item.flags() | Qt.ItemFlag.ItemIsEditable)
                desc_item.setData(Qt.ItemDataRole.UserRole, playlist)
                self.playlist_table.setItem(row, 2, desc_item)

                # Program count
                program_count = playlist.get("program_count", 0)
                count_item = QTableWidgetItem(str(program_count))
                count_item.setFlags(
                    count_item.flags() & ~Qt.ItemFlag.ItemIsEditable
                )  # Not editable
                # Set data role for proper sorting (as integer)
                count_item.setData(Qt.ItemDataRole.DisplayRole, program_count)
                count_item.setData(Qt.ItemDataRole.UserRole, playlist)
                self.playlist_table.setItem(row, 3, count_item)
        finally:
            # Re-enable sorting if it was enabled before
            self.playlist_table.setSortingEnabled(was_sorting_enabled)

        log.message(f"✅ Populated playlist table with {len(all_playlists)} playlists")

    def create_new_playlist(self) -> None:
        """Create a new playlist."""
        from PySide6.QtWidgets import QInputDialog

        from jdxi_editor.ui.programs.database import get_database

        name, ok = QInputDialog.getText(self, "New Playlist", "Enter playlist name:")

        if ok and name.strip():
            db = get_database()
            playlist_id = db.create_playlist(name.strip())
            if playlist_id:
                log.message(f"✅ Created playlist: {name}")
                self.populate_table()
                self._notify_playlist_changed()
            else:
                log.error(f"❌ Failed to create playlist: {name}")
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Failed to create playlist '{name}'. It may already exist.",
                )

    def refresh_playlists(self) -> None:
        """Refresh the playlist table."""
        self.populate_table()

    def delete_selected_playlist(self) -> None:
        """Delete the selected playlist."""
        if not self.playlist_table:
            return

        selected_rows = self.playlist_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(
                self, "No Selection", "Please select a playlist to delete."
            )
            return

        row = selected_rows[0].row()
        id_item = self.playlist_table.item(row, 0)
        if not id_item:
            return

        playlist = id_item.data(Qt.ItemDataRole.UserRole)
        if not playlist:
            return

        playlist_id = playlist["id"]
        playlist_name = playlist["name"]

        reply = QMessageBox.question(
            self,
            "Delete Playlist",
            f"Are you sure you want to delete playlist '{playlist_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            from jdxi_editor.ui.programs.database import get_database

            db = get_database()
            if db.delete_playlist(playlist_id):
                log.message(f"✅ Deleted playlist: {playlist_name}")
                self.populate_table()
                self._notify_playlist_changed(playlist_id=playlist_id)
            else:
                log.error(f"❌ Failed to delete playlist: {playlist_name}")
                QMessageBox.warning(
                    self, "Error", f"Failed to delete playlist '{playlist_name}'."
                )

    def _on_playlist_item_changed(self, item: QTableWidgetItem) -> None:
        """
        Handle changes to playlist name or description.

        :param item: The table item that was changed
        """
        if not self.playlist_table:
            return

        row = item.row()
        col = item.column()

        # Only handle name (col 1) and description (col 2) changes
        if col not in [1, 2]:
            return

        # Get playlist data
        playlist = item.data(Qt.ItemDataRole.UserRole)
        if not playlist:
            return

        playlist_id = playlist["id"]
        new_value = item.text().strip()

        from jdxi_editor.ui.programs.database import get_database

        db = get_database()

        if col == 1:  # Name column
            if db.update_playlist(playlist_id, name=new_value):
                try:
                    log.message(
                        f"✅ Updated playlist {playlist_id} name to: {new_value}"
                    )
                    # Update stored playlist data
                    playlist["name"] = new_value
                    for c in range(4):
                        table_item = self.playlist_table.item(row, c)
                        if table_item:
                            table_item.setData(Qt.ItemDataRole.UserRole, playlist)
                    self._notify_playlist_changed()
                except Exception as ex:
                    log.error(f"Error {ex} occurred updating playlist")
            else:
                log.error(f"❌ Failed to update playlist {playlist_id} name")
                # Revert the change
                self.playlist_table.blockSignals(True)
                item.setText(playlist.get("name", ""))
                self.playlist_table.blockSignals(False)
        elif col == 2:  # Description column
            value = new_value or ""  # never pass None
            if db.update_playlist(playlist_id, description=value):
                log.message(f"Updated playlist {playlist_id} description")
                playlist["description"] = value
                for c in range(4):
                    table_item = self.playlist_table.item(row, c)
                    if table_item:
                        table_item.setData(Qt.ItemDataRole.UserRole, playlist)
                self._notify_playlist_changed()
            else:
                log.error(f"Failed to update playlist {playlist_id} description")
                self.playlist_table.blockSignals(True)
                item.setText(playlist.get("description", "") or "")
                self.playlist_table.blockSignals(False)

    def _on_playlist_selected(self, item: QTableWidgetItem) -> None:
        """
        Handle double-click on a playlist.
        Could open playlist editor or show playlist programs.

        :param item: The table item that was double-clicked
        """
        # For now, just log it. Could be extended to show playlist contents
        playlist = item.data(Qt.ItemDataRole.UserRole)
        if playlist:
            log.message(
                f"📋 Selected playlist: {playlist['name']} (ID: {playlist['id']})"
            )

    def _notify_playlist_changed(self, playlist_id: Optional[int] = None) -> None:
        """
        Notify that a playlist has changed (created, deleted, or updated).

        :param playlist_id: Optional playlist ID that was deleted (for clearing editor table)
        """
        self.playlist_changed.emit()
        if self.on_playlist_changed_callback:
            self.on_playlist_changed_callback()
