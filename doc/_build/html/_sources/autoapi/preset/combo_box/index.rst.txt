preset.combo_box
================

.. py:module:: preset.combo_box

.. autoapi-nested-parse::

   combo_box.py

   This module defines a custom combo box widget for selecting presets in the JDXI editor.
   It provides a user-friendly interface for searching and selecting presets from a list,
   and emits a signal when a preset is loaded. The widget includes a search box, a category
   selector, and a load button. The presets are displayed in a combo box, allowing users
   to filter and select them easily.
   #                 selected_text.split(":")[0].strip()



Classes
-------

.. autoapisummary::

   preset.combo_box.PresetComboBox


Module Contents
---------------

.. py:class:: PresetComboBox(presets, parent=None)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   A custom widget for selecting presets from a combo box.


   .. py:attribute:: preset_loaded


   .. py:attribute:: preset_list


   .. py:attribute:: full_presets


   .. py:attribute:: index_mapping
      :value: []



   .. py:attribute:: category_mapping


   .. py:attribute:: presets


   .. py:attribute:: search_box


   .. py:attribute:: combo_box


   .. py:attribute:: category_combo_box


   .. py:attribute:: load_button


   .. py:method:: _on_load_clicked()

      Handle load button click.



   .. py:method:: _filter_presets(search_text: str)

      Filter presets based on the search text.

      :param search_text: str
      :return: None



   .. py:method:: update_category_combo_box_categories()

      Update the category combo box with available categories.



   .. py:method:: set_presets(presets)


   .. py:method:: current_preset()

      Get the currently selected preset.



   .. py:method:: on_category_changed(_)

      Handle category selection change.



   .. py:method:: _populate_presets(search_text: str = '')

      Populate the program list with available presets.



