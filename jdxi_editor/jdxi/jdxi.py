"""
Composition of main JDXi components
"""

from jdxi_editor.ui.style import (
    JDXiDimensions,
    JDXiIconRegistry,
    JDXiStyle,
    JDXiThemeManager,
)


class JDXi:
    """Composition of main JDXI UI components as a single, immutable container."""

    Style: JDXiStyle = JDXiStyle
    ThemeManager: JDXiThemeManager = JDXiThemeManager
    IconRegistry: JDXiIconRegistry = JDXiIconRegistry
    Dimensions: JDXiDimensions = JDXiDimensions
