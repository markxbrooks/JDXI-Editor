Midi Player refactoring

Right now editor.py is acting as:
UI layout factory
MIDI file domain service
Playback engine
Worker/thread orchestration layer
USB recording subsystem
Track classification logic
State machine
Message factory
That’s why it feels unmanageable.
This is not a Builder-pattern problem.
It’s a responsibility segregation problem.
Step 1 — Categorize What You Actually Have
From your grep output, these group cleanly:
A. UI Construction
ui_init
build_panel
_build_left_panel
_build_right_panel
init_ruler
init_midi_file_controls
init_transport_controls
init_mute_controls
init_automation_usb_grid
...
_build_specs
_build_button_specs
_build_checkbox_specs
➡ This is a UI layout module
B. MIDI File Loading / Analysis
midi_load_file
midi_extract_events
detect_initial_tempo
calculate_tick_duration
calculate_duration
midi_channel_select
detect_and_assign_drum_tracks
_classify_tracks
_apply_channel_assignments
➡ This is a MIDI domain service
C. Playback Engine
midi_playback_start
midi_play_next_event
process_tracks
buffer_message
handle_set_tempo
calculate_start_tick
prepare_for_playback
stop_all_notes
update_event_index
➡ This is a Playback Engine
D. Worker / Thread Coordination
setup_worker
setup_playback_worker
start_playback_worker
_connect_to_worker
midi_playback_worker_stop
midi_playback_worker_disconnect
➡ This is a Playback Controller / Worker Adapter
E. USB Recording
usb_populate_devices
usb_start_recording
usb_select_recording_file
on_usb_save_recording_toggled
➡ This is a USBRecordingService
F. Transport State Machine
transport_set_state
midi_playback_pause_toggle
_resume_playback
_pause_playback
stop_playback
reset_midi_state
reset_tempo
➡ This is a TransportStateController
Step 2 — The Correct Restructure
You split by behavior, not by “file size”.
Proposed Architecture
midi_player/
│
├── editor.py                 # Thin UI orchestration layer
├── layout.py                 # UI builders only
├── playback_engine.py        # Pure MIDI playback logic
├── worker_controller.py      # QThread / worker glue
├── midi_analyzer.py          # Track classification + tempo detection
├── transport.py              # Transport state machine
├── usb_recorder.py           # Audio capture subsystem
├── message_factory.py        # MIDI message builders
Step 3 — What editor.py Should Become
It should become thin:
class MidiPlayerEditor(QWidget):

    def __init__(self):
        super().__init__()

        self.playback_engine = PlaybackEngine()
        self.transport = TransportController(self.playback_engine)
        self.analyzer = MidiAnalyzer()
        self.usb_recorder = USBRecorder()
        self.worker_controller = PlaybackWorkerController(
            self.playback_engine
        )

        self.ui = MidiPlayerLayout(self)
        self._connect_components()
Notice:
editor orchestrates
it does not process MIDI
it does not calculate tempo
it does not buffer messages
Step 4 — Playback Engine Becomes Pure
Move all of this:
process_tracks
buffer_message
handle_set_tempo
midi_play_next_event
calculate_start_tick
Into:
class PlaybackEngine:
    def load_file(self, midi_file): ...
    def start(self, start_tick: int): ...
    def stop(self): ...
    def process_next_event(self): ...
No Qt here.
No UI calls.
Pure logic.
That makes it testable without GUI.
Step 5 — Extract MIDI Analysis
Move:
detect_initial_tempo
_classify_tracks
_detect_drum_tracks
_apply_channel_assignments
Into:
class MidiAnalyzer:
    def analyze(self, midi_file) -> MidiAnalysisResult:
        ...
This becomes a deterministic service.
Step 6 — Extract Transport State Machine
Right now transport state is scattered.
Instead:
class TransportState(Enum):
    STOPPED = auto()
    PLAYING = auto()
    PAUSED = auto()


class TransportController:
    def __init__(self, engine: PlaybackEngine):
        self.state = TransportState.STOPPED
        self.engine = engine
All play/pause logic moves here.
Step 7 — Extract Worker Glue
All of:
setup_worker
_connect_to_worker
midi_playback_worker_handle_result
Becomes:
class PlaybackWorkerController(QObject):
    def __init__(self, engine: PlaybackEngine):
        ...
This class ONLY handles:
QThread
signals
result routing
Step 8 — Result
Your editor shrinks from ~200 methods to ~25 orchestration methods.
Each subsystem becomes:
Smaller
Testable
Replaceable
Profileable
Important: Do NOT Refactor Everything At Once
Safe incremental sequence:
Extract MidiAnalyzer first (lowest UI coupling)
Extract PlaybackEngine
Extract TransportController
Extract USBRecorder
Extract Worker layer last
Architectural Insight
Your MIDI player has evolved into a small DAW subsystem.
It needs:
Clear domain layer
Clear transport layer
Clear IO layer
Clear UI layer
Right now they’re fused.