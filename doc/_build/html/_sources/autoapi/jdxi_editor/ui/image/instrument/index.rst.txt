jdxi_editor.ui.image.instrument
===============================

.. py:module:: jdxi_editor.ui.image.instrument

.. autoapi-nested-parse::

   Module: JD-Xi Instrument Display Renderer
   =========================================

   This module provides functions to generate a visual representation of the Roland JD-Xi synthesizer
   interface using PySide6. It renders key UI elements, including the display, sequencer section,
   and keyboard.

   Functions
   ---------
   - :func:`draw_instrument_pixmap`
   - :func:`draw_display`
   - :func:`draw_sequencer`

   Dependencies
   ------------
   - PySide6.QtCore (Qt)
   - PySide6.QtGui (QFont, QPixmap, QImage, QPainter, QPen, QColor)
   - jdxi_editor.ui.windows.jdxi.dimensions (JDXI_WIDTH, JDXI_HEIGHT, etc.)

   Usage
   -----
   These functions generate and display a graphical representation of the JD-Xi’s controls,
   which can be integrated into a larger PySide6-based UI.



Functions
---------

.. autoapisummary::

   jdxi_editor.ui.image.instrument.draw_instrument_pixmap
   jdxi_editor.ui.image.instrument.draw_sequencer


Module Contents
---------------

.. py:function:: draw_instrument_pixmap() -> PySide6.QtGui.QPixmap

   Create a visual representation of the JD-Xi instrument panel.

   :return: QPixmap representation of the JD-Xi interface.
   :rtype: QPixmap


.. py:function:: draw_sequencer(painter: PySide6.QtGui.QPainter) -> None

   Draw the sequencer section of the JD-Xi interface.

   :param painter: QPainter instance used for drawing.
   :type painter: QPainter
   :return: None
   :rtype: None


