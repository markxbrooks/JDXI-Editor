"""Generic Qt dialog helpers for PicoUI."""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QFileDialog, QMessageBox, QWidget


class QtDialogService:
    """Thin wrapper around QMessageBox / QFileDialog for presenters."""

    def __init__(self, parent: QWidget | None = None) -> None:
        self.parent = parent

    def warning(self, title: str, message: str) -> None:
        QMessageBox.warning(self.parent, title, message)

    def error(self, title: str, message: str) -> None:
        QMessageBox.critical(self.parent, title, message)

    def info(self, title: str, message: str) -> None:
        QMessageBox.information(self.parent, title, message)

    def ask_save_filename(
        self,
        *,
        title: str = "Save File",
        default_name: str = "",
        filter: str = "All Files (*)",
        options: Any | None = None,
    ) -> str | None:
        kwargs: dict[str, Any] = {}
        if options is not None:
            kwargs["options"] = options
        filename, _ = QFileDialog.getSaveFileName(
            self.parent,
            title,
            default_name,
            filter,
            **kwargs,
        )
        return filename or None
