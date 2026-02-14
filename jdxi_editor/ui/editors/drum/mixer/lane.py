from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QSizePolicy, QVBoxLayout, QWidget


class MixerLane(QGroupBox):
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)

        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(6, 10, 6, 6)
        outer_layout.setSpacing(4)

        self._strip_container = QWidget(self)
        self._strip_layout = QHBoxLayout(self._strip_container)

        self._strip_layout.setContentsMargins(2, 2, 2, 2)
        self._strip_layout.setSpacing(3)

        outer_layout.addWidget(self._strip_container)

    # public API only
    def add_strip(self, widget: QWidget) -> None:
        self._strip_layout.addWidget(widget)
