jdxi_editor.ui.editors.digital.partial.editor
=============================================

.. py:module:: jdxi_editor.ui.editors.digital.partial.editor

.. autoapi-nested-parse::

   Digital Partial Editor Module

   This module defines the `DigitalPartialEditor` class, a specialized editor for managing a single
   digital partial in a synthesizer. It extends the `PartialEditor` class, providing a structured UI
   to control and modify parameters related to oscillators, filters, amplifiers, and modulation sources.

   Classes:
       - DigitalPartialEditor: A `QWidget` subclass that allows users to modify digital synthesis
         parameters using a tabbed interface with various control sections.

   Features:
       - Supports editing a single partial within a digital synth part.
       - Provides categorized parameter sections: Oscillator, Filter, Amp, LFO, and Mod LFO.
       - Integrates with `MIDIHelper` for real-time MIDI parameter updates.
       - Uses icons for waveform selection, filter controls, and modulation settings.
       - Stores UI controls for easy access and interaction.

   Usage:
       ```python
       from PySide6.QtWidgets import QApplication
       from midi_helper import MIDIHelper

       app = QApplication([])
       midi_helper = MIDIHelper()
       editor = DigitalPartialEditor(midi_helper=midi_helper)
       editor.show()
       app.exec()
       ```

   Dependencies:
       - PySide6 (for UI components)
       - MIDIHelper (for MIDI communication)
       - DigitalParameter, DigitalCommonParameter (for parameter management)
       - WaveformButton (for waveform selection UI)
       - QIcons generated from waveform base64 data



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.digital.partial.editor.DigitalPartialEditor


Module Contents
---------------

.. py:class:: DigitalPartialEditor(midi_helper: Optional[jdxi_editor.midi.io.helper.MidiIOHelper] = None, synth_number: int = 1, partial_number: int = 1, preset_type: jdxi_editor.jdxi.synth.type.JDXiSynth = None, parent: Optional[PySide6.QtWidgets.QWidget] = None)

   Bases: :py:obj:`jdxi_editor.ui.editors.synth.partial.PartialEditor`


   Editor for address single partial


   .. py:attribute:: filter_mode_switch
      :value: None


      Initialize the DigitalPartialEditor

      :param midi_helper: MidiIOHelper
      :param synth_number: int
      :param partial_number: int
      :param preset_type: JDXiSynth
      :param parent: QWidget


   .. py:attribute:: partial_address_default


   .. py:attribute:: partial_address_map


   .. py:attribute:: bipolar_parameters


   .. py:attribute:: midi_helper
      :value: None



   .. py:attribute:: partial_number
      :value: 1



   .. py:attribute:: preset_type
      :value: None



   .. py:attribute:: controls
      :type:  Dict[Union[jdxi_editor.midi.data.parameter.digital.partial.AddressParameterDigitalPartial, jdxi_editor.midi.data.parameter.digital.common.AddressParameterDigitalCommon], PySide6.QtWidgets.QWidget]


   .. py:attribute:: tab_widget


   .. py:attribute:: oscillator_tab


   .. py:attribute:: filter_tab


   .. py:attribute:: amp_tab


   .. py:attribute:: lfo_tab


   .. py:attribute:: mod_lfo_tab


   .. py:attribute:: updating_from_spinbox
      :value: False



   .. py:method:: __str__()


   .. py:method:: __repr__()


   .. py:method:: update_filter_controls_state(mode: int)

      Update filter controls enabled state based on mode

      :param mode: int



   .. py:method:: _on_waveform_selected(waveform: jdxi_editor.midi.data.digital.oscillator.DigitalOscWave)

      Handle waveform button clicks

      :param waveform: DigitalOscWave



