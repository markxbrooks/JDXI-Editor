adsr.graph
==========

.. py:module:: adsr.graph


Classes
-------

.. autoapisummary::

   adsr.graph.ADSRGraph


Module Contents
---------------

.. py:class:: ADSRGraph(parent=None)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   .. py:attribute:: point_moved


   .. py:attribute:: attack_x
      :value: 0.1



   .. py:attribute:: decay_x
      :value: 0.3



   .. py:attribute:: sustain_level
      :value: 0.5



   .. py:attribute:: release_x
      :value: 0.7



   .. py:attribute:: dragging
      :value: None



   .. py:method:: paintEvent(event)

      Paint the ADSR graph.
      :param event: QPaintEvent



   .. py:method:: mousePressEvent(event)

      Handle mouse press event.
      :param event: QMouseEvent



   .. py:method:: mouseMoveEvent(event)

      Handle mouse move event.
      :param event: QMouseEvent



   .. py:method:: mouseReleaseEvent(event)

      Handle mouse release event.
      :param event: QMouseEvent



