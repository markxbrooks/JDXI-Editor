#!/usr/bin/env python3
"""
Unit tests for EffectParamRegistry.

Verifies that the registry correctly resolves parameter names to param objects
for Effect1, Effect2, Delay, and Reverb parameters.

Run: pytest tests/test_effect_param_registry.py -v
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath("."))

from jdxi_editor.midi.data.effects.param.registry import EffectParamRegistry
from jdxi_editor.midi.data.parameter.effects.effects import (
    DelayParam,
    Effect1Param,
    Effect2Param,
    ReverbParam,
)


class TestEffectParamRegistry(unittest.TestCase):
    """Test suite for EffectParamRegistry."""

    def setUp(self):
        """Set up registry with effect param classes."""
        self.registry = EffectParamRegistry(
            (Effect1Param, Effect2Param, DelayParam, ReverbParam)
        )

    def test_registry_resolves_effect1_params(self):
        """Test that registry resolves Effect 1 parameter names."""
        param = self.registry.resolve("EFX1_LEVEL")
        self.assertIsNotNone(param, "Registry should resolve EFX1_LEVEL")
        self.assertEqual(param.name, "EFX1_LEVEL")

        param = self.registry.resolve("EFX1_TYPE")
        self.assertIsNotNone(param, "Registry should resolve EFX1_TYPE")

    def test_registry_resolves_effect2_params(self):
        """Test that registry resolves Effect 2 parameter names."""
        param = self.registry.resolve("EFX2_LEVEL")
        self.assertIsNotNone(param, "Registry should resolve EFX2_LEVEL")
        self.assertEqual(param.name, "EFX2_LEVEL")

    def test_registry_resolves_delay_params(self):
        """Test that registry resolves Delay parameter names."""
        param = self.registry.resolve("DELAY_LEVEL")
        self.assertIsNotNone(param, "Registry should resolve DELAY_LEVEL")
        self.assertEqual(param.name, "DELAY_LEVEL")

        self.assertIsNotNone(self.registry.resolve("DELAY_ON_OFF"))
        self.assertIsNotNone(self.registry.resolve("DELAY_TYPE"))
        self.assertIsNotNone(self.registry.resolve("DELAY_FEEDBACK"))

    def test_registry_resolves_reverb_params(self):
        """Test that registry resolves Reverb parameter names."""
        param = self.registry.resolve("REVERB_LEVEL")
        self.assertIsNotNone(param, "Registry should resolve REVERB_LEVEL")
        self.assertEqual(param.name, "REVERB_LEVEL")

        self.assertIsNotNone(self.registry.resolve("REVERB_ON_OFF"))
        self.assertIsNotNone(self.registry.resolve("REVERB_TYPE"))
        self.assertIsNotNone(self.registry.resolve("REVERB_TIME"))

    def test_registry_returns_none_for_unknown_param(self):
        """Test that registry returns None for unknown parameter names."""
        self.assertIsNone(self.registry.resolve("UNKNOWN_PARAM"))
        self.assertIsNone(self.registry.resolve(""))


if __name__ == "__main__":
    unittest.main()
