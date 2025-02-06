To set up DivingBoard to work properly:

    Running:
        1) Place the DivingBoard folder on the Desktop, ie make it /home/pi/Desktop/DivingBoard/divingBoard.py

    External Activity LED:
        1) Enter CLI and type:
            sudo nano /boot/config.txt
        2) add the following lines to the end, where XX is the gpio pin number of the pin to be used as the external ACT LED:
            #act led now on gpio XX
            dtparam=act_led_gpio=XX
        3) reboot the pi to test that it worked.

    Start up automatically:
        1) Enter CLI and type:
            crontab -e
        2) Add the following lines to the end of the file:
            @reboot python3 /home/pi/Desktop/DivingBoard/divingBoard.py &
        3) Save the file and reboot the Pi to test that it worked.

    Encoder Buttons:
        buttonA = gpiozero.Button(5)
        buttonB = gpiozero.Button(6)
        buttonC = gpiozero.Button(13)
        buttonF = gpiozero.Button(12)
        
    Thinking LED:
        thinkingPin = 3

The DivingBoard stores information about different MIDI equipment in .dbd (Diving Board Data) files- aside from the first line (see below), these are just CSV files with each line holding the info required for one parameter, laid out like so:

    Synth,Partial,Section,Name,address,minimum,maximum,read-in index,Display Mode

Where:
    Synth,Partial,Section
        These categorise where the parameter is stored, like a file directory.
        EG: An,A,Filter denotes a parameter stored in the Filter section of the first partial of the analogue synth engine.
        The names Synth, Partial and Section are based on terminology from the Roland JD-Xi synthesiser, but don't have to be used as such- think of them as three layers of heirarchy for organising different groups of controls.
        All three levels of the heirarchy must be used, even if they aren't required. For example, the analogue engine on the JD-Xi only has one partial, so technically 'A' in 'An,A,Filter' isn't needed.
    Name
        The label for the parameter that will show up on-screen
        This has a maximum of four characters, in order that all parameters fit on-screen
    address
        A dot-separated list of every possible MIDI message associated with the parameter, in order from minimum parameter value to maximum value.
    minimum,maximum
        The minimum and maximum values of the parameter.
        These elements of the parameter data are sort of unnecessary to store now, and could be calculated at run-time instead. This change may be implemented in the future.
    read-in index
        Not in use currently, planned for a 'parameter peek' feature in which the current value of parameters is shown on-screen when a button is pressed.
        Refers to the position of the value of the parameter in the sysex dump of the current patch that can be coaxed from the JD-Xi. As this is synth-specific, this may not be implemented.
    Display Mode
        Refers to the way the parameter's current level is displayed on-screen
            Mostly just during the 'parameter peek' planned feature, as updating the LCD with the current value of the parameter continuously introduces heavy latency.
        Display mode 1 = 0-127, 2 = -63 - +63, 3 = -100 - +100 in increments of ten, and a space-separated list of words = possible values (written for display on the screen)
            Only the space-separated list of words appears on-screen at the moment, and is reserved for stuff like different reverb types, different waveforms, or other short lists of discrete values

The first line of the file contains additional info used by the programme, including
    Name
        Used to identify the synth to users
    MIDI port name
        *Will* be used to auto-identify the connected MIDI device and choose which DBD file to use.
