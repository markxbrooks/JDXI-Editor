# sheep

import os
import time
from mido import MidiFile
import mido
import fluidsynth

from jdxi_editor.midi.synth_select import list_and_select_instrument

# Configuration
HW_PORT_HINT = "Roland JDXi"  # adjust if your port name differs
SF2_PATH = os.path.expanduser("~/SoundFonts/FluidR3_GM.sf2")
# SF2_PATH = os.path.expanduser("~/SoundFonts/Guitar/Guitar.sf2")
MIDI_FILE_PATH = "tests/sheep.mid"  # Test file with tempo changes


def find_hw_output_name(prefer_hw=True):
    outs = mido.get_output_names()
    for name in outs:
        if HW_PORT_HINT in name:
            return name
    return None


def open_hw_output():
    port_name = find_hw_output_name(True)
    if port_name:
        print(f"[INFO] Opening hardware MIDI output: {port_name}")
        return mido.open_output(port_name)
    print("[INFO] Hardware MIDI output not found. Will use FluidSynth.")
    return None


def setup_fluidsynth(sf2_path):
    if not os.path.exists(sf2_path):
        raise FileNotFoundError(f"SoundFont not found at {sf2_path}")
    fs = fluidsynth.Synth()
    # On macOS, default audio driver is typically CoreAudio; pyFluidSynth uses PortAudio by default on some builds.
    # The "driver" parameter is optional; omit if you encounter issues.
    try:
        fs.start(driver=None)  # let Fluidsynth pick a sensible default
    except TypeError:
        fs.start()  # compatibility fallback
    
    # Load the SoundFont first
    fs.sfload(sf2_path)
    print(f"[INFO] FluidSynth started with SF2: {sf2_path}")
    
    # Now let user select instrument
    try:
        list_and_select_instrument(fs)
    except Exception as e:
        print(f"[WARN] Could not select instrument: {e}")
        # Fallback to default program
        fs.program_select(0, 0, 0, 0)  # channel 0, bank 0, preset 0
    
    return fs


def midi_to_events(in_port, sink_send, use_sw, fs=None):
    # Forward messages from the input port to the sink
    print("[INFO] Starting MIDI routing. Press Ctrl+C to exit.")
    try:
        for msg in in_port:
            if use_sw:
                # Translate to FluidSynth
                if msg.type == 'note_on' and msg.velocity > 0:
                    fs.noteon(0, msg.note, msg.velocity)
                elif (msg.type == 'note_off') or (msg.type == 'note_on' and msg.velocity == 0):
                    fs.noteoff(0, msg.note)
                elif msg.type == 'control_change':
                    fs.cc(0, msg.control, msg.value)
                elif msg.type == 'program_change':
                    fs.program_change(0, msg.program)
                # You can extend with aftertouch, pitchwheel, etc.
            else:
                sink_send.send(msg)
    except KeyboardInterrupt:
        print("[INFO] Stopped by user.")
    finally:
        in_port.close()


def ticks_to_seconds(ticks: int, tempo: int, ticks_per_beat: int) -> float:
    """
    Convert MIDI ticks to seconds using the same formula as the main player.
    :param ticks: int
    :param tempo: int (μs per quarter note)
    :param ticks_per_beat: int
    :return: float
    """
    return (tempo / 1_000_000.0) * (ticks / ticks_per_beat)


def get_total_duration_in_seconds(midi_file):
    """
    Calculate the correct duration accounting for tempo changes.
    Uses the same approach as the main player.
    """
    ticks_per_beat = midi_file.ticks_per_beat
    current_tempo = 500_000  # default: 120 BPM
    time_seconds = 0
    last_tick = 0

    # Collect all events with absolute ticks
    events = []
    for track in midi_file.tracks:
        abs_tick = 0
        for msg in track:
            abs_tick += msg.time
            events.append((abs_tick, msg))

    # Sort all events by tick
    events.sort(key=lambda x: x[0])

    for abs_tick, msg in events:
        delta_ticks = abs_tick - last_tick
        time_seconds += (current_tempo / 1_000_000) * (delta_ticks / ticks_per_beat)
        last_tick = abs_tick

        if msg.type == "set_tempo":
            current_tempo = msg.tempo

    return time_seconds


