from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel

from jdxi_editor.ui.style import Style
from jdxi_editor.ui.widgets.midi.slider.amp.envelope import AmpEnvelopeSlider
from jdxi_editor.ui.widgets.midi.slider.amp.level import AmpLevelSlider
from jdxi_editor.ui.widgets.midi.slider.filter.cutoff import FilterCutoffSlider
from jdxi_editor.ui.widgets.midi.slider.filter.resonance import FilterResonanceSlider
from jdxi_editor.ui.windows.jdxi.dimensions import JDXIDimensions


def add_slider_container(central_widget, midi_helper, width, margin):
    slider_container = QWidget(central_widget)
    slider_container.setGeometry(width - 430, margin, 250, 140)

    main_layout = QVBoxLayout(slider_container)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(3)

    slider_row_container = QWidget(slider_container)
    slider_row_layout = QHBoxLayout(slider_row_container)
    slider_row_layout.setContentsMargins(0, 0, 0, 0)
    slider_row_layout.setSpacing(3)

    slider_height = JDXIDimensions.SLIDER_HEIGHT
    slider_style = Style.JDXI_ADSR

    def create_slider_with_label(label_text, slider_widget):
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
    filter_resonance_slider = FilterResonanceSlider(
        midi_helper, label="Reson."
    )
    amp_level_slider = AmpLevelSlider(midi_helper, label="Level")
    amp_env_slider = AmpEnvelopeSlider(midi_helper, label="Env")

    # Add sliders with labels to the row

    filter_cutoff_container = create_slider_with_label(
        "Cutoff", filter_cutoff_slider
    )
    filter_resonance_container = create_slider_with_label(
        "Reson", filter_resonance_slider
    )
    amp_level_container = create_slider_with_label("Level", amp_level_slider)
    amp_env_container = create_slider_with_label("Env", amp_env_slider)

    slider_row_layout.addWidget(
        create_columns_with_label(
            "Filter", filter_cutoff_container, filter_resonance_container
        )
    )
    slider_row_layout.addWidget(
        create_columns_with_label("Amp", amp_level_container, amp_env_container)
    )

    # Add to main layout
    main_layout.addWidget(slider_row_container)
