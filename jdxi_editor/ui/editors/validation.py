"""
Validation utilities for editor sections.

This module provides validation functions to ensure editor sections
are configured correctly, preventing bugs like using FILTER parameters
in AMP sections or vice versa.

Usage:
    # Run validation directly
    python jdxi_editor/ui/editors/validation.py
    
    # Or run the unit tests
    python -m unittest tests.test_editor_validation
    
    # Or use in code
    from jdxi_editor.ui.editors.validation import validate_digital_sections
    errors = validate_digital_sections()
    if errors:
        # Handle validation errors
"""

from typing import Dict, List, Optional, Set, Type

from picomidi.sysex.parameter.address import AddressParameter

from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital
from jdxi_editor.ui.adsr.spec import ADSRSpec, ADSRStage


def validate_adsr_spec(
    section_name: str,
    adsr_spec: Dict[ADSRStage, ADSRSpec],
    expected_prefix: str,
) -> List[str]:
    """
    Validate that ADSR_SPEC uses parameters with the expected prefix.
    
    Args:
        section_name: Name of the section being validated (e.g., "DigitalAmpSection")
        adsr_spec: The ADSR_SPEC dictionary to validate
        expected_prefix: Expected parameter prefix (e.g., "AMP_ENV", "FILTER_ENV")
    
    Returns:
        List of error messages (empty if validation passes)
    """
    errors = []
    
    if not adsr_spec:
        return errors
    
    # Map of ADSR stages to expected parameter name patterns
    stage_to_param = {
        ADSRStage.ATTACK: f"{expected_prefix}_ATTACK_TIME",
        ADSRStage.DECAY: f"{expected_prefix}_DECAY_TIME",
        ADSRStage.SUSTAIN: f"{expected_prefix}_SUSTAIN_LEVEL",
        ADSRStage.RELEASE: f"{expected_prefix}_RELEASE_TIME",
    }
    
    # PEAK is optional and may not exist for all envelope types
    if expected_prefix == "FILTER_ENV":
        stage_to_param[ADSRStage.PEAK] = f"{expected_prefix}_DEPTH"
    
    for stage, spec in adsr_spec.items():
        if not isinstance(spec, ADSRSpec):
            errors.append(
                f"{section_name}: ADSR_SPEC[{stage}] is not an ADSRSpec instance"
            )
            continue
        
        param = spec.param
        if param is None:
            errors.append(f"{section_name}: ADSR_SPEC[{stage}].param is None")
            continue
        
        # Get parameter name
        param_name = getattr(param, "name", None)
        if param_name is None:
            # Try to get it from the parameter object itself
            param_name = str(param)
        
        # Check if this stage should have a parameter
        expected_param_pattern = stage_to_param.get(stage)
        if expected_param_pattern is None:
            # PEAK might not be required for all envelope types
            if stage == ADSRStage.PEAK and expected_prefix == "AMP_ENV":
                # AMP doesn't have a PEAK parameter, so this is OK if missing
                continue
            else:
                errors.append(
                    f"{section_name}: ADSR_SPEC[{stage}] has unexpected stage "
                    f"(expected one of: {list(stage_to_param.keys())})"
                )
            continue
        
        # Validate parameter name matches expected prefix
        if not param_name.startswith(expected_prefix):
            # Check if it's using the wrong prefix
            wrong_prefixes = ["FILTER_ENV", "AMP_ENV", "OSC_PITCH_ENV"]
            for wrong_prefix in wrong_prefixes:
                if wrong_prefix != expected_prefix and param_name.startswith(wrong_prefix):
                    errors.append(
                        f"{section_name}: ADSR_SPEC[{stage}] uses wrong parameter: "
                        f"{param_name} (expected {expected_param_pattern}, "
                        f"found {wrong_prefix} parameter)"
                    )
                    break
            else:
                errors.append(
                    f"{section_name}: ADSR_SPEC[{stage}] parameter '{param_name}' "
                    f"doesn't match expected pattern '{expected_param_pattern}'"
                )
    
    return errors


