jdxi_editor.midi.data.parameter.synth
=====================================

.. py:module:: jdxi_editor.midi.data.parameter.synth

.. autoapi-nested-parse::

   SynthParameter Base Class
   =========================
   Module for representing and managing synthesizer parameters as enum values.

   This module defines the `SynthParameter` enum, which models the various parameters
   of address synthesizer with associated addresses and valid value ranges. It includes methods
   for value validation, display name formatting, and lookups by address or name.

   Classes:
       SynthParameter (Enum): Enum class representing synthesizer parameters with associated
                               addresses and valid value ranges. Provides methods for validating
                               parameter values, retrieving display names, and finding parameters
                               by their address or name.

   .. method:: display_name (property)

      Returns the display name of the parameter by formatting
      the enum name with spaces and title casing.

   .. method:: validate_value(value

      int): Validates the provided value against the parameter's valid
      range and returns the value if it is valid.

   .. method:: get_name_by_address(address

      int): Static method that returns the name of the parameter
      corresponding to address given address.

   .. method:: get_by_name(param_name

      str): Static method that returns the `SynthParameter` member
      corresponding to address given name.
      

   # Example usage
   >>> value = 0x123
   >>> offset = create_offset(value)

   >>> print(offset)  # Output: (0x00, 0x01, 0x23)



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.parameter.synth.AddressParameter


Module Contents
---------------

.. py:class:: AddressParameter(address: int, min_val: int, max_val: int)

   Bases: :py:obj:`enum.Enum`


   Base class for synthesizer parameters with associated addresses and valid value ranges.


   .. py:attribute:: CONVERSION_OFFSETS
      :type:  Dict[str, int]


   .. py:attribute:: address


   .. py:attribute:: min_val


   .. py:attribute:: max_val


   .. py:attribute:: switches
      :value: []



   .. py:attribute:: bipolar_parameters
      :value: []



   .. py:method:: __str__() -> str

      Returns a string representation of the parameter.

      :return: str string representation



   .. py:method:: __repr__() -> str

      Returns a string representation of the parameter.

      :return: str string representation



   .. py:method:: message_position()
      :classmethod:


      Returns the position of the message in the SysEx message.

      :return: int



   .. py:method:: get_parameter_by_address(address: int) -> Optional[T]
      :classmethod:


      Get the parameter member by address.

      :param address: int
      :return: parameter member or None



   .. py:property:: is_switch
      :type: bool


      Returns True if parameter is a switch (e.g. ON/OFF)

      :return: bool True if switch, False otherwise


   .. py:property:: is_bipolar
      :type: bool


      Returns True if parameter is bipolar (e.g. -64 to +63)

      :return: bool True if bipolar, False otherwise


   .. py:property:: display_name
      :type: str


      Returns the display name of the parameter by formatting the enum name with spaces

      :return: str formatted display name


   .. py:method:: validate_value(value: int) -> int

      Validate the value against the parameter's valid range.

      :param value: int value to validate
      :return: int validated value



   .. py:method:: get_name_by_address(address: int) -> Optional[str]
      :staticmethod:


      Get the parameter name by address.

      :param address: int address of the parameter
      :return: str name of the parameter or None



   .. py:method:: get_by_name(param_name: str) -> Optional[T]
      :staticmethod:


      Get the parameter member by name.

      :param param_name: str name of the parameter
      :return: parameter member or None



   .. py:method:: get_address_for_partial(partial_number: int = 0) -> Tuple[int, int]

      Get the address for the partial number.

      :param partial_number: int
      :return: int default area to be subclassed



   .. py:method:: convert_value(value: int, reverse: bool = False) -> int

      Converts value in both directions based on CONVERSION_OFFSETS

      :param value: int The value
      :param reverse: bool The reverse flag
      :return: int The converted value



   .. py:method:: convert_to_midi(slider_value: int) -> int

      Convert from display value to MIDI value

      :param slider_value: int The display value
      :return: int The MIDI value



   .. py:method:: convert_from_midi(midi_value: int) -> int

      Convert from MIDI value to display value

      :param midi_value: int The MIDI value
      :return: int The display value



   .. py:method:: get_switch_text(value: int) -> str

      Get the text representation of the switch value.

      :param value: int value to convert
      :return: str text representation



   .. py:method:: get_nibbled_size() -> int

      Get the nibbled size for the parameter

      :return: int size in nibbles



   .. py:method:: get_offset() -> tuple[int, int, int]

      Return a 3-byte tuple representing the address offset (UMB, LMB, LSB)
      for use with Address.add_offset(). The upper middle byte (UMB) is fixed at 0x00.

      :return: tuple[int, int, int] A 3-byte offset.



   .. py:method:: get_tooltip() -> str

      Get tooltip for the parameter



   .. py:property:: lsb
      :type: Optional[int]


      Return the least significant byte (LSB) of the address.

      :return: int LSB of the address


   .. py:method:: get_envelope_param_type()
      :abstractmethod:



