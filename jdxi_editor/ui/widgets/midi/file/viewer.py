"""
UI components for MIDI file player.
"""

from PySide6.QtCore import QMargins, Qt
from PySide6.QtWidgets import QLabel, QSlider, QWidget, QVBoxLayout

from jdxi_editor.midi.playback.state import MidiPlaybackState

from jdxi_editor.ui.widgets.midi.track_viewer import MidiTrackViewer
from picoui.helpers.layout import create_layout_with_items, create_widget_with_layout


class MidiFileViewer(QWidget):
    """UI class for MIDI file player interface."""

    def __init__(self, midi_state: MidiPlaybackState, parent: "MidiFilePlayer"):
        """constructor"""
        super().__init__()
        self.midi_track_viewer: MidiTrackViewer | None = None
        self.parent = parent
        self.midi_state = midi_state
        self.position_slider = QSlider()
        self.position_label = QLabel()
        self.setup_ui()

    def setup_ui(self):
        """setup ui"""
        layout = QVBoxLayout(self)
        layout.addWidget(self._build_ui())

    def _build_ui(self) -> QWidget:
        """
        init_ruler

        :return: QWidget
        """
        self.init_midi_file_position_label()
        self.init_midi_file_position_slider()
        widgets = [self.position_label, self.position_slider]
        ruler_layout = create_layout_with_items(
            items=widgets,
            margins=QMargins(0, 0, 0, 0),
            spacing=0,
            start_stretch=False,
            end_stretch=False,
        )
        ruler_container = create_widget_with_layout(layout=ruler_layout)
        return ruler_container

    def init_midi_file_position_slider(self):
        """Midi File position slider"""
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setEnabled(False)
        self.position_slider.sliderReleased.connect(
            self.parent.midi_scrub_position
        )

    def init_midi_file_position_label(self):
        """Midi File position label"""
        self.position_label = QLabel("Playback Position: 0:00 / 0:00")
        self.midi_track_viewer = MidiTrackViewer()
        self.position_label.setFixedWidth(
            self.midi_track_viewer.get_track_controls_width()
        )

