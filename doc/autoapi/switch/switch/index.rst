switch.switch
=============

.. py:module:: switch.switch

.. autoapi-nested-parse::

   Module: switch_widget
   =====================

   This module provides a custom PySide6 QWidget implementation for a switch-style button with
   text display. The `Switch` class allows users to cycle through predefined values by clicking
   a button, emitting a `valueChanged` signal when toggled.

   Classes:
   --------
   - `Switch`: A custom widget that displays a label and a button, cycling through provided values
     when clicked.

   Usage Example:
   --------------
   >>> switch = Switch("Mode", ["Off", "On"])
   >>> switch.valueChanged.connect(lambda index: print(f"Switch changed to: {index}"))
   >>> switch.setValue(1)  # Sets the switch to "On"



Classes
-------

.. autoapisummary::

   switch.switch.Switch


Module Contents
---------------

.. py:class:: Switch(label: str, values: list[str], parent: PySide6.QtWidgets.QWidget = None, tooltip: str = '')

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   Custom switch widget with text display


   .. py:attribute:: valueChanged


   .. py:attribute:: values


   .. py:attribute:: current_index
      :value: 0



   .. py:attribute:: label


   .. py:attribute:: button


   .. py:method:: _on_clicked()

      Handle button clicks



   .. py:method:: setValue(value: int)

      Set current value



   .. py:method:: setLabel(text: str)

      Set label text



   .. py:method:: value() -> int

      Get current value



