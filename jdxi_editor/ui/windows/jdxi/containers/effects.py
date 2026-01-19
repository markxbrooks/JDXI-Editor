"""
Effects buttons
"""

from PySide6.QtWidgets import QVBoxLayout, QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.ui.windows.jdxi.helpers.button_row import create_button_row


def add_effects_container(central_widget, open_vocal_fx, open_effects):
    """Effects button in top row"""
    fx_container = QWidget(central_widget)
    fx_container.setGeometry(
        JDXi.UI.Dimensions.EFFECTS.X,
        JDXi.UI.Dimensions.EFFECTS.Y,
        JDXi.UI.Dimensions.EFFECTS.WIDTH,
        JDXi.UI.Dimensions.EFFECTS.HEIGHT,
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
    fx_container.setStyleSheet(JDXi.UI.Style.TRANSPARENT)
    return vocal_effects_button, effects_button
