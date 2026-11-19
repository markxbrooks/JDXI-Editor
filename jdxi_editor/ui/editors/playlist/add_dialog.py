"""
Add Programs dialog: tick several programs, filtered by a search box, and add
them to a playlist in one go.

Programs are added in the order they were ticked, so a set list can be built
in one pass. Ticks survive filtering: search for one band, tick, search for
another, tick, then Add.
"""

from typing import Iterable, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

PROGRAM_ID_ROLE = Qt.ItemDataRole.UserRole


class AddProgramsDialog(QDialog):
    """Pick one or more programs to add to a playlist."""

    def __init__(
        self,
        playlist_name: str,
        programs: Iterable,
        used: Optional[dict] = None,
        parent: Optional[QWidget] = None,
    ):
        """
        :param playlist_name: shown in the prompt
        :param programs: JDXiProgram-like objects (with .id and .name)
        :param used: program ID -> how often it is already in the playlist
        """
        super().__init__(parent)
        self.setWindowTitle("Add Programs to Playlist")
        self.resize(460, 520)
        used = used or {}
        self._ticked: list[str] = []  # program IDs in the order ticked

        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel(
                f"Tick the programs to add to '{playlist_name}'.\n"
                "They are added in the order you tick them."
            )
        )
        self.search = QLineEdit(self)
        self.search.setPlaceholderText("Search programs...")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self._filter)
        layout.addWidget(self.search)

        self.list = QListWidget(self)
        for program in programs:
            text = f"{program.id} - {program.name or ''}"
            if used.get(program.id):
                text += f"  (in playlist ×{used[program.id]})"
            item = QListWidgetItem(text)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            item.setData(PROGRAM_ID_ROLE, program.id)
            self.list.addItem(item)
        self.list.itemChanged.connect(self._on_item_changed)
        # Double-click or Space ticks a row as well as its checkbox
        self.list.itemDoubleClicked.connect(self._toggle)
        layout.addWidget(self.list)

        self.count_label = QLabel(self)
        layout.addWidget(self.count_label)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        self._update_count()
        self.search.setFocus()

    # --- Public -------------------------------------------------------------

    def selected_program_ids(self) -> list[str]:
        """Ticked program IDs, in the order they were ticked."""
        return list(self._ticked)

    def set_checked(self, program_id: str, checked: bool = True) -> None:
        """Tick or untick `program_id` (as clicking its checkbox would)."""
        for row in range(self.list.count()):
            item = self.list.item(row)
            if item.data(PROGRAM_ID_ROLE) == program_id:
                item.setCheckState(
                    Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
                )
                return

    def visible_program_ids(self) -> list[str]:
        """Program IDs the search currently shows."""
        return [
            self.list.item(r).data(PROGRAM_ID_ROLE)
            for r in range(self.list.count())
            if not self.list.item(r).isHidden()
        ]

    # --- Internals ----------------------------------------------------------

    def _filter(self, text: str) -> None:
        words = text.lower().split()
        for row in range(self.list.count()):
            item = self.list.item(row)
            haystack = item.text().lower()
            item.setHidden(not all(w in haystack for w in words))

    def _toggle(self, item: QListWidgetItem) -> None:
        checked = item.checkState() == Qt.CheckState.Checked
        item.setCheckState(Qt.CheckState.Unchecked if checked else Qt.CheckState.Checked)

    def _on_item_changed(self, item: QListWidgetItem) -> None:
        program_id = item.data(PROGRAM_ID_ROLE)
        if item.checkState() == Qt.CheckState.Checked:
            if program_id not in self._ticked:
                self._ticked.append(program_id)
        elif program_id in self._ticked:
            self._ticked.remove(program_id)
        self._update_count()

    def _update_count(self) -> None:
        n = len(self._ticked)
        self.count_label.setText(
            "Nothing ticked yet" if n == 0 else f"{n} program{'s' if n != 1 else ''} ticked"
        )
        ok = self.buttons.button(QDialogButtonBox.StandardButton.Ok)
        ok.setText("Add" if n <= 1 else f"Add {n}")
        ok.setEnabled(n > 0)
