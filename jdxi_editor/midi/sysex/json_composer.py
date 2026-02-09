"""
JDXiSysExComposer
"""

import json
import os
from pathlib import Path
from typing import Any, Optional, Union

from decologr import Decologr as log

from jdxi_editor.midi.data.address.address import (
    JDXiSysExOffsetTemporaryToneUMB,
    JDXiSysExAddress,
)
from jdxi_editor.midi.data.parameter.drum.partial import DrumPartialParam
from jdxi_editor.midi.sysex.sections import SysExSection
from jdxi_editor.project import __package_name__
from jdxi_editor.ui.windows.midi.debugger import parse_sysex_byte


class JDXiJSONComposer:
    """JSON SysExComposer"""

    def __init__(self, editor: Optional["SynthEditor"] = None):
        self.json_string = None
        if editor:
            self.editor = editor
            self.address = editor.address
        self.temp_folder = Path.home() / f".{__package_name__}" / "temp"
        if not os.path.exists(self.temp_folder):
            self.temp_folder.mkdir(parents=True, exist_ok=True)

    def compose_message(
        self,
        editor: "SynthEditor",
    ) -> Optional[dict[Union[str, Any], Union[str, Any]]]:
        """
        :param editor: SynthEditor Editor instance to process

        :return: str JSON SysEx message
        """
        if editor:
            self.editor = editor
            self.address = editor.address
        try:
            editor_data = {SysExSection.JD_XI_HEADER: "f041100000000e"}
            if not hasattr(editor, "address"):
                log.warning(f"Skipping invalid editor: {editor}, has no address")
                return None
            if not hasattr(editor, "get_controls_as_dict"):
                log.warning(
                    f"Skipping invalid editor: {editor}, has no get_controls_as_dict method"
                )
                return None
            # --- Convert address to hex string without spaces (safely convert to int)
            address_bytes = editor.address.to_bytes()
            address_hex = "".join(
                [
                    f"{int(x) if not isinstance(x, int) else x:02x}"
                    for x in address_bytes
                ]
            )
            synth_tone_byte = address_hex[4:6]
            editor_data[SysExSection.ADDRESS] = address_hex

            editor_data[SysExSection.TEMPORARY_AREA] = parse_sysex_byte(
                editor.address.umb, JDXiSysExOffsetTemporaryToneUMB
            )
            synth_tone_map = {
                "20": "PARTIAL_1",
                "21": "PARTIAL_2",
                "22": "PARTIAL_3",
            }
            editor_data[SysExSection.SYNTH_TONE] = synth_tone_map.get(
                synth_tone_byte, "UNKNOWN_SYNTH_TONE"
            )
            # editor_data[SysExSection.SYNTH_TONE] = synth_tone_map.get(synth_tone_byte, "COMMON")
            # Get the raw control values instead of the full control data
            other_data = editor.get_controls_as_dict()
            for k, v in other_data.items():
                # If the value is a list/array, take just the first value (the actual control value)
                if isinstance(v, (list, tuple)) and len(v) > 0:
                    editor_data[k] = v[0]
                else:
                    editor_data[k] = v

            # Add tone name parameters if available
            if hasattr(editor, "tone_names") and hasattr(editor, "preset_type"):
                tone_name = editor.tone_names.get(editor.preset_type, "")
                if tone_name:
                    # Convert tone name string to TONE_NAME_1 through TONE_NAME_12
                    # Pad to 12 characters and truncate if longer
                    tone_name_padded = tone_name.ljust(12)[:12]
                    for i, char in enumerate(tone_name_padded, start=1):
                        ascii_value = ord(char)
                        editor_data[f"TONE_NAME_{i}"] = ascii_value
                    log.message(f"Including tone name in JSON: '{tone_name}'")

            # Convert combined_data to JSON string
            self.json_string = editor_data  # json.dumps(editor_data, indent=4)
            return self.json_string

        except (ValueError, TypeError, OSError, IOError) as ex:
            log.error(f"Error sending message: {ex}")
            return None

    def save_json(self, file_path: str) -> None:
        """
        Save the JSON string to a file

        :param file_path: str File path to save the JSON
        :return: None
        """
        try:
            with open(file_path, "w", encoding="utf-8") as file_handle:
                json.dump(self.json_string, file_handle, ensure_ascii=False, indent=2)
            log.message(f"JSON saved successfully to {file_path}")
        except Exception as ex:
            log.error(f"Error saving JSON: {ex}")

    def process_editor(self, editor: "SynthEditor", temp_folder: Path) -> Path:
        """
        Process the editor and save the JSON

        :param editor: SynthEditor Editor instance to process
        :param temp_folder: str Temporary folder to save the JSON
        :return: None
        """
        if temp_folder:
            self.temp_folder = temp_folder
        os.makedirs(temp_folder, exist_ok=True)

        # Special handling for DigitalSynthEditor: save Common and Modify separately
        from picomidi.constant import Midi

        from jdxi_editor.midi.data.address.address import (
            JDXiSysExOffsetProgramLMB,
            JDXiSysExOffsetSuperNATURALLMB,
            JDXiSysExAddress,
        )
        from jdxi_editor.midi.data.parameter.digital import (
            DigitalCommonParam,
            DigitalModifyParam,
        )
        from jdxi_editor.midi.data.parameter.drum.common import (
            DrumCommonParam,
        )
        from jdxi_editor.ui.editors.digital.editor import DigitalSynthEditor
        from jdxi_editor.ui.editors.drum.editor import DrumCommonEditor

        if isinstance(editor, DigitalSynthEditor):
            # Separate Common and Modify controls
            common_controls = {}
            modify_controls = {}
            other_controls = {}

            controls_dict = editor.get_controls_as_dict()
            for param, widget in editor.controls.items():
                param_name = param.name
                value = controls_dict.get(param_name)

                # Check if this is a Common parameter
                if isinstance(param, DigitalCommonParam):
                    common_controls[param_name] = value
                # Check if this is a Modify parameter
                elif isinstance(param, DigitalModifyParam):
                    modify_controls[param_name] = value
                else:
                    other_controls[param_name] = value

            # Save Common section with Common address
            if common_controls:
                # For Common, we need: MSB=0x19, UMB=editor.address.umb, LMB=0x00 (COMMON), LSB=0x00
                # The editor.address.umb is already correct (0x01 for DS1, 0x21 for DS2)
                # We just need to ensure LMB is set to COMMON (0x00)

                common_address = JDXiSysExAddress(
                    msb=editor.address.msb,  # 0x19 (TEMPORARY_TONE)
                    umb=editor.address.umb,  # 0x01 for DS1, 0x21 for DS2 (includes SuperNATURAL offset)
                    lmb=JDXiSysExOffsetSuperNATURALLMB.COMMON.STATUS,  # 0x00 (COMMON)
                    lsb=Midi.VALUE.ZERO,  # 0x00
                )
                self._save_editor_section(
                    editor, common_controls, common_address, temp_folder, "COMMON"
                )

            # Save Modify section with Modify address (current editor address)
            if modify_controls or other_controls:
                # Combine modify and other controls
                all_modify_controls = {**modify_controls, **other_controls}
                self._save_editor_section(
                    editor, all_modify_controls, editor.address, temp_folder, "MODIFY"
                )

            # Return the Common file path if it exists, otherwise Modify
            if common_controls:
                common_address_hex = "".join(
                    [f"{x:02x}" for x in common_address.to_bytes()]
                )
                return temp_folder / f"jdxi_tone_data_{common_address_hex}.json"
            else:
                address_hex = "".join([f"{x:02x}" for x in editor.address.to_bytes()])
                return temp_folder / f"jdxi_tone_data_{address_hex}.json"
        elif isinstance(editor, DrumCommonEditor):
            # Special handling for DrumCommonEditor: save Common and Partial separately
            # Separate Common and Partial controls
            common_controls = {}
            partial_controls = {}

            controls_dict = editor.get_controls_as_dict()
            log.message(
                f"Found {len(editor.controls)} controls in editor",
                scope=self.__class__.__name__,
            )
            log.message(
                f"controls_dict has {len(controls_dict)} entries",
                scope=self.__class__.__name__,
            )

            # First, check if KIT_LEVEL is in controls_dict (from get_controls_as_dict)
            if "KIT_LEVEL" in controls_dict:
                log.message(
                    f"KIT_LEVEL found in controls_dict = {controls_dict['KIT_LEVEL']}",
                    scope=self.__class__.__name__,
                )
            else:
                log.warning(
                    "KIT_LEVEL NOT found in controls_dict",
                    scope=self.__class__.__name__,
                )
                log.message(
                    f"Available keys in controls_dict: {list(controls_dict.keys())[:10]}...",
                    scope=self.__class__.__name__,
                )

            for param, widget in editor.controls.items():
                param_name = param.name

                # Get value directly from widget to ensure we have the current value
                # This is more reliable than using controls_dict which might have stale values
                widget_value = None
                try:
                    if hasattr(widget, "value"):
                        # Custom Slider widget has value() method that returns slider.value()
                        widget_value = widget.value()
                    elif hasattr(widget, "slider"):
                        # Direct QSlider access (fallback)
                        widget_value = widget.slider.STATUS()
                    else:
                        # Fallback to controls_dict
                        widget_value = controls_dict.get(param_name)

                    # Ensure we have a valid integer value
                    if widget_value is None:
                        widget_value = controls_dict.get(param_name)

                    value = int(widget_value) if widget_value is not None else 0
                except Exception as ex:
                    log.warning(
                        f"Error getting value for {param_name}: {ex}",
                        scope=self.__class__.__name__,
                    )
                    value = controls_dict.get(param_name, 0)

                log.message(
                    f"Parameter {param_name}: widget.value()={widget_value}, controls_dict={controls_dict.get(param_name)}, final={value}",
                    scope=self.__class__.__name__,
                )

                # Check if this is a Common parameter
                # Use isinstance to check if param is an instance of the enum class
                if isinstance(param, DrumCommonParam):
                    # Special check for KIT_LEVEL - warn if it's 0 as it might indicate the slider wasn't updated
                    if param_name == "KIT_LEVEL" and value == 0:
                        log.warning(
                            f"KIT_LEVEL is 0 - this might indicate the slider wasn't updated from the synth",
                            scope=self.__class__.__name__,
                        )
                        log.message(
                            f"Widget value: {widget_value}, controls_dict value: {controls_dict.get(param_name)}",
                            scope=self.__class__.__name__,
                        )
                    common_controls[param_name] = value
                    log.message(
                        f"Added Common parameter {param_name} = {value}",
                        scope=self.__class__.__name__,
                    )
                # Check if this is a Partial parameter
                elif isinstance(param, DrumPartialParam):
                    partial_controls[param_name] = value
                    log.message(
                        f"Added Partial parameter {param_name} = {value}",
                        scope=self.__class__.__name__,
                    )
                else:
                    log.warning(
                        f"Unknown parameter type for {param_name}: {type(param)}",
                        scope=self.__class__.__name__,
                    )

            log.message(
                f"Separated {len(common_controls)} Common and {len(partial_controls)} Partial controls",
                scope=self.__class__.__name__,
            )

            # If no common controls found, try alternative identification methods
            if not common_controls:
                log.warning(
                    "No Common controls found via isinstance check",
                    scope=self.__class__.__name__,
                )
                log.message(
                    "Trying alternative method to identify Common parameters...",
                    scope=self.__class__.__name__,
                )

                # Get all Common parameter names from the enum
                common_param_names = {param.name for param in DrumCommonParam}
                log.message(
                    f"Known Common parameter names: {common_param_names}",
                    scope=self.__class__.__name__,
                )

                # Check each control by name
                for param, widget in editor.controls.items():
                    param_name = param.name
                    value = controls_dict.get(param_name)

                    # Check if parameter name is in Common enum
                    if param_name in common_param_names:
                        common_controls[param_name] = value
                        log.message(
                            f"Added Common parameter by name: {param_name} = {value}",
                            scope=self.__class__.__name__,
                        )
                    # Also check if it's a known Common parameter
                    elif param_name == "KIT_LEVEL":
                        common_controls[param_name] = value
                        log.message(
                            f"Force-added KIT_LEVEL by name = {value}",
                            scope=self.__class__.__name__,
                        )

                if common_controls:
                    log.message(
                        f"Found {len(common_controls)} Common controls via name matching",
                        scope=self.__class__.__name__,
                    )
                else:
                    log.error(
                        "Still no Common controls found after name matching!",
                        scope=self.__class__.__name__,
                    )
                    # Last resort: if KIT_LEVEL is in controls_dict, add it anyway
                    if "KIT_LEVEL" in controls_dict:
                        common_controls["KIT_LEVEL"] = controls_dict["KIT_LEVEL"]
                        log.message(
                            f"Force-added KIT_LEVEL from controls_dict = {common_controls['KIT_LEVEL']}",
                            scope=self.__class__.__name__,
                        )

            # Save Common section with Common address (19700000)
            # Always try to save Common if we have any Common controls or KIT_LEVEL
            if common_controls or "KIT_LEVEL" in controls_dict:
                # For Drum Common: MSB=0x19, UMB=0x70, LMB=0x00 (COMMON), LSB=0x00
                common_address = JDXiSysExAddress(
                    msb=editor.address.msb,  # 0x19 (TEMPORARY_TONE)
                    umb=editor.address.umb,  # 0x70 (DRUM_KIT)
                    lmb=JDXiSysExOffsetProgramLMB.COMMON.value,  # 0x00 (COMMON)
                    lsb=Midi.VALUE.ZERO,  # 0x00
                )

                # Ensure KIT_LEVEL is included if it exists
                if "KIT_LEVEL" in controls_dict and "KIT_LEVEL" not in common_controls:
                    common_controls["KIT_LEVEL"] = controls_dict["KIT_LEVEL"]
                    log.message(
                        f"Added KIT_LEVEL to common_controls = {common_controls['KIT_LEVEL']}",
                        scope=self.__class__.__name__,
                    )

                if common_controls:
                    self._save_editor_section(
                        editor, common_controls, common_address, temp_folder, "COMMON"
                    )
                    log.message(
                        f"Saved Common section with {len(common_controls)} parameters to address {common_address.to_bytes()}",
                        scope=self.__class__.__name__,
                    )
                else:
                    log.warning(
                        "common_controls is empty, skipping Common section save",
                        scope=self.__class__.__name__,
                    )

            # Save Partial sections - each partial has its own address
            # Note: Partial controls are typically saved by individual partial editors,
            # but if there are any in the main editor, we'll save them with the editor's address
            if partial_controls:
                # Use the editor's current address for partials (which may be a partial address)
                self._save_editor_section(
                    editor, partial_controls, editor.address, temp_folder, "PARTIAL"
                )

            # Return the Common file path if it exists, otherwise the first partial
            if common_controls:
                common_address_hex = "".join(
                    [f"{x:02x}" for x in common_address.to_bytes()]
                )
                return temp_folder / f"jdxi_tone_data_{common_address_hex}.json"
            else:
                address_hex = "".join([f"{x:02x}" for x in editor.address.to_bytes()])
                return temp_folder / f"jdxi_tone_data_{address_hex}.json"
        else:
            # Standard processing for other editors
            self.compose_message(editor)
            address_hex = "".join([f"{x:02x}" for x in editor.address.to_bytes()])
            json_temp_file = self.temp_folder / f"jdxi_tone_data_{address_hex}.json"
            self.save_json(str(json_temp_file))
            log.message(f"JSON saved successfully to {json_temp_file}")
            return json_temp_file

    def _save_editor_section(
        self,
        editor: "SynthEditor",
        controls_dict: dict,
        address: JDXiSysExAddress,
        temp_folder: Path,
        section_name: str,
    ) -> Path:
        """
        Save a specific section (Common or Modify) of an editor with a given address.

        :param editor: SynthEditor Editor instance
        :param controls_dict: dict Dictionary of parameter names to values
        :param address: RolandSysExAddress Address to use for this section
        :param temp_folder: Path Temporary folder to save the JSON
        :param section_name: str Name of the section (e.g., "COMMON", "MODIFY")
        :return: Path Path to the saved JSON file
        """
        try:
            editor_data = {SysExSection.JD_XI_HEADER: "f041100000000e"}

            # Convert address to hex string
            address_hex = "".join([f"{x:02x}" for x in address.to_bytes()])
            editor_data[SysExSection.ADDRESS] = address_hex

            # Determine TEMPORARY_AREA and SYNTH_TONE
            from jdxi_editor.midi.data.address.address import (
                JDXiSysExOffsetTemporaryToneUMB,
            )
            from jdxi_editor.ui.windows.midi.debugger import parse_sysex_byte

            editor_data[SysExSection.TEMPORARY_AREA] = parse_sysex_byte(
                address.umb, JDXiSysExOffsetTemporaryToneUMB
            )

            # Determine SYNTH_TONE based on LMB
            synth_tone_byte = address_hex[4:6]
            synth_tone_map = {
                "00": "COMMON",
                "20": "PARTIAL_1",
                "21": "PARTIAL_2",
                "22": "PARTIAL_3",
                "50": "MODIFY",
            }
            editor_data[SysExSection.SYNTH_TONE] = synth_tone_map.get(
                synth_tone_byte, "UNKNOWN_SYNTH_TONE"
            )

            # Add control values
            for k, v in controls_dict.items():
                # If the value is a list/array, take just the first value
                if isinstance(v, (list, tuple)) and len(v) > 0:
                    editor_data[k] = v[0]
                else:
                    editor_data[k] = v

            # Add tone name parameters if available
            if hasattr(editor, "tone_names") and hasattr(editor, "preset_type"):
                tone_name = editor.tone_names.get(editor.preset_type, "")
                if tone_name:
                    # Convert tone name string to TONE_NAME_1 through TONE_NAME_12
                    tone_name_padded = tone_name.ljust(12)[:12]
                    for i, char in enumerate(tone_name_padded, start=1):
                        ascii_value = ord(char)
                        editor_data[f"TONE_NAME_{i}"] = ascii_value
                    log.message(
                        f"Including tone name in JSON: '{tone_name}'",
                        scope=self.__class__.__name__,
                    )

            # Save JSON file
            json_temp_file = temp_folder / f"jdxi_tone_data_{address_hex}.json"
            with open(json_temp_file, "w", encoding="utf-8") as file_handle:
                json.dump(editor_data, file_handle, ensure_ascii=False, indent=2)

            log.message(
                f"JSON saved successfully for {section_name} section: {json_temp_file}",
                scope=self.__class__.__name__,
            )
            return json_temp_file

        except Exception as ex:
            log.error(f"Error saving {section_name} section: {ex}")
            raise
