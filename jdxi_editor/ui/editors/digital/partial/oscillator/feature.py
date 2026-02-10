"""
Re-export OscillatorFeature from base.layout.spec so existing imports from this module still work.
OscillatorFeature is defined in base so layout.spec does not import from digital (avoids circular import).
"""

from jdxi_editor.ui.editors.base.layout.spec import OscillatorFeature

__all__ = ["OscillatorFeature"]
