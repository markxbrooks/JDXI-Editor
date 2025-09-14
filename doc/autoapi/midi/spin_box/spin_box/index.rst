midi.spin_box.spin_box
======================

.. py:module:: midi.spin_box.spin_box

.. autoapi-nested-parse::

   Midi Spin Box



Classes
-------

.. autoapisummary::

   midi.spin_box.spin_box.MidiSpinBox


Module Contents
---------------

.. py:class:: MidiSpinBox(parent=None)

   Bases: :py:obj:`PySide6.QtWidgets.QSpinBox`


   Custom QSpinBox to display MIDI channels as 1-16,


   .. py:method:: valueFromText(text: str) -> int


   .. py:method:: textFromValue(value: int) -> str


