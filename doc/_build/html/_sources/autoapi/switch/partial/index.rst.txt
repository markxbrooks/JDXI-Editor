switch.partial
==============

.. py:module:: switch.partial

.. autoapi-nested-parse::

   Module: partials_panel
   ======================

   This module provides a graphical user interface for controlling individual
   partials within a digital synthesizer patch using PySide6. It includes
   checkbox-based widgets to enable and select specific partials.

   Classes:
   --------
   - `PartialSwitch`: A UI component representing a single partial with ON/OFF
     and selection controls.
   - `PartialsPanel`: A container widget that groups multiple `PartialSwitch`
     components for managing multiple partials at once.

   Features:
   ---------
   - Uses `QCheckBox` widgets to toggle partial states.
   - Supports custom styling with a dark theme and red-accented selection indicators.
   - Integrates `qtawesome` icons for better UI visualization.
   - Emits signals when partial states change, allowing external components
     to respond to updates dynamically.

   Usage Example:
   --------------
   >>> panel = PartialsPanel()
   >>> panel.show()



Classes
-------

.. autoapisummary::

   switch.partial.PartialSwitch


Module Contents
---------------

.. py:class:: PartialSwitch(partial: jdxi_editor.midi.data.digital.partial.DigitalPartial, parent=None)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   Widget for controlling address single partial's state


   .. py:attribute:: stateChanged


   .. py:attribute:: partial


   .. py:attribute:: enable_check


   .. py:attribute:: select_check


   .. py:method:: _on_state_changed(_)

      Handle checkbox state changes



   .. py:method:: setState(enabled: bool, selected: bool)

      Set the partial state



   .. py:method:: setSelected(selected: bool)

      Set the partial state



