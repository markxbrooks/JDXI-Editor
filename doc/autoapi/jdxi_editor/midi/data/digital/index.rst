jdxi_editor.midi.data.digital
=============================

.. py:module:: jdxi_editor.midi.data.digital


Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/jdxi_editor/midi/data/digital/filter/index
   /autoapi/jdxi_editor/midi/data/digital/lfo/index
   /autoapi/jdxi_editor/midi/data/digital/oscillator/index
   /autoapi/jdxi_editor/midi/data/digital/partial/index


Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.digital.DigitalOscWave
   jdxi_editor.midi.data.digital.DigitalPartial


Package Contents
----------------

.. py:class:: DigitalOscWave

   Bases: :py:obj:`enum.IntEnum`


   Oscillator waveform types


   .. py:attribute:: SAW
      :value: 0



   .. py:attribute:: SQUARE
      :value: 1



   .. py:attribute:: PW_SQUARE
      :value: 2



   .. py:attribute:: TRIANGLE
      :value: 3



   .. py:attribute:: SINE
      :value: 4



   .. py:attribute:: NOISE
      :value: 5



   .. py:attribute:: SUPER_SAW
      :value: 6



   .. py:attribute:: PCM
      :value: 7



   .. py:property:: display_name
      :type: str


      Get display name for the waveform


   .. py:property:: description
      :type: str


      Get full description of the waveform


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



