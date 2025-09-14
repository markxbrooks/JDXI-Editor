jdxi_editor.midi.data.control_change.analog
===========================================

.. py:module:: jdxi_editor.midi.data.control_change.analog

.. autoapi-nested-parse::

   Analog Control Change



Attributes
----------

.. autoapisummary::

   jdxi_editor.midi.data.control_change.analog.DigitalRPN_Partial1
   jdxi_editor.midi.data.control_change.analog.DigitalRPN_Partial2
   jdxi_editor.midi.data.control_change.analog.DigitalRPN_Partial3


Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.control_change.analog.AnalogControlChange
   jdxi_editor.midi.data.control_change.analog.RPNValue
   jdxi_editor.midi.data.control_change.analog.AnalogRPN
   jdxi_editor.midi.data.control_change.analog.PartialRPNValue
   jdxi_editor.midi.data.control_change.analog.PartialRPNValue


Functions
---------

.. autoapisummary::

   jdxi_editor.midi.data.control_change.analog.make_digital_rpn


Module Contents
---------------

.. py:class:: AnalogControlChange

   Bases: :py:obj:`jdxi_editor.midi.data.control_change.base.ControlChange`


   Analog synth CC parameters


   .. py:attribute:: CUTOFF
      :value: 102



   .. py:attribute:: RESONANCE
      :value: 105



   .. py:attribute:: LEVEL
      :value: 117



   .. py:attribute:: LFO_RATE
      :value: 16



   .. py:method:: get_display_value(param: int, value: int) -> str
      :staticmethod:


      Convert raw value to display value



.. py:class:: RPNValue

   Represents a MIDI RPN value with its MSB, LSB, and value range.


   .. py:attribute:: msb_lsb
      :type:  Tuple[int, int]


   .. py:attribute:: value_range
      :type:  Tuple[int, int]


   .. py:method:: midi_bytes(value: int)

      Generate CC messages for this RPN and a given value.



.. py:class:: AnalogRPN

   Bases: :py:obj:`enum.Enum`


   Analog synth RPN parameters with their MSB, LSB, and value range.


   .. py:attribute:: ENVELOPE


   .. py:attribute:: LFO_SHAPE


   .. py:attribute:: LFO_PITCH_DEPTH


   .. py:attribute:: LFO_FILTER_DEPTH


   .. py:attribute:: LFO_AMP_DEPTH


   .. py:attribute:: PULSE_WIDTH


.. py:class:: PartialRPNValue

   Represents a MIDI RPN value with base MSB/LSB, value range, and partial.


   .. py:attribute:: base_msb_lsb
      :type:  Tuple[int, int]


   .. py:attribute:: value_range
      :type:  Tuple[int, int]


   .. py:attribute:: partial
      :type:  int


   .. py:property:: msb_lsb
      :type: Tuple[int, int]


      Return the dynamically adjusted MSB/LSB based on the partial number.


   .. py:method:: __post_init__() -> None


   .. py:method:: midi_bytes(value: int) -> list[tuple[Any, int, int]]

      Generate CC messages for this RPN and a given value.



.. py:class:: PartialRPNValue

   .. py:attribute:: base_msb_lsb
      :type:  Tuple[int, int]


   .. py:attribute:: value_range
      :type:  Tuple[int, int]


   .. py:attribute:: partial
      :type:  int


   .. py:property:: msb_lsb
      :type: Tuple[int, int]



.. py:function:: make_digital_rpn(partial: int) -> shiboken6.Shiboken.Object

   make_digital_rpn

   :param partial: int
   :return: Object


.. py:data:: DigitalRPN_Partial1

.. py:data:: DigitalRPN_Partial2

.. py:data:: DigitalRPN_Partial3

