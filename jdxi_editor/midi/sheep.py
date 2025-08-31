## sheep
import os
import time
from mido import MidiFile
import mido
from fluidsynth import Synth

# Configuration
HW_PORT_HINT = "Roland JDXi"            # adjust if your port name differs
SF2_PATH = os.path.expanduser("~/SoundFonts/FluidR3_GM.sf2")
MIDI_FILE_PATH = os.path.expanduser("~/MIDI/test.mid")  # optional: provide a test MIDI file

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
    fs = Synth()
    # On macOS, default audio driver is typically CoreAudio; pyFluidSynth uses PortAudio by default on some builds.
    # The "driver" parameter is optional; omit if you encounter issues.
    try:
        fs.start(driver=None)  # let Fluidsynth pick a sensible default
    except TypeError:
        fs.start()  # compatibility fallback
    fs.sfload(sf2_path)
    fs.program_select(0, 0, 0, 0)  # channel 0, bank 0, preset 0
    print(f"[INFO] FluidSynth started with SF2: {sf2_path}")
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
        # We'll implement a simple forwarder: replay the file in real-time
        start_time = time.time()
        with mido.open_output/mido.open_input as dummy:  # placeholder to show intent
            pass
        # Serialize events with timing
        # We'll create a simple scheduler: wait for delta times
        # This minimal approach keeps dependencies light
        current_time = 0.0
        for msg in mid.play():
            if use_sw:
                if msg.type == 'note_on' and msg.velocity > 0:
                    fs.noteon(0, msg.note, msg.velocity)
                elif (msg.type == 'note_off') or (msg.type == 'note_on' and msg.velocity == 0):
                    fs.noteoff(0, msg.note)
                elif msg.type == 'control_change':
                    fs.cc(0, msg.control, msg.value)
                elif msg.type == 'program_change':
                    fs.program_change(0, msg.program)
            else:
                # If someone modified this script to feed live MIDI, they'd forward here
                pass
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