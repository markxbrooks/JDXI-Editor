# JSON File Save Architecture

## Overview

JDXI Editor saves patch data to JSON files using a multi-step process that creates separate JSON files for each editor (synth type) and then zips them together into a single `.jsz` file.

## Save Flow

### 1. User Initiates Save (`PatchManager`)

When the user clicks "Save" in the Patch Manager dialog:

**Location**: `jdxi_editor/ui/windows/patch/manager.py`

```python
def _handle_action(self):
    # Creates a temporary folder with date and random number
    temp_folder = Path.home() / f".{__package_name__}" / "temp" / f"{date_str}_{random_int}/"
    
    # Iterates through all registered editors
    for editor in self.editors:
        # Skips certain editor types
        if isinstance(editor, (PatternSequenceEditor, ProgramEditor, MidiFileEditor)):
            continue
        
        # Validates editor has required attributes
        if not hasattr(editor, "address") or not hasattr(editor, "get_controls_as_dict"):
            continue
        
        # Processes each editor to create a JSON file
        self.json_composer.process_editor(editor, temp_folder)
    
    # Zips all JSON files into a single .jsz file
    zip_directory(temp_folder, file_path)
```

### 2. Editor Processing (`JDXiJSONComposer`)

**Location**: `jdxi_editor/midi/sysex/json_composer.py`

Each editor is processed individually:

```python
def process_editor(self, editor: SynthEditor, temp_folder: Path) -> Path:
    # Creates temp folder if needed
    os.makedirs(temp_folder, exist_ok=True)
    
    # Composes the JSON message from editor data
    self.compose_message(editor)
    
    # Creates filename based on editor address
    address_hex = ''.join([f"{x:02x}" for x in editor.address.to_bytes()])
    json_temp_file = temp_folder / f"jdxi_tone_data_{address_hex}.json"
    
    # Saves JSON to file
    self.save_json(str(json_temp_file))
    return json_temp_file
```

### 3. JSON Composition (`compose_message`)

**Location**: `jdxi_editor/midi/sysex/json_composer.py`

Builds the JSON structure for a single editor:

```python
def compose_message(self, editor: SynthEditor) -> dict:
    editor_data = {"JD_XI_HEADER": "f041100000000e"}
    
    # Converts address to hex string
    address_hex = ''.join([f"{x:02x}" for x in editor.address.to_bytes()])
    editor_data["ADDRESS"] = address_hex
    
    # Determines temporary area (ANALOG_SYNTH, DIGITAL_SYNTH_1, DRUM_KIT, etc.)
    editor_data["TEMPORARY_AREA"] = parse_sysex_byte(
        editor.address.umb, AddressOffsetTemporaryToneUMB
    )
    
    # Determines synth tone (PARTIAL_1, PARTIAL_2, PARTIAL_3, COMMON, etc.)
    synth_tone_byte = address_hex[4:6]
    synth_tone_map = {
        "20": "PARTIAL_1",
        "21": "PARTIAL_2",
        "22": "PARTIAL_3",
    }
    editor_data["SYNTH_TONE"] = synth_tone_map.get(synth_tone_byte, "UNKNOWN_SYNTH_TONE")
    
    # Gets all control values from the editor
    other_data = editor.get_controls_as_dict()
    for k, v in other_data.items():
        # Handles list/array values (takes first element)
        if isinstance(v, (list, tuple)) and len(v) > 0:
            editor_data[k] = v[0]
        else:
            editor_data[k] = v
    
    return editor_data
```

### 4. Control Value Extraction (`get_controls_as_dict`)

**Location**: `jdxi_editor/ui/editors/synth/base.py`

Extracts current parameter values from the editor's controls:

```python
def get_controls_as_dict(self):
    controls_data = {}
    for param in self.controls:
        controls_data[param.name] = param.value
    return controls_data
```

**Note**: `self.controls` is a dictionary mapping `AddressParameter` → `QWidget` (Slider/ComboBox/etc.)
- Keys: `AddressParameter` enum instances (e.g., `AddressParameterAnalog.OSC_WAVEFORM`)
- Values: UI widgets (e.g., `Slider`, `ComboBox`, `Switch`)

