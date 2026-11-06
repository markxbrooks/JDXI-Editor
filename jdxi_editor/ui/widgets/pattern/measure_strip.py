"""
Measure Strip

A horizontal row of square tiles, one per measure, above the step grid. Each
tile shows the measure number and a miniature of its 4 × 16 steps in the part
colours, so it is visible at a glance which measures hold notes. The selected
measure has a red outline; the measure playing has a light bar under it. The
last tile (+) adds a measure.

    [ 1 ▪▫▪▫ ][ 2 ▫▫▫▫ ][ 3 ▪▪▫▫ ] … [ + ]
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import QHBoxLayout, QScrollArea, QSizePolicy, QWidget

from jdxi_editor.ui.style.midi_player import PatternEditorStyle as Style

TILE_WIDTH = 60
TILE_HEIGHT = 48
TILE_SPACING = 6
CELL_GAP = 1  # px between the miniature's steps and rows


class MeasureTile(QWidget):
    """One measure: number and miniature; click to select."""

    clicked = Signal(int)

    def __init__(self, index: int, measure_widget, parent: Optional[QWidget] = None):
        """
        :param index: measure index (0-based; shown from 1)
        :param measure_widget: PatternMeasureWidget whose buttons are drawn
        """
        super().__init__(parent)
        self.index = index
        self.measure_widget = measure_widget
        self.selected = False
        self.playing = False
        self.setFixedSize(TILE_WIDTH, TILE_HEIGHT)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(f"Measure {index + 1}")
        # Redraw whenever a step of this measure changes
        for row in measure_widget.buttons:
            for button in row:
                button.toggled.connect(self.update)

    def set_selected(self, selected: bool) -> None:
        if self.selected != selected:
            self.selected = selected
            self.update()

    def set_playing(self, playing: bool) -> None:
        if self.playing != playing:
            self.playing = playing
            self.update()

    def active_steps(self) -> int:
        return sum(b.isChecked() for row in self.measure_widget.buttons for b in row)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.index)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        frame = QRectF(0.5, 0.5, self.width() - 1, self.height() - 5)
        painter.setBrush(QColor(Style.SURFACE_ALT if self.selected else Style.SURFACE))
        border = Style.ACCENT if self.selected else Style.BORDER
        painter.setPen(QPen(QColor(border), 2 if self.selected else 1))
        painter.drawRoundedRect(frame, 4, 4)

        painter.setPen(QColor(Style.TEXT if self.selected else Style.TEXT_SECONDARY))
        font = painter.font()
        font.setPixelSize(10)
        painter.setFont(font)
        painter.drawText(QRectF(5, 2, self.width() - 10, 12), Qt.AlignmentFlag.AlignLeft, str(self.index + 1))

        # Miniature: 4 rows of 16 steps under the number
        buttons = self.measure_widget.buttons
        steps = max((len(row) for row in buttons), default=16) or 16
        left, top = 5.0, 16.0
        width = self.width() - 10
        height = self.height() - 5 - top - 4
        cell_w = (width - CELL_GAP * (steps - 1)) / steps
        cell_h = (height - CELL_GAP * (len(buttons) - 1)) / max(1, len(buttons))
        painter.setPen(Qt.PenStyle.NoPen)
        for row, row_buttons in enumerate(buttons):
            on = QColor(Style.PART_COLORS.get(row, Style.STEP_ON))
            for step, button in enumerate(row_buttons):
                if button.isChecked():
                    color = on.darker(260) if button.property("muted") else on
                else:
                    color = QColor(Style.BACKGROUND)
                painter.setBrush(color)
                x = left + step * (cell_w + CELL_GAP)
                y = top + row * (cell_h + CELL_GAP)
                painter.drawRect(QRectF(x, y, cell_w, cell_h))

        if self.playing:
            painter.setBrush(QColor(Style.PLAYHEAD))
            painter.drawRoundedRect(QRectF(4, self.height() - 3, self.width() - 8, 3), 1.5, 1.5)
        painter.end()


class AddMeasureTile(QWidget):
    """The + tile at the end of the strip."""

    clicked = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setFixedSize(TILE_WIDTH, TILE_HEIGHT)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Add a measure")

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(Style.BORDER_HOVER), 1, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(QRectF(0.5, 0.5, self.width() - 1, self.height() - 5), 4, 4)
        painter.setPen(QColor(Style.TEXT_SECONDARY))
        font = painter.font()
        font.setPixelSize(20)
        painter.setFont(font)
        painter.drawText(QRectF(0, 0, self.width(), self.height() - 4), Qt.AlignmentFlag.AlignCenter, "+")
        painter.end()


class MeasureStrip(QScrollArea):
    """Horizontally scrolling row of MeasureTiles followed by the + tile."""

    measure_clicked = Signal(int)
    add_requested = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.tiles: list[MeasureTile] = []
        self._current: Optional[int] = None
        self._playing: Optional[int] = None

        self._content = QWidget()
        self._layout = QHBoxLayout(self._content)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(TILE_SPACING)
        self.add_tile = AddMeasureTile()
        self.add_tile.clicked.connect(self.add_requested)
        self._layout.addWidget(self.add_tile)
        self._layout.addStretch()

        self.setWidget(self._content)
        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.Shape.NoFrame)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setFixedHeight(TILE_HEIGHT + 14)  # room for the scrollbar
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def sizeHint(self) -> QSize:
        return QSize(TILE_WIDTH * 8, TILE_HEIGHT + 14)

    # --- Tiles -------------------------------------------------------------

    def count(self) -> int:
        return len(self.tiles)

    def add_measure(self, measure_widget) -> MeasureTile:
        tile = MeasureTile(len(self.tiles), measure_widget)
        tile.clicked.connect(self.measure_clicked)
        self._layout.insertWidget(len(self.tiles), tile)
        self.tiles.append(tile)
        return tile

    def remove_measure(self, index: int) -> None:
        if not 0 <= index < len(self.tiles):
            return
        self._discard(self.tiles.pop(index))
        for i, remaining in enumerate(self.tiles):  # renumber
            remaining.index = i
            remaining.setToolTip(f"Measure {i + 1}")
            remaining.update()
        if self._current is not None and self._current >= len(self.tiles):
            self.set_current(len(self.tiles) - 1 if self.tiles else None)

    def clear(self) -> None:
        while self.tiles:
            self._discard(self.tiles.pop())
        self._current = None
        self._playing = None

    def _discard(self, tile: MeasureTile) -> None:
        """Remove a tile now (deleteLater alone leaves it drawn until the next event loop pass)."""
        self._layout.removeWidget(tile)
        tile.hide()
        tile.setParent(None)
        tile.deleteLater()

    def refresh(self) -> None:
        """Redraw every tile (e.g. after mutes change)."""
        for tile in self.tiles:
            tile.update()

    # --- Selection and playback ---------------------------------------------

    def current(self) -> Optional[int]:
        return self._current

    def set_current(self, index: Optional[int]) -> None:
        """Outline the selected measure and scroll it into view."""
        self._current = index
        for i, tile in enumerate(self.tiles):
            tile.set_selected(i == index)
        if index is not None and 0 <= index < len(self.tiles):
            self.ensureWidgetVisible(self.tiles[index], TILE_WIDTH, 0)

    def set_playing(self, index: Optional[int]) -> None:
        """Mark the measure playing (None: not playing)."""
        self._playing = index
        for i, tile in enumerate(self.tiles):
            tile.set_playing(i == index)
        if index is not None and 0 <= index < len(self.tiles):
            self.ensureWidgetVisible(self.tiles[index], TILE_WIDTH, 0)
