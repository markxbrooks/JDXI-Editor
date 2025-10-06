jdxi_editor.ui.windows.midi.debugger
====================================

.. py:module:: jdxi_editor.ui.windows.midi.debugger

.. autoapi-nested-parse::

   debugger module
   ====================
   MIDI Debugger for monitoring and interacting with MIDI commands and SysEx messages.

   This class provides a graphical user interface (GUI) for sending, decoding,
   and logging MIDI messages, including SysEx messages. It allows the user to input
   MIDI commands in hexadecimal format, send them to a connected MIDI device,
   and view the decoded output for further analysis. The debugger supports both
   standard MIDI messages and Roland-specific address-based SysEx messages,
   including their parameters, values, and checksums.

   Key Features:
   - Send MIDI messages in hexadecimal format to a MIDI device.
   - Decode Roland SysEx messages with detailed information, including areas, commands, and parameters.
   - Display decoded message data in a readable table format.
   - Log responses from MIDI devices, including message sending success and failure information.
   - Validate checksum for SysEx messages to ensure message integrity.
   - Provides an easy-to-use interface with instructions, buttons, and output areas for effective debugging.

   .. attribute:: SYSEX_AREAS

      Mappings for SysEx area IDs to their human-readable names.

      :type: :py:class:`dict`

   .. attribute:: COMMANDS

      Mappings for SysEx command IDs to their human-readable names.

      :type: :py:class:`dict`

   .. attribute:: SECTIONS

      Mappings for SysEx section IDs to their human-readable names.

      :type: :py:class:`dict`

   .. attribute:: GROUPS

      Mappings for SysEx group IDs to their human-readable names.

      :type: :py:class:`dict`

   .. attribute:: PARAMETERS

      Mappings for SysEx parameter IDs to their human-readable names.

      :type: :py:class:`dict`

   .. method:: __init__(self, midi_helper, parent=None)

      Initializes the MIDI debugger with a MIDI helper.

   .. method:: _decode_sysex_new(self, message)

      Decodes a SysEx message in the new format.

   .. method:: _decode_sysex_15(self, message)

      Decodes a 15-byte SysEx address message.

   .. method:: _decode_sysex(self, message)

      Decodes a general SysEx message.

   .. method:: _decode_current(self)

      Decodes the currently entered MIDI message from the input field.

   .. method:: _send_commands(self)

      Sends the entered MIDI commands to the connected MIDI device.

   .. method:: log_response(self, text)

      Logs a response message to the response log.

   .. method:: handle_midi_response(self, message)

      Handles incoming MIDI messages and logs them.
      

   This class is useful for MIDI developers, musicians, and anyone working with MIDI devices, providing both real-time MIDI debugging and SysEx message analysis capabilities.



Attributes
----------

.. autoapisummary::

   jdxi_editor.ui.windows.midi.debugger.T


Classes
-------

.. autoapisummary::

   jdxi_editor.ui.windows.midi.debugger.EnumWithAddress
   jdxi_editor.ui.windows.midi.debugger.MIDIDebugger


Functions
---------

.. autoapisummary::

   jdxi_editor.ui.windows.midi.debugger.parse_sysex_byte
   jdxi_editor.ui.windows.midi.debugger.parse_sysex_message
   jdxi_editor.ui.windows.midi.debugger.parse_parameter


Module Contents
---------------

.. py:data:: T

.. py:class:: EnumWithAddress

   Bases: :py:obj:`Protocol`


   Base class for protocol classes.

   Protocol classes are defined as::

       class Proto(Protocol):
           def meth(self) -> int:
               ...

   Such classes are primarily used with static type checkers that recognize
   structural subtyping (static duck-typing), for example::

       class C:
           def meth(self) -> int:
               return 0

       def func(x: Proto) -> int:
           return x.meth()

       func(C())  # Passes static type check

   See PEP 544 for details. Protocol classes decorated with
   @typing.runtime_checkable act as simple-minded runtime protocols that check
   only the presence of given attributes, ignoring their type signatures.
   Protocol classes can be generic, they are defined as::

       class GenProto(Protocol[T]):
           def meth(self) -> T:
               ...


   .. py:method:: message_position() -> int
      :classmethod:


      Get the position of the message in the SysEx message.
      :return: int - the position of the message



   .. py:method:: get_parameter_by_address(address: int) -> Optional[T]
      :classmethod:


      Get the enum member by address.
      :param address: int
      :return: Optional[T] - the enum member or None if not found



.. py:function:: parse_sysex_byte(byte_value: int, enum_cls: EnumWithAddress) -> str

   Get the name of a SysEx byte value using a given enum class.

   :param byte_value: int
   :param enum_cls: EnumWithAddress
   :return: name of the parameter or "Unknown" if not found


.. py:function:: parse_sysex_message(message: bytes, enum_cls: EnumWithAddress) -> Tuple[str, int]

   Parse a SysEx message and return the name and byte value of the specified parameter.

   :param message: str
   :param enum_cls: EnumWithAddress
   :return: Tuple containing the name and byte value


.. py:function:: parse_parameter(offset: int, parameter_type: jdxi_editor.midi.data.parameter.synth.AddressParameter) -> str

   Parses JD-Xi tone parameters from SysEx data for Digital, Analog, and Digital Common types.

   :param offset: int - The offset in the SysEx message where the parameter starts.
   :param parameter_type: AddressParameter - The parameter type to parse.
   :return: str name


.. py:class:: MIDIDebugger(midi_helper: jdxi_editor.midi.io.helper.MidiIOHelper, parent: PySide6.QtWidgets.QWidget = None)

   Bases: :py:obj:`PySide6.QtWidgets.QMainWindow`


   .. py:attribute:: midi_helper


   .. py:attribute:: command_input


   .. py:attribute:: send_button


   .. py:attribute:: clear_button


   .. py:attribute:: decode_button


   .. py:attribute:: decoded_text


   .. py:attribute:: response_log


   .. py:attribute:: sysex_parser


   .. py:method:: _decode_current()

      Decode the currently entered SysEx message(s)



   .. py:method:: _decode_sysex_15(message)

      Decode a 15-byte Roland address SysEx message.



   .. py:method:: _send_commands() -> None

      Send all valid SysEx MIDI messages from user-entered text input.



   .. py:method:: send_message(match: str) -> None

      Send a SysEx message based on the provided hex string.

      :param match: str - Hex string representing the SysEx message
      :return: None



   .. py:method:: log_response(text)

      Add text to response log



   .. py:method:: handle_midi_response(message)

      Handle incoming MIDI message



