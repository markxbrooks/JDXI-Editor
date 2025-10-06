jdxi_editor.ui.editors.synth.base
=================================

.. py:module:: jdxi_editor.ui.editors.synth.base

.. autoapi-nested-parse::

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



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.synth.base.SynthBase


Module Contents
---------------

.. py:class:: SynthBase(midi_helper: Optional[jdxi_editor.midi.io.helper.MidiIOHelper] = None, parent: PySide6.QtWidgets.QWidget = None)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   base class for all synth editors


   .. py:attribute:: preset_type
      :value: None



   .. py:attribute:: parent
      :value: None



   .. py:attribute:: tone_names


   .. py:attribute:: partial_editors


   .. py:attribute:: sysex_data
      :value: None



   .. py:attribute:: address
      :value: None



   .. py:attribute:: partial_number
      :value: None



   .. py:attribute:: bipolar_parameters
      :value: []



   .. py:attribute:: controls
      :type:  Dict[jdxi_editor.midi.data.parameter.synth.AddressParameter, PySide6.QtWidgets.QWidget]


   .. py:attribute:: _midi_helper
      :value: None



   .. py:attribute:: midi_requests
      :value: []



   .. py:attribute:: sysex_composer


   .. py:property:: midi_helper
      :type: jdxi_editor.midi.io.helper.MidiIOHelper



   .. py:method:: send_raw_message(message: bytes) -> bool

      Send a raw MIDI message using the MIDI helper.

      :param message: bytes MIDI message to send
      :return: bool True on success, False otherwise



   .. py:method:: edit_tone_name()

      edit_tone_name

      :return: None



   .. py:method:: data_request(channel=None, program=None)

      Request the current value of the NRPN parameter from the device.

      :param channel: int MIDI channel to send the request on (discarded)
      :param program: int Program number to request data for (discarded)



   .. py:method:: _on_midi_message_received(message: mido.Message) -> None

      Handle incoming MIDI messages

      :param message: mido.Message MIDI message received
      :return: None



   .. py:method:: send_tone_name(parameter_cls: jdxi_editor.midi.data.parameter.synth.AddressParameter, tone_name: str) -> None

      send_tone_name

      :param tone_name: str Name of the Tone/preset
      :param parameter_cls: AddressParameter
      Send the characters of the tone name to SysEx parameters.



   .. py:method:: send_midi_parameter(param: jdxi_editor.midi.data.parameter.synth.AddressParameter, value: int, address: jdxi_editor.midi.data.address.address.RolandSysExAddress = None) -> bool

      Send MIDI parameter with error handling

      :param address: RolandSysExAddress
      :param param: AddressParameter the parameter to send
      :param value: int value to send
      :return: bool True on success, False otherwise



   .. py:method:: get_controls_as_dict()

      Get the current values of self.controls as a dictionary.

      :returns: dict A dictionary of control parameter names and their values.



   .. py:method:: _on_parameter_changed(param: jdxi_editor.midi.data.parameter.synth.AddressParameter, display_value: int, address: jdxi_editor.midi.data.address.address.RolandSysExAddress = None) -> None

      Handle parameter change event, convert display value to MIDI value,

      :param param: AddressParameter Parameter that was changed
      :param display_value: int Display value from the UI control
      :return: None



   .. py:method:: _create_parameter_slider(param: jdxi_editor.midi.data.parameter.synth.AddressParameter, label: str, vertical: bool = False, initial_value: Optional[int] = 0, address: jdxi_editor.midi.data.address.address.RolandSysExAddress = None, show_value_label: bool = True) -> jdxi_editor.ui.widgets.slider.Slider

      Create a slider for an address parameter with proper display conversion.

      :param param: AddressParameter Parameter to create slider for
      :param label: str label for the slider
      :param initial_value: int initial value for the slider
      :param vertical: bool whether the slider is vertical
      :param address: RolandSysExAddress
      :param show_value_label: str whether to show the value label
      :return: Slider



   .. py:method:: _create_parameter_combo_box(param: jdxi_editor.midi.data.parameter.synth.AddressParameter, label: str = None, options: list = None, values: list = None, show_label: bool = True) -> jdxi_editor.ui.widgets.combo_box.combo_box.ComboBox

      Create a combo box for an address parameter with options and values.

      :param param: AddressParameter
      :param label: str label for the combo box
      :param options: list of options to display in the combo box
      :param values: list of values corresponding to the options
      :param show_label: bool whether to show the label
      :return: ComboBox



   .. py:method:: _create_parameter_spin_box(param: jdxi_editor.midi.data.parameter.synth.AddressParameter, label: str = None) -> jdxi_editor.ui.widgets.spin_box.spin_box.SpinBox

      Create address spin box for address parameter with proper display conversion

      :param param: AddressParameter Parameter to create spin box for
      :param label: str label for the spin box
      :return: SpinBox



   .. py:method:: _create_parameter_switch(param: jdxi_editor.midi.data.parameter.synth.AddressParameter, label: str, values: list[str]) -> jdxi_editor.ui.widgets.switch.switch.Switch

      Create a switch for an address parameter with specified label and values.

      :param param: AddressParameter Parameter to create switch for
      :param label: str label for the switch
      :param values: list of values for the switch
      :return: Switch



   .. py:method:: _init_synth_data(synth_type: jdxi_editor.jdxi.synth.type.JDXiSynth = JDXiSynth.DIGITAL_SYNTH_1, partial_number: Optional[int] = 0)

      Initialize synth-specific data.



   .. py:method:: _update_slider(param: jdxi_editor.midi.data.parameter.synth.AddressParameter, midi_value: int, successes: list = None, failures: list = None, slider: PySide6.QtWidgets.QWidget = None) -> None

      Update slider based on parameter and value.

      :param param: AddressParameter
      :param midi_value: int value
      :param successes: list
      :param failures: list
      :return: None



   .. py:method:: _update_switch(param: jdxi_editor.midi.data.parameter.synth.AddressParameter, midi_value: int, successes: list = None, failures: list = None) -> None

      Update switch based on parameter and value.

      :param param: AddressParameter
      :param midi_value: int value
      :param successes: list
      :param failures: list
      :return: None



   .. py:method:: _update_partial_slider(partial_no: int, param: jdxi_editor.midi.data.parameter.synth.AddressParameter, value: int, successes: list = None, failures: list = None) -> None

      Update the slider for a specific partial based on the parameter and value.

      :param partial_no: int
      :param param: AddressParameter
      :param value: int
      :param successes: list list of successful updates
      :param failures: list list of failed updates
      :return: None



