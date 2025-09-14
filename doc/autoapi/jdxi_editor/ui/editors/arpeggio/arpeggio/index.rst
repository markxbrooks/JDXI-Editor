jdxi_editor.ui.editors.arpeggio.arpeggio
========================================

.. py:module:: jdxi_editor.ui.editors.arpeggio.arpeggio

.. autoapi-nested-parse::

   Arpeggio Editor Module

   This module defines the `ArpeggioEditor` class, a specialized editor for configuring arpeggiator
   settings within a synthesizer. It extends the `SynthEditor` class, providing a user-friendly
   interface to control various arpeggiator parameters.

   Classes:
       - ArpeggioEditor: A `QWidget` subclass that allows users to modify arpeggiator parameters
         such as style, grid, duration, velocity, accent, swing, octave range, and motif.

   Features:
       - Provides an intuitive UI with labeled controls and dropdown menus for parameter selection.
       - Includes a toggle switch to enable or disable the arpeggiator.
       - Displays an instrument image for better user engagement.
       - Uses MIDI integration to send real-time parameter changes to the synthesizer.
       - Supports dynamic visualization and interaction through sliders and combo boxes.

   Usage:
       ```python
       from PySide6.QtWidgets import QApplication
       from midi_helper import MIDIHelper

       app = QApplication([])
       midi_helper = MIDIHelper()
       editor = ArpeggioEditor(midi_helper=midi_helper)
       editor.show()
       app.exec()
       ```

   Dependencies:
       - PySide6 (for UI components)
       - MIDIHelper (for MIDI communication)
       - ArpeggioParameter (for managing parameter addresses and value ranges)
       - Slider (for smooth control over numerical parameters)



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.arpeggio.arpeggio.ArpeggioEditor


Module Contents
---------------

.. py:class:: ArpeggioEditor(midi_helper: jdxi_editor.midi.io.helper.MidiIOHelper, preset_helper: Optional[jdxi_editor.jdxi.preset.helper.JDXiPresetHelper] = None, parent: Optional[PySide6.QtWidgets.QWidget] = None)

   Bases: :py:obj:`jdxi_editor.ui.editors.synth.simple.BasicEditor`


   Arpeggio Editor Window


   .. py:attribute:: midi_helper


   .. py:attribute:: preset_helper
      :value: None



   .. py:attribute:: address


   .. py:attribute:: partial_number
      :value: 0



   .. py:attribute:: instrument_icon_folder
      :value: 'arpeggiator'



   .. py:attribute:: default_image
      :value: 'arpeggiator2.png'



   .. py:attribute:: controls
      :type:  Dict[jdxi_editor.midi.data.parameter.synth.AddressParameter, PySide6.QtWidgets.QWidget]


   .. py:attribute:: title_label


   .. py:attribute:: image_label


   .. py:attribute:: switch_button


   .. py:attribute:: style_combo


   .. py:attribute:: grid_combo


   .. py:attribute:: duration_combo


   .. py:attribute:: velocity_slider


   .. py:attribute:: accent_slider


   .. py:attribute:: octave_combo


   .. py:attribute:: motif_combo


