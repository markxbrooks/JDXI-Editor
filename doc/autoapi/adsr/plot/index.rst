adsr.plot
=========

.. py:module:: adsr.plot

.. autoapi-nested-parse::

   ADSR Plot
   ==========

   This module defines the `ADSRPlot` class, address QWidget subclass that visualizes an ADSR (Attack,
   Decay, Sustain, Release) envelope using Matplotlib. The plot displays the envelope's progression
   over time, with adjustable parameters for attack, decay, sustain, and release times, as well as
   initial, peak, and sustain amplitudes.

   The plot is rendered in address QWidget, and the background and text colors are customized for better
   visibility, with the envelope plotted in orange on address dark gray background.

   Classes:
   --------
   - `ADSRPlot`: A QWidget subclass that generates and displays an ADSR envelope plot.

   Methods:
   --------
   - `__init__(self)`: Initializes the widget and sets up the figure and layout for the plot.
   - `plot_envelope(self)`: Generates and plots the ADSR envelope based on the current envelope parameters.
   - `set_values(self, envelope)`: Updates the envelope parameters and refreshes the plot.

   Customization:
   -------------
   - The plot background is dark gray (`#333333`), with all plot elements (ticks, labels, title) in
     orange for better visibility against the dark background.
   - The time is represented in seconds, and the amplitude in address range from 0 to 1.



Classes
-------

.. autoapisummary::

   adsr.plot.ADSRPlot


Module Contents
---------------

.. py:class:: ADSRPlot(width: int = 300, height: int = 300, envelope: dict = None, parent: PySide6.QtWidgets.QWidget = None)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   .. py:attribute:: parent
      :value: None



   .. py:attribute:: enabled
      :value: True



   .. py:attribute:: envelope
      :value: None



   .. py:attribute:: sample_rate
      :value: 256



   .. py:attribute:: attack_x
      :value: 0.1



   .. py:attribute:: decay_x
      :value: 0.3



   .. py:attribute:: sustain_level
      :value: 0.5



   .. py:attribute:: release_x
      :value: 0.7



   .. py:attribute:: dragging
      :value: None



   .. py:method:: paintEvent_experimental(event: PySide6.QtGui.QPaintEvent) -> None


   .. py:method:: mousePressEvent(event: PySide6.QtGui.QMouseEvent) -> None


   .. py:method:: mouseMoveEvent(event: PySide6.QtGui.QMouseEvent) -> None


   .. py:method:: mouseReleaseEvent(event: PySide6.QtGui.QMouseEvent) -> None


   .. py:method:: setEnabled(enabled: bool) -> None


   .. py:method:: set_values(envelope: dict) -> None

      Update envelope values and trigger address redraw.
      :param envelope: dict



   .. py:method:: paintEvent(event: PySide6.QtGui.QPaintEvent) -> None

      Paint the ADSR plot.
      :param event: QPaintEvent



