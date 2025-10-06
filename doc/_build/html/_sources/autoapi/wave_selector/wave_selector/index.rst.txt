wave_selector.wave_selector
===========================

.. py:module:: wave_selector.wave_selector

.. autoapi-nested-parse::

   Wave selector test class



Attributes
----------

.. autoapisummary::

   wave_selector.wave_selector.PCM_WAVES_CATEGORIZED
   wave_selector.wave_selector.app
   wave_selector.wave_selector.window
   wave_selector.wave_selector.selected_wave_number


Classes
-------

.. autoapisummary::

   wave_selector.wave_selector.WaveSelector


Module Contents
---------------

.. py:class:: WaveSelector(wave_list)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   Wave Selector


   .. py:attribute:: category_combo


   .. py:attribute:: wave_combo


   .. py:attribute:: wave_list


   .. py:attribute:: categories


   .. py:method:: update_waves()


   .. py:method:: get_selected_wave_number()

      Returns the wave number of the selected wave from the wave_combo.

      :returns: The wave number of the selected wave.
      :rtype: int



.. py:data:: PCM_WAVES_CATEGORIZED

.. py:data:: app

.. py:data:: window

.. py:data:: selected_wave_number

