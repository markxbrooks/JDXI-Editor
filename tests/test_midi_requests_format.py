"""The generated RQ1 requests must be well formed, or the JD-Xi ignores them."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("."))

from jdxi_editor.midi.sysex.request.midi_requests import MidiRequests
from jdxi_editor.midi.sysex.request.read_session import address_from_rq1_hex

# name -> (address, size) from the JD-Xi parameter address map
_EXPECTED = {
    "PROGRAM_COMMON": ("18000000", "00000040"),
    "PROGRAM_VOCAL_EFFECT": ("18000100", "00000018"),
    "PROGRAM_EFFECT1": ("18000200", "00000111"),
    "PROGRAM_EFFECT2": ("18000400", "00000111"),
    "PROGRAM_DELAY": ("18000600", "00000064"),
    "PROGRAM_REVERB": ("18000800", "00000063"),
    "PROGRAM_ZONE_DIGITAL1": ("18003000", "00000023"),
    "PROGRAM_ZONE_DIGITAL2": ("18003100", "00000023"),
    "PROGRAM_ZONE_ANALOG": ("18003200", "00000023"),
    "PROGRAM_ZONE_DRUMS": ("18003300", "00000023"),
    "PROGRAM_CONTROLLER": ("18004000", "0000000c"),
    "ANALOG": ("19420000", "00000040"),
}


def _bytes(request: str) -> list[int]:
    return [int(t, 16) for t in request.split()]


class TestRq1Format(unittest.TestCase):
    def test_program_requests_have_address_and_size(self):
        for name, (address, size) in _EXPECTED.items():
            with self.subTest(name=name):
                data = _bytes(getattr(MidiRequests, name))
                # F0 41 10 00 00 00 0E 11 | address×4 | size×4 | checksum F7
                self.assertEqual(len(data), 18)
                self.assertEqual(data[7], 0x11)
                self.assertEqual(address_from_rq1_hex(getattr(MidiRequests, name)), address)
                self.assertEqual("".join(f"{b:02x}" for b in data[12:16]), size)

    def test_checksums(self):
        for name in _EXPECTED:
            with self.subTest(name=name):
                data = _bytes(getattr(MidiRequests, name))
                self.assertEqual((sum(data[8:16]) + data[16]) % 128, 0)


if __name__ == "__main__":
    unittest.main()