def validate_section_parameters(
    section_name: str,
    param_specs: List,
    expected_prefixes: Set[str],
) -> List[str]:
    """
    Validate that PARAM_SPECS use parameters with expected prefixes.
    
    Args:
        section_name: Name of the section being validated
        param_specs: List of SliderSpec/SwitchSpec/ComboBoxSpec objects
        expected_prefixes: Set of allowed parameter name prefixes
    
    Returns:
        List of error messages (empty if validation passes)
    """
    errors = []
    
    for spec in param_specs:
        param = getattr(spec, "param", None)
        if param is None:
            continue
        
        param_name = getattr(param, "name", None)
        if param_name is None:
            param_name = str(param)
        
        # Check if parameter name starts with any expected prefix
        matches_prefix = any(param_name.startswith(prefix) for prefix in expected_prefixes)
        
        if not matches_prefix:
            # Check for common wrong prefixes
            wrong_prefixes = {
                "FILTER_ENV": ["AMP_ENV", "OSC_PITCH_ENV"],
                "AMP_ENV": ["FILTER_ENV", "OSC_PITCH_ENV"],
                "FILTER_": ["AMP_"],
                "AMP_": ["FILTER_"],
            }
            
            found_wrong = False
            for prefix, wrong_list in wrong_prefixes.items():
                if param_name.startswith(prefix):
                    for wrong_prefix in wrong_list:
                        if wrong_prefix in expected_prefixes:
                            errors.append(
                                f"{section_name}: Parameter '{param_name}' uses wrong prefix "
                                f"'{prefix}' (should use '{wrong_prefix}')"
                            )
                            found_wrong = True
                            break
                    if found_wrong:
                        break
            
            if not found_wrong:
                errors.append(
                    f"{section_name}: Parameter '{param_name}' doesn't match "
                    f"expected prefixes: {expected_prefixes}"
                )
    
    return errors


def validate_digital_sections() -> Dict[str, List[str]]:
    """
    Validate all digital editor sections for correct parameter usage.
    
    Returns:
        Dictionary mapping section names to lists of error messages
    """
    from jdxi_editor.ui.editors.digital.partial.amp import DigitalAmpSection
    from jdxi_editor.ui.editors.digital.partial.filter import DigitalFilterSection
    
    all_errors = {}
    
    # Validate DigitalAmpSection
    amp_errors = []
    if hasattr(DigitalAmpSection, "ADSR_SPEC"):
        amp_adsr_errors = validate_adsr_spec(
            "DigitalAmpSection",
            DigitalAmpSection.ADSR_SPEC,
            "AMP_ENV",
        )
        amp_errors.extend(amp_adsr_errors)
    
    if hasattr(DigitalAmpSection, "PARAM_SPECS"):
        amp_param_errors = validate_section_parameters(
            "DigitalAmpSection",
            DigitalAmpSection.PARAM_SPECS,
            {"AMP_", "LEVEL_", "CUTOFF_"},
        )
        amp_errors.extend(amp_param_errors)
    
    if amp_errors:
        all_errors["DigitalAmpSection"] = amp_errors
    
    # Validate DigitalFilterSection
    filter_errors = []
    if hasattr(DigitalFilterSection, "ADSR_SPEC"):
        filter_adsr_errors = validate_adsr_spec(
            "DigitalFilterSection",
            DigitalFilterSection.ADSR_SPEC,
            "FILTER_ENV",
        )
        filter_errors.extend(filter_adsr_errors)
    
    if hasattr(DigitalFilterSection, "PARAM_SPECS"):
        filter_param_errors = validate_section_parameters(
            "DigitalFilterSection",
            DigitalFilterSection.PARAM_SPECS,
            {"FILTER_"},
        )
        filter_errors.extend(filter_param_errors)
    
    if filter_errors:
        all_errors["DigitalFilterSection"] = filter_errors
    
    return all_errors


if __name__ == "__main__":
    """Run validation when executed directly."""
    import sys
    from pathlib import Path

    # Add project root to path if running directly
    project_root = Path(__file__).parent.parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    errors = validate_digital_sections()
    
    if errors:
        print("❌ Validation failed!")
        print("=" * 60)
        for section_name, section_errors in errors.items():
            print(f"\n{section_name}:")
            for error in section_errors:
                print(f"  • {error}")
        exit(1)
    else:
        print("✅ All sections validated successfully!")
        exit(0)
