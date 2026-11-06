"""
Manager-style Edit Buffer operations: Read from JD-Xi (+ optional status).
"""

from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

from jdxi_editor.ui.editors.helpers.widgets import create_round_button_with_label


def create_read_from_jdxi_row(
    on_read: Callable[[], None],
    *,
    status_label: Optional[QLabel] = None,
) -> tuple[QWidget, QPushButton, QLabel]:
    """
    Build a compact row with a Read from JD-Xi button and status label.

    :param on_read: Click handler
    :param status_label: Optional existing label; created if omitted
    :return: (row_widget, button, status_label)
    """
    row = QHBoxLayout()
    read, button = create_round_button_with_label(
        "Read from JD-Xi",
        "mdi.download",
        on_read,
        "Request current parameters from the synthesizer (RQ1)",
    )
    label = status_label or QLabel("")
    label.setWordWrap(True)
    row.addWidget(read)
    row.addWidget(label, stretch=1)
    container = QWidget()
    container.setLayout(row)
    return container, button, label


def create_preset_nav_row(
    on_prev: Callable[[], None],
    on_next: Callable[[], None],
    on_load: Callable[[], None],
) -> tuple[QWidget, QPushButton, QPushButton, QPushButton]:
    """Previous / Next / Load controls for factory preset auditioning."""
    row = QHBoxLayout()
    prev, prev_btn = create_round_button_with_label(
        "Previous", "mdi.chevron-left", on_prev, "Previous preset"
    )
    load, load_btn = create_round_button_with_label(
        "Load",
        "mdi.check",
        on_load,
        "Load selected factory preset and read parameters",
    )
    nxt, next_btn = create_round_button_with_label(
        "Next", "mdi.chevron-right", on_next, "Next preset"
    )
    row.addStretch()
    row.addWidget(prev)
    row.addWidget(load)
    row.addWidget(nxt)
    row.addStretch()
    container = QWidget()
    container.setLayout(row)
    return container, prev_btn, next_btn, load_btn


def create_part_syx_row(
    on_import: Callable[[], None],
    on_export: Callable[[], None],
) -> QWidget:
    """Import / Export per-part .syx librarian buttons."""
    row = QHBoxLayout()
    import_row, _ = create_round_button_with_label(
        "Import .syx",
        "mdi.file-import-outline",
        on_import,
        "Load a single-part SysEx file into this editor",
    )
    export_row, _ = create_round_button_with_label(
        "Export .syx",
        "mdi.file-export-outline",
        on_export,
        "Save this part as a SysEx file",
    )
    row.addWidget(import_row)
    row.addWidget(export_row)
    row.addStretch()
    container = QWidget()
    container.setLayout(row)
    return container
