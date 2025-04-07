from PySide6.QtWidgets import QWidget, QHBoxLayout

from jdxi_editor.ui.style import Style
from jdxi_editor.ui.windows.jdxi.dimensions import JDXIDimensions
from jdxi_editor.ui.windows.jdxi.helpers.button_row import create_button_row


def add_effects_container(central_widget, open_vocal_fx, open_effects):
    # Effects button in top row
    fx_container = QWidget(central_widget)
    fx_container.setGeometry(JDXIDimensions.WIDTH - 170, JDXIDimensions.MARGIN + 20, 180, 80)
    fx_layout = QHBoxLayout(fx_container)
    vocal_effects_row, vocal_effects_button = create_button_row(
        "Vocoder",
        open_vocal_fx,
        vertical=True,
    )
    effects_row, effects_button = create_button_row(
        "Effects", open_effects, vertical=True, spacing=10
    )
    vocal_effects_row.setSpacing(3)
    fx_layout.setSpacing(3)
    fx_layout.addLayout(vocal_effects_row)
    fx_layout.addLayout(effects_row)
    fx_container.setStyleSheet(Style.JDXI_TRANSPARENT)
    return vocal_effects_button, effects_button
