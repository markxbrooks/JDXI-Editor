indicator.led
=============

.. py:module:: indicator.led


Classes
-------

.. autoapisummary::

   indicator.led.LEDIndicator


Module Contents
---------------

.. py:class:: LEDIndicator(parent=None, alignment_state=None)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   LED-style indicator widget


   .. py:attribute:: _state
      :value: False



   .. py:attribute:: _blink
      :value: False



   .. py:attribute:: _blink_state
      :value: False



   .. py:attribute:: _timer


   .. py:attribute:: _on_color


   .. py:attribute:: _off_color


   .. py:attribute:: _blink_color


   .. py:method:: set_active(active)


   .. py:method:: sizeHint() -> PySide6.QtCore.QSize

      Get recommended size



   .. py:method:: set_state(state: bool)

      Set LED state

      :param state: True for on, False for off



   .. py:method:: blink()

      Trigger momentary blink



   .. py:method:: _reset_blink()

      Reset blink state



   .. py:method:: paintEvent(event)

      Paint the LED indicator



