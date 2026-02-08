"""
Synth Control Base Module

This module defines the `SynthControlBase` class, a Qt-based widget that provides MIDI
control functionality for synthesizer parameters in the JD-Xi editor.

It facilitates:
- Sending and receiving MIDI SysEx messages.
- Handling parameter updates through UI elements (sliders, combo boxes, spin boxes, switches).
- Managing MIDI helper instances for communication.

Dependencies:
- PySide6 for GUI components.
- jdxi_editor.midi for MIDI communication.
- jdxi_editor.ui.widgets for UI elements.

Classes:
- SynthControlBase: A base widget for controlling synth parameters via MIDI.
"""

import threading
from typing import Dict, Optional

import mido
from decologr import Decologr as log
from picomidi.sysex.parameter.address import AddressParameter
from PySide6.QtWidgets import QTabWidget, QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.core.synth.factory import create_synth_data
from jdxi_editor.core.synth.type import JDXiSynth
from jdxi_editor.log.slider_parameter import log_slider_parameters
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.control_change.base import ControlChange
from jdxi_editor.midi.data.parameter.digital.spec import TabDefinitionMixin
from jdxi_editor.midi.io.delay import send_with_delay
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.sysex.composer import JDXiSysExComposer
from jdxi_editor.ui.widgets.combo_box.combo_box import ComboBox
from jdxi_editor.ui.widgets.controls.registry import ControlRegistry
from jdxi_editor.ui.widgets.slider import Slider
from jdxi_editor.ui.widgets.spin_box.spin_box import SpinBox
from jdxi_editor.ui.widgets.switch.switch import Switch
from jdxi_editor.ui.windows.patch.name_editor import PatchNameEditor


