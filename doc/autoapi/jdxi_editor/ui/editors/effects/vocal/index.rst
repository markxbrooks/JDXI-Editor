jdxi_editor.ui.editors.effects.vocal
====================================

.. py:module:: jdxi_editor.ui.editors.effects.vocal

.. autoapi-nested-parse::

   VocalFXEditor Module

   This module defines the `VocalFXEditor` class, a PySide6-based editor for controlling
   the Vocal FX section of the Roland JD-Xi synthesizer. It provides a graphical interface
   for adjusting various vocal effects such as vocoder settings, auto-pitch parameters,
   and mixer controls.

   Features:
   - Scrollable UI with multiple tabs for organizing vocal effect settings.
   - Support for vocoder controls, including envelope, mic sensitivity, and synthesis levels.
   - Auto-pitch settings with selectable pitch type, scale, key, and gender adjustment.
   - Mixer section for controlling levels, panning, reverb, and delay send levels.
   - MIDI integration for real-time parameter control using `MIDIHelper`.
   - Dynamic instrument image loading to visually represent the effect in use.

   Dependencies:
   - PySide6 for UI components.
   - `MIDIHelper` for sending MIDI messages to the JD-Xi.
   - `VocalFXParameter` for managing effect-specific MIDI parameters.



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.effects.vocal.VocalFXEditor


Module Contents
---------------

.. py:class:: VocalFXEditor(midi_helper: Optional[jdxi_editor.midi.io.helper.MidiIOHelper] = None, preset_helper: jdxi_editor.jdxi.preset.helper.JDXiPresetHelper = None, parent: Optional[PySide6.QtWidgets.QWidget] = None)

   Bases: :py:obj:`jdxi_editor.ui.editors.synth.simple.BasicEditor`


   Vocal Effects Window Class


   .. py:attribute:: preset_helper
      :value: None



   .. py:attribute:: address


   .. py:attribute:: controls
      :type:  Dict[jdxi_editor.midi.data.parameter.synth.AddressParameter, PySide6.QtWidgets.QWidget]


   .. py:attribute:: title_label


   .. py:attribute:: image_label


   .. py:attribute:: default_image
      :value: 'vocal_fx.png'



   .. py:attribute:: instrument_icon_folder
      :value: 'vocal_fx'



   .. py:attribute:: tab_widget


   .. py:method:: _create_common_section() -> PySide6.QtWidgets.QWidget

      _create_common_section

      :return: QWidget



   .. py:method:: _create_vocal_effect_section() -> PySide6.QtWidgets.QWidget

      Create general vocal effect controls section



   .. py:method:: _create_mixer_section() -> PySide6.QtWidgets.QWidget

      _create_mixer_section

      :return: QWidget



   .. py:method:: _create_auto_pitch_section()

      _create_auto_pitch_section

      :return: QWidget



