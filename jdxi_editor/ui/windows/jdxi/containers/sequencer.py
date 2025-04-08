from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtWidgets import QHBoxLayout, QGridLayout
from PySide6.QtCore import Qt, QRect

from jdxi_editor.ui.style import Style
from jdxi_editor.ui.style.helpers import generate_sequencer_button_style, toggle_button_style
from jdxi_editor.ui.widgets.button import SequencerSquare
from jdxi_editor.ui.windows.jdxi.dimensions import JDXIDimensions


def create_sequencer_buttons_row(
    midi_helper,
    on_context_menu,
    on_save_favorite
):
    """Create sequencer button row layout with interactive buttons"""
    row_layout = QHBoxLayout()
    sequencer_buttons = []

    grid = QGridLayout()
    grid.setAlignment(Qt.AlignmentFlag.AlignLeft)
    grid.setGeometry(QRect(1,
                           1,
                           JDXIDimensions.SEQUENCER_GRID_WIDTH,
                           JDXIDimensions.SEQUENCER_GRID_HEIGHT)
                     )
    grid.setHorizontalSpacing(2)

    for i in range(16):
        button = SequencerSquare(i, midi_helper)
        button.setFixedSize(JDXIDimensions.SEQUENCER_SQUARE_SIZE, JDXIDimensions.SEQUENCER_SQUARE_SIZE)
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


def add_sequencer_container(central_widget,
                            create_favorite_button_row,
                            midi_helper,
                            on_context_menu,
                            on_save_favorite
                            ):
    # Beginning of sequencer section
    sequencer_container = QWidget(central_widget)
    sequencer_container.setGeometry(JDXIDimensions.SEQUENCER_CONTAINER_X,
                                    JDXIDimensions.SEQUENCER_CONTAINER_Y,
                                    JDXIDimensions.SEQUENCER_CONTAINER_WIDTH,
                                    JDXIDimensions.SEQUENCER_CONTAINER_HEIGHT)
    sequencer_container_layout = QHBoxLayout(sequencer_container)
    sequencer_label = QLabel("Sequencer")
    sequencer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    sequencer_label.setStyleSheet(Style.JDXI_TRANSPARENT)
    sequencer_layout = QHBoxLayout()
    favorites_button_row, favorite_button = create_favorite_button_row()
    sequencer, sequencer_buttons = create_sequencer_buttons_row(
        midi_helper=midi_helper,
        on_context_menu=on_context_menu,
        on_save_favorite=on_save_favorite
    )
    sequencer_layout.addLayout(sequencer)
    sequencer_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
    sequencer_container_layout.addLayout(favorites_button_row)
    sequencer_container_layout.addLayout(sequencer_layout)
    return sequencer_buttons, favorite_button


def create_favorite_button_row():
    """Create a circular button to set and unset favorited"""
    text = "Favorites"
    row = QHBoxLayout()
    row.setSpacing(10)
    """
    button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    button.customContextMenuRequested.connect(
        lambda pos, b=button: self._show_favorite_context_menu(pos, b)
    )
    """

    # Add label with color based on text
    label = QLabel(text)
    # Add spacer to push button to right
    row.addStretch()
    # Add button
    favorite_button = QPushButton()
    favorite_button.setFixedSize(30, 30)
    favorite_button.setCheckable(True)
    # Style the button with brighter hover/border_pressed/selected  states
    favorite_button.setStyleSheet(Style.JDXI_BUTTON_ROUND)
    row.addWidget(favorite_button)
    return row, favorite_button
