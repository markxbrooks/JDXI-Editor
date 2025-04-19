import unittest
from unittest.mock import Mock, call
import time

from jdxi_editor.midi.data.constants.constants import DT1_COMMAND_12, RQ1_COMMAND_11
from jdxi_editor.midi.preset_loader import PresetLoader
from jdxi_editor.midi.data.preset_type import PresetType


class TestPresetLoader(unittest.TestCase):
    def setUp(self):
        self.midi_helper = Mock()


if __name__ == '__main__':
    unittest.main()
