import unittest

from jdxi_editor.jdxi.midi.constant import MidiConstant
from jdxi_editor.midi.data.address.address import RolandSysExAddress, AddressStartMSB, AddressOffsetSystemUMB
from jdxi_editor.midi.data.address.helpers import apply_address_offset
from jdxi_editor.midi.data.parameter.program.zone import AddressParameterProgramZone
from jdxi_editor.midi.message.roland import RolandSysEx
from jdxi_editor.midi.sysex.composer import JDXiSysExComposer

"""from jdxi_editor import (
    JDXiSysExComposer,
    RolandSysExAddress,
    AddressStartMSB,
    AddressOffsetSystemUMB,
    AddressParameterProgramZone,
    MidiConstant,
)"""


class TestJDXiSysExComposer(unittest.TestCase):
    def setUp(self):
        self.composer = JDXiSysExComposer()

    def test_compose_arpeggio_switch_sysex(self):
        # 1) Create the base address (before offset)
        base_address = RolandSysExAddress(
            msb=AddressStartMSB.TEMPORARY_PROGRAM,
            umb=AddressOffsetSystemUMB.COMMON,
            lmb=0x00,
            lsb=MidiConstant.ZERO_BYTE,
        )

        # 2) Parameter and value
        param = AddressParameterProgramZone.ARPEGGIO_SWITCH
        value = 1  # ON

        # 3) Compute the expected address AFTER offset
        expected_address = apply_address_offset(base_address, param)

        # 4) Compose the SysEx
        sysex = self.composer.compose_message(base_address, param, value)

        # --- Structured-object assertions ---
        self.assertIsInstance(sysex, RolandSysEx)
        self.assertEqual(
            sysex.sysex_address,
            expected_address,
            f"Expected address {expected_address}, got {sysex.sysex_address}"
        )

        # --- Raw-bytes assertions ---
        raw = sysex.to_bytes()
        self.assertIsInstance(raw, (bytes, bytearray))
        data = list(raw)

        # Start / End
        self.assertEqual(data[0], 0xF0)
        self.assertEqual(data[-1], 0xF7)

        # Manufacturer ID
        self.assertEqual(data[1:4], [0x41, 0x10, 0x00])

        # Verify expected address bytes occur in the raw message
        ea = [expected_address.msb,
              expected_address.umb,
              expected_address.lmb,
              expected_address.lsb]
        for i in range(len(data) - 3):
            if data[i:i+4] == ea:
                break
        else:
            self.fail(f"Expected address bytes {ea} not found in {data}")

        # Verify the data byte
        self.assertIn(value, data)

        # (Optional) Debug
        print("Raw SysEx bytes:", data)


if __name__ == '__main__':
    unittest.main()
