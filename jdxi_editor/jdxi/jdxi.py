"""
Composition of main JDXi components 
"""

from jdxi_editor.jdxi.style import JDXiStyle, JDXiThemeManager
from jdxi_editor.jdxi.style.icons import IconRegistry
from jdxi_editor.ui.windows.jdxi.dimensions import JDXiDimensions

class JDXi:
    """ Composition of main JDXI UI components"""
    STYLE: JDXiStyle
    THEME: JDXiThemeManager
    ICONS: IconRegistry
    DIMENSIONS: JDXiDimensions