**Important**: The current implementation accesses `param.value`, but `AddressParameter` objects don't have a `value` attribute. The actual value is stored in the widget (e.g., `slider.value()`). This may be a bug that needs investigation.

## JSON File Structure

Each JSON file follows this structure:

```json
{
  "JD_XI_HEADER": "f041100000000e",
  "ADDRESS": "19420000",
  "TEMPORARY_AREA": "ANALOG_SYNTH",
  "SYNTH_TONE": "UNKNOWN_SYNTH_TONE",
  "OSC_WAVEFORM": 22,
  "OSC_PITCH_COARSE": 23,
  "OSC_PITCH_FINE": 24,
  "FILTER_CUTOFF": 33,
  "FILTER_RESONANCE": 35,
  ...
}
```

### Field Descriptions

- **JD_XI_HEADER**: Fixed header identifying this as a JD-Xi SysEx message
- **ADDRESS**: Hex string representation of the editor's memory address (8 hex digits)
- **TEMPORARY_AREA**: The synth area (ANALOG_SYNTH, DIGITAL_SYNTH_1, DIGITAL_SYNTH_2, DRUM_KIT)
- **SYNTH_TONE**: The tone/partial within the area (PARTIAL_1, PARTIAL_2, PARTIAL_3, COMMON, UNKNOWN_SYNTH_TONE)
- **Parameter fields**: All parameter names and their current values (e.g., `OSC_WAVEFORM: 22`)

## File Naming Convention

Each editor creates a JSON file named:
```
jdxi_tone_data_{address_hex}.json
```

Where `address_hex` is the 8-character hex representation of the editor's address.

**Examples**:
- `jdxi_tone_data_19420000.json` - Analog Synth editor
- `jdxi_tone_data_11194200.json` - Digital Synth 1 Common
- `jdxi_tone_data_11214200.json` - Digital Synth 1 Partial 1

## Final Output

All individual JSON files are zipped together into a single `.jsz` file (or `.json` if using the alternative save function).

## Editor Registration

Editors are registered when they're created and shown:

**Location**: `jdxi_editor/ui/windows/jdxi/instrument.py`

```python
def register_editor(self, editor: SynthEditor) -> None:
    self.editors.append(editor)
```

The `self.editors` list contains all active editors:
- `AnalogSynthEditor`
- `DigitalSynthEditor` (for Digital Synth 1)
- `DigitalSynth2Editor` (for Digital Synth 2)
- `DrumCommonEditor` (for Drum Kit)
- `ArpeggioEditor`
- `EffectsCommonEditor`
- `VocalFXEditor`
- Partial editors (nested within main editors)

## Issues and Considerations

### 1. Drum Settings Not Saving (FIXED)

**Problem**: `DrumCommonEditor` was not creating its `DrumCommonSection`, so common controls (like KIT_LEVEL) were never added to `self.controls`, resulting in an empty dictionary when saving.

**Solution**: Added `DrumCommonSection` creation in `DrumCommonEditor.setup_ui()` method.

### 2. Parameter Value Access (POTENTIAL BUG)

**Issue**: `get_controls_as_dict()` accesses `param.value`, but `AddressParameter` enum objects don't have a `value` attribute. The actual value is stored in the widget.

**Current Code**:
```python
for param in self.controls:
    controls_data[param.name] = param.value  # This may fail!
```

**Expected Code**:
```python
for param, widget in self.controls.items():
    controls_data[param.name] = widget.value()  # Get value from widget
```

This may work if there's a property or if exceptions are being caught, but should be verified.

### 3. Multiple Files vs Single File

The current implementation creates separate JSON files for each editor and zips them. There's also a `save_all_controls_to_single_file()` function that combines all editors into one JSON file, but it's not currently used by `PatchManager`.

## Related Files

- `jdxi_editor/ui/windows/patch/manager.py` - Patch save/load UI
- `jdxi_editor/midi/sysex/json_composer.py` - JSON composition logic
- `jdxi_editor/ui/editors/synth/base.py` - Base editor class with `get_controls_as_dict()`
- `jdxi_editor/ui/io/controls.py` - Alternative single-file save function
- `jdxi_editor/ui/editors/drum/editor.py` - Drum editor (now fixed)

