jdxi_editor.jdxi.preset.data
============================

.. py:module:: jdxi_editor.jdxi.preset.data

.. autoapi-nested-parse::

   Module: preset_data

   This module defines the `JDXIPresetData` class, which provides methods to retrieve
   structured preset data for different JD-Xi synth types, including Analog, Digital1,
   Digital2, and Drum. It calculates MIDI bank and program values for use in MIDI Program
   Change messages.

   Classes:
       - JDXIPresetData: Provides static methods for looking up JD-Xi presets by synth type
         and index.

   Constants and Enums (from imports):
       - JDXISynth: Enum representing synth types (ANALOG, DIGITAL_1, DIGITAL_2, DRUM).
       - JDXIPresets: Named preset lists for each synth type.

   Example usage:
   =============
   >>>from jdxi_editor.jdxi.synth.type import JDXISynth
   ...preset_data = JDXIPresetData.get_preset_details(JDXISynth.DIGITAL_1, 10)
   ...print(preset_data)
       # Output:
       # {
       #     'presets': [...],
       #     'bank_msb': 1,
       #     'bank_lsb': 0,
       #     'program': 10
       # }
   >>>import json
   ...from dataclasses import asdict
   ...
   ...preset = JDXiPresetData.get_preset_details(JDXiSynth.ANALOG_SYNTH, 5)
   ...
   ...with open("preset.json", "w") as f:
   ...    json.dump(asdict(preset), f, indent=2)
   ...
   ...with open("preset.json", "r") as f:
   ...    data = json.load(f)
   ...    preset = JDXiPresetData(**data)



Classes
-------

.. autoapisummary::

   jdxi_editor.jdxi.preset.data.JDXiPresetData


Module Contents
---------------

.. py:class:: JDXiPresetData

   .. py:attribute:: name
      :type:  str


   .. py:attribute:: presets
      :type:  List[str]


   .. py:attribute:: bank_msb
      :type:  int


   .. py:attribute:: bank_lsb
      :type:  int


   .. py:attribute:: program
      :type:  int


   .. py:method:: from_dict(data: dict) -> JDXiPresetData
      :staticmethod:



   .. py:method:: get_preset_details(synth_type: str, preset_number: int) -> JDXiPresetData
      :staticmethod:



   .. py:method:: to_dict()


