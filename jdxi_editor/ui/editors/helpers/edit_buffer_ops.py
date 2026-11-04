"""
Manager-style Edit Buffer operations: Read from JD-Xi (+ optional status).
"""

from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget


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
    button = QPushButton("Read from JD-Xi")
    button.setToolTip("Request current parameters from the synthesizer (RQ1)")
    button.clicked.connect(on_read)
    label = status_label or QLabel("")
    label.setWordWrap(True)
    row.addWidget(button)
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
    prev_btn = QPushButton("◀")
    prev_btn.setToolTip("Previous preset")
    prev_btn.clicked.connect(on_prev)
    next_btn = QPushButton("▶")
    next_btn.setToolTip("Next preset")
    next_btn.clicked.connect(on_next)
    load_btn = QPushButton("Load")
    load_btn.setToolTip("Load selected factory preset and read parameters")
    load_btn.clicked.connect(on_load)
    row.addStretch()
    row.addWidget(prev_btn)
    row.addWidget(load_btn)
    row.addWidget(next_btn)
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
    import_btn = QPushButton("Import .syx")
    import_btn.setToolTip("Load a single-part SysEx file into this editor")
    import_btn.clicked.connect(on_import)
    export_btn = QPushButton("Export .syx")
    export_btn.setToolTip("Save this part as a SysEx file")
    export_btn.clicked.connect(on_export)
    row.addWidget(import_btn)
    row.addWidget(export_btn)
    row.addStretch()
    container = QWidget()
    container.setLayout(row)
    return container
