jdxi_editor.ui.editors.drum.partial.wmt
=======================================

.. py:module:: jdxi_editor.ui.editors.drum.partial.wmt

.. autoapi-nested-parse::

   Module: drum_wmt
   ================

   This module defines the `DrumWMTSection` class, which provides a PySide6-based
   user interface for editing drum WMT parameters in the Roland JD-Xi synthesizer.
   It extends the `QWidget` base class and integrates MIDI communication for real-time
   parameter adjustments and preset management.

   Key Features:
   -------------
   - Provides a graphical editor for modifying drum WMT parameters, including
     wave selection, gain, FXM color, depth, tempo sync, coarse tune, fine tune, pan,
     random pan switch, alternate pan switch, velocity range lower, velocity range upper,
     velocity fade width lower, velocity fade width upper, and wave level.

   Dependencies:
   -------------
   - PySide6 (for UI components and event handling)
   - MIDIHelper (for handling MIDI communication)
   - PresetHandler (for managing synth presets)
   - Various custom enums and helper classes (AnalogParameter, AnalogCommonParameter, etc.)

   Usage:
   ------
   The `DrumWMTSection` class can be instantiated as part of a larger PySide6 application.
   It requires a `MIDIHelper` instance for proper communication with the synthesizer.

   Example:
   --------
       midi_helper = MIDIHelper()
       editor = DrumWMTSection(midi_helper)
       editor.show()



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.drum.partial.wmt.DrumWMTSection


Module Contents
---------------

.. py:class:: DrumWMTSection(controls, create_parameter_combo_box, create_parameter_slider, create_parameter_switch, midi_helper, address=None)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   Drum TVF Section for the JDXI Editor


   .. py:attribute:: l_wave_combos


   .. py:attribute:: l_wave_search_boxes


   .. py:attribute:: l_wave_selectors


   .. py:attribute:: r_wave_combos


   .. py:attribute:: r_wave_search_boxes


   .. py:attribute:: r_wave_selectors


   .. py:attribute:: wmt_tab_widget
      :value: None



   .. py:attribute:: controls


   .. py:attribute:: _create_parameter_slider


   .. py:attribute:: _create_parameter_combo_box


   .. py:attribute:: _create_parameter_switch


   .. py:attribute:: midi_helper


   .. py:attribute:: address
      :value: None



   .. py:method:: setup_ui()

      setup UI



   .. py:method:: _create_wmt_layout(wmt_index: int) -> PySide6.QtWidgets.QFormLayout

      _create_wmt_layout

      :param wmt_index: int
      :return: QFormLayout



   .. py:method:: _populate_l_waves(wmt_index)


   .. py:method:: _populate_r_waves(wmt_index)


   .. py:method:: _create_wmt1_layout()


   .. py:method:: _create_wmt2_layout()


   .. py:method:: _create_wmt3_layout()


   .. py:method:: _create_wmt4_layout()


