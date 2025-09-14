Troubleshooting
===============

Welcome to the comprehensive troubleshooting guide for **JDXI-Editor**! This guide will help you diagnose and resolve common issues, from basic startup problems to advanced MIDI communication issues. We've organized solutions by category and severity to help you find the right fix quickly.

Before You Begin
================

**Gathering Information**
   Before troubleshooting, collect this information:
   - **Operating System**: Version and architecture (64-bit/32-bit)
   - **JDXI-Editor Version**: Check Help > About or run with ``--version``
   - **JD-Xi Firmware**: Check your synthesizer's firmware version
   - **Python Version**: If using source installation (``python --version``)
   - **Error Messages**: Copy exact error text and stack traces
   - **Log Files**: Located in ``~/.jdxi_editor/logs/`` (macOS/Linux) or ``%USERPROFILE%\.jdxi_editor\logs\`` (Windows)

**Log File Locations**
   - **macOS/Linux**: ``~/.jdxi_editor/logs/jdxi_editor.log``
   - **Windows**: ``%USERPROFILE%\.jdxi_editor\logs\jdxi_editor.log``
   - **Log Rotation**: Logs are automatically rotated when they reach 1MB

**Quick Diagnostic Commands**
   .. code-block:: console

      # Check JDXI-Editor version
      $ jdxi_manager --version
      
      # Check Python version (if applicable)
      $ python --version
      
      # List MIDI devices
      $ python -c "import rtmidi; print(rtmidi.MidiIn().get_ports())"

Common Issues by Category
=========================

** Startup & Launch Issues**
   Problems with application startup and initialization.

** MIDI Connection Issues**
   Problems with MIDI communication and device detection.

** Performance Issues**
   Slow response, high CPU usage, and memory problems.

** Editor & Interface Issues**
   Problems with the user interface and editor functionality.

** File & Data Issues**
   Problems with presets, projects, and data management.

** System-Specific Issues**
   Platform-specific problems and solutions.

Startup & Launch Issues
========================

**Application Won't Start**

**Symptoms:**
   - Application crashes immediately on launch
   - No error message or blank screen
   - Application starts but freezes during initialization

**Solutions:**

   1. **Check System Requirements**
      .. code-block:: console

         # Verify Python version (if using source installation)
         $ python --version
         # Should be 3.8 or higher
         
         # Check available memory
         $ free -h  # Linux
         $ vm_stat  # macOS
         $ wmic OS get TotalVisibleMemorySize  # Windows

   2. **Clear Configuration Files**
      .. code-block:: console

         # macOS/Linux
         $ rm -rf ~/.jdxi_editor/
         
         # Windows
         $ rmdir /s %USERPROFILE%\.jdxi_editor

   3. **Run with Debug Logging**
      .. code-block:: console

         # Enable verbose logging
         $ jdxi_manager --debug
         
         # Or for Python installation
         $ python -m jdxi_editor.main --debug

   4. **Check Dependencies**
      .. code-block:: console

         # Verify Qt6 installation
         $ python -c "from PySide6.QtWidgets import QApplication; print('Qt6 OK')"
         
         # Verify MIDI libraries
         $ python -c "import rtmidi; print('RtMidi OK')"

**Slow Startup Time**

**Symptoms:**
   - Application takes 30+ seconds to start
   - Progress bar shows slow loading
   - Interface appears gradually

**Solutions:**

   1. **Normal Behavior**
      - **Expected**: 30-60 seconds is normal for first launch
      - **Reason**: Application initializes many UI components and MIDI connections
      - **Solution**: Be patient, subsequent launches are faster

   2. **Optimize Startup**
      .. code-block:: console

         # Close other MIDI applications
         # Disable unnecessary startup programs
         # Ensure adequate RAM (8GB+ recommended)

   3. **Check for Conflicting Software**
      - Close other MIDI applications (DAWs, sequencers)
      - Disable antivirus real-time scanning temporarily
      - Check for USB port conflicts

**Permission Errors**

**Symptoms:**
   - "Permission denied" errors
   - Cannot create log files
   - Cannot save presets or settings

**Solutions:**

   1. **macOS**
      .. code-block:: console

         # Fix permissions
         $ sudo chown -R $(whoami) ~/.jdxi_editor/
         
         # Allow app in Security & Privacy
         # System Preferences > Security & Privacy > General

   2. **Windows**
      .. code-block:: console

         # Run as Administrator
         # Right-click JDXI-Editor > Run as Administrator
         
         # Fix folder permissions
         $ icacls "%USERPROFILE%\.jdxi_editor" /grant %USERNAME%:F

   3. **Linux**
      .. code-block:: console

         # Fix ownership
         $ sudo chown -R $USER:$USER ~/.jdxi_editor/
         
         # Add to audio group
         $ sudo usermod -a -G audio $USER

