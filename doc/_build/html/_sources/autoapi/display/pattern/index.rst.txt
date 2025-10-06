display.pattern
===============

.. py:module:: display.pattern

.. autoapi-nested-parse::

   Pattern Display Widget



Classes
-------

.. autoapisummary::

   display.pattern.PatternDisplay


Module Contents
---------------

.. py:class:: PatternDisplay(parent: PySide6.QtWidgets.QWidget = None)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   Pattern Display Widget


   .. py:attribute:: pattern_type
      :value: 0



   .. py:attribute:: octave_range
      :value: 0



   .. py:attribute:: accent_rate
      :value: 0



   .. py:method:: set_pattern(pattern_type: int, octave_range: int, accent_rate: int) -> None


   .. py:method:: paintEvent(event: PySide6.QtGui.QPaintEvent) -> None

      Paint the pattern display.

      :param event: QPaintEvent



   .. py:method:: _draw_grid(painter: PySide6.QtGui.QPainter, x: int, y: int, width: int, height: int) -> None

      Draw the grid.

      :param painter: QPainter
      :param x: int
      :param y: int
      :param width: int
      :param height: int



   .. py:method:: _get_pattern_points(x: int, y: int, width: int, height: int) -> list

      Get the pattern points.

      :param x: int
      :param y: int
      :param width: int
      :param height: int



   .. py:method:: _draw_pattern(painter: PySide6.QtGui.QPainter, points: list) -> None

      Draw the pattern.

      :param painter: QPainter
      :param points: list



   .. py:method:: _generate_up_pattern() -> list


   .. py:method:: _generate_down_pattern()


   .. py:method:: _generate_updown_pattern()


   .. py:method:: _generate_random_pattern()


   .. py:method:: _generate_note_order_pattern()


   .. py:method:: _generate_up2_pattern()


   .. py:method:: _generate_down2_pattern()


   .. py:method:: _generate_upanddown_pattern()


