jdxi_editor.ui.dialogs.settings
===============================

.. py:module:: jdxi_editor.ui.dialogs.settings

.. autoapi-nested-parse::

   Preferences Dialog

   Sets settings for various biotoolkit features



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.dialogs.settings.UiPreferencesDialog


Functions
---------

.. autoapisummary::

   jdxi_editor.ui.dialogs.settings.log_settings


Module Contents
---------------

.. py:function:: log_settings()

.. py:class:: UiPreferencesDialog(parent)

   Bases: :py:obj:`PySide6.QtWidgets.QDialog`


   .. py:attribute:: icon_size
      :value: None



   .. py:attribute:: settings


   .. py:method:: ui_setup(parent: PySide6.QtWidgets.QWidget = None)

      ui_setup
      :param parent: QWidget
      :return: None



   .. py:method:: load_log_level_from_settings()

      Load and migrate log level from settings (handles legacy string values).



   .. py:method:: update_log_level(level)

      Update log level for the current logger and all handlers



   .. py:method:: on_save_settings()

      on_save_settings
      :return: None