MIDI Connection Issues
======================

**No MIDI Devices Detected**

**Symptoms:**
   - "No MIDI devices found" message
   - Empty MIDI port list
   - Cannot connect to JD-Xi

**Solutions:**

   1. **Check Hardware Connection**
      - Ensure JD-Xi is powered on
      - Verify USB cable is properly connected
      - Try different USB ports
      - Test with different USB cable

   2. **Check Device Recognition**
      .. code-block:: console

         # List MIDI devices
         $ python -c "import rtmidi; print('Input ports:', rtmidi.MidiIn().get_ports()); print('Output ports:', rtmidi.MidiOut().get_ports())"

   3. **Driver Issues**
      - **Windows**: Install Roland USB-MIDI driver
      - **macOS**: Check Audio MIDI Setup utility
      - **Linux**: Install ALSA MIDI support

   4. **Port Conflicts**
      - Close other MIDI applications
      - Restart MIDI services
      - Reboot computer

**MIDI Communication Errors**

**Symptoms:**
   - "MIDI message validation failed" errors
   - Parameters not updating on synthesizer
   - Intermittent MIDI communication

**Solutions:**

   1. **Validate MIDI Messages**
      .. code-block:: console

         # Check MIDI message format
         $ python -c "from jdxi_editor.midi.sysex.validation import validate_midi_message; print(validate_midi_message([0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x00, 0xF7]))"

   2. **Check MIDI Port Status**
      - Verify input/output ports are open
      - Check for port conflicts
      - Restart MIDI connection

   3. **SysEx Message Issues**
      - Ensure JD-Xi is in correct mode
      - Check synthesizer settings
      - Verify firmware compatibility

**Connection Timeout**

**Symptoms:**
   - "Connection timeout" messages
   - Slow parameter updates
   - MIDI indicators not blinking

**Solutions:**

   1. **Increase Timeout Values**
      - Check MIDI settings in preferences
      - Increase connection timeout
      - Enable retry mechanisms

   2. **Optimize MIDI Settings**
      - Reduce MIDI buffer size
      - Disable unnecessary MIDI filtering
      - Use dedicated MIDI interface

   3. **System Optimization**
      - Close background applications
      - Check USB power management
      - Update USB drivers

Performance Issues
==================

**Slow Response Time**

**Symptoms:**
   - Delayed parameter updates
   - Sluggish interface response
   - High CPU usage

**Solutions:**

   1. **System Resource Management**
      .. code-block:: console

         # Check system resources
         $ top  # Linux/macOS
         $ tasklist  # Windows
         
         # Monitor MIDI activity
         $ python -c "import rtmidi; print('MIDI ports:', len(rtmidi.MidiIn().get_ports()))"

   2. **Optimize MIDI Settings**
      - Reduce MIDI update frequency
      - Disable unnecessary MIDI monitoring
      - Use efficient MIDI message formats

   3. **Application Settings**
      - Disable real-time parameter updates
      - Reduce UI refresh rate
      - Close unused editor tabs

**High Memory Usage**

**Symptoms:**
   - Application uses excessive RAM
   - System becomes slow
   - Out of memory errors

**Solutions:**

   1. **Memory Management**
      .. code-block:: console

         # Check memory usage
         $ ps aux | grep jdxi  # Linux/macOS
         $ tasklist /fi "imagename eq jdxi*"  # Windows

   2. **Optimize Application**
      - Close unused editor windows
      - Clear MIDI message buffers
      - Restart application periodically

   3. **System Optimization**
      - Increase virtual memory
      - Close other applications
      - Check for memory leaks

**CPU Usage Issues**

**Symptoms:**
   - High CPU usage even when idle
   - System fans running constantly
   - Application becomes unresponsive

**Solutions:**

   1. **Identify CPU-Intensive Operations**
      - Check MIDI message processing
      - Monitor UI update frequency
      - Profile application performance

   2. **Optimize Performance**
      - Reduce MIDI polling frequency
      - Disable unnecessary real-time updates
      - Use efficient data structures

   3. **System-Level Solutions**
      - Update system drivers
      - Check for background processes
      - Optimize power settings

Editor & Interface Issues
=========================

**Editor Windows Not Loading**

**Symptoms:**
   - Blank editor windows
   - Missing parameter controls
   - Editor tabs not responding

