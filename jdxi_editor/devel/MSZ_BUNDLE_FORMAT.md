# MSZ Music Bundle Format

## Overview

The `.msz` (Music Bundle) format is a bundled file format that combines:
- **All synthesizer parameters** (JSON files for Analog, Digital, and Drum synths)
- **MIDI files** (song data ready to play)

This allows you to save a complete "song" with all its patches and MIDI data in a single file, ready to load and play.

## File Structure

An `.msz` file is a ZIP archive containing:

```
song.msz
├── jdxi_tone_data_*.json    (Multiple JSON files for each synth editor)
└── song.mid                  (MIDI file, if available)
```

### JSON Files
- One JSON file per synth editor (Analog, Digital Synth 1, Digital Synth 2, Drum Kit)
- Each file contains all parameters for that synth
- Files are named based on their MIDI address (e.g., `jdxi_tone_data_19700000.json`)

### MIDI File
- Standard MIDI file format (`.mid`)
- Contains the song/sequence data
- Automatically loaded into the MIDI File Editor when the bundle is opened

## Usage

### Saving a Music Bundle

1. **Set up your patches**: Configure all your synth parameters (Analog, Digital, Drum)
2. **Load/Edit your MIDI file**: Open the MIDI File Editor and load or create your MIDI sequence
3. **Save as .msz**:
   - Go to **File → Save Patch...**
   - In the file dialog, select **"Music Bundle (*.msz)"** from the file type dropdown
   - Choose a filename (e.g., `my_song.msz`)
   - Click **Save**

The bundle will include:
- All current synth parameter settings
- The MIDI file (if one is loaded in the MIDI File Editor)

### Loading a Music Bundle

1. **Load the bundle**:
   - Go to **File → Load Patch...**
   - Select your `.msz` file
   - Click **Load**

2. **What happens**:
   - All synth parameters are loaded and applied
   - The MIDI file (if present) is automatically loaded into the MIDI File Editor
   - You're ready to play!

## Compatibility

- **Backward Compatible**: The existing `.jsz` format still works (patch files without MIDI)
- **Forward Compatible**: `.msz` files can be opened by the same loader (MIDI file is optional)

## Technical Details

### Save Process
1. All synth editors are processed to create JSON files
2. If a MIDI file is loaded in `MidiFileEditor`, it's saved as `song.mid` in the bundle
3. All files are zipped into a single `.msz` archive

### Load Process
1. The ZIP archive is opened
2. JSON files are extracted and loaded (via `MidiIOHelper.load_patch()`)
3. MIDI files are extracted to a temporary location
4. The MIDI file is loaded into `MidiFileEditor` and initialized
5. All parameters and MIDI data are ready to use

## File Extensions

- **`.msz`**: Music Bundle (includes patches + MIDI file)
- **`.jsz`**: Patch Bundle (includes patches only, no MIDI)
- **`.json`**: Single patch file (legacy format)
- **`.syx`**: SysEx file (legacy format)

## Benefits

1. **Complete Song Preservation**: Save everything needed to recreate a song
2. **Easy Sharing**: One file contains all patches and MIDI data
3. **Ready to Play**: Load the bundle and immediately start playing
4. **Organized**: All related data is bundled together

## Notes

- If no MIDI file is loaded when saving, the bundle will only contain JSON files (works like `.jsz`)
- If a MIDI file exists in the bundle but `MidiFileEditor` is not available, a warning is logged but the patch still loads
- The MIDI file is optional - bundles without MIDI files work exactly like `.jsz` files

