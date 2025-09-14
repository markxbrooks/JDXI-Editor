jdxi_editor.jdxi.synth.data
===========================

.. py:module:: jdxi_editor.jdxi.synth.data


Classes
-------

.. autoapisummary::

   jdxi_editor.jdxi.synth.data.JDXISynthData


Module Contents
---------------

.. py:class:: JDXISynthData

   Bases: :py:obj:`jdxi_editor.jdxi.synth.midi_config.MidiSynthConfig`, :py:obj:`jdxi_editor.jdxi.synth.instrument_display.InstrumentDisplayConfig`


   Synth Data


   .. py:attribute:: msb
      :type:  int


   .. py:attribute:: umb
      :type:  int


   .. py:attribute:: lmb
      :type:  int


   .. py:attribute:: address
      :type:  jdxi_editor.midi.data.address.address.RolandSysExAddress


   .. py:attribute:: common_parameters
      :type:  Optional[Union[jdxi_editor.midi.data.parameter.drum.common.AddressParameterDrumCommon, jdxi_editor.midi.data.parameter.analog.AddressParameterAnalog, jdxi_editor.midi.data.parameter.digital.AddressParameterDigitalCommon]]
      :value: None



   .. py:method:: __post_init__() -> None

      Post Init



   .. py:property:: group_map
      :type: Dict[int, jdxi_editor.midi.data.address.address.Address]


      Group Map

      :return: Dict[int, AddressOffsetProgramLMB] The group map
      Default: Only common address (override in subclasses).


   .. py:method:: get_partial_lmb(partial_number: int) -> jdxi_editor.midi.data.address.address.AddressOffsetProgramLMB

      Resolve the address for a given partial number.

      :param partial_number: int The partial number
      :return: AddressOffsetProgramLMB The address offset



