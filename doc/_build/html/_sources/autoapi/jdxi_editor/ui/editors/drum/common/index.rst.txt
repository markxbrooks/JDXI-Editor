jdxi_editor.ui.editors.drum.common
==================================

.. py:module:: jdxi_editor.ui.editors.drum.common

.. autoapi-nested-parse::

   Module: drum_common
   ===================

   This module defines the `DrumCommonSection` class, which provides a PySide6-based
   user interface for editing drum common parameters in the Roland JD-Xi synthesizer.
   It extends the `QWidget` base class and integrates MIDI communication for real-time
   parameter adjustments and preset management.

   Key Features:
   -------------
   - Provides a graphical editor for modifying drum common parameters, including
     kit level, partial pitch bend range, and partial receive expression.



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.drum.common.DrumCommonSection


Module Contents
---------------

.. py:class:: DrumCommonSection(controls: dict, create_parameter_combo_box: Callable, create_parameter_slider: Callable, midi_helper: jdxi_editor.midi.io.helper.MidiIOHelper, address: jdxi_editor.midi.data.address.address.RolandSysExAddress)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   Drum Common Section for the JDXI Editor


   .. py:attribute:: controls


   .. py:attribute:: address


   .. py:attribute:: _create_parameter_slider


   .. py:attribute:: _create_parameter_combo_box


   .. py:attribute:: midi_helper


   .. py:method:: setup_ui()

      setup UI



