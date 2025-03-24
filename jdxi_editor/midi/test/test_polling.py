import sys
import rtmidi
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import QTimer


class MidiMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MIDI Monitor")
        self.setGeometry(100, 100, 400, 200)

        # Create UI Elements
        self.layout = QVBoxLayout()
        self.label = QLabel("Waiting for MIDI messages...", self)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        # Initialize MIDI input
        self.midi_in = rtmidi.MidiIn()
        self.midi_in.open_port(0)  # Change index if needed

        # Set up a QTimer to poll for MIDI messages
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll_midi)
        self.timer.start(10)  # Poll every 10 milliseconds

    def poll_midi(self):
        """Poll for MIDI messages and update UI."""
        message = self.midi_in.get_message()
        if message:
            midi_data, timestamp = message
            midi_text = f"Received MIDI: {midi_data} at {timestamp:.6f} sec"
            self.label.setText(midi_text)
            print(midi_text)  # Also print to console for debugging

    def closeEvent(self, event):
        """Ensure MIDI port is closed when the app exits."""
        self.midi_in.close_port()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MidiMonitor()
    window.show()
    sys.exit(app.exec())
