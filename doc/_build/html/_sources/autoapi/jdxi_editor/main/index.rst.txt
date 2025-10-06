jdxi_editor.main
================

.. py:module:: jdxi_editor.main

.. autoapi-nested-parse::

   Main entry point for the JD-Xi Editor application.

   This module sets up the application environment, including logging, MIDI message listening,
   and application window initialization. It also manages the application's lifecycle,
   from initialization to event loop execution.

   Functions:
       midi_callback(msg): Callback function for handling incoming MIDI messages.

       listen_midi(port_name, callback): Listens for MIDI messages on the specified port
       and triggers the provided callback function.

       setup_logging(): Configures logging for the application, including console and file
        logging with rotation.

       main(): Main entry point to initialize and run the JD-Xi Editor application,
       set up the window, and handle MIDI message listening.



Attributes
----------

.. autoapisummary::

   jdxi_editor.main.profiling


Functions
---------

.. autoapisummary::

   jdxi_editor.main.main
   jdxi_editor.main.setup_splash_screen


Module Contents
---------------

.. py:function:: main()

.. py:function:: setup_splash_screen(app)

.. py:data:: profiling
   :value: False


