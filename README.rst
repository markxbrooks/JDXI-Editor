JDXI-Editor
===========

.. image:: ./resources/jdxi_cartoon_600.png
   :alt: Roland JD-Xi Cartoon

**JDXI-Editor**: A powerful MIDI editor for the **Roland JD-Xi synthesizer**, built with **Python**, **Qt Framework**, and **RtMidi**. Simplify MIDI editing, preset selection, and sound design without hardware menus. Perfect for musicians and sound designers!

It's designed to implement as many features as possible from Roland's MIDI implementation—without the need to dive through hardware menus. 🎛️

.. warning::
   This app is a work in progress and not yet feature-complete—but feel free to try it out and share your feedback!

Features of JDXI-Editor for Roland JD-Xi Synthesizer
----------------------------------------------------
- **On-Screen Keyboard**: Easily play and test sounds from your JD-Xi.
- **Preset Selection with Search**: Quickly find and load presets.
- **Octave Shifting**: Adjust octave ranges for precise sound control.
- **Digital & Analog Synth Editors**: Edit JD-Xi's digital and analog synths directly.
- **Drum Part Editor**: Customize drum sounds and patterns 🥁.
- **Effects Editor**: Edit reverb, delay, vocoder, and arpeggiator settings.
- **MIDI Debugger**: Monitor and debug MIDI messages efficiently.

Designed for musicians, sound designers, and MIDI enthusiasts looking to unlock the full potential of the Roland JD-Xi synthesizer!

Current App Preview
-------------------

.. image:: ./resources/main_window_0.6.gif
   :alt: Roland JD-Xi Main Editor Window

Roland JD-Xi MIDI Editor Video Demo
-----------------------------------
Watch how **JDXI-Editor** simplifies sound design and MIDI editing for the **Roland JD-Xi synthesizer**:

.. image:: https://img.youtube.com/vi/vw-T-9LJkng/0.jpg
   :target: https://www.youtube.com/watch?v=vw-T-9LJkng
   :alt: Watch the demo

Getting Started
===============

MacOS 🖥️
---------
There is a new build for MacOS Sequoia. See the `releases page <https://github.com/markxbrooks/JDXI-Editor/releases/tag/v0.0.8>`_

Windows 📦
----------
There is a new build for Windows See the `releases page <https://github.com/markxbrooks/JDXI-Editor/releases/tag/v0.0.8>`_

Python 🐍
---------
If you're a Python developer, you may wish to run the program from a Python environment:

.. code-block:: bash

   $ git clone https://github.com/markxbrooks/JDXI-Editor.git
   $ cd JDXI-Editor
   $ python -m venv venv
   $ source venv/bin/activate
   $ python -m pip install -r requirements.txt
   $ python -m jdxi_editor.main

Documentation
=============
Access JD-Xi documentation in the format that works best for you:

Available Formats:
------------------

HTML Documentation:
~~~~~~~~~~~~~~~~~~~
https://markxbrooks.github.io/JDXI-Editor/

PDF Documentation:
~~~~~~~~~~~~~~~~~~
Coming soon!

UI Previews
===========

Digital & Analog Synths
-----------------------

.. image:: ./resources/analog_synth_600.png
   :alt: Analog Synth
   :target: ./resources/analog_synth.png

.. image:: ./resources/digital_synth_600.png
   :alt: Digital Synths
   :target: ./resources/digital_synth.png

Midi File Player
----------------

.. image:: ./resources/midi_player_600.png
   :alt: Midi File Player
   :target: ./resources/midi_player.png

Pattern Sequencer
-----------------

.. image:: ./resources/pattern_600.png
   :alt: Pattern Sequencer
   :target: ./resources/pattern.png

Effects and Arpeggiator
------------------------

.. image:: ./resources/effects_600.png
   :alt: Effects and Arpeggiator
   :target: ./resources/effects.png

Vocal Effects
-------------

.. image:: ./resources/vocal_effects_600.png
   :alt: Vocal Effects Window
   :target: ./resources/vocal_effects.png

Log Viewer and MIDI Debugger
-----------------------------

.. image:: ./resources/logs_and_midi_600.png
   :alt: Logs and MIDI Debugger
   :target: ./resources/logs_and_midi.png

MIDI Configuration
------------------

.. image:: ./resources/midi_config_200.png
   :alt: MIDI Configuration Window
   :target: ./resources/midi_config.png

Features
========

- On-screen Keyboard
- Preset selection with search
- Octave shifting
- JD-Xi-style LCD Display
- ADSR displays
- Pitch ENV displays
- Digital Synth Parts 1 & 2 (including 3 partials per part)
- Analog Synth Editor
- Drum Part Editor 🥁
- Effects: Reverb, Delay, Vocoder
- Arpeggiator Editor

Coming Soon
===========

- Pattern Sequencer (one measure is implemented)
- PW Display widget is sorely needed

Frequently Asked Questions
=========================

What is JDXI-Editor?
--------------------
JDXI-Editor is a Python-based MIDI editor for the Roland JD-Xi synthesizer, built with the Qt Framework and RtMidi.

Does JDXI-Editor work on MacOS and Windows?
--------------------------------------------
Yes, JDXI-Editor supports MacOS, and a Windows version is coming soon!

What features does JDXI-Editor offer?
-------------------------------------
JDXI-Editor provides preset selection, synth editing, drum part customization, effects editing, and more.

Links
=====

- Learn more about the `Roland JD-Xi Synthesizer <https://www.roland.com/global/products/jd-xi/>`_.
- Explore the `Qt Framework <https://www.qt.io/>`_ for building cross-platform apps.
- Discover `RtMidi <https://www.music.mcgill.ca/~gary/rtmidi/>`_, a real-time MIDI library.

Contribute and Share Feedback
=============================
JDXI-Editor is a growing project! 
- ⭐ Star this repository to support its development.
- 🛠️ Contribute features or report issues via `GitHub Issues <https://github.com/markxbrooks/JDXI-Editor/issues>`_.

Credits
=======

- `Qt <https://www.qt.io/>`_
- `RtMidi <https://www.music.mcgill.ca/~gary/rtmidi/>`_
- `Cursor.ai <https://cursor.so>`_
- `qtawesome <https://github.com/spyder-ide/qtawesome>`_
- Inspiration from many great JD-Xi editor projects that paved the way
- **Roland**, for creating such a powerful little synth!

.. note::
   Made with 🎹 and ☕ by @markxbrooks
