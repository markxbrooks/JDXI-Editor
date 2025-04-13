from PySide6.QtWidgets import QGroupBox, QFormLayout, QWidget, QVBoxLayout, QScrollArea

from jdxi_editor.midi.data.parameter.drum.common import DrumCommonParameter
from jdxi_editor.midi.data.parameter.drum.partial import DrumPartialParameter
from jdxi_editor.ui.windows.jdxi.dimensions import JDXIDimensions


class DrumPitchSection(QWidget):
    """Drum Pitch Section for the JDXI Editor"""

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
        pitch_group = QGroupBox("Pitch")
        pitch_layout = QFormLayout()
        pitch_group.setLayout(pitch_layout)
        # grid_layout.addWidget(pitch_group, 0, 0)

        # Add pitch parameters
        partial_level_slider = self._create_parameter_slider(
            DrumPartialParameter.PARTIAL_LEVEL, "Partial Level"
        )
        pitch_layout.addRow(partial_level_slider)

        partial_coarse_tune_slider = self._create_parameter_slider(
            DrumPartialParameter.PARTIAL_COARSE_TUNE, "Partial Coarse Tune"
        )
        pitch_layout.addRow(partial_coarse_tune_slider)

        partial_fine_tune_slider = self._create_parameter_slider(
            DrumPartialParameter.PARTIAL_FINE_TUNE, "Partial Fine Tune"
        )
        pitch_layout.addRow(partial_fine_tune_slider)

        partial_random_pitch_depth_slider = self._create_parameter_slider(
            DrumPartialParameter.PARTIAL_RANDOM_PITCH_DEPTH,
            "Partial Random Pitch Depth",
        )
        pitch_layout.addRow(partial_random_pitch_depth_slider)

        partial_pan_slider = self._create_parameter_slider(
            DrumPartialParameter.PARTIAL_PAN, "Partial Pan"
        )
        pitch_layout.addRow(partial_pan_slider)

        partial_random_pan_depth_slider = self._create_parameter_slider(
            DrumPartialParameter.PARTIAL_RANDOM_PAN_DEPTH, "Partial Random Pan Depth"
        )
        pitch_layout.addRow(partial_random_pan_depth_slider)

        partial_alternate_pan_depth_slider = self._create_parameter_slider(
            DrumPartialParameter.PARTIAL_ALTERNATE_PAN_DEPTH,
            "Partial Alternate Pan Depth",
        )
        pitch_layout.addRow(partial_alternate_pan_depth_slider)

        partial_env_mode_combo = self._create_parameter_combo_box(
            DrumPartialParameter.PARTIAL_ENV_MODE,
            "Partial Env Mode",
            ["NO-SUS", "SUSTAIN"],
            [0, 1],
        )
        pitch_layout.addRow(partial_env_mode_combo)

        # return pitch_group
        pitch_group.setLayout(scrolled_layout)
        scrolled_layout.addWidget(pitch_group)
