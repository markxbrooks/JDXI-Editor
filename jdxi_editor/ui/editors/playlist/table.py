"""
Playlist Widget Module

This module defines the `PlaylistWidget` class, a widget for managing
playlists in a sortable, editable table with database integration.

Classes:
    PlaylistWidget(QWidget)
        A widget for displaying and managing playlists.
"""

from typing import Any, Callable, Optional

from decologr import Decologr as log
from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMenu,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
)

from jdxi_editor.ui.common import JDXi, QVBoxLayout, QWidget
from jdxi_editor.ui.editors.helpers.widgets import create_jdxi_button, create_jdxi_row
from jdxi_editor.ui.style import JDXiUIDimensions, JDXiUIStyle
from jdxi_editor.ui.widgets.editor.helper import transfer_layout_items


class PlaylistTable(QWidget):
    """Widget for managing playlists in a database table."""

    # Signal emitted when a playlist is created, deleted, or updated
    playlist_changed = Signal()
    # The selected playlist changed (its ID, or None)
    playlist_selected = Signal(object)

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
        self.rename_playlist_button: Optional[QPushButton] = None
        self.duplicate_playlist_button: Optional[QPushButton] = None
        self.refresh_playlist_button: Optional[QPushButton] = None
        self.playlist_table: Optional[QTableWidget] = None

        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the playlist UI."""
        layout = QVBoxLayout(self)

        # Add icon row at the top (transfer items to avoid "already has a parent" errors)
        icon_row_container = QHBoxLayout()
        icon_row = JDXi.UI.Icon.create_generic_musical_icon_row()

        transfer_layout_items(icon_row, icon_row_container)
        layout.addLayout(icon_row_container)

        # Button layout for create/delete/refresh (round style + icon + label)
        button_layout = QHBoxLayout()
        self._add_round_action_button(
            JDXi.UI.Icon.PLUS_CIRCLE,
            "New Playlist",
            self.create_new_playlist,
            button_layout,
            name="create_playlist",
        )
        self._add_round_action_button(
            JDXi.UI.Icon.PENCIL,
            "Rename",
            self.rename_selected_playlist,
            button_layout,
            name="rename_playlist",
        )
        self._add_round_action_button(
            JDXi.UI.Icon.COPY,
            "Duplicate",
            self.duplicate_selected_playlist,
            button_layout,
            name="duplicate_playlist",
        )
        self._add_round_action_button(
            JDXi.UI.Icon.TRASH_FILL,
            "Delete Playlist",
            self.delete_selected_playlist,
            button_layout,
            name="delete_playlist",
        )
        self._add_round_action_button(
            JDXi.UI.Icon.REFRESH,
            "Refresh Playlist",
            self.refresh_playlists,
            button_layout,
            name="refresh_playlist",
        )
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

        # One playlist at a time: selecting it opens it beside the list
        self.playlist_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.playlist_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.playlist_table.itemSelectionChanged.connect(
            lambda: self.playlist_selected.emit(self.selected_playlist_id())
        )

        # Connect item changed to save edits
        self.playlist_table.itemChanged.connect(self._on_playlist_item_changed)

        # Connect double-click to edit playlist
        self.playlist_table.itemDoubleClicked.connect(self._on_playlist_selected)

        # Right-click a playlist (or the empty space below) for its actions
        self.playlist_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.playlist_table.customContextMenuRequested.connect(self._show_playlist_menu)

        layout.addWidget(self.playlist_table)

        # Populate table (with error handling)
        try:
            log.message("🔨Calling populate_table()...", scope="PlaylistWidget")
            self.populate_table()
            log.message(
                "✅ Playlist table populated successfully", scope="PlaylistWidget"
            )
        except Exception as e:
            log.error(
                f"❌ Error populating playlist table: {e}", scope="PlaylistWidget"
            )
            import traceback

            log.error(traceback.format_exc())

    def _add_round_action_button(
        self,
        icon_enum: Any,
        text: str,
        slot: Any,
        layout: QHBoxLayout,
        *,
        name: Optional[str] = None,
        checkable: bool = False,
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

    def _get_table_style(self) -> str:
        """
        Get custom styling for tables with rounded corners and charcoal embossed cells.

        :return: str CSS style string
        """
        return JDXi.UI.Style.DATABASE_TABLE_STYLE

    def populate_table(self) -> None:
        """Populate the playlist table from SQLite database."""
        if not self.playlist_table:
            log.warning(
                scope="PlaylistWidget", message="Playlist table not initialized"
            )
            return

        try:
            from jdxi_editor.ui.programs.database import get_database

            # Get all playlists from database
            db = get_database()
            all_playlists = db.get_all_playlists()
        except Exception as e:
            log.error(
                scope="PlaylistWidget",
                message=f"Error getting playlists from database: {e}",
            )
            import traceback

            log.error(traceback.format_exc())
            all_playlists = []

        keep_id = self.selected_playlist_id()
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
        if keep_id is not None:
            self.select_playlist_id(keep_id)

        log.message(
            f"✅ Populated playlist table with {len(all_playlists)} playlists",
            scope="PlaylistWidget",
        )

    def create_new_playlist(self) -> None:
        """Create a new playlist."""
        from PySide6.QtWidgets import QInputDialog

        from jdxi_editor.ui.programs.database import get_database

        name, ok = QInputDialog.getText(self, "New Playlist", "Enter playlist name:")

        if ok and name.strip():
            db = get_database()
            playlist_id = db.create_playlist(name.strip())
            if playlist_id:
                log.message(f"✅ Created playlist: {name}", scope="PlaylistWidget")
                self.populate_table()
                self._notify_playlist_changed()
            else:
                log.error(
                    f"❌Failed to create playlist: {name}", scope="PlaylistWidget"
                )
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Failed to create playlist '{name}'. It may already exist.",
                )

    # --- Selection, rename, duplicate -----------------------------------------

    def selected_playlist(self) -> Optional[dict]:
        if not self.playlist_table:
            return None
        rows = self.playlist_table.selectionModel().selectedRows()
        item = self.playlist_table.item(rows[0].row(), 0) if rows else None
        return item.data(Qt.ItemDataRole.UserRole) if item is not None else None

    def selected_playlist_id(self) -> Optional[int]:
        playlist = self.selected_playlist()
        return playlist["id"] if playlist else None

    def select_playlist_id(self, playlist_id: Optional[int]) -> None:
        """Select the row of `playlist_id` (None clears the selection)."""
        if not self.playlist_table:
            return
        if playlist_id is None:
            self.playlist_table.clearSelection()
            return
        for row in range(self.playlist_table.rowCount()):
            item = self.playlist_table.item(row, 0)
            playlist = item.data(Qt.ItemDataRole.UserRole) if item else None
            if playlist and playlist["id"] == playlist_id:
                self.playlist_table.selectRow(row)
                return

    def rename_selected_playlist(self) -> None:
        """Rename the selected playlist (the name cell can still be edited in place)."""
        from PySide6.QtWidgets import QInputDialog

        from jdxi_editor.ui.programs.database import get_database

        playlist = self.selected_playlist()
        if not playlist:
            QMessageBox.information(self, "No Selection", "Please select a playlist to rename.")
            return
        name, ok = QInputDialog.getText(self, "Rename Playlist", "New name:", text=playlist["name"] or "")
        name = name.strip()
        if not ok or not name or name == playlist["name"]:
            return
        if get_database().update_playlist(playlist["id"], name=name):
            self.populate_table()
            self.select_playlist_id(playlist["id"])
            self._notify_playlist_changed()
        else:
            QMessageBox.warning(self, "Error", f"Could not rename the playlist to '{name}'. The name may already be used.")

    def duplicate_selected_playlist(self) -> None:
        """Copy the selected playlist, tracks included, under a new name."""
        from PySide6.QtWidgets import QInputDialog

        from jdxi_editor.ui.programs.database import get_database

        playlist = self.selected_playlist()
        if not playlist:
            QMessageBox.information(self, "No Selection", "Please select a playlist to duplicate.")
            return
        name, ok = QInputDialog.getText(
            self, "Duplicate Playlist", "Name of the copy:", text=f"{playlist['name']} (copy)"
        )
        name = name.strip()
        if not ok or not name:
            return
        new_id = get_database().duplicate_playlist(playlist["id"], name)
        if new_id:
            self.populate_table()
            self._notify_playlist_changed()
            self.select_playlist_id(new_id)
        else:
            QMessageBox.warning(self, "Error", f"Could not create '{name}'. The name may already be used.")

    def _show_playlist_menu(self, pos: QPoint) -> None:
        row = self.playlist_table.indexAt(pos).row()
        if row >= 0:
            self.playlist_table.selectRow(row)
        self.build_playlist_menu(on_playlist=row >= 0).exec(
            self.playlist_table.viewport().mapToGlobal(pos)
        )

    def build_playlist_menu(self, on_playlist: bool = True) -> QMenu:
        """The right-click menu: actions on the selected playlist (when the
        click was on one), and New Playlist."""
        menu = QMenu(self)
        has_one = on_playlist and self.selected_playlist_id() is not None

        def add(text, icon, slot, enabled=True):
            action = menu.addAction(JDXi.UI.Icon.get_icon(icon, color=JDXi.UI.Style.FOREGROUND), text)
            action.setEnabled(enabled)
            action.triggered.connect(slot)

        add("Rename…", JDXi.UI.Icon.PENCIL, self.rename_selected_playlist, has_one)
        add("Edit Description…", JDXi.UI.Icon.PENCIL, self.edit_selected_description, has_one)
        add("Duplicate…", JDXi.UI.Icon.COPY, self.duplicate_selected_playlist, has_one)
        add("Delete…", JDXi.UI.Icon.TRASH_FILL, self.delete_selected_playlist, has_one)
        menu.addSeparator()
        add("New Playlist…", JDXi.UI.Icon.PLUS_CIRCLE, self.create_new_playlist)
        return menu

    def edit_selected_description(self) -> None:
        """Change the selected playlist's description."""
        from PySide6.QtWidgets import QInputDialog

        playlist = self.selected_playlist()
        if not playlist:
            return
        text, ok = QInputDialog.getText(
            self, "Edit Description", f"Description of '{playlist['name']}':",
            text=playlist.get("description") or "",
        )
        if not ok:
            return
        from jdxi_editor.ui.programs.database import get_database

        if get_database().update_playlist(playlist["id"], description=text.strip()):
            self.populate_table()  # keeps the selection
            self._notify_playlist_changed()
        else:
            QMessageBox.warning(self, "Error", "Failed to save the description.")

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
                log.message(
                    f"✅ Deleted playlist: {playlist_name}", scope="PlaylistWidget"
                )
                self.populate_table()
                self._notify_playlist_changed(playlist_id=playlist_id)
            else:
                log.error(
                    f"❌ Failed to delete playlist: {playlist_name}",
                    scope="PlaylistWidget",
                )
                QMessageBox.warning(
                    self,
                    "Error",
                    scope="PlaylistWidget",
                    message=f"Failed to delete playlist '{playlist_name}'.",
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
                        f"✅ Updated playlist {playlist_id} name to: {new_value}",
                        scope="PlaylistWidget",
                    )
                    # Update stored playlist data
                    playlist["name"] = new_value
                    for c in range(4):
                        table_item = self.playlist_table.item(row, c)
                        if table_item:
                            table_item.setData(Qt.ItemDataRole.UserRole, playlist)
                    self._notify_playlist_changed()
                except Exception as ex:
                    log.error(
                        scope="PlaylistWidget",
                        message=f"Error {ex} occurred updating playlist",
                    )
            else:
                log.error(
                    f"❌Failed to update playlist {playlist_id} name",
                    scope="PlaylistWidget",
                )
                # Revert the change
                self.playlist_table.blockSignals(True)
                item.setText(playlist.get("name", ""))
                self.playlist_table.blockSignals(False)
        elif col == 2:  # Description column
            value = new_value or ""  # never pass None
            if db.update_playlist(playlist_id, description=value):
                log.message(
                    scope="PlaylistWidget",
                    message=f"Updated playlist {playlist_id} description",
                )
                playlist["description"] = value
                for c in range(4):
                    table_item = self.playlist_table.item(row, c)
                    if table_item:
                        table_item.setData(Qt.ItemDataRole.UserRole, playlist)
                self._notify_playlist_changed()
            else:
                log.error(
                    scope="PlaylistWidget",
                    message=f"Failed to update playlist {playlist_id} description",
                )
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
                f"📋 Selected playlist: {playlist['name']} (ID: {playlist['id']})",
                scope="PlaylistWidget",
            )

    def _notify_playlist_changed(self, playlist_id: Optional[int] = None) -> None:
        """
        Notify that a playlist has changed (created, deleted, or updated).

        :param playlist_id: Optional playlist ID that was deleted (for clearing editor table)
        """
        self.playlist_changed.emit()
        if self.on_playlist_changed_callback:
            self.on_playlist_changed_callback()