class SynthBase(QWidget):
    """base class for all synth editors"""

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        parent: QWidget = None,
        address: Optional[RolandSysExAddress] = None,
    ):
        """
        Initialize the SynthBase editor with MIDI helper and parent widget.

        :param midi_helper: Optional[MidiIOHelper] instance for MIDI communication
        :param parent: QWidget Parent widget for this editor
        :param address: Optional[RolandSysExAddress] Address for MIDI communication (can be set later)
        """
        super().__init__(parent)
        self.midi_channel: int | None = None  # Default to Digital
        self.tab_widget: QTabWidget | None = None
        self.preset_type = None
        self.parent = parent
        # --- Store all Tone/Preset names for access by Digital Displays
        self.tone_names = {
            JDXiSynth.DIGITAL_SYNTH_1: "",
            JDXiSynth.DIGITAL_SYNTH_2: "",
            JDXiSynth.ANALOG_SYNTH: "",
            JDXiSynth.DRUM_KIT: "",
        }
        self.controls = ControlRegistry()
        self._control_registries: Dict[tuple, ControlRegistry] = {}
        self.partial_editors = {}
        self.sysex_data = None
        self.address: Optional[RolandSysExAddress] = address
        self.partial_number = None
        self.bipolar_parameters = []
        self.analog: bool = False
        self._midi_helper = midi_helper
        self.midi_requests = []
        self.sysex_composer = JDXiSysExComposer()

    @property
    def midi_helper(self) -> MidiIOHelper:
        return self._midi_helper

    @midi_helper.setter
    def midi_helper(self, helper: MidiIOHelper) -> None:
        """
        Set the MIDI helper for sending and receiving MIDI messages.

        :param helper: MidiIOHelper instance to use for MIDI communication
        :return: None
        """
        self._midi_helper = helper

    def get_control_registry(
        self, synth_type: str, partial_no: int = 1
    ) -> ControlRegistry:
        """
        Return the ControlRegistry for a given part/partial (Analog, Digital1, Digital2, Drums).
        One registry per (synth_type, partial_no); creates on first use.

        :param synth_type: JDXiSynth.ANALOG_SYNTH, DIGITAL_SYNTH_1, DIGITAL_SYNTH_2, DRUM_KIT
        :param partial_no: Partial number (e.g. 1, 2 for digital; 1..N for drums)
        :return: ControlRegistry for that partial
        """
        key = (synth_type, partial_no)
        if key not in self._control_registries:
            self._control_registries[key] = ControlRegistry()
        return self._control_registries[key]

    def _get_address_from_hierarchy(
        self, parameter_cls: AddressParameter = None
    ) -> Optional[RolandSysExAddress]:
        """
        Get address from self, parent, or parent.parent if available.
        If no address is found and we're dealing with a ProgramEditor or ProgramCommonParam,
        create a program address.

        :param parameter_cls: Optional[AddressParameter] Parameter class hint (e.g., ProgramCommonParam)
        :return: Optional[RolandSysExAddress] The address if found, None otherwise
        """
        # Check if we need a program address based on parameter class or editor type
        needs_program_address = False
        is_program_editor = (
            hasattr(self, "__class__") and "ProgramEditor" in self.__class__.__name__
        )

        if parameter_cls is not None:
            from jdxi_editor.midi.data.parameter.program.common import (
                ProgramCommonParam,
            )

            if parameter_cls == ProgramCommonParam or (
                hasattr(parameter_cls, "__name__")
                and "ProgramCommonParam" in parameter_cls.__name__
            ):
                needs_program_address = True

        # If we're in a ProgramEditor or using ProgramCommonParam, we need a program address
        needs_program_address = needs_program_address or is_program_editor

        # Try self first
        if hasattr(self, "address") and self.address is not None:
            if isinstance(self.address, RolandSysExAddress) and hasattr(
                self.address, "add_offset"
            ):
                return self.address

        # If self is ProgramEditor and has no address, create one
        if is_program_editor:
            from jdxi_editor.midi.data.address.program import ProgramCommonAddress

            return ProgramCommonAddress()

        # Try parent
        if hasattr(self, "parent") and self.parent is not None:
            if hasattr(self.parent, "address") and self.parent.address is not None:
                if isinstance(self.parent.address, RolandSysExAddress) and hasattr(
                    self.parent.address, "add_offset"
                ):
                    return self.parent.address
            # If parent is ProgramEditor and has no address, create one
            if (
                hasattr(self.parent, "__class__")
                and "ProgramEditor" in self.parent.__class__.__name__
            ):
                from jdxi_editor.midi.data.address.program import ProgramCommonAddress

                return ProgramCommonAddress()

        # Try parent.parent
        if (
            hasattr(self, "parent")
            and self.parent is not None
            and hasattr(self.parent, "parent")
            and self.parent.parent is not None
        ):
            if (
                hasattr(self.parent.parent, "address")
                and self.parent.parent.address is not None
            ):
                if isinstance(
                    self.parent.parent.address, RolandSysExAddress
                ) and hasattr(self.parent.parent.address, "add_offset"):
                    return self.parent.parent.address
            # If parent.parent is ProgramEditor and has no address, create one
            if (
                hasattr(self.parent.parent, "__class__")
                and "ProgramEditor" in self.parent.parent.__class__.__name__
            ):
                from jdxi_editor.midi.data.address.program import ProgramCommonAddress

                return ProgramCommonAddress()

        return None

    def send_control_change(self, control_change: ControlChange, value: int):
        """Send MIDI CC message"""
        if self.midi_helper:
            control_change_number = (
                control_change.value
                if isinstance(control_change, ControlChange)
                else control_change
            )
            self.midi_helper.send_control_change(
                control_change_number, value, self.midi_channel
            )

    def send_raw_message(self, message: bytes) -> bool:
        """
        Send a raw MIDI message using the MIDI helper.

        :param message: bytes MIDI message to send
        :return: bool True on success, False otherwise
        """
        if not self._midi_helper:
            log.message("MIDI helper not initialized")
            return False
        return self._midi_helper.send_raw_message(message)

    def edit_tone_name(self):
        """
        edit_tone_name

        :return: None
        """
        if not hasattr(self, "synth_data") or self.synth_data is None:
            log.error("Cannot edit tone name: synth_data is not initialized")
            return
        if self.preset_type is None:
            log.error("Cannot edit tone name: preset_type is not set")
            return
        # Try to get address from hierarchy (self, parent, or parent.parent)
        # We'll determine parameter_cls later, so pass None for now
        address = self._get_address_from_hierarchy(parameter_cls=None)
        if address is None:
            log.error(
                "Cannot edit tone name: address is not initialized in self, parent, or parent.parent"
            )
            return
        tone_name = self.tone_names.get(self.preset_type, "")
        tone_name_dialog = PatchNameEditor(current_name=tone_name)
        if hasattr(self, "partial_parameters"):
            parameter_cls = self.synth_data.partial_parameters
        else:
            parameter_cls = self.synth_data.common_parameters
        if parameter_cls is None:
            log.error("Cannot edit tone name: parameter class is not available")
            return
        if tone_name_dialog.exec():  # If the user clicks Save
            sysex_string = tone_name_dialog.get_sysex_string()
            log.message(f"SysEx string: {sysex_string}")
            self.send_tone_name(parameter_cls, sysex_string, address=address)
            self.data_request()

    def data_request(self, channel=None, program=None):
        """
        Request the current value of the NRPN parameter from the device.

        :param channel: int MIDI channel to send the request on (discarded)
        :param program: int Program number to request data for (discarded)
        """
        threading.Thread(
            target=send_with_delay,
            args=(
                self._midi_helper,
                self.midi_requests,
            ),
        ).start()

    def _build_sliders(self, specs: list["SliderSpec"]):
        """build sliders"""
        return [
            self._create_parameter_slider(
                spec.param,
                spec.label,
                vertical=spec.vertical,
            )
            for spec in specs
        ]

    def _build_combo_boxes(self, specs: list["ComboBoxSpec"]):
        """build combo boxes"""
        return [
            self._create_parameter_combo_box(
                spec.param, spec.label, spec.options, spec.values
            )
            for spec in specs
        ]

    def _build_switches(self, specs: list["SwitchSpec"]):
        return [
            self._create_parameter_switch(spec.param, spec.label, spec.options)
            for spec in specs
        ]

    def _on_midi_message_received(self, message: mido.Message) -> None:
        """
        Handle incoming MIDI messages

        :param message: mido.Message MIDI message received
        :return: None
        """
        if not message.type == "clock":
            log.message(f"MIDI message: {message}")
            self.blockSignals(True)
            self.data_request()
            self.blockSignals(False)

    def send_tone_name(
        self,
        parameter_cls: AddressParameter,
        tone_name: str,
        address: RolandSysExAddress = None,
    ) -> None:
        """
        send_tone_name

        :param parameter_cls: AddressParameter Parameter class containing TONE_NAME parameters
        :param tone_name: str Name of the Tone/preset
        :param address: Optional[RolandSysExAddress] Address to use, or None to get from hierarchy
        Send the characters of the tone name to SysEx parameters.
        """
        # --- Get address from hierarchy if not provided
        if address is None:
            address = self._get_address_from_hierarchy(parameter_cls=parameter_cls)
        if address is None:
            log.error(
                "Cannot send tone name: address is not available in self, parent, or parent.parent"
            )
            return

        # --- Ensure the tone name is exactly 12 characters (pad with spaces if shorter)
        tone_name = tone_name.ljust(12)[:12]

        # --- Iterate over characters and send them to corresponding parameters
        for i, char in enumerate(tone_name):
            ascii_value = ord(char)
            try:
                param = getattr(parameter_cls, f"TONE_NAME_{i + 1}")
                if param is None:
                    log.warning(
                        f"TONE_NAME_{i + 1} not found in {parameter_cls.__name__}, skipping"
                    )
                    continue
                self.send_midi_parameter(param, ascii_value, address=address)
            except AttributeError:
                log.warning(
                    f"TONE_NAME_{i + 1} not found in {parameter_cls.__name__}, skipping"
                )
                continue

    def send_midi_parameter(
        self, param: AddressParameter, value: int, address: RolandSysExAddress = None
    ) -> bool:
        """
        Send MIDI parameter with error handling

        :param address: RolandSysExAddress
        :param param: AddressParameter the parameter to send
        :param value: int value to send
        :return: bool True on success, False otherwise
        """
        if not address:
            # Try to get address from hierarchy (self, parent, or parent.parent)
            address = self._get_address_from_hierarchy(parameter_cls=None)
        if address is None:
            log.error(
                f"Cannot send MIDI parameter {param.name if param else 'Unknown'}: "
                f"address is not available in self, parent, or parent.parent"
            )
            return False
        # Validate that address is a proper RolandSysExAddress instance with required methods
        if not isinstance(address, RolandSysExAddress):
            log.error(
                f"Cannot send MIDI parameter {param.name if param else 'Unknown'}: "
                f"address is not a RolandSysExAddress instance (got {type(address)})"
            )
            return False
        if not hasattr(address, "add_offset"):
            log.error(
                f"Cannot send MIDI parameter {param.name if param else 'Unknown'}: "
                f"address does not have add_offset method"
            )
            return False
        if param is None:
            log.error("Cannot send MIDI parameter: parameter is None")
            return False
        if not getattr(self, "sysex_composer", None) or not callable(
            getattr(self.sysex_composer, "compose_message", None)
        ):
            log.error(
                f"Cannot send MIDI parameter {param.name}: sysex_composer or compose_message not available"
            )
            return False
        if not getattr(self, "_midi_helper", None) or not callable(
            getattr(self._midi_helper, "send_midi_message", None)
        ):
            log.error(
                f"Cannot send MIDI parameter {param.name}: midi_helper or send_midi_message not available"
            )
            return False
        try:
            # --- Ensure value is an integer (handle enums, strings, floats)
            def safe_int(val):
                # --- Reject parameter specs / tuples (e.g. param passed as value by mistake)
                if isinstance(val, (tuple, list)):
                    log.error(
                        f"Cannot convert value (parameter spec?) to int for parameter {param.name}"
                    )
                    return 0
                # --- Check for enums FIRST (IntEnum inherits from int, so isinstance check must come after)
                if hasattr(val, "value") and not isinstance(
                    val, type
                ):  # --- Handle enums (but not enum classes)
                    enum_val = val.value
                    # --- Ensure we get the actual integer value, not the enum
                    if isinstance(enum_val, int) and not hasattr(enum_val, "value"):
                        return enum_val
                    # --- If enum_val is still an enum, recurse
                    if hasattr(enum_val, "value"):
                        return safe_int(enum_val)
                    try:
                        return int(float(enum_val))  # Handle string enum values
                    except (ValueError, TypeError):
                        log.error(
                            f"Cannot convert enum value {enum_val} to int for parameter {param.name}"
                        )
                        return 0
                if isinstance(val, int):
                    return val
                if val is None:
                    return 0
                try:
                    return int(float(val))  # --- Handle floats and strings
                except (ValueError, TypeError):
                    log.error(
                        f"Cannot convert value {val} to int for parameter {param.name}"
                    )
                    return 0

            midi_value = safe_int(value)
            sysex_message = self.sysex_composer.compose_message(
                address=address, param=param, value=midi_value
            )
            result = self._midi_helper.send_midi_message(sysex_message)
            return bool(result)
        except Exception as ex:
            log.error(f"MIDI error setting {param.name}: {ex}")
            return False

    def get_controls_as_dict(self):
        """
        Get the current values of self.controls as a dictionary.

        :returns: dict A dictionary of control parameter names and their values.
        """
        try:
            controls_data = {}
            for param, widget in self.controls.items():
                # --- Get value from widget - all custom widgets have a value() method
                # --- (Slider, ComboBox, SpinBox, Switch all implement value())
                if hasattr(widget, "value"):
                    controls_data[param.name] = widget.value()
                elif hasattr(widget, "isChecked") and hasattr(widget, "waveform"):
                    # --- Handle waveform buttons (AnalogWaveformButton, etc.)
                    # --- Check if this button is checked, and if so, use its waveform value
                    if widget.isChecked():
                        controls_data[param.name] = widget.waveform.STATUS
                    # --- If not checked, don't add it - the checked button will be found by the editor's override
                elif hasattr(widget, "isChecked"):
                    # --- QPushButton or other checkable widgets
                    controls_data[param.name] = 1 if widget.isChecked() else 0
                else:
                    # Fallback for unexpected widget types
                    log.warning(
                        f"Widget for {param.name} has no value() method: {type(widget)}"
                    )
                    controls_data[param.name] = 0
            return controls_data
        except Exception as ex:
            log.error(f"Failed to get controls: {ex}")
            return {}

    def _add_tab(
        self,
        *,
        key: TabDefinitionMixin,
        widget: QWidget,
    ) -> None:
        # Handle both regular icons and generated waveform icons
        from jdxi_editor.midi.data.digital.oscillator import WaveForm

        # Check if icon is a WaveformType value (string that matches WaveformType attributes)
        waveform_type_values = {
            WaveForm.ADSR,
            WaveForm.UPSAW,
            WaveForm.SQUARE,
            WaveForm.PWSQU,
            WaveForm.TRIANGLE,
            WaveForm.SINE,
            WaveForm.SAW,
            WaveForm.SPSAW,
            WaveForm.PCM,
            WaveForm.NOISE,
            WaveForm.LPF_FILTER,
            WaveForm.HPF_FILTER,
            WaveForm.BYPASS_FILTER,
            WaveForm.BPF_FILTER,
            WaveForm.FILTER_SINE,
        }

        # Handle icon - could be a string (qtawesome icon name) or WaveformType value
        if isinstance(key.icon, str) and key.icon in waveform_type_values:
            # Use generated icon for waveform types
            icon = JDXi.UI.Icon.get_generated_icon(key.icon)
        elif isinstance(key.icon, str) and key.icon.startswith("mdi."):
            # Direct qtawesome icon name (e.g., "mdi.numeric-1-circle-outline")
            icon = JDXi.UI.Icon.get_icon(key.icon, color=JDXi.UI.Style.GREY)
        else:
            # Use regular icon from registry
            icon = JDXi.UI.Icon.get_icon(key.icon, color=JDXi.UI.Style.GREY)

        self.tab_widget.addTab(
            widget,
            icon,
            key.label,
        )
        setattr(self, key.attr_name, widget)

    def _on_parameter_changed(
        self,
        param: AddressParameter,
        display_value: int,
        address: RolandSysExAddress = None,
    ) -> None:
        """
        Handle parameter change event, convert display value to MIDI value,

        :param param: AddressParameter Parameter that was changed
        :param display_value: int Display value from the UI control
        :return: None
        """
        try:
            # --- Send MIDI message
            if not address:
                address = self.address
            if not callable(getattr(self, "send_midi_parameter", None)):
                return
            if not self.send_midi_parameter(param, display_value, address):
                log.message(f"Failed to send parameter {param.name}")
        except Exception as ex:
            log.error(f"Error handling parameter {param.name}: {ex}")

    def _create_parameter_slider(
        self,
        param: AddressParameter,
        label: str,
        vertical: bool = False,
        initial_value: Optional[int] = 0,
        address: RolandSysExAddress = None,
        show_value_label: bool = True,
    ) -> Slider:
        """
        Create a slider for an address parameter with proper display conversion.

        :param param: AddressParameter Parameter to create slider for
        :param label: str label for the slider
        :param initial_value: int initial value for the slider
        :param vertical: bool whether the slider is vertical
        :param address: RolandSysExAddress
        :param show_value_label: str whether to show the value label
        :return: Slider
        """
        get_display_value = getattr(param, "get_display_value", None)
        if callable(get_display_value):
            display_min, display_max = get_display_value()
        else:
            display_min, display_max = param.min_val, param.max_val
        get_tooltip = getattr(param, "get_tooltip", None)
        if callable(get_tooltip):
            tooltip = get_tooltip()
        else:
            tooltip = f"{param.name} ({display_min} to {display_max})"

        slider = Slider(
            label,
            min_value=display_min,
            max_value=display_max,
            midi_helper=self.midi_helper,
            vertical=vertical,
            show_value_label=show_value_label,
            is_bipolar=param.is_bipolar,
            tooltip=tooltip,
        )
        if not address:
            address = self.address
        if param.name in self.bipolar_parameters or param.is_bipolar:
            slider.setValueDisplayFormat(lambda v: f"{v:+d}" if v != 0 else "0")
            slider.setCenterMark(0)
            slider.setTickPosition(Slider.TickPosition.TicksBothSides)
            slider.setTickInterval((display_max - display_min) // 4)
        slider.valueChanged.connect(
            lambda v: self._on_parameter_changed(param, v, address)
        )
        self.controls[param] = slider
        return slider

    def _create_parameter_combo_box(
        self,
        param: AddressParameter,
        label: str = None,
        options: list = None,
        values: list = None,
        show_label: bool = True,
    ) -> ComboBox:
        """
        Create a combo box for an address parameter with options and values.

        :param param: AddressParameter
        :param label: str label for the combo box
        :param options: list of options to display in the combo box
        :param values: list of values corresponding to the options (or options if options is None)
        :param show_label: bool whether to show the label
        :return: ComboBox
        """
        # Handle case where values is provided but options is None
        # --- If values is a list of strings, treat it as options and generate numeric values
        if options is None and values is not None:
            if isinstance(values, list) and len(values) > 0:
                # Check if values contains strings (likely options)
                if isinstance(values[0], str):
                    options = values
                    # Generate numeric values from indices
                    values = list(range(len(options)))
                else:
                    # Values are numeric, generate options from values
                    options = [str(v) for v in values]

        # --- Ensure options is not None (provide empty list as fallback)
        if options is None:
            options = []
            if values is None:
                values = []

        if hasattr(param, "get_display_value"):
            display_min, display_max = param.get_display_value()
        else:
            display_min, display_max = param.min_val, param.max_val
        if hasattr(param, "get_tooltip"):
            tooltip = param.get_tooltip()
        else:
            tooltip = f"{param.name} ({display_min} to {display_max})"
        combo_box = ComboBox(
            label=label,
            options=options,
            values=values,
            show_label=show_label,
            tooltip=tooltip,
        )
        combo_box.valueChanged.connect(lambda v: self._on_parameter_changed(param, v))
        self.controls[param] = combo_box
        return combo_box

    def _create_parameter_spin_box(
        self, param: AddressParameter, label: str = None
    ) -> SpinBox:
        """
        Create address spin box for address parameter with proper display conversion

        :param param: AddressParameter Parameter to create spin box for
        :param label: str label for the spin box
        :return: SpinBox
        """
        if hasattr(param, "get_display_value"):
            display_min, display_max = param.get_display_value()
        else:
            display_min, display_max = param.min_val, param.max_val
        if hasattr(param, "get_tooltip"):
            tooltip = param.get_tooltip()
        else:
            tooltip = f"{param.name} ({display_min} to {display_max})"
        spin_box = SpinBox(
            label=label, low=display_min, high=display_max, tooltip=tooltip
        )
        # --- Connect value changed signal
        spin_box.valueChanged.connect(lambda v: self._on_parameter_changed(param, v))
        # --- Store control reference
        self.controls[param] = spin_box
        return spin_box

    def _create_parameter_switch(
        self, param: AddressParameter, label: str, values: list[str]
    ) -> Switch:
        """
        Create a switch for an address parameter with specified label and values.

        :param param: AddressParameter Parameter to create switch for
        :param label: str label for the switch
        :param values: list of values for the switch
        :return: Switch
        """
        if hasattr(param, "get_display_value"):
            display_min, display_max = param.get_display_value()
        else:
            display_min, display_max = param.min_val, param.max_val
        if hasattr(param, "get_tooltip"):
            tooltip = param.get_tooltip()
        else:
            tooltip = f"{param.name} ({display_min} to {display_max})"
        switch = Switch(label=label, values=values, tooltip=tooltip)
        switch.valueChanged.connect(lambda v: self._on_parameter_changed(param, v))
        self.controls[param] = switch
        return switch

    def _init_synth_data(
        self,
        synth_type: str = JDXiSynth.DIGITAL_SYNTH_1,
        partial_number: Optional[int] = 0,
    ):
        """Initialize synth-specific data."""
        from jdxi_editor.core.synth.factory import create_synth_data

        self.synth_data = create_synth_data(synth_type, partial_number=partial_number)
        # Dynamically assign attributes
        for attr in [
            "address",
            "preset_type",
            "instrument_default_image",
            "instrument_icon_folder",
            "presets",
            "preset_list",
            "midi_requests",
            "midi_channel",
            "common_parameters",
            "partial_parameters",
        ]:
            if hasattr(self.synth_data, attr):
                setattr(self, attr, getattr(self.synth_data, attr))

    def _update_slider(
        self,
        param: AddressParameter,
        midi_value: int,
        successes: list = None,
        failures: list = None,
        slider: QWidget = None,
    ) -> None:
        """
        Update slider based on parameter and value.

        :param param: AddressParameter
        :param midi_value: int value
        :param successes: list
        :param failures: list
        :return: None
        """
        if slider is None:
            slider = self.controls.get(param)
        if slider:
            if hasattr(param, "convert_from_midi"):
                slider_value = param.convert_from_midi(midi_value)
            else:
                slider_value = midi_value
            log_slider_parameters(self.address, param, midi_value, slider_value)
            slider.blockSignals(True)
            slider.setValue(midi_value)
            slider.blockSignals(False)
            successes.append(param.name)
        else:
            failures.append(param.name)

    def _update_switch(
        self,
        param: AddressParameter,
        midi_value: int,
        successes: list = None,
        failures: list = None,
    ) -> None:
        """
        Update switch based on parameter and value.

        :param param: AddressParameter
        :param midi_value: int value
        :param successes: list
        :param failures: list
        :return: None
        """
        if not midi_value:
            return
        switch = self.controls.get(param)
        try:
            midi_value = int(midi_value)
            if switch:
                switch.blockSignals(True)
                switch.setValue(midi_value)
                switch.blockSignals(False)
                successes.append(param.name)
                log.parameter(f"Updated {midi_value} for", param)
            else:
                failures.append(param.name)
        except Exception as ex:
            log.error(
                f"Error {ex} occurred setting switch {param.name} to {midi_value}"
            )
            failures.append(param.name)

    def _update_partial_slider(
        self,
        partial_no: int,
        param: AddressParameter,
        value: int,
        successes: list = None,
        failures: list = None,
    ) -> None:
        """
        Update the slider for a specific partial based on the parameter and value.

        :param partial_no: int
        :param param: AddressParameter
        :param value: int
        :param successes: list list of successful updates
        :param failures: list list of failed updates
        :return: None
        """
        if value is None:
            return

        partial_editor = self.partial_editors.get(partial_no)
        if not partial_editor:
            failures.append(param.name)
            return

        # Resolve control: try lfo_depth_controls, then controls by param, then by param name
        slider = None
        if hasattr(partial_editor, "lfo_depth_controls"):
            slider = partial_editor.lfo_depth_controls.get(param)
        if slider is None and hasattr(partial_editor, "controls"):
            slider = partial_editor.controls.get(param)
        if slider is None and hasattr(partial_editor, "controls"):
            param_name = getattr(param, "name", None)
            if param_name:
                for k, w in partial_editor.controls.items():
                    if getattr(k, "name", None) == param_name:
                        slider = w
                        break

        if not slider:
            failures.append(param.name)
            return
        synth_data = create_synth_data(self.synth_data.preset_type, partial_no)
        self.address.lmb = synth_data.lmb
        slider_value = param.convert_from_midi(value)
        log_slider_parameters(self.address, param, value, slider_value)
        if hasattr(slider, "blockSignals"):
            slider.blockSignals(True)
        if hasattr(slider, "setValue"):
            slider.setValue(slider_value)
        if hasattr(slider, "blockSignals"):
            slider.blockSignals(False)
        successes.append(param.name)
