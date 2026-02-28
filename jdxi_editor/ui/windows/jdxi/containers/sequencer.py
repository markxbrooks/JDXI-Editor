"""
sequencer.py

Create a midi-enabled sequencer buttons row

Create a sequencer container

"""

from typing import Callable

from PySide6.QtCore import QRect, Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton
)

from jdxi_editor.ui.common import JDXi, QVBoxLayout, QWidget
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.style.factory import (
    generate_sequencer_button_style,
    toggle_button_style
)
from jdxi_editor.ui.widgets.button.sequencer import SequencerSquare


def create_sequencer_buttons_row(
    midi_helper: MidiIOHelper, on_context_menu: Callable, on_save_favorite: Callable
):
    """Create sequencer button row layout with interactive buttons"""
    row_layout = QHBoxLayout()
    sequencer_buttons = []

    grid = QGridLayout()
    grid.setAlignment(Qt.AlignmentFlag.AlignLeft)
    grid.setGeometry(
        QRect(
            1,
            1,
            JDXi.UI.Dimensions.SEQUENCER.GRID.WIDTH,
            JDXi.UI.Dimensions.SEQUENCER.GRID.HEIGHT
)
    )
    grid.setHorizontalSpacing(3)

    for i in range(16):
        button = SequencerSquare(i, midi_helper)
        button.setFixedSize(
            JDXi.UI.Dimensions.SEQUENCER.SQUARE_SIZE,
            JDXi.UI.Dimensions.SEQUENCER.SQUARE_SIZE
)
        button.setCheckable(True)
        button.setChecked(False)
        button.setStyleSheet(generate_sequencer_button_style(button.isChecked()))

        button.customContextMenuRequested.connect(
            lambda pos, b=button: on_context_menu(pos, b)
        )
        button.setToolTip(f"Save Favorite {i}")  # initial tooltip
        button.toggled.connect(
            lambda checked, btn=button: toggle_button_style(btn, checked)
        )
        button.clicked.connect(
            lambda _, index=i, but=button: on_save_favorite(but, index)
        )

        grid.addWidget(button, 0, i)
        sequencer_buttons.append(button)

    row_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
    row_layout.addLayout(grid)

    return row_layout, sequencer_buttons


def add_sequencer_container(
    central_widget,
    # --- create_favorite_button_row,
    midi_helper,
    on_context_menu,
    on_save_favorite
):
    # --- Beginning of sequencer section
    sequencer_container = QWidget(central_widget)
    sequencer_container.setGeometry(
        JDXi.UI.Dimensions.SEQUENCER.CONTAINER.X,
        JDXi.UI.Dimensions.SEQUENCER.CONTAINER.Y,
        JDXi.UI.Dimensions.SEQUENCER.CONTAINER.WIDTH,
        JDXi.UI.Dimensions.SEQUENCER.CONTAINER.HEIGHT
)
    sequencer_container_layout = QHBoxLayout(sequencer_container)
    sequencer_label = QLabel("Sequencer")
    sequencer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    sequencer_label.setStyleSheet(JDXi.UI.Style.TRANSPARENT)
    sequencer_layout = QHBoxLayout()
    # --- favorites_button_row, favorite_button = create_favorite_button_row()
    sequencer, sequencer_buttons = create_sequencer_buttons_row(
        midi_helper=midi_helper,
        on_context_menu=on_context_menu,
        on_save_favorite=on_save_favorite
)
    sequencer_layout.addLayout(sequencer)
    sequencer_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
    sequencer_container_layout.addLayout(sequencer_layout)
    return sequencer_buttons  # favorite_button


def add_favorite_button_container(central_widget):
    """Create a circular button to set and unset favorites"""
    favourites_button_container = QWidget(central_widget)
    favourites_button_container.setGeometry(
        JDXi.UI.Dimensions.SEQUENCER.CONTAINER.X - 50,
        JDXi.UI.Dimensions.SEQUENCER.CONTAINER.Y,
        100,
        200
)
    text = "Fav."
    row = QHBoxLayout()
    row.setSpacing(1)
    favourite_button_column = QVBoxLayout()
    favourite_button_column.setSpacing(1)
    """
    button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    button.customContextMenuRequested.connect(
        lambda pos, b=button: self._show_favorite_context_menu(pos, b)
    )
    """
    # --- Add label with color based on text
    favourite_button_label = QLabel(text)
    # --- Add spacer to push button to right
    row.addStretch()
    # --- Add button
    favorite_button = QPushButton()
    favorite_button.setFixedSize(30, 30)
    favorite_button.setCheckable(True)
    # --- Style the button with brighter hover/border_pressed/selected  states
    favorite_button.setStyleSheet(JDXi.UI.Style.BUTTON_ROUND)
    favorite_button.setToolTip("Favorite: Mark current settings as a favorite")
    row.addLayout(favourite_button_column)
    favourite_button_column.addWidget(favourite_button_label)
    favourite_button_column.addWidget(favorite_button)
    favourites_button_container.setLayout(row)
    return favorite_button
