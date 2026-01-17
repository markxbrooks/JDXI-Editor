"""
Composition of main JDXi components 
"""

from jdxi_editor.jdxi.style import JDXiStyle, JDXiThemeManager
from jdxi_editor.jdxi.style.icons import IconRegistry
from jdxi_editor.ui.windows.jdxi.dimensions import JDXiDimensions

class JDXi:
    """Composition of main JDXI UI components as a single, immutable container."""
    STYLE: JDXiStyle = JDXiStyle # if JDXiStyle is a class
    THEME: JDXiThemeManager = JDXiThemeManager
    ICONS: IconRegistry = IconRegistry
    DIMENSIONS: JDXiDimensions = JDXiDimensions
