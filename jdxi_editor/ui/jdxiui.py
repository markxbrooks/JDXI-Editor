"""
Composition of main JDXi components
"""

from jdxi_editor.ui.constant import JDXiUIConstants
from jdxi_editor.ui.parameters import JDXiUIParameters
from jdxi_editor.ui.preset.tone.lists import JDXiUIPreset
from jdxi_editor.ui.programs import JDXiUIProgramList
from jdxi_editor.ui.style import (
    JDXiUIDimensions,
    JDXiUIIconRegistry,
    JDXiUIStyle,
    JDXiUIThemeManager,
)


class JDXiUI:
    """Composition of main JDXI UI components as a single container."""

    Style: JDXiUIStyle = JDXiUIStyle
    ThemeManager: JDXiUIThemeManager = JDXiUIThemeManager
    IconRegistry: JDXiUIIconRegistry = JDXiUIIconRegistry
    Dimensions: JDXiUIDimensions = JDXiUIDimensions
    Parameters: JDXiUIParameters = JDXiUIParameters
    Constants: JDXiUIConstants = JDXiUIConstants
    Preset: JDXiUIPreset = JDXiUIPreset
    Program: JDXiUIProgramList = JDXiUIProgramList
