"""
Slider container
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from jdxi_editor.jdxi.jdxi import JDXi
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


def add_slider_container(central_widget, midi_helper):
    """ad slider container"""
    slider_container = QWidget(central_widget)
    slider_container.setGeometry(
        JDXi.UI.Dimensions.SLIDER.X,
        JDXi.UI.Dimensions.SLIDER.Y,
        JDXi.UI.Dimensions.SLIDER.CONTAINER.WIDTH,
        JDXi.UI.Dimensions.SLIDER.CONTAINER.HEIGHT,
    )

    main_layout = QVBoxLayout(slider_container)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(3)

    slider_row_container = QWidget(slider_container)
    slider_row_layout = QHBoxLayout(slider_row_container)
    slider_row_layout.setContentsMargins(0, 0, 0, 0)
    slider_row_layout.setSpacing(3)

    slider_height = JDXi.UI.Dimensions.SLIDER.HEIGHT
    slider_style = JDXi.UI.Style.ADSR_DISABLED

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

    # Create sliders with tooltips
    filter_cutoff_slider = FilterCutoffSlider(midi_helper, label="Cutoff")
    filter_cutoff_slider.setToolTip(
        "Filter Cutoff: Sets the filter cutoff frequency for all MIDI channels"
    )

    filter_resonance_slider = FilterResonanceSlider(midi_helper, label="Reson.")
    filter_resonance_slider.setToolTip(
        "Filter Resonance: Sets the filter resonance (Q) for all MIDI channels"
    )

    amp_level_slider = AmpLevelSlider(midi_helper, label="Level")
    amp_level_slider.setToolTip(
        "Amp Level: Sets the amplifier level for all MIDI channels"
    )

    amp_env_slider = AmpEnvelopeSlider(midi_helper, label="Env")
    amp_env_slider.setToolTip(
        "Amp Envelope: Sets the amplifier envelope depth for all MIDI channels"
    )

    lfo_rate_slider = LFORateSlider(midi_helper, label="Rate")
    lfo_rate_slider.setToolTip(
        "LFO Rate: Sets the LFO rate (speed) for all MIDI channels"
    )

    lfo_pitch_slider = LFOPitchSlider(midi_helper, label="Pitch")
    lfo_pitch_slider.setToolTip(
        "LFO Pitch Depth: Sets the LFO pitch modulation depth for all MIDI channels"
    )

    lfo_filter_slider = LFOFilterDepthSlider(midi_helper, label="Filter")
    lfo_filter_slider.setToolTip(
        "LFO Filter Depth: Sets the LFO filter modulation depth for all MIDI channels"
    )

    lfo_amp_slider = LFOAmpDepthSlider(midi_helper, label="Amp")
    lfo_amp_slider.setToolTip(
        "LFO Amp Depth: Sets the LFO amplitude modulation depth for all MIDI channels"
    )

    effect1_slider = Effect1Slider(midi_helper, label="Efx1")
    effect1_slider.setToolTip(
        "Effect 1: Sets the Effect 1 send level for all MIDI channels"
    )

    effect2_slider = Effect2Slider(midi_helper, label="Efx2")
    effect2_slider.setToolTip(
        "Effect 2: Sets the Effect 2 send level for all MIDI channels"
    )

    lfo_shape_slider = LFOShapeSlider(midi_helper, label="LFSh")
    lfo_shape_slider.setToolTip(
        "LFO Shape: Sets the LFO waveform shape for all MIDI channels"
    )

    delay_slider = DelaySlider(midi_helper, label="Delay")
    delay_slider.setToolTip("Delay: Sets the delay send level for all MIDI channels")

    reverb_slider = ReverbSlider(midi_helper, label="Reverb")
    reverb_slider.setToolTip("Reverb: Sets the reverb send level for all MIDI channels")

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
    slider_row_container.setStyleSheet(JDXi.UI.Style.ADSR_DISABLED)
    main_layout.addWidget(slider_row_container)
