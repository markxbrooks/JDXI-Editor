"""
Slider container
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel

from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.ui.widgets.midi.slider.amp import AmpEnvelopeSlider, AmpLevelSlider
from jdxi_editor.ui.widgets.midi.slider.effects import (
    DelaySlider,
    Effect1Slider,
    Effect2Slider,
    ReverbSlider,
)
from jdxi_editor.ui.widgets.midi.slider.filter.cutoff import FilterCutoffSlider
from jdxi_editor.ui.widgets.midi.slider.filter.resonance import FilterResonanceSlider
from jdxi_editor.ui.widgets.midi.slider.lfo import (
    LFOAmpDepthSlider,
    LFOFilterDepthSlider,
    LFOPitchSlider,
    LFORateSlider,
)
from jdxi_editor.ui.widgets.midi.slider.lfo.shape import LFOShapeSlider
from jdxi_editor.ui.windows.jdxi.dimensions import JDXiDimensions


def add_slider_container(central_widget, midi_helper):
    """ad slider container"""
    slider_container = QWidget(central_widget)
    slider_container.setGeometry(
        JDXiDimensions.SLIDER_X,
        JDXiDimensions.SLIDER_Y,
        JDXiDimensions.SLIDER_CONTAINER_WIDTH,
        JDXiDimensions.SLIDER_CONTAINER_HEIGHT,
    )

    main_layout = QVBoxLayout(slider_container)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(3)

    slider_row_container = QWidget(slider_container)
    slider_row_layout = QHBoxLayout(slider_row_container)
    slider_row_layout.setContentsMargins(0, 0, 0, 0)
    slider_row_layout.setSpacing(3)

    slider_height = JDXiDimensions.SLIDER_HEIGHT
    slider_style = JDXiStyle.ADSR_DISABLED

    def create_slider_with_label(label_text, slider_widget):
        """create a slider with a label"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        label = QLabel(label_text)
        label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        label.setMaximumHeight(20)

        slider_widget.setFixedHeight(slider_height)
        slider_widget.setStyleSheet(slider_style)

        # layout.addWidget(label)
        layout.addWidget(slider_widget)

        return container

    def create_columns_with_label(label_text, container1, container2):
        """create a column with a label"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        label = QLabel(label_text)
        label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        label.setMaximumHeight(20)

        layout.addWidget(label)
        row_layout = QHBoxLayout()
        layout.addLayout(row_layout)

        row_layout.addWidget(container1)
        row_layout.addWidget(container2)

        return container

    # Create sliders
    filter_cutoff_slider = FilterCutoffSlider(midi_helper, label="Cutoff")

    filter_resonance_slider = FilterResonanceSlider(midi_helper, label="Reson.")
    amp_level_slider = AmpLevelSlider(midi_helper, label="Level")
    amp_env_slider = AmpEnvelopeSlider(midi_helper, label="Env")

    lfo_rate_slider = LFORateSlider(midi_helper, label="Rate")
    lfo_pitch_slider = LFOPitchSlider(midi_helper, label="Pitch")

    lfo_filter_slider = LFOFilterDepthSlider(midi_helper, label="Filter")
    lfo_amp_slider = LFOAmpDepthSlider(midi_helper, label="Amp")

    Effect1Slider(midi_helper, label="Efx1")
    Effect2Slider(midi_helper, label="Efx2")
    LFOShapeSlider(midi_helper, label="LFSh")

    delay_slider = DelaySlider(midi_helper, label="Delay")
    reverb_slider = ReverbSlider(midi_helper, label="Reverb")

    filter_cutoff_container = create_slider_with_label("Cut.", filter_cutoff_slider)
    filter_resonance_container = create_slider_with_label(
        "Reson.", filter_resonance_slider
    )

    amp_level_container = create_slider_with_label("Level", amp_level_slider)
    amp_env_container = create_slider_with_label("Env", amp_env_slider)

    lfo_rate_container = create_slider_with_label("Rate", lfo_rate_slider)
    lfo_pitch_container = create_slider_with_label("Pitch", lfo_pitch_slider)

    lfo_filter_container = create_slider_with_label("Filter", lfo_filter_slider)
    lfo_amp_container = create_slider_with_label("Amp", lfo_amp_slider)

    # lfo_shape_container = create_slider_with_label("LFO", lfo_shape_slider)

    delay_container = create_slider_with_label("Dely.", delay_slider)
    reverb_container = create_slider_with_label("Revb.", reverb_slider)

    slider_row_layout.addWidget(
        create_columns_with_label(
            "Filter", filter_cutoff_container, filter_resonance_container
        )
    )
    slider_row_layout.addWidget(
        create_columns_with_label("Amp", amp_level_container, amp_env_container)
    )
    slider_row_layout.addWidget(
        create_columns_with_label("LFO", lfo_rate_container, lfo_pitch_container)
    )
    slider_row_layout.addWidget(
        create_columns_with_label("LFO", lfo_filter_container, lfo_amp_container)
    )
    slider_row_layout.addWidget(
        create_columns_with_label("Effects", delay_container, reverb_container)
    )

    # Add to main layout
    slider_row_container.setStyleSheet(JDXiStyle.ADSR_DISABLED)
    main_layout.addWidget(slider_row_container)
