wheel.mod
=========

.. py:module:: wheel.mod

.. autoapi-nested-parse::

   Modulation Wheel



Classes
-------

.. autoapisummary::

   wheel.mod.ModWheel


Module Contents
---------------

.. py:class:: ModWheel(label='Mod', bidirectional=True, parent=None, midi_helper=None, channel=0)

   Bases: :py:obj:`jdxi_editor.ui.widgets.wheel.wheel.WheelWidget`


   Modulation Wheel


   .. py:attribute:: label
      :value: 'Mod'



   .. py:attribute:: bidirectional
      :value: True



   .. py:attribute:: parent
      :value: None



   .. py:attribute:: value
      :value: 0.0



   .. py:attribute:: midi_helper
      :value: None



   .. py:attribute:: channel
      :value: 0



   .. py:method:: set_value(value)

      Set modulation wheel value (0.0 to 1.0) and send MIDI CC1.



