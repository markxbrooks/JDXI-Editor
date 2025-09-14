wheel.wheel
===========

.. py:module:: wheel.wheel

.. autoapi-nested-parse::

   WheelWidget
   (c) 2025 JDXI Editor



Classes
-------

.. autoapisummary::

   wheel.wheel.WheelWidget


Module Contents
---------------

.. py:class:: WheelWidget(parent=None, bidirectional=False, label='Wheel')

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   Wheel Widget for Pitch and Mod Wheels


   .. py:attribute:: valueChanged


   .. py:attribute:: _value
      :value: 0.0



   .. py:attribute:: label
      :value: 'Wheel'



   .. py:attribute:: bidirectional
      :value: False



   .. py:attribute:: _drag_active
      :value: False



   .. py:attribute:: snap_animation


   .. py:method:: get_value()


   .. py:method:: set_value(value: float) -> None

      set_value

      :param value: float
      :return: None



   .. py:attribute:: value


   .. py:method:: paintEvent(event: PySide6.QtGui.QMouseEvent) -> None

      paintEvent

      :param event: QMouseEvent
      :return: None



   .. py:method:: mousePressEvent(event: PySide6.QtGui.QMouseEvent)

      mousePressEvent

      :param event: QMouseEvent
      :return: None



   .. py:method:: mouseMoveEvent(event: PySide6.QtGui.QMouseEvent) -> None

      mouseMoveEvent

      :param event: QMouseEvent
      :return: None



   .. py:method:: mouseReleaseEvent(event: PySide6.QtGui.QMouseEvent) -> None

      mouseReleaseEvent

      :param event: QMouseEvent
      :return: None



   .. py:method:: _update_value_from_mouse(y: int) -> None

      _update_value_from_mouse

      :param y: int
      :return: None



