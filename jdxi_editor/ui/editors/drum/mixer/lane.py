from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class MixerLane(QGroupBox):
    def __init__(self, title: str, parent=None, columns: int = 0):
        """
        :param title: lane title (drum family)
        :param columns: 0 for one row of strips, else strips wrap into a grid
            this many columns wide (the side lanes, which stand as tall as the kit)
        """
        super().__init__(title, parent)

        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self._columns = columns
        self._count = 0

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(6, 10, 6, 6)
        outer_layout.setSpacing(4)

        self._strip_container = QWidget(self)
        self._strip_layout = QGridLayout() if columns else QHBoxLayout()
        self._strip_container.setLayout(self._strip_layout)

        self._strip_layout.setContentsMargins(2, 2, 2, 2)
        self._strip_layout.setSpacing(3)

        outer_layout.addWidget(self._strip_container)
        if columns:
            outer_layout.addStretch()

    # public API only
    def add_strip(self, widget: QWidget) -> None:
        if self._columns:
            row, column = divmod(self._count, self._columns)
            self._strip_layout.addWidget(widget, row, column)
        else:
            self._strip_layout.addWidget(widget)
        self._count += 1
