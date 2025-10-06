jdxi_editor.midi.data.digital.partial
=====================================

.. py:module:: jdxi_editor.midi.data.digital.partial

.. autoapi-nested-parse::

   Digital Partial



Attributes
----------

.. autoapisummary::

   jdxi_editor.midi.data.digital.partial.DIGITAL_PARTIAL_NAMES


Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.digital.partial.DigitalPartialOffset
   jdxi_editor.midi.data.digital.partial.DigitalPartial


Module Contents
---------------

.. py:class:: DigitalPartialOffset

   Bases: :py:obj:`enum.IntEnum`


   Offsets for each partial's parameters


   .. py:attribute:: PARTIAL_1
      :value: 32



   .. py:attribute:: PARTIAL_2
      :value: 33



   .. py:attribute:: PARTIAL_3
      :value: 34



.. py:class:: DigitalPartial

   Bases: :py:obj:`enum.IntEnum`


   Digital synth partial numbers and structure types


   .. py:attribute:: PARTIAL_1
      :value: 1



   .. py:attribute:: PARTIAL_2
      :value: 2



   .. py:attribute:: PARTIAL_3
      :value: 3



   .. py:attribute:: SINGLE
      :value: 0



   .. py:attribute:: LAYER_1_2
      :value: 1



   .. py:attribute:: LAYER_2_3
      :value: 2



   .. py:attribute:: LAYER_1_3
      :value: 3



   .. py:attribute:: LAYER_ALL
      :value: 4



   .. py:attribute:: SPLIT_1_2
      :value: 5



   .. py:attribute:: SPLIT_2_3
      :value: 6



   .. py:attribute:: SPLIT_1_3
      :value: 7



   .. py:property:: switch_param
      :type: jdxi_editor.midi.data.parameter.digital.common.AddressParameterDigitalCommon


      Get the switch parameter for this partial


   .. py:property:: select_param
      :type: jdxi_editor.midi.data.parameter.digital.common.AddressParameterDigitalCommon


      Get the select parameter for this partial


   .. py:property:: is_partial
      :type: bool


      Returns True if this is address partial number (not address structure preset_type)


   .. py:property:: is_structure
      :type: bool


      Returns True if this is address structure preset_type (not address partial number)


   .. py:method:: get_partials() -> List[DigitalPartial]
      :classmethod:


      Get list of partial numbers (not structure types)



   .. py:method:: get_structures() -> List[DigitalPartial]
      :classmethod:


      Get list of structure types (not partial numbers)



.. py:data:: DIGITAL_PARTIAL_NAMES
   :value: ['COMMON', 'PARTIAL_1', 'PARTIAL_2', 'PARTIAL_3']


