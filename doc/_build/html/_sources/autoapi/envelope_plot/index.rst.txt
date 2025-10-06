envelope_plot
=============

.. py:module:: envelope_plot

.. autoapi-nested-parse::

   Pitch Envelope Plot
   ===================

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



Attributes
----------

.. autoapisummary::

   envelope_plot.app


Classes
-------

.. autoapisummary::

   envelope_plot.WMTEnvPlot


Functions
---------

.. autoapisummary::

   envelope_plot.midi_value_to_float


Module Contents
---------------

.. py:function:: midi_value_to_float(value: int) -> float

   Convert MIDI value (0-127) to a float in the range [0.0, 1.0].

   :param value: int
   :return: float in range [0.0, 1.0]


.. py:class:: WMTEnvPlot(width: int = JDXiStyle.ADSR_PLOT_WIDTH, height: int = JDXiStyle.ADSR_PLOT_HEIGHT, envelope: dict = None, parent: PySide6.QtWidgets.QWidget = None)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   A QWidget-based plot for displaying envelope curves,
   supporting both a modern velocity-style plot and
   a vintage LCD-style pitch envelope plot.


   .. py:attribute:: point_moved
      :value: None



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



   .. py:attribute:: peak_level
      :value: 0.5



   .. py:attribute:: release_x
      :value: 0.7



   .. py:attribute:: dragging
      :value: None



   .. py:method:: setEnabled(enabled)


   .. py:method:: set_values(envelope: dict) -> None

      Update the envelope values and refresh the plot.

      :param envelope: dict
      :return: None



   .. py:method:: paintEvent(event)

      Paint the plot in the style of an LCD



.. py:data:: app

