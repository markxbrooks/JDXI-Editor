jdxi_editor.jdxi.synth.digital
==============================

.. py:module:: jdxi_editor.jdxi.synth.digital

.. autoapi-nested-parse::

   Digital Synth Data



Classes
-------

.. autoapisummary::

   jdxi_editor.jdxi.synth.digital.DigitalSynthData


Module Contents
---------------

.. py:class:: DigitalSynthData

   Bases: :py:obj:`jdxi_editor.jdxi.synth.data.JDXISynthData`


   Digital Synth Data


   .. py:attribute:: synth_number
      :type:  int
      :value: 1



   .. py:attribute:: partial_number
      :type:  int
      :value: 0



   .. py:attribute:: partial_parameters
      :type:  jdxi_editor.midi.data.parameter.digital.AddressParameterDigitalPartial
      :value: None



   .. py:method:: __post_init__() -> None

      Post Init



   .. py:property:: group_map
      :type: Dict[int, jdxi_editor.midi.data.address.address.Address]


      Group Map


   .. py:property:: partial_lmb
      :type: int


      Partial LMB


