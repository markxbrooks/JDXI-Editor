jdxi_editor.midi.message
========================

.. py:module:: jdxi_editor.midi.message


Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/jdxi_editor/midi/message/areas/index
   /autoapi/jdxi_editor/midi/message/channel/index
   /autoapi/jdxi_editor/midi/message/control_change/index
   /autoapi/jdxi_editor/midi/message/effects/index
   /autoapi/jdxi_editor/midi/message/identity_request/index
   /autoapi/jdxi_editor/midi/message/jdxi/index
   /autoapi/jdxi_editor/midi/message/midi/index
   /autoapi/jdxi_editor/midi/message/program/index
   /autoapi/jdxi_editor/midi/message/program_change/index
   /autoapi/jdxi_editor/midi/message/roland/index
   /autoapi/jdxi_editor/midi/message/synths/index
   /autoapi/jdxi_editor/midi/message/sysex/index


Classes
-------

.. autoapisummary::

   jdxi_editor.midi.message.ChannelMessage
   jdxi_editor.midi.message.ProgramChangeMessage
   jdxi_editor.midi.message.MidiMessage
   jdxi_editor.midi.message.ControlChangeMessage
   jdxi_editor.midi.message.IdentityRequestMessage


Package Contents
----------------

.. py:class:: ChannelMessage

   Bases: :py:obj:`jdxi_editor.midi.message.midi.MidiMessage`


   MIDI Channel Message


   .. py:attribute:: channel
      :type:  int
      :value: 0



   .. py:attribute:: status
      :type:  int
      :value: 0



   .. py:attribute:: data1
      :type:  Optional[int]
      :value: None



   .. py:attribute:: data2
      :type:  Optional[int]
      :value: None



   .. py:method:: to_message_list() -> List[int]

      Convert to list of bytes for sending



.. py:class:: ProgramChangeMessage

   Bases: :py:obj:`jdxi_editor.midi.message.channel.ChannelMessage`


   MIDI Program Change message


   .. py:attribute:: status
      :type:  int
      :value: 192



   .. py:attribute:: program
      :type:  int
      :value: 0



   .. py:method:: __post_init__()


.. py:class:: MidiMessage

   MIDI message base class


   .. py:attribute:: MIDI_MAX_VALUE
      :value: 127



   .. py:attribute:: MIDI_STATUS_MASK
      :value: 240



   .. py:attribute:: MIDI_CHANNEL_MASK
      :value: 15



   .. py:method:: to_message_list() -> List[int]
      :abstractmethod:


      Convert to list of bytes for sending, must be implemented in subclass



   .. py:method:: to_bytes() -> bytes

      Convert to bytes for sending



   .. py:method:: to_hex_string() -> str

      Convert message to a formatted hexadecimal string.



.. py:class:: ControlChangeMessage

   Bases: :py:obj:`jdxi_editor.midi.message.midi.MidiMessage`


   MIDI Control Change message


   .. py:attribute:: channel
      :type:  int


   .. py:attribute:: controller
      :type:  int


   .. py:attribute:: value
      :type:  int


   .. py:attribute:: status
      :type:  int
      :value: 176



   .. py:method:: __post_init__()


   .. py:method:: to_message_list() -> List[int]

      Convert Control Change message to a list of bytes for sending

      :return: list



.. py:class:: IdentityRequestMessage

   Bases: :py:obj:`jdxi_editor.midi.message.midi.MidiMessage`


   MIDI Identity Request message


   .. py:attribute:: device_id
      :type:  int
      :value: 16



   .. py:method:: to_message_list() -> List[int]

      Convert to list of bytes for sending

      :return: list



