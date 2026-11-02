def send_volume_cc(midi_output, channel: int, volume: int):
    msg = midi_cc_volume(channel, volume)
    midi_output.send(msg)