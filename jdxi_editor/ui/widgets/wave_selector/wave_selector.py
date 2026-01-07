"""
Wave selector test class
"""

from PySide6.QtWidgets import QApplication, QComboBox, QVBoxLayout, QWidget

from jdxi_editor.log.logger import Logger as log


class WaveSelector(QWidget):
    """Wave Selector"""

    def __init__(self, wave_list: list[dict[str, str]]) -> None:
        super().__init__()

        self.setWindowTitle("Wave Selector")
        layout = QVBoxLayout(self)

        self.category_combo = QComboBox()
        self.wave_combo = QComboBox()
        self.wave_list = wave_list
        self.categories = ["No selection"] + sorted(
            set(w["Category"] for w in wave_list)
        )
        self.category_combo.addItems(self.categories)
        self.category_combo.currentIndexChanged.connect(self.update_waves)
        layout.addWidget(self.category_combo)
        layout.addWidget(self.wave_combo)
        self.update_waves()

    def update_waves(self) -> None:
        selected_category = self.category_combo.currentText()

        if not isinstance(self.wave_list, list):
            raise ValueError(
                "wave_list is not a list. It should be a list of wave dictionaries."
            )
        if selected_category == "No selection":
            filtered_waves = self.wave_list  # Show all waves
        else:
            filtered_waves = [
                w for w in self.wave_list if w["Category"] == selected_category
            ]
        self.wave_combo.clear()
        self.wave_combo.addItems(
            [f"{w['Wave Number']}: {w['Wave Name']}" for w in filtered_waves]
        )

    def get_selected_wave_number(self) -> int | None:
        """
        Returns the wave number of the selected wave from the wave_combo.

        Returns:
            int: The wave number of the selected wave.
        """
        selected_text = self.wave_combo.currentText()
        if selected_text:
            wave_number = int(
                selected_text.split(":")[0].strip()
            )  # Extract wave number
            return wave_number
        return None


# Sample wave data for testing
PCM_WAVES_CATEGORIZED = [
    {"Category": "Lead & Synth Waves", "Wave Number": 1, "Wave Name": "Calc.Saw"},
    {"Category": "Lead & Synth Waves", "Wave Number": 2, "Wave Name": "DistSaw Wave"},
    {"Category": "Bass Waves", "Wave Number": 30, "Wave Name": "Hollow Bass"},
    {
        "Category": "Bell & Metallic Tones",
        "Wave Number": 36,
        "Wave Name": "Bell Wave 1",
    },
]

# Run the application
app = QApplication([])
window = WaveSelector(PCM_WAVES_CATEGORIZED)
window.show()

# Example: Get the selected wave number
selected_wave_number = window.get_selected_wave_number()
log.message(f"Selected Wave Number: {selected_wave_number}")

app.exec()
