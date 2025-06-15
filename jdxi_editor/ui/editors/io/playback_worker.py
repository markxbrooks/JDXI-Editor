"""
Playback Worker to play Midi files in a new thread
"""

from PySide6.QtCore import QObject, Signal, Slot


class MidiPlaybackWorker(QObject):
    """
    PlaybackWorker
    """
    result_ready = Signal()  # e.g., to notify when a frame is processed

    def __init__(self, parent=None):
        super().__init__(parent)
        self.editor = None  # Reference to MidiFileEditor

    def set_editor(self, editor):
        self.editor = editor

    @Slot()
    def do_work(self):
        if self.editor:
            self.editor.midi_play_next_event()
            self.result_ready.emit()
