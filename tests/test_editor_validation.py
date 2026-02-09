#!/usr/bin/env python3
"""
Unit tests for editor section validation.

This test suite validates that editor sections use the correct parameters,
preventing bugs like using FILTER parameters in AMP sections.
"""

import sys
import unittest
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from jdxi_editor.ui.editors.validation import (
    validate_adsr_spec,
    validate_digital_sections,
)
from jdxi_editor.ui.adsr.spec import ADSRStage, ADSRSpec
from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital


class TestEditorValidation(unittest.TestCase):
    """Test suite for editor section validation."""

    def test_validate_amp_adsr_spec_correct(self):
        """Test that correct AMP ADSR spec passes validation."""
        correct_spec = {
            ADSRStage.ATTACK: ADSRSpec(ADSRStage.ATTACK, Digital.Param.AMP_ENV_ATTACK_TIME),
            ADSRStage.DECAY: ADSRSpec(ADSRStage.DECAY, Digital.Param.AMP_ENV_DECAY_TIME),
            ADSRStage.SUSTAIN: ADSRSpec(ADSRStage.SUSTAIN, Digital.Param.AMP_ENV_SUSTAIN_LEVEL),
            ADSRStage.RELEASE: ADSRSpec(ADSRStage.RELEASE, Digital.Param.AMP_ENV_RELEASE_TIME),
        }
        
        errors = validate_adsr_spec("TestAmpSection", correct_spec, "AMP_ENV")
        self.assertEqual(len(errors), 0, f"Correct AMP ADSR spec should pass validation: {errors}")

    def test_validate_amp_adsr_spec_wrong_filter_params(self):
        """Test that AMP ADSR spec with FILTER parameters fails validation."""
        wrong_spec = {
            ADSRStage.ATTACK: ADSRSpec(ADSRStage.ATTACK, Digital.Param.FILTER_ENV_ATTACK_TIME),
            ADSRStage.DECAY: ADSRSpec(ADSRStage.DECAY, Digital.Param.FILTER_ENV_DECAY_TIME),
        }
        
        errors = validate_adsr_spec("TestAmpSection", wrong_spec, "AMP_ENV")
        self.assertGreater(len(errors), 0, "AMP ADSR spec with FILTER parameters should fail")
        self.assertTrue(
            any("FILTER_ENV" in error and "AMP_ENV" in error for error in errors),
            f"Error should mention wrong parameter type: {errors}"
        )

    def test_validate_filter_adsr_spec_correct(self):
        """Test that correct FILTER ADSR spec passes validation."""
        correct_spec = {
            ADSRStage.ATTACK: ADSRSpec(ADSRStage.ATTACK, Digital.Param.FILTER_ENV_ATTACK_TIME),
            ADSRStage.DECAY: ADSRSpec(ADSRStage.DECAY, Digital.Param.FILTER_ENV_DECAY_TIME),
            ADSRStage.SUSTAIN: ADSRSpec(ADSRStage.SUSTAIN, Digital.Param.FILTER_ENV_SUSTAIN_LEVEL),
            ADSRStage.RELEASE: ADSRSpec(ADSRStage.RELEASE, Digital.Param.FILTER_ENV_RELEASE_TIME),
            ADSRStage.PEAK: ADSRSpec(ADSRStage.PEAK, Digital.Param.FILTER_ENV_DEPTH),
        }
        
        errors = validate_adsr_spec("TestFilterSection", correct_spec, "FILTER_ENV")
        self.assertEqual(len(errors), 0, f"Correct FILTER ADSR spec should pass validation: {errors}")

    def test_validate_filter_adsr_spec_wrong_amp_params(self):
        """Test that FILTER ADSR spec with AMP parameters fails validation."""
        wrong_spec = {
            ADSRStage.ATTACK: ADSRSpec(ADSRStage.ATTACK, Digital.Param.AMP_ENV_ATTACK_TIME),
            ADSRStage.DECAY: ADSRSpec(ADSRStage.DECAY, Digital.Param.AMP_ENV_DECAY_TIME),
        }
        
        errors = validate_adsr_spec("TestFilterSection", wrong_spec, "FILTER_ENV")
        self.assertGreater(len(errors), 0, "FILTER ADSR spec with AMP parameters should fail")
        self.assertTrue(
            any("AMP_ENV" in error and "FILTER_ENV" in error for error in errors),
            f"Error should mention wrong parameter type: {errors}"
        )

    def test_validate_digital_sections_integration(self):
        """Integration test: validate all digital sections."""
        errors = validate_digital_sections()
        
        # This test will fail if there are validation errors
        if errors:
            error_messages = []
            for section_name, section_errors in errors.items():
                error_messages.append(f"{section_name}:")
                error_messages.extend(f"  • {e}" for e in section_errors)
            
            self.fail(
                f"Digital sections validation failed:\n" + "\n".join(error_messages)
            )

    def test_amp_section_has_correct_adsr_params(self):
        """Test that DigitalAmpSection uses AMP_ENV parameters."""
        from jdxi_editor.ui.editors.digital.partial.amp.section import DigitalAmpSection
        
        if not hasattr(DigitalAmpSection, "ADSR_SPEC"):
            self.skipTest("DigitalAmpSection has no ADSR_SPEC")
        
        adsr_spec = DigitalAmpSection.ADSR_SPEC
        
        # Check each stage uses AMP_ENV parameters
        for stage, spec in adsr_spec.items():
            param = spec.param
            param_name = getattr(param, "name", str(param))
            
            self.assertTrue(
                param_name.startswith("AMP_ENV"),
                f"DigitalAmpSection ADSR_SPEC[{stage}] uses '{param_name}' "
                f"but should use AMP_ENV parameter"
            )

    def test_filter_section_has_correct_adsr_params(self):
        """Test that DigitalFilterSection uses FILTER_ENV parameters."""
        from jdxi_editor.ui.editors.digital.partial.filter import DigitalFilterSection
        
        if not hasattr(DigitalFilterSection, "ADSR_SPEC"):
            self.skipTest("DigitalFilterSection has no ADSR_SPEC")
        
        adsr_spec = DigitalFilterSection.ADSR_SPEC
        
        # Check each stage uses FILTER_ENV parameters
        for stage, spec in adsr_spec.items():
            param = spec.param
            param_name = getattr(param, "name", str(param))
            
            self.assertTrue(
                param_name.startswith("FILTER_ENV"),
                f"DigitalFilterSection ADSR_SPEC[{stage}] uses '{param_name}' "
                f"but should use FILTER_ENV parameter"
            )


if __name__ == "__main__":
    unittest.main()