**Solutions:**

   1. **Check Editor Initialization**
      .. code-block:: console

         # Verify editor modules
         $ python -c "from jdxi_editor.ui.editors import *; print('Editors OK')"

   2. **Reset Editor State**
      - Close and reopen editor windows
      - Restart application
      - Clear editor cache

   3. **Check MIDI Connection**
      - Ensure MIDI is properly connected
      - Verify synthesizer communication
      - Test with different presets

**Parameter Controls Not Working**

**Symptoms:**
   - Sliders and knobs not responding
   - Parameter values not updating
   - MIDI messages not being sent

**Solutions:**

   1. **Check Parameter Mapping**
      - Verify parameter addresses
      - Check MIDI message format
      - Test with known working parameters

   2. **MIDI Communication**
      - Verify MIDI output port
      - Check message validation
      - Monitor MIDI traffic

   3. **Interface Issues**
      - Restart editor windows
      - Check for UI conflicts
      - Update application

**Preset Loading Issues**

**Symptoms:**
   - Presets not loading
   - Corrupted preset data
   - Preset names not displaying

**Solutions:**

   1. **Check Preset Files**
      .. code-block:: console

         # Verify preset directory
         $ ls -la ~/.jdxi_editor/presets/  # Linux/macOS
         $ dir %USERPROFILE%\.jdxi_editor\presets\  # Windows

   2. **Validate Preset Data**
      - Check JSON format
      - Verify parameter ranges
      - Test with factory presets

   3. **Reset Preset System**
      - Clear preset cache
      - Reload factory presets
      - Rebuild preset database

File & Data Issues
==================

**Preset Files Corrupted**

**Symptoms:**
   - "Invalid preset format" errors
   - Presets load with wrong values
   - Application crashes when loading presets

**Solutions:**

   1. **Validate Preset Files**
      .. code-block:: console

         # Check JSON validity
         $ python -c "import json; json.load(open('preset.json'))"

   2. **Recover Presets**
      - Use backup preset files
      - Restore from version control
      - Recreate corrupted presets

   3. **Prevent Corruption**
      - Always close application properly
      - Use reliable storage media
      - Regular backup of presets

**Project Files Not Saving**

**Symptoms:**
   - "Cannot save project" errors
   - Projects not appearing in file list
   - Data loss when closing application

**Solutions:**

   1. **Check File Permissions**
      .. code-block:: console

         # Fix permissions
         $ chmod 755 ~/.jdxi_editor/projects/  # Linux/macOS
         $ icacls "%USERPROFILE%\.jdxi_editor\projects" /grant %USERNAME%:F  # Windows

   2. **Verify Disk Space**
      .. code-block:: console

         # Check available space
         $ df -h  # Linux/macOS
         $ dir  # Windows

   3. **File System Issues**
      - Check for disk errors
      - Defragment disk (Windows)
      - Use different storage location

**MIDI File Playback Issues**

**Symptoms:**
   - MIDI files not playing
   - Incorrect timing or notes
   - Audio recording problems

**Solutions:**

   1. **Check MIDI File Format**
      - Verify MIDI file compatibility
      - Check file encoding
      - Test with different MIDI files

   2. **Audio System Issues**
      - Check audio drivers
      - Verify audio interface
      - Test with different audio settings

   3. **Timing Issues**
      - Adjust MIDI clock settings
      - Check system audio latency
      - Synchronize with external clock

System-Specific Issues
======================

**macOS Issues**

**Gatekeeper Security**
   .. code-block:: console

      # Allow app in Security & Privacy
      # System Preferences > Security & Privacy > General
      
      # Or bypass Gatekeeper
      $ xattr -d com.apple.quarantine /Applications/JD-Xi\ Editor.app

**MIDI Setup**
   .. code-block:: console

      # Open Audio MIDI Setup
      $ open /Applications/Utilities/Audio\ MIDI\ Setup.app
      
      # Check MIDI configuration
      # Verify JD-Xi appears in device list

**Permission Issues**
   .. code-block:: console

      # Fix application permissions
      $ sudo chown -R $(whoami) /Applications/JD-Xi\ Editor.app
      
      # Fix user directory permissions
      $ chmod -R 755 ~/.jdxi_editor/

**Windows Issues**

**Driver Problems**
   .. code-block:: console

      # Install Roland USB-MIDI driver
      # Download from Roland website
      
      # Check Device Manager
      $ devmgmt.msc
      
      # Verify MIDI devices appear

**Antivirus Interference**
   - Add JDXI-Editor to antivirus exceptions
   - Disable real-time scanning temporarily
   - Check Windows Defender settings

