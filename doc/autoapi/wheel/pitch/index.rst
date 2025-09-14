wheel.pitch
===========

.. py:module:: wheel.pitch

.. autoapi-nested-parse::

   Pitch Wheel Widget



Classes
-------

.. autoapisummary::

   wheel.pitch.PitchWheel


Module Contents
---------------

.. py:class:: PitchWheel(label='Pitch', bidirectional=True, parent=None, midi_helper=None, channel=0)

   Bases: :py:obj:`jdxi_editor.ui.widgets.wheel.wheel.WheelWidget`


   Pitch Bend Wheel


   .. py:attribute:: bidirectional
      :value: True



   .. py:attribute:: label
      :value: 'Pitch'



   .. py:attribute:: parent
      :value: None



   .. py:attribute:: value
      :value: 0.0



   .. py:attribute:: midi_helper
      :value: None



   .. py:attribute:: channel
      :value: 0



   .. py:method:: set_value(value)

      Set wheel value in the range -1.0 to 1.0 and send pitch bend.



