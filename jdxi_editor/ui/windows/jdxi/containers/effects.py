"""
Effects buttons
"""

from PySide6.QtWidgets import QVBoxLayout, QWidget

from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.ui.windows.jdxi.dimensions import JDXiDimensions
from jdxi_editor.ui.windows.jdxi.helpers.button_row import create_button_row


def add_effects_container(central_widget, open_vocal_fx, open_effects):
    """Effects button in top row"""
    fx_container = QWidget(central_widget)
    fx_container.setGeometry(
        JDXiDimensions.EFFECTS_X,
        JDXiDimensions.EFFECTS_Y,
        JDXiDimensions.EFFECTS_WIDTH,
        JDXiDimensions.EFFECTS_HEIGHT,
    )
    fx_layout = QVBoxLayout(fx_container)
    vocal_effects_row, vocal_effects_button = create_button_row(
        "Vocoder",
        open_vocal_fx,
        vertical=True,
    )
    effects_row, effects_button = create_button_row(
        "Effects", open_effects, vertical=True, spacing=10
    )
    vocal_effects_row.setSpacing(3)
    fx_layout.setSpacing(6)
    fx_layout.addLayout(vocal_effects_row)
    fx_layout.addLayout(effects_row)
    fx_container.setStyleSheet(JDXiStyle.TRANSPARENT)
    return vocal_effects_button, effects_button
