import os
import time
from pathlib import Path

import mido
import rtmidi

from decologr import Decologr as log
from jdxi_editor.ui.widgets.midi.utils import ticks_to_seconds
from picomidi.constant import Midi

# Constants
default_tempo = Midi.TEMPO.BPM_120_USEC  # microseconds per beat (120 BPM)


def buffer_midi_tracks(
    midi_file: mido.MidiFile, muted_tracks=None, muted_channels=None
):
    """
    Preprocess MIDI tracks into a sorted list of (absolute_ticks, raw_bytes, tempo) tuples.
    Meta messages are excluded except for set_tempo.
    """
    if muted_tracks is None:
        muted_tracks = set()
    if muted_channels is None:
        muted_channels = set()

    buffered_messages_list = []
    default_tempo = Midi.TEMPO.BPM_120_USEC  # 120 BPM in microseconds per beat

    for i, track in enumerate(midi_file.tracks):
        if i + Midi.CHANNEL.DISPLAY_TO_BINARY in muted_tracks:
            log.message(
                f"🚫 Skipping muted track {i + Midi.CHANNEL.DISPLAY_TO_BINARY} ({track.name})"
            )
            continue
        absolute_time_ticks = 0
        current_tempo = default_tempo

        for msg in track:
            absolute_time_ticks += msg.time

            if msg.type == "set_tempo":
                current_tempo = msg.tempo
                buffered_messages_list.append(
                    (absolute_time_ticks, None, current_tempo)
                )
            elif not msg.is_meta:
                if hasattr(msg, "channel"):
                    log.message(
                        f"🔍 Checking msg.channel={msg.channel + Midi.CHANNEL.BINARY_TO_DISPLAY} in muted_channels={muted_channels}"
                    )
                    if msg.channel + Midi.CHANNEL.BINARY_TO_DISPLAY in muted_channels:
                        log.message(f"🚫 Skipping muted channel {msg.channel}")
                        continue
                log.message(f"🎵 Adding midi msg to buffer: {msg}")
                raw_bytes = msg.bytes()
                buffered_messages_list.append(
                    (absolute_time_ticks, raw_bytes, current_tempo)
                )

    buffered_messages_list.sort(key=lambda x: x[0])
    return buffered_messages_list

def play_buffered(
    buffered_msgs: list,
    midi_out_port: rtmidi.MidiOut,
    ticks_per_beat: int,
    play_program_changes: bool = True,
):
    """
    play_buffered

    :param buffered_msgs: list
    :param midi_out_port: rtmidi.MidiOut
    :param ticks_per_beat: int
    :param play_program_changes: bool Whether or not to suppress Program Changes
    :return:
    Playback function with program change control
    """
    start_time = time.time()

    for i, (abs_ticks, msg, tempo) in enumerate(buffered_msgs):
        # Convert absolute tick time to seconds
        msg_time_sec = ticks_to_seconds(abs_ticks, tempo, ticks_per_beat)
        # Compute delay relative to start
        delay = msg_time_sec - (time.time() - start_time)

        if delay > 0:
            time.sleep(delay)

        # Send message based on type and program change flag
        if not msg.is_meta:
            if msg.type == "program_change":
                if play_program_changes:
                    midi_out_port.send_message(msg.bytes())
                else:
                    # Skip program change if disabled
                    continue
            else:
                midi_out_port.send_message(msg.bytes())


if __name__ == "__main__":
    import os

    import mido
    import rtmidi

    try:
        midi_out = rtmidi.MidiOut()
        available_ports = midi_out.get_ports()

        if available_ports:
            print(f"Opening MIDI port: {available_ports[0]}")
            midi_out.open_port(0)
        else:
            print("Creating virtual MIDI output port...")
            midi_out.open_virtual_port("My Virtual MIDI Output")

        music_folder = Path.home() / "Desktop" / "music"
        midi_files = [
            f for f in os.listdir(music_folder) if f.lower().endswith((".mid", ".midi"))
        ]
        midi_files.sort(key=str.lower)

        if not midi_files:
            print("❌ No MIDI files found.")
            exit(1)

        print("Available MIDI files:")
        for idx, f in enumerate(midi_files):
            print(f"{idx}: {f}")

        file_indices = (
            input("Enter file numbers to play in order (e.g., 0 2 5): ").strip().split()
        )
        try:
            playlist = [
                os.path.join(music_folder, midi_files[int(i)]) for i in file_indices
            ]
        except (IndexError, ValueError):
            print("❌ Invalid input.")
            exit(1)

        play_pc_input = input("Play Program Changes? (y/n): ").strip().lower()
        play_program_changes = play_pc_input == "y"

        # === Playback Loop ===
        for file_path in playlist:
            print(f"\n🎵 Playing: {os.path.basename(file_path)}")
            midi_playback_file = mido.MidiFile(file_path)
            buffered_messages = buffer_midi_tracks(midi_playback_file)
            play_buffered(
                buffered_messages,
                midi_out,
                play_program_changes=play_program_changes,
                ticks_per_beat=midi_playback_file.ticks_per_beat,
            )

        print("✅ Playlist finished.")
    except Exception as e:
        print(f"❌ Error: {e}")
