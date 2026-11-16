"""Test-wide setup."""

import os

# Tests check the built-in controller maps, not the user's edited copy in
# ~/.jdxi_editor/midi_controllers.json
os.environ["JDXI_EDITOR_MIDI_CONTROLLERS"] = ""
