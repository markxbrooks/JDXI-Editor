# Synth Selecr


#         and has loaded FluidR3_GM.sf2 via fs.sfload(...) and fs.program_select(...)
# Channel is the MIDI channel you want to set (0-15)

GM_INSTRUMENT_NAMES = [
    "Acoustic Grand Piano",
    "Bright Acoustic Piano",
    "Electric Grand Piano",
    "Honky-tonk Piano",
    "Electric Piano 1",
    "Electric Piano 2",
    "Harpsichord",
    "Clavinet",
    "String Ensemble 1",
    "String Ensemble 2",
    "Synth String 1",
    "Synth String 2",
    "Choir Aahs",
    "Voice Oohs",
    "Synth Pad 1",
    "Synth Pad 2",
    "Warm Pad",
    "Polysynth",
    "Synth Bass 1",
    "Synth Bass 2",
    "Acoustic Guitar (nylon)",
    "Acoustic Guitar (steel)",
    "Electric Guitar (jazz)",
    "Electric Guitar (clean)",
    "Electric Guitar (muted)",
    "Overdriven Guitar",
    "Distortion Guitar",
    "Guitar Harmonics",
    "Acoustic Bass",
    "Electric Bass (finger)",
    "Electric Bass (pick)",
    "Fretless Bass",
    "Slap Bass 1",
    "Slap Bass 2",
    "Synth Bass 3",
    "Synth Keys",
    "Violin",
    "Viola",
    "Cello",
    "Contrabass",
    "Tremolo Strings",
    "Pizzicato Strings",
    "Orchestral Harp",
    "Timpani",
    "String Ensemble 3",
    "String Ensemble 4",
    "Syn Orchestra 1",
    "Syn Orchestra 2",
    "Choir Aahs 2",
    "Voice Oohs 2",
    "Synth Pad 3",
    "Warm Pad 2",
    "Synth Drum",
    "Prog. Harm. Organ",
    "Chorus Organ",
    "Pipe Organ",
    "Rhodes Piano",
    "Encore Organ",
    "Synth Lead 1",
    "Synth Lead 2",
    "Synth Lead 3",
    "Synth Lead 4",
    "Choir Vox",
    "Starry Pad",
    "Glassy Strings",
    "Astral Synth",
    "Warm Pad 3",
    "Polysynth 2",
    "Muted Trumpet",
    "Brass Section",
    "Synth Brass 1",
    "Synth Brass 2",
    "Soprano Sax",
    "Alto Sax",
    "Baritone Sax",
    "Trumpet",
    "Trombone",
    "Tuba",
    "Muted Trumpet",
    "French Horn",
    "Brass Section 2",
    "Synth Brass 3",
    "Orchestra Hit",
    "Trumpet 2",
    "Tremolo",
    "Percussive Hits",
    "Music Box",
    "Far East",
    "Calimba",
    "Toy Piano",
    "Percussive Org",
    "Distortion Guitar 2",
    "Guitar Fret Noise",
    "Breath Noise",
    "Seashore",
    "Bird Tweet",
    "Telephone Ring",
    "Helicopter",
    "Applause",
    "Gunshot",
]


def list_and_select_instrument(
    fs, channel=0, prompt="Select an instrument by number (1-128): "
):
    """
    fs: a FluidSynth Synth instance
    channel: MIDI channel to apply the program change (0-15)
    """
    # Ensure the SF2 loaded has GM mappings; GM_INSTRUMENT_NAMES length should be 128
    print("Available GM instruments:")
    for i, name in enumerate(GM_INSTRUMENT_NAMES):
        # Print in two columns for readability
        print(f"{i+1:3}: {name}", end="\t")
        if (i + 1) % 4 == 0:
            print()
    if len(GM_INSTRUMENT_NAMES) % 4 != 0:
        print()

    while True:
        try:
            choice = input(prompt)
            if not choice:
                continue
            n = int(choice)
            if 1 <= n <= 128:
                program = n - 1  # convert to 0-based
                fs.program_change(channel, program)
                print(f"Selected instrument #{n}: {GM_INSTRUMENT_NAMES[program]}")
                break
            else:
                print("Please enter a number between 1 and 128.")
        except ValueError:
            print("Invalid input. Enter a number between 1 and 128.")


# Example usage after loading SF2 and initializing fs:
# fs = setup_fluidsynth(SF2_PATH)
# list_and_select_instrument(fs, channel=0)
