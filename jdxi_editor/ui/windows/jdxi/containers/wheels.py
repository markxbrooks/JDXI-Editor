from PySide6.QtWidgets import QHBoxLayout, QLabel

from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.ui.widgets.wheel.mod import ModWheel
from jdxi_editor.ui.widgets.wheel.pitch import PitchWheel


def build_wheel_label_row():
    label_layout = QHBoxLayout()
    label_layout.setContentsMargins(0, 0, 0, 0)
    label_layout.addStretch()

    for text in ["Pitch", "Mod"]:
        label = QLabel(text)
        label.setStyleSheet(JDXiStyle.TRANSPARENT)
        label_layout.addWidget(label)
        label_layout.addStretch()

    return label_layout


def build_wheel_row(midi_helper):
    wheel_layout = QHBoxLayout()
    wheel_layout.addStretch()

    pitch_wheel = PitchWheel(midi_helper=midi_helper, bidirectional=True)
    pitch_wheel.setMinimumWidth(20)
    wheel_layout.addWidget(pitch_wheel)
    wheel_layout.addStretch()
    mod_wheel = ModWheel(midi_helper=midi_helper, bidirectional=True)
    mod_wheel.setMinimumWidth(20)
    wheel_layout.addWidget(mod_wheel)

    wheel_layout.addStretch()
    return wheel_layout
