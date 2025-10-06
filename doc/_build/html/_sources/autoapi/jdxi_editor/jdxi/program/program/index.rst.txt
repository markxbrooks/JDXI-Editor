jdxi_editor.jdxi.program.program
================================

.. py:module:: jdxi_editor.jdxi.program.program

.. autoapi-nested-parse::

   program = JDXiProgram.from_patch(
       name="Fat Synth Stack",
       genre="EDM",
       tempo=128,
       analog=JDXiPresetData.get_preset_details(JDXiSynth.ANALOG_SYNTH, 4),
       digital_1=JDXiPresetData.get_preset_details(JDXiSynth.DIGITAL_SYNTH_1, 12),
       digital_2=JDXiPresetData.get_preset_details(JDXiSynth.DIGITAL_SYNTH_2, 25),
       drums=JDXiPresetData.get_preset_details(JDXiSynth.DRUM_KIT, 7),
   )

   # Save to JSON
   program.to_json("my_fat_patch.json")

   # Load from JSON
   loaded = JDXiProgram.from_json("my_fat_patch.json")
   print(loaded.name, loaded.tempo)



Classes
-------

.. autoapisummary::

   jdxi_editor.jdxi.program.program.JDXiProgram
   jdxi_editor.jdxi.program.program.JDXiProgramOld


Module Contents
---------------

.. py:class:: JDXiProgram

   .. py:attribute:: id
      :type:  str


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: genre
      :type:  Optional[str]
      :value: None



   .. py:attribute:: tempo
      :type:  Optional[int]
      :value: None



   .. py:attribute:: measure_length
      :type:  Optional[int]
      :value: None



   .. py:attribute:: scale
      :type:  Optional[str]
      :value: None



   .. py:attribute:: msb
      :type:  Optional[int]
      :value: None



   .. py:attribute:: lsb
      :type:  Optional[int]
      :value: None



   .. py:attribute:: pc
      :type:  Optional[int]
      :value: None



   .. py:attribute:: analog
      :type:  Optional[str]
      :value: None



   .. py:attribute:: digital_1
      :type:  Optional[str]
      :value: None



   .. py:attribute:: digital_2
      :type:  Optional[str]
      :value: None



   .. py:attribute:: drums
      :type:  Optional[str]
      :value: None



   .. py:method:: __getitem__(key)


   .. py:method:: __str__()


   .. py:method:: from_patch(name: str, analog: jdxi_editor.jdxi.preset.data.JDXiPresetData, digital_1: jdxi_editor.jdxi.preset.data.JDXiPresetData, digital_2: jdxi_editor.jdxi.preset.data.JDXiPresetData, drums: jdxi_editor.jdxi.preset.data.JDXiPresetData, genre: Optional[str] = None, tempo: Optional[int] = None) -> JDXiProgram
      :staticmethod:



   .. py:method:: to_json(filepath: str) -> None


   .. py:method:: to_dict()


   .. py:method:: from_json(filepath: str) -> JDXiProgram
      :staticmethod:



   .. py:method:: from_dict(data: dict) -> JDXiProgram
      :staticmethod:



.. py:class:: JDXiProgramOld

   .. py:attribute:: id
      :type:  str


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: genre
      :type:  Optional[str]
      :value: None



   .. py:attribute:: tempo
      :type:  Optional[int]
      :value: None



   .. py:attribute:: measure_length
      :type:  Optional[int]
      :value: None



   .. py:attribute:: scale
      :type:  Optional[str]
      :value: None



   .. py:attribute:: msb
      :type:  Optional[int]
      :value: None



   .. py:attribute:: lsb
      :type:  Optional[int]
      :value: None



   .. py:attribute:: pc
      :type:  Optional[int]
      :value: None



   .. py:attribute:: analog
      :type:  Optional[jdxi_editor.jdxi.preset.data.JDXiPresetData]
      :value: None



   .. py:attribute:: digital_1
      :type:  Optional[jdxi_editor.jdxi.preset.data.JDXiPresetData]
      :value: None



   .. py:attribute:: digital_2
      :type:  Optional[jdxi_editor.jdxi.preset.data.JDXiPresetData]
      :value: None



   .. py:attribute:: drums
      :type:  Optional[jdxi_editor.jdxi.preset.data.JDXiPresetData]
      :value: None



   .. py:method:: from_patch(name: str, analog: jdxi_editor.jdxi.preset.data.JDXiPresetData, digital_1: jdxi_editor.jdxi.preset.data.JDXiPresetData, digital_2: jdxi_editor.jdxi.preset.data.JDXiPresetData, drums: jdxi_editor.jdxi.preset.data.JDXiPresetData, genre: Optional[str] = None, tempo: Optional[int] = None) -> JDXiProgram
      :staticmethod:



   .. py:method:: to_json(filepath: str) -> None


   .. py:method:: to_dict()


   .. py:method:: from_json(filepath: str) -> JDXiProgram
      :staticmethod:



   .. py:method:: from_dict(data: dict) -> JDXiProgram
      :staticmethod:



