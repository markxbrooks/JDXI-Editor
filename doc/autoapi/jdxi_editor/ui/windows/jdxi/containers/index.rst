jdxi_editor.ui.windows.jdxi.containers
======================================

.. py:module:: jdxi_editor.ui.windows.jdxi.containers


Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/jdxi_editor/ui/windows/jdxi/containers/arpeggiator/index
   /autoapi/jdxi_editor/ui/windows/jdxi/containers/digital_display/index
   /autoapi/jdxi_editor/ui/windows/jdxi/containers/effects/index
   /autoapi/jdxi_editor/ui/windows/jdxi/containers/octave/index
   /autoapi/jdxi_editor/ui/windows/jdxi/containers/parts/index
   /autoapi/jdxi_editor/ui/windows/jdxi/containers/program/index
   /autoapi/jdxi_editor/ui/windows/jdxi/containers/sequencer/index
   /autoapi/jdxi_editor/ui/windows/jdxi/containers/sliders/index
   /autoapi/jdxi_editor/ui/windows/jdxi/containers/title/index
   /autoapi/jdxi_editor/ui/windows/jdxi/containers/tone/index
   /autoapi/jdxi_editor/ui/windows/jdxi/containers/wheels/index


Functions
---------

.. autoapisummary::

   jdxi_editor.ui.windows.jdxi.containers.add_arpeggiator_buttons
   jdxi_editor.ui.windows.jdxi.containers.add_digital_display
   jdxi_editor.ui.windows.jdxi.containers.add_effects_container
   jdxi_editor.ui.windows.jdxi.containers.add_octave_buttons
   jdxi_editor.ui.windows.jdxi.containers.create_parts_container
   jdxi_editor.ui.windows.jdxi.containers.add_program_container
   jdxi_editor.ui.windows.jdxi.containers.create_program_buttons_row
   jdxi_editor.ui.windows.jdxi.containers.add_sequencer_container
   jdxi_editor.ui.windows.jdxi.containers.add_favorite_button_container
   jdxi_editor.ui.windows.jdxi.containers.create_sequencer_buttons_row
   jdxi_editor.ui.windows.jdxi.containers.add_slider_container
   jdxi_editor.ui.windows.jdxi.containers.add_title_container
   jdxi_editor.ui.windows.jdxi.containers.add_tone_container
   jdxi_editor.ui.windows.jdxi.containers.create_tone_buttons_row
   jdxi_editor.ui.windows.jdxi.containers.build_wheel_row
   jdxi_editor.ui.windows.jdxi.containers.build_wheel_label_row


Package Contents
----------------

.. py:function:: add_arpeggiator_buttons(widget)

   Add arpeggiator up/down buttons to the interface


.. py:function:: add_digital_display(central_widget, parent)

   Add container with digital display on the JD-Xi image


.. py:function:: add_effects_container(central_widget, open_vocal_fx, open_effects)

   Effects button in top row


.. py:function:: add_octave_buttons(widget, send_octave)

   Add octave up/down buttons to the interface


.. py:function:: create_parts_container(parent_widget, on_open_d1, on_open_d2, on_open_drums, on_open_analog, on_open_arp, on_select_synth)

   Create the Parts Select container widget


.. py:function:: add_program_container(central_widget, create_program_buttons_row)

   add program container


.. py:function:: create_program_buttons_row()

   create program navigation buttons


.. py:function:: add_sequencer_container(central_widget, midi_helper, on_context_menu, on_save_favorite)

.. py:function:: add_favorite_button_container(central_widget)

   Create a circular button to set and unset favorites


.. py:function:: create_sequencer_buttons_row(midi_helper, on_context_menu, on_save_favorite)

   Create sequencer button row layout with interactive buttons


.. py:function:: add_slider_container(central_widget, midi_helper)

   ad slider container


.. py:function:: add_title_container(central_widget)

   add container for main title


.. py:function:: add_tone_container(central_widget, create_tone_buttons_horizontal_layout, previous_tone, next_tone)

   For tone buttons


.. py:function:: create_tone_buttons_row(previous_tone, next_tone)

.. py:function:: build_wheel_row(midi_helper)

.. py:function:: build_wheel_label_row()

