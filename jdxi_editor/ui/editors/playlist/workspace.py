"""
Playlist workspace: the playlists on the left, the selected playlist's tracks
on the right, in one tab.

Selecting a playlist in the list opens it in the editor straight away; picking
one in the editor's search box selects it in the list. Track counts in the list
follow additions and removals in the editor.
"""

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QSplitter, QWidget

from jdxi_editor.ui.editors.playlist.editor import PlaylistEditor
from jdxi_editor.ui.editors.playlist.table import PlaylistTable


class PlaylistWorkspace(QWidget):
    """The playlist list and the playlist editor side by side."""

    def __init__(
        self,
        playlists: PlaylistTable,
        editor: PlaylistEditor,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.playlists = playlists
        self.editor = editor
        self._syncing = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.splitter.addWidget(playlists)
        self.splitter.addWidget(editor)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 3)
        self.splitter.setChildrenCollapsible(False)
        layout.addWidget(self.splitter)

        # The ID column is for the database, not for choosing a playlist
        if playlists.playlist_table is not None:
            playlists.playlist_table.setColumnHidden(0, True)

        playlists.playlist_selected.connect(self._on_list_selected)
        editor.playlist_selected.connect(self._on_editor_selected)
        editor.playlist_programs_changed.connect(self._on_tracks_changed)

    def _on_list_selected(self, playlist_id: Optional[int]) -> None:
        """A playlist was selected in the list: edit it."""
        if self._syncing or playlist_id is None:
            return
        if playlist_id == self.editor._selected_playlist_id():
            return
        self._syncing = True
        try:
            self.editor.select_playlist(playlist_id)
        finally:
            self._syncing = False

    def _on_editor_selected(self, playlist_id: Optional[int]) -> None:
        """A playlist was picked in the editor's search box: select it in the list."""
        if self._syncing or playlist_id == self.playlists.selected_playlist_id():
            return
        self._syncing = True
        try:
            self.playlists.select_playlist_id(playlist_id)
        finally:
            self._syncing = False

    def _on_tracks_changed(self) -> None:
        """Tracks were added or removed: refresh the counts in the list."""
        self._syncing = True
        try:
            self.playlists.populate_table()  # keeps the selected row
        finally:
            self._syncing = False
