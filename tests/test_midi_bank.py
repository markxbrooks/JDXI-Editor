"""Unit tests for the Bank value object (no Qt / theme deps)."""

import unittest

from jdxi_editor.midi.bank import Bank


class TestBank(unittest.TestCase):
    def test_defaults_to_zero(self) -> None:
        bank = Bank()
        self.assertEqual((bank.msb, bank.lsb), (0, 0))

    def test_in_range(self) -> None:
        bank = Bank(msb=95, lsb=64)
        self.assertEqual((bank.msb, bank.lsb), (95, 64))

    def test_msb_out_of_range(self) -> None:
        with self.assertRaises(ValueError):
            Bank(msb=128, lsb=0)
        with self.assertRaises(ValueError):
            Bank(msb=-1, lsb=0)

    def test_lsb_out_of_range(self) -> None:
        with self.assertRaises(ValueError):
            Bank(msb=0, lsb=128)
        with self.assertRaises(ValueError):
            Bank(msb=0, lsb=-1)

    def test_frozen(self) -> None:
        bank = Bank(msb=1, lsb=2)
        with self.assertRaises(Exception):
            bank.msb = 3  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