def play_midi_with_tempo_handling(mid, fs, use_sw):
    """Play MIDI file with proper tempo change handling using the main player approach"""
    
    # Collect all events with absolute ticks and tempo
    events = []
    current_tempo = 500_000  # Default tempo (120 BPM)
    ticks_per_beat = mid.ticks_per_beat
    
    for track in mid.tracks:
        abs_tick = 0
        for msg in track:
            abs_tick += msg.time
            events.append((abs_tick, msg, current_tempo))
            
            # Update tempo when we encounter a tempo change
            if msg.type == 'set_tempo':
                current_tempo = msg.tempo
    
    # Sort events by tick
    events.sort(key=lambda x: x[0])
    
    # Play messages with proper timing
    start_time = time.time()
    print(f"[INFO] Starting playback with {mido.tempo2bpm(500_000):.1f} BPM")
    
    for abs_tick, msg, msg_tempo in events:
        # Calculate when this message should be played using its tempo
        msg_time_sec = ticks_to_seconds(abs_tick, msg_tempo, ticks_per_beat)
        target_time = start_time + msg_time_sec
        
        # Wait until it's time to play this message
        while time.time() < target_time:
            time.sleep(0.001)  # Small sleep to avoid busy waiting
        
        # Handle different message types
        if use_sw and fs:
            if msg.type == 'set_tempo':
                bpm = mido.tempo2bpm(msg.tempo)
                print(f"[INFO] Tempo change to {bpm:.1f} BPM at {msg_time_sec:.2f}s")
                
            elif msg.type == 'note_on' and msg.velocity > 0:
                fs.noteon(0, msg.note, msg.velocity)
                
            elif (msg.type == 'note_off') or (msg.type == 'note_on' and msg.velocity == 0):
                fs.noteoff(0, msg.note)
                
            elif msg.type == 'control_change':
                fs.cc(0, msg.control, msg.value)
                
            elif msg.type == 'program_change':
                fs.program_change(0, msg.program)
                
            elif msg.type == 'time_signature':
                print(f"[INFO] Time signature: {msg.numerator}/{msg.denominator} at {msg_time_sec:.2f}s")


def main():
    # 1) Try hardware first
    hw_out = open_hw_output()
    use_sw = False
    fs = None

    if hw_out is None:
        # 2) Fallback to FluidSynth
        use_sw = True
        fs = setup_fluidsynth(SF2_PATH)

    # 3) Prepare an input source
    # If a MIDI file is provided, use it; else, you can switch to live input.
    if os.path.exists(MIDI_FILE_PATH):
        print(f"[INFO] Playing MIDI file: {MIDI_FILE_PATH}")
        mid = MidiFile(MIDI_FILE_PATH)
        
        # Calculate correct duration using the main player approach
        correct_duration = get_total_duration_in_seconds(mid)
        print(f"[INFO] Correct file duration: {correct_duration:.2f} seconds")
        print(f"[INFO] Mido calculated duration: {mid.length:.2f} seconds")
        print(f"[INFO] Difference: {abs(correct_duration - mid.length):.2f} seconds")
        
        # Play with proper tempo handling
        play_midi_with_tempo_handling(mid, fs, use_sw)
        print("[INFO] MIDI file playback finished.")
    else:
        # 4) Live MIDI input (demo: waits for input)
        input_ports = mido.get_input_names()
        if not input_ports:
            print("[WARN] No MIDI input sources found. Exiting.")
            return
        in_port_name = input_ports[0]
        print(f"[INFO] Opening MIDI input: {in_port_name}")
        in_port = mido.open_input(in_port_name)
        midi_to_events(in_port, hw_out, use_sw, fs)

    # Cleanup
    if hw_out:
        hw_out.close()
    if fs:
        fs.delete()
    print("[INFO] Exited cleanly.")


if __name__ == "__main__":
    main()
