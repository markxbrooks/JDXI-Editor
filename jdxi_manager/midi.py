class MIDIHelper:
    # MIDI constants
    ROL_ID = 0x41
    JDXI_ID = bytes([0x00, 0x00, 0x00, 0x0E])
    DT1 = 0x12
    
    @staticmethod
    def create_sysex_message(address, data):
        """Create a Roland SysEx message"""
        # Format: F0 41 10 00 00 00 0E 12 [addr] [data] F7
        msg = bytes([0xF0, MIDIHelper.ROL_ID, 0x10]) + \
              bytes([0x00, 0x00, 0x00]) + \
              MIDIHelper.JDXI_ID + \
              bytes([MIDIHelper.DT1]) + \
              address + \
              data + \
              bytes([0xF7])
        return msg
        
    @staticmethod
    def create_parameter_message(synth_num, partial, parameter, value):
        """Create a parameter change message for Digital Synth"""
        # Base address for Digital Synth 1/2
        base = 0x19
        part = 0x20 if synth_num == 1 else 0x21
        
        # Calculate parameter address
        if parameter < 0x40:  # Common parameters
            addr = bytes([base, part, 0x00, parameter])
        else:
            # Partial parameters
            partial_offset = 0x20 + (partial - 1)
            addr = bytes([base, part, partial_offset, parameter - 0x40])
            
        return MIDIHelper.create_sysex_message(addr, bytes([value])) 