**DLL Issues**
   .. code-block:: console

      # Install Visual C++ Redistributable
      # Download from Microsoft website
      
      # Check system files
      $ sfc /scannow

**Linux Issues**

**MIDI Permissions**
   .. code-block:: console

      # Add user to audio group
      $ sudo usermod -a -G audio $USER
      
      # Check ALSA MIDI
      $ aconnect -l
      
      # Install MIDI support
      $ sudo apt install alsa-utils

**Qt Dependencies**
   .. code-block:: console

      # Install Qt libraries
      $ sudo apt install qt5-default libqt5widgets5
      
      # Or for Qt6
      $ sudo apt install qt6-base-dev

**AppImage Issues**
   .. code-block:: console

      # Install FUSE
      $ sudo apt install fuse
      
      # Make executable
      $ chmod +x JD-Xi-Editor-*.AppImage
      
      # Run with debug
      $ ./JD-Xi-Editor-*.AppImage --debug

Advanced Troubleshooting
========================

**Debug Mode**

Enable debug logging for detailed troubleshooting:

.. code-block:: console

   # Run with debug logging
   $ jdxi_manager --debug
   
   # Or for Python installation
   $ python -m jdxi_editor.main --debug
   
   # Check log files
   $ tail -f ~/.jdxi_editor/logs/jdxi_editor.log

**MIDI Monitoring**

Monitor MIDI traffic to diagnose communication issues:

.. code-block:: console

   # List MIDI ports
   $ python -c "import rtmidi; print('Input:', rtmidi.MidiIn().get_ports()); print('Output:', rtmidi.MidiOut().get_ports())"
   
   # Monitor MIDI messages
   $ python -c "import rtmidi; midi = rtmidi.MidiIn(); midi.open_port(0); print('Monitoring MIDI...')"

**System Diagnostics**

Check system health and compatibility:

.. code-block:: console

   # Check Python environment
   $ python -c "import sys; print(sys.version, sys.platform)"
   
   # Check Qt installation
   $ python -c "from PySide6.QtWidgets import QApplication; print('Qt6 version:', QApplication.applicationVersion())"
   
   # Check MIDI libraries
   $ python -c "import rtmidi, mido; print('MIDI libraries OK')"

**Performance Profiling**

Profile application performance:

.. code-block:: console

   # Monitor CPU usage
   $ top -p $(pgrep jdxi)
   
   # Monitor memory usage
   $ ps aux | grep jdxi
   
   # Check system resources
   $ htop  # Linux/macOS

Getting Help
============

**Self-Service Resources**

   1. **Check Log Files**
      - Review error messages in log files
      - Look for patterns in error occurrences
      - Check system resource usage

   2. **Test with Minimal Setup**
      - Use factory presets only
      - Disable all non-essential features
      - Test with single MIDI device

   3. **Reproduce Issues**
      - Document exact steps to reproduce
      - Note system state when issue occurs
      - Test with different configurations

**Community Support**

   1. **GitHub Issues**
      - Search existing issues
      - Create detailed bug reports
      - Include system information and logs

   2. **Community Forums**
      - Ask questions in discussions
      - Share solutions with others
      - Get help from experienced users

   3. **Documentation**
      - Review user guide thoroughly
      - Check API documentation
      - Look for video tutorials

**Professional Support**

   1. **Direct Support**
      - Contact development team
      - Request custom solutions
      - Get priority assistance

   2. **Training & Consulting**
      - Professional training sessions
      - Custom development services
      - System integration support

**Reporting Issues**

When reporting issues, include:

   1. **System Information**
      - Operating system and version
      - JDXI-Editor version
      - Python version (if applicable)
      - JD-Xi firmware version

   2. **Error Details**
      - Exact error messages
      - Stack traces
      - Log file excerpts

   3. **Reproduction Steps**
      - Detailed steps to reproduce
      - Expected vs. actual behavior
      - Screenshots or videos

   4. **Configuration**
      - MIDI setup
      - Application settings
      - Hardware configuration

**Emergency Recovery**

If all else fails:

   1. **Reset to Factory Defaults**
      .. code-block:: console

         # Remove configuration
         $ rm -rf ~/.jdxi_editor/  # Linux/macOS
         $ rmdir /s %USERPROFILE%\.jdxi_editor  # Windows

   2. **Reinstall Application**
      - Uninstall completely
      - Clear all configuration files
      - Reinstall from scratch

   3. **System Reset**
      - Restart computer
      - Check hardware connections
      - Update system drivers

Remember: Most issues have simple solutions. Start with the basic troubleshooting steps, check the log files, and don't hesitate to ask for help from the community or support team!
