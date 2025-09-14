jdxi_editor.jdxi.synth.drum
===========================

.. py:module:: jdxi_editor.jdxi.synth.drum

.. autoapi-nested-parse::

   Drum Synth Data



Classes
-------

.. autoapisummary::

   jdxi_editor.jdxi.synth.drum.DrumSynthData


Module Contents
---------------

.. py:class:: DrumSynthData

   Bases: :py:obj:`jdxi_editor.jdxi.synth.data.JDXISynthData`


   Drum Synth Data


   .. py:attribute:: partial_number
      :type:  int
      :value: 0



   .. py:attribute:: partial_parameters
      :type:  jdxi_editor.midi.data.parameter.drum.partial.AddressParameterDrumPartial
      :value: None



   .. py:attribute:: _group_map
      :type:  Dict[int, jdxi_editor.midi.data.address.address.AddressOffsetDrumKitLMB]


   .. py:method:: __post_init__() -> None

      Post Init



   .. py:method:: _build_group_map() -> None

      Build the map once after initialization.



   .. py:property:: group_map
      :type: Dict[int, jdxi_editor.midi.data.address.address.Address]


      Return the drum group map.


   .. py:property:: partial_lmb
      :type: jdxi_editor.midi.data.address.address.Address


      Return the LMB for the current partial number.


   .. py:method:: get_partial_lmb(partial_number: int) -> jdxi_editor.midi.data.address.address.Address

      Return the LMB for a given partial number.



