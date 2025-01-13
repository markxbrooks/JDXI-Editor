# JDXI-Manager

![image info](./resources/jdxi.png)

A Manager for the Roland JD-Xi instrument, written in Python and the Qt Framework 

Designed to implement as many features at possible of the Roldand MIDI implementation without menu diving :-)

Not at all feature-complete or even complete, but have a go and let me know your feedback.

![image info](./resources/jdxi_app_600.png ) 

Current view of the Roland JD-Xi Manager App.


Getting started quick guide:

There are no builds yet, so you'll have to run it from a Python shell.

```code 

    $ git clone https://github.com/markxbrooks/JDXI-Manager.git
    $ cd JDXI-Manager
    $ python -m venv venv
    $ source venv/bin/activate
    $ python -r requirements.txt
    $ python -m jdxi_manager.main