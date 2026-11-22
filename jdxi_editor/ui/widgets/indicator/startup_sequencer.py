"""
Startup sequencer

A row of 16 sequencer squares, styled like the Instrument window's, that light
up one after another as the application starts. Used on the splash screen in
place of a progress bar; it takes the same setValue(0-100).

Example:
    >>> sequencer = StartupSequencer()
    >>> sequencer.setValue(50)  # squares 1-8 lit
"""

import math
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.ui.style.factory import generate_sequencer_button_style

STEP_COUNT = 16
STEP_SPACING = 3  # as the Instrument window's sequencer row


class StartupSequencer(QFrame):
    """16 sequencer squares lit in proportion to the startup progress (0-100)."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("StartupSequencer")
        self._value = 0
        self.steps: list[QPushButton] = []

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(STEP_SPACING)
        layout.addStretch()
        size = JDXi.UI.Dimensions.SEQUENCER.SQUARE_SIZE
        for _ in range(STEP_COUNT):
            step = QPushButton()
            step.setFixedSize(size, size)
            step.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            # A display, not buttons: no hover or press styling
            step.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            step.setProperty("active", None)
            self.steps.append(step)
            layout.addWidget(step)
        layout.addStretch()
        self._show()

    def value(self) -> int:
        return self._value

    def setValue(self, value: int) -> None:
        """Startup progress (0-100): light that share of the squares."""
        self._value = min(max(int(value), 0), 100)
        self._show()

    @property
    def lit_steps(self) -> int:
        """Number of squares lit (a square lights as soon as progress reaches it)."""
        return math.ceil(self._value * STEP_COUNT / 100)

    def _show(self) -> None:
        lit = self.lit_steps
        for index, step in enumerate(self.steps):
            active = index < lit
            if step.property("active") == active:
                continue
            step.setProperty("active", active)
            step.setStyleSheet(generate_sequencer_button_style(active))
        self.repaint()  # startup blocks the event loop between updates
