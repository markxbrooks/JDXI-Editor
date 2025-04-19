"""
MOD LFO section of the digital partial editor.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox

from jdxi_editor.midi.data.parameter.digital.partial import AddressParameterDigitalPartial


class DigitalModLFOSection(QWidget):
    """MOD LFO section for the digital partial editor."""

    def __init__(
        self,
        create_parameter_slider,
        create_parameter_combo_box,
        on_parameter_changed,
        controls,
    ):
        super().__init__()
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_combo_box = create_parameter_combo_box
        self._on_parameter_changed = on_parameter_changed
        self.controls = controls
        self._init_ui()

    def _init_ui(self):
        mod_lfo_layout = QVBoxLayout()
        self.setLayout(mod_lfo_layout)

        # Shape and sync controls
        top_row = QHBoxLayout()
        self.mod_lfo_shape = self._create_parameter_combo_box(
            AddressParameterDigitalPartial.MOD_LFO_SHAPE,
            "Shape",
            ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"],
        )
        top_row.addWidget(self.mod_lfo_shape)

        self.mod_lfo_sync = self._create_parameter_combo_box(
            AddressParameterDigitalPartial.MOD_LFO_TEMPO_SYNC_SWITCH, "Sync", ["OFF", "ON"]
        )
        top_row.addWidget(self.mod_lfo_sync)
        mod_lfo_layout.addLayout(top_row)

        # Rate and note controls
        rate_row = QHBoxLayout()
        rate_row.addWidget(
            self._create_parameter_slider(AddressParameterDigitalPartial.MOD_LFO_RATE, "Rate")
        )
        self.mod_lfo_note = self._create_parameter_combo_box(
            AddressParameterDigitalPartial.MOD_LFO_TEMPO_SYNC_NOTE,
            "Note",
            ["1/1", "1/2", "1/4", "1/8", "1/16"],
        )
        rate_row.addWidget(self.mod_lfo_note)
        mod_lfo_layout.addLayout(rate_row)

        # Modulation depths
        depths_group = QGroupBox("Depths")
        depths_layout = QVBoxLayout()
        depths_group.setLayout(depths_layout)

        depths_layout.addWidget(
            self._create_parameter_slider(
                AddressParameterDigitalPartial.MOD_LFO_PITCH_DEPTH, "Pitch"
            )
        )
        depths_layout.addWidget(
            self._create_parameter_slider(
                AddressParameterDigitalPartial.MOD_LFO_FILTER_DEPTH, "Filter"
            )
        )
        depths_layout.addWidget(
            self._create_parameter_slider(
                AddressParameterDigitalPartial.MOD_LFO_AMP_DEPTH, "Amp"
            )
        )
        depths_layout.addWidget(
            self._create_parameter_slider(AddressParameterDigitalPartial.MOD_LFO_PAN, "Pan")
        )

        mod_lfo_layout.addWidget(depths_group)
        mod_lfo_layout.addWidget(
            self._create_parameter_slider(
                AddressParameterDigitalPartial.MOD_LFO_RATE_CTRL, "Rate Ctrl"
            )
        )
        mod_lfo_layout.addStretch()
