def send_volume_cc(midi_output, channel: int, volume: int):
    msg = midi_cc_volume(channel, volume)
    midi_output.send(msg)
    
def midi_cc_volume(channel: int, volume: int) -> list[int]:
    if not 1 <= channel <= 16:
        raise ValueError("MIDI channel must be 1..16")

    v = max(0, min(127, volume))
    status = 0xB0 + (channel - 1)
    return [status, 0x07, v]


# Examples
print(midi_cc_volume(1, 100))   # [176, 7, 100]
print(midi_cc_volume(8, 64))    # [183, 7, 64]
print(midi_cc_volume(16, 127))  # [191, 7, 127]