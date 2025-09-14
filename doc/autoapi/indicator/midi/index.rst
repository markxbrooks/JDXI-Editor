indicator.midi
==============

.. py:module:: indicator.midi


Classes
-------

.. autoapisummary::

   indicator.midi.MIDIIndicator


Module Contents
---------------

.. py:class:: MIDIIndicator(parent=None)

   Bases: :py:obj:`PySide6.QtWidgets.QLabel`


   MIDI activity indicator light


   .. py:attribute:: active
      :value: False



   .. py:attribute:: connected
      :value: False



   .. py:attribute:: blink_timer


   .. py:method:: paintEvent(event)

      Draw the indicator light



   .. py:method:: blink()

      Trigger activity blink



   .. py:method:: set_connected(connected: bool)

      Set connection state



   .. py:method:: _reset_active()

      Reset active state after blink



