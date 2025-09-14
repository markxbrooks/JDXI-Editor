jdxi_editor.jdxi.synth.analog
=============================

.. py:module:: jdxi_editor.jdxi.synth.analog

.. autoapi-nested-parse::

   Analog Synth Data



Classes
-------

.. autoapisummary::

   jdxi_editor.jdxi.synth.analog.AnalogSynthData


Module Contents
---------------

.. py:class:: AnalogSynthData

   Bases: :py:obj:`jdxi_editor.jdxi.synth.data.JDXISynthData`


   Analog Synth Data


   .. py:method:: __post_init__() -> None

      Post Init



   .. py:property:: group_map
      :type: Dict[int, jdxi_editor.midi.data.address.address.Address]


      Group Map

      :return: Dict[int, AddressOffsetProgramLMB] The group map
      Default: Only common address (override in subclasses).


