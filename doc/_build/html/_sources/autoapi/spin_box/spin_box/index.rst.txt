spin_box.spin_box
=================

.. py:module:: spin_box.spin_box

.. autoapi-nested-parse::

   spin_box.py
   ===========

   This module provides a custom `SpinBox` widget that extends `QWidget`.

   The `SpinBox` class combines a label and a numerical input (QSpinBox), allowing users
   to select a value within a defined range. It emits a `valueChanged` signal whenever the
   selected value changes.

   Classes
   --------
   - SpinBox: A labeled spin box for integer value selection.

   Example Usage
   --------------
   .. code-block:: python

       from PySide6.QtWidgets import QApplication
       from spin_box import SpinBox

       app = QApplication([])

       spin_box = SpinBox("Select Number:", 0, 100)
       spin_box.valueChanged.connect(lambda v: print(f"Selected Value: {v}"))

       spin_box.show()
       app.exec()

   .. attribute:: - valueChanged (Signal)



      :type: :class:`Emitted when the selected value changes.`

   .. method:: - setValue(value: int): Set the selected value in the spin box.

   .. method:: - value() -> int: Get the currently selected value.

   .. method:: - setEnabled(enabled: bool): Enable or disable the widget.

   .. method:: - setVisible(visible: bool): Show or hide the widget.

   .. method:: - setMinimumWidth(width: int): Set the minimum width of the label.

   .. method:: - setMaximumWidth(width: int): Set the maximum width of the label.





Classes
-------

.. autoapisummary::

   spin_box.spin_box.SpinBox


Module Contents
---------------

.. py:class:: SpinBox(label: str, low: int, high: int = None, tooltip: str = '', parent=None)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   Custom SpinBox widget with label and value mapping.


   .. py:attribute:: valueChanged


   .. py:attribute:: low


   .. py:attribute:: high
      :value: None



   .. py:attribute:: label_widget


   .. py:attribute:: spin_box


   .. py:method:: _on_valueChanged(value: int)

      Emit the corresponding value when the selected value changes.



   .. py:method:: setValue(value: int)

      Set spin box index based on the value.



   .. py:method:: value() -> int

      Return the currently selected value.



   .. py:method:: setEnabled(enabled: bool)

      Enable or disable the sipn box and label.



   .. py:method:: setVisible(visible: bool)

      Show or hide the spin box and label.



   .. py:method:: setMinimumWidth(width: int)

      Set the minimum width of the label.



   .. py:method:: setMaximumWidth(width: int)

      Set the maximum width of the label.



