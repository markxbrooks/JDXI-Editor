from PySide6.QtCore import Qt
from PySide6.QtWidgets import QButtonGroup, QLabel, QVBoxLayout, QWidget

from jdxi_editor.jdxi.synth.type import JDXiSynth
from jdxi_editor.ui.style import JDXiStyle
from jdxi_editor.ui.style.dimensions import JDXiDimensions
from jdxi_editor.ui.windows.jdxi.helpers.button_row import create_button_row


def create_parts_container(
    parent_widget,
    on_open_d1,
    on_open_d2,
    on_open_drums,
    on_open_analog,
    on_open_arp,
    on_select_synth,
):
    """Create the Parts Select container widget"""
    parts_container = QWidget(parent_widget)
    parts_container.setGeometry(
        JDXiDimensions.PARTS.X,
        JDXiDimensions.PARTS.Y,
        JDXiDimensions.PARTS.WIDTH,
        JDXiDimensions.PARTS.HEIGHT,
    )
    parts_layout = QVBoxLayout(parts_container)
    parts_layout.setSpacing(3)

    parts_label = QLabel("Parts Select")
    parts_label.setStyleSheet(JDXiStyle.PARTS_SELECT)
    parts_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    parts_layout.addWidget(parts_label)

    digital1_row, digital1_button = create_button_row("Digital Synth 1", on_open_d1)
    digital2_row, digital2_button = create_button_row("Digital Synth 2", on_open_d2)
    drums_row, drums_button = create_button_row("Drums", on_open_drums)
    analog_row, analog_button = create_button_row("Analog Synth", on_open_analog)
    arp_row, arp_button = create_button_row("Arpeggiator", on_open_arp)

    # Connect buttons to synth selector
    analog_button.clicked.connect(lambda: on_select_synth(JDXiSynth.ANALOG_SYNTH))
    digital1_button.clicked.connect(lambda: on_select_synth(JDXiSynth.DIGITAL_SYNTH_1))
    digital2_button.clicked.connect(lambda: on_select_synth(JDXiSynth.DIGITAL_SYNTH_2))
    drums_button.clicked.connect(lambda: on_select_synth(JDXiSynth.DRUM_KIT))

    # Button group ensures one active selection
    button_group = QButtonGroup()
    for b in [digital1_button, digital2_button, analog_button, drums_button]:
        button_group.addButton(b)
    button_group.setExclusive(True)

    for row in [digital1_row, digital2_row, drums_row, analog_row, arp_row]:
        parts_layout.addLayout(row)

    parts_container.setStyleSheet(JDXiStyle.TRANSPARENT)

    return parts_container, {
        "digital1": digital1_button,
        "digital2": digital2_button,
        "analog": analog_button,
        "drums": drums_button,
        "arp": arp_button,
    }
