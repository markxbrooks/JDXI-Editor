"""
JD-Xi Editor UI setup.

This class defines the main user interface for the JD-Xi Editor application, inheriting from QMainWindow.
Key Features:
- Initializes the main window with a tabbed editor interface.

Methods:
    - __init__: Initializes the UI adds elements and sets up the main layout.
    - _close_editor_tab: Handles the closing of editor tabs.

"""


from PySide6.QtWidgets import QMainWindow, QTabWidget

from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.project import __version__, __program__


class MainEditor(QMainWindow):
    """JD-Xi UI setup, with as little as possible functionality, which is to be super-classed"""

    def __init__(self,
                 parent: QMainWindow = None):
        """
        Constructor for the MainEditor class. Initializes the main layout and sets up the editor tab widget.
        :param parent: JDXiInstrument
        """
        super().__init__(parent=parent)
        self.jdxi_main_window = parent
        self.editor_registry = None
        self.editors = []
        self.editor_tab_widget = QTabWidget()
        self.editor_tab_widget.setTabsClosable(False)
        self.setCentralWidget(self.editor_tab_widget)  # if this is a QMainWindow
        self.editor_tab_widget.setStyleSheet(JDXiStyle.TABS_MAIN_EDITOR)
        self.setStyleSheet(JDXiStyle.EDITOR)
        self.setWindowTitle(f"{__program__} - {__version__}")
