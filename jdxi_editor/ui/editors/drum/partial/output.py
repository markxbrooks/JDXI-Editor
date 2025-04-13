from PySide6.QtWidgets import QGroupBox, QFormLayout, QWidget, QVBoxLayout, QScrollArea

from jdxi_editor.midi.data.parameter.drum.common import DrumCommonParameter
from jdxi_editor.midi.data.parameter.drum.partial import DrumPartialParameter
from jdxi_editor.ui.windows.jdxi.dimensions import JDXIDimensions


class DrumOutputSection(QWidget):
    """Drum Output Section for the JDXI Editor"""

    def __init__(
        self,
        controls,
        create_parameter_combo_box,
        create_parameter_slider,
        midi_helper,
    ):
        super().__init__()
        self.controls = controls
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_combo_box = create_parameter_combo_box
        self.midi_helper = midi_helper
        self.setup_ui()

    def setup_ui(self):
        """setup UI"""
        layout = QVBoxLayout(self)

        scroll_area = QScrollArea()
        scroll_area.setMinimumHeight(JDXIDimensions.SCROLL_AREA_HEIGHT)
        scroll_area.setWidgetResizable(True)  # Important for resizing behavior
        layout.addWidget(scroll_area)

        scrolled_widget = QWidget()
        scrolled_layout = QVBoxLayout(scrolled_widget)

        # Add widgets to scrolled_layout here if needed

        scroll_area.setWidget(scrolled_widget)

        # Pitch Group
        output_group = QGroupBox("Output")
        output_layout = QFormLayout()
        output_group.setLayout(output_layout)

        # Add output parameters
        partial_output_level_slider = self._create_parameter_slider(
            DrumPartialParameter.PARTIAL_OUTPUT_LEVEL, "Output Level"
        )
        output_layout.addRow(partial_output_level_slider)

        partial_chorus_send_level_slider = self._create_parameter_slider(
            DrumPartialParameter.PARTIAL_CHORUS_SEND_LEVEL, "Chorus Send Level"
        )
        output_layout.addRow(partial_chorus_send_level_slider)

        partial_reverb_send_level_slider = self._create_parameter_slider(
            DrumPartialParameter.PARTIAL_REVERB_SEND_LEVEL, "Reverb Send Level"
        )
        output_layout.addRow(partial_reverb_send_level_slider)

        partial_output_assign_combo = self._create_parameter_combo_box(
            DrumPartialParameter.PARTIAL_OUTPUT_ASSIGN,
            "Output Assign",
            ["EFX1", "EFX2", "DLY", "REV", "DIR"],
            [0, 1, 2, 3, 4],
        )
        output_layout.addRow(partial_output_assign_combo)
        scrolled_layout.addWidget(output_group)
