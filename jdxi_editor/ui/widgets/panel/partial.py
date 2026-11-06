"""
Partial Panel

The three partials' ON / SELECT buttons, laid out like a section of the JD-Xi
panel: a small uppercase label over a deep red rule, then the lit buttons.

    PARTIAL 1        PARTIAL 2        PARTIAL 3
    ─────────        ─────────        ─────────
    [ON][SELECT]     [ON][SELECT]     [ON][SELECT]
"""

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from jdxi_editor.midi.data.digital.partial import DigitalPartial
from jdxi_editor.ui.style.editor_style import AppEditorStyle as Style
from jdxi_editor.ui.widgets.switch.partial import PartialSwitch


class PartialsPanel(QWidget):
    """Panel containing all partial switches"""

    def __init__(self, parent: QWidget = None):
        """Initialize the PartialsPanel.

        :param parent: QWidget
        """
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.setSpacing(3)
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)

        partial_layout = QHBoxLayout()
        partial_layout.setSpacing(28)
        partial_layout.addStretch()

        # Create switches for each partial (not structure types)
        self.switches = {}
        for partial in DigitalPartial.get_partials():  # Only get actual partials
            section = QVBoxLayout()
            section.setSpacing(4)
            label = QLabel(f"PARTIAL {partial.value}")
            label.setStyleSheet(
                f"color: {Style.TEXT_SECONDARY}; font-size: 10px; font-weight: 600;"
                " letter-spacing: 1px; background: transparent;"
            )
            section.addWidget(label)
            rule = QFrame()
            rule.setFixedHeight(2)
            rule.setStyleSheet(f"background-color: {Style.METALLIC_RED}; border: none;")
            section.addWidget(rule)
            switch = PartialSwitch(partial)
            self.switches[partial] = switch
            section.addWidget(switch)
            partial_layout.addLayout(section)

        layout.addLayout(partial_layout)
        partial_layout.addStretch()
