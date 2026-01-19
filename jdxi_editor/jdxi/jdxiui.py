"""
Composition of main JDXi components
"""


from jdxi_editor.jdxi.preset import JDXiPresetList
from jdxi_editor.ui.constant import JDXiUIConstants
from jdxi_editor.ui.parameters import UiParameters
from jdxi_editor.ui.style import (
    JDXiDimensions,
    JDXiIconRegistry,
    JDXiStyle,
    JDXiThemeManager,
)


class JDXiUI:
    """Composition of main JDXI UI components as a single, immutable container."""

    Style: JDXiStyle = JDXiStyle
    ThemeManager: JDXiThemeManager = JDXiThemeManager
    IconRegistry: JDXiIconRegistry = JDXiIconRegistry
    Dimensions: JDXiDimensions = JDXiDimensions
    Parameters: UiParameters = UiParameters
    Constants: JDXiUIConstants = JDXiUIConstants
    Preset: JDXiPresetList = JDXiPresetList
    Program: JDXiProgramList = JDXiProgramList

