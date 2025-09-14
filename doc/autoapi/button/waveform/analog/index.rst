button.waveform.analog
======================

.. py:module:: button.waveform.analog

.. autoapi-nested-parse::

   Module for AnalogWaveformButton UI Component.

   This module defines the `AnalogWaveformButton` class, a specialized button for selecting oscillator waveforms in the JD-Xi editor. It inherits from `WaveformButton` and emits a signal when a waveform is selected.

   Features:
   - Displays selectable waveform options with a styled QPushButton.
   - Emits `waveform_selected` signal upon selection.
   - Custom styling for default, checked, and hover states.



Classes
-------

.. autoapisummary::

   button.waveform.analog.AnalogWaveformButton


Module Contents
---------------

.. py:class:: AnalogWaveformButton(waveform: jdxi_editor.midi.wave.form.Waveform, style: str = 'digital', parent: PySide6.QtWidgets.QWidget = None)

   Bases: :py:obj:`jdxi_editor.ui.widgets.button.waveform.waveform.WaveformButton`


   Button for selecting oscillator waveform


   .. py:attribute:: waveform_selected


