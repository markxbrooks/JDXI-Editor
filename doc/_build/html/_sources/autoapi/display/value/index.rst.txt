display.value
=============

.. py:module:: display.value

.. autoapi-nested-parse::

   Value Display Widget



Classes
-------

.. autoapisummary::

   display.value.ValueDisplay


Module Contents
---------------

.. py:class:: ValueDisplay(name: str, min_val: int, max_val: int, format_str: str = '{}', parent: PySide6.QtWidgets.QWidget = None)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   Value Display Widget


   .. py:attribute:: valueChanged


   .. py:attribute:: min_val


   .. py:attribute:: max_val


   .. py:attribute:: format_str
      :value: '{}'



   .. py:attribute:: name_label


   .. py:attribute:: value_label


   .. py:method:: setValue(value: int) -> None

      Set the value of the display.

      :param value: int



   .. py:method:: value() -> int

      Get the value of the display.

      :return: int



