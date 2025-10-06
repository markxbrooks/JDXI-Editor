jdxi_editor.jdxi.synth.factory
==============================

.. py:module:: jdxi_editor.jdxi.synth.factory

.. autoapi-nested-parse::

   Synth Factory



Functions
---------

.. autoapisummary::

   jdxi_editor.jdxi.synth.factory.create_synth_data


Module Contents
---------------

.. py:function:: create_synth_data(synth_type: jdxi_editor.jdxi.synth.type.JDXiSynth, partial_number: int = 0) -> Union[jdxi_editor.jdxi.synth.analog.AnalogSynthData, jdxi_editor.jdxi.synth.drum.DrumSynthData, jdxi_editor.jdxi.synth.digital.DigitalSynthData, None]

   Factory function to create synth data based on the synth type and partial number.

   :param synth_type: str
   :param partial_number: int
   :return: JDXISynthData


