"""
Trim dialog

Choose the range to keep when trimming a MIDI file or one of its tracks: a
start and end time, each shown as a bar and beat too, and each settable from
the playback position.
"""

from typing import Callable, Optional

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi

# Shortest range that can be kept
MIN_LENGTH_SECONDS = 0.01


class TrimDialog(QDialog):
    """Start and end (seconds) of the part of a MIDI file or track to keep."""

    def __init__(
        self,
        *,
        title: str,
        description: str,
        start: float,
        end: float,
        duration: float,
        bar_beat: Callable[[float], tuple[int, int]],
        playhead: Callable[[], float],
        parent: Optional[QWidget] = None,
    ):
        """
        :param title: Window title
        :param description: What the trim does, shown above the range
        :param start: Initial start (seconds)
        :param end: Initial end (seconds)
        :param duration: Length of the file (seconds)
        :param bar_beat: 1-based (bar, beat) at a time in seconds
        :param playhead: Playback position (seconds), snapped as the player snaps
        :param parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(380)
        JDXi.UI.Theme.apply_editor_style(self)
        self._bar_beat = bar_beat
        self._playhead = playhead

        description_label = QLabel(description)
        description_label.setWordWrap(True)

        self.start_spin, start_row, self.start_position = self._time_row(duration)
        self.end_spin, end_row, self.end_position = self._time_row(duration)
        self.start_spin.setValue(max(0.0, min(start, duration)))
        self.end_spin.setValue(max(0.0, min(end, duration)))

        form = QFormLayout()
        form.addRow("Start", start_row)
        form.addRow("End", end_row)

        self.length_label = QLabel()

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.ok_button = buttons.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setText("Trim")

        layout = QVBoxLayout(self)
        layout.addWidget(description_label)
        layout.addLayout(form)
        layout.addWidget(self.length_label)
        layout.addWidget(buttons)

        self.start_spin.valueChanged.connect(self._update)
        self.end_spin.valueChanged.connect(self._update)
        self._update()

    def _time_row(
        self, duration: float
    ) -> tuple[QDoubleSpinBox, QHBoxLayout, QLabel]:
        """Seconds spin box, its bar:beat and a button to take the playhead."""
        spin = QDoubleSpinBox()
        spin.setRange(0.0, max(duration, 0.0))
        spin.setDecimals(2)
        spin.setSingleStep(0.1)
        spin.setSuffix(" s")
        position = QLabel()
        playhead = QPushButton("Playhead")
        playhead.setToolTip("Use the playback position")
        playhead.clicked.connect(lambda: spin.setValue(self._playhead()))
        row = QHBoxLayout()
        row.addWidget(spin)
        row.addWidget(position)
        row.addWidget(playhead)
        return spin, row, position

    def _update(self, *_args) -> None:
        start, end = self.range_seconds()
        for spin, label in (
            (self.start_spin, self.start_position),
            (self.end_spin, self.end_position),
        ):
            bar, beat = self._bar_beat(spin.value())
            label.setText(f"bar {bar}.{beat}")
        valid = end - start >= MIN_LENGTH_SECONDS
        self.ok_button.setEnabled(valid)
        self.length_label.setText(
            f"Keeps {end - start:.2f} s" if valid else "End must be after Start"
        )

    def range_seconds(self) -> tuple[float, float]:
        """(start, end) in seconds."""
        return self.start_spin.value(), self.end_spin.value()
