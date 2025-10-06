combo_box.combo_box
===================

.. py:module:: combo_box.combo_box

.. autoapi-nested-parse::

   combo_box.py
   ============

   This module provides a custom `ComboBox` widget that extends `QWidget`.

   The `ComboBox` class combines a label and a dropdown menu (QComboBox), allowing users
   to select from a list of options, where each option is mapped to a corresponding integer value.
   It emits a `valueChanged` signal whenever the selected value changes.

   Classes
   --------
   - ComboBox: A labeled combo box with a value-mapping system.

   Example Usage
   --------------
   .. code-block:: python

       from PySide6.QtWidgets import QApplication
       from combo_box import ComboBox

       app = QApplication([])

       options = ["Low", "Medium", "High"]
       values = [10, 50, 100]

       combo = ComboBox("Select Level:", options, values)
       combo.valueChanged.connect(lambda v: log.message(f"Selected Value: {v}"))

       combo.show()
       app.exec()

   .. attribute:: - valueChanged (Signal)



      :type: :class:`Emitted when the selected value changes.`

   .. method:: - setValue(value: int): Set the selected value in the combo box.

   .. method:: - setOptions(options: list, values: list): Update the combo box options and their corresponding values.

   .. method:: - value() -> int: Get the currently selected value.

   .. method:: - setEnabled(enabled: bool): Enable or disable the widget.

   .. method:: - setVisible(visible: bool): Show or hide the widget.

   .. method:: - setMinimumWidth(width: int): Set the minimum width of the label.

   .. method:: - setMaximumWidth(width: int): Set the maximum width of the label.





Classes
-------

.. autoapisummary::

   combo_box.combo_box.ComboBox


Module Contents
---------------

.. py:class:: ComboBox(label: str, options: list, values: list = None, parent=None, show_label: bool = True, tooltip: str = '')

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   Custom ComboBox widget with label and value mapping.


   .. py:attribute:: valueChanged


   .. py:attribute:: options


   .. py:attribute:: values
      :value: None



   .. py:attribute:: label_widget


   .. py:attribute:: combo_box


   .. py:method:: _on_valueChanged(index: int) -> None

      Emit the corresponding value when the selected index changes.

      :param index: int



   .. py:method:: setLabelVisible(visible: bool) -> None

      Show or hide the label dynamically.

      :param visible: bool



   .. py:method:: setValue(value: int) -> None

      Set combo box index based on the value.

      :param value: int



   .. py:method:: value() -> int

      Get current index

      :return: int



