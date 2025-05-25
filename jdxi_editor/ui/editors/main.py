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

from jdxi_editor.jdxi.synth.type import JDXiSynth
from jdxi_editor.log.logger import Logger as log
from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.ui.editors import (
    AnalogSynthEditor,
    DigitalSynthEditor,
    DrumCommonEditor,
    ArpeggioEditor,
    EffectsCommonEditor,
    VocalFXEditor,
    ProgramEditor, SynthEditor,
)
from jdxi_editor.ui.editors.digital.editor import DigitalSynth2Editor
from jdxi_editor.ui.editors.io.player import MidiFileEditor
from jdxi_editor.ui.editors.io.preset import PresetEditor
from jdxi_editor.ui.editors.pattern.pattern import PatternSequenceEditor
from jdxi_editor.project import __version__, __program__
# from jdxi_editor.ui.windows.jdxi.instrument import JDXiInstrument


class MainEditor(QMainWindow):
    """JD-Xi UI setup, with as little as possible functionality, which is to be super-classed"""

    def __init__(self, parent: QMainWindow = None):
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
        self.editor_tab_widget.tabCloseRequested.connect(self._close_editor_tab)
        self.setCentralWidget(self.editor_tab_widget)  # if this is a QMainWindow
        self.editor_tab_widget.setStyleSheet(JDXiStyle.TABS_MAIN_EDITOR)
        self.setStyleSheet(JDXiStyle.EDITOR)
        self.setWindowTitle(f"{__program__} - {__version__}")
        # self.init_ui()

    def init_ui(self) -> None:
        """
        Initialize the UI for the MainEditor
        :return:
        """
        self.show_editor("program")
        self.show_editor("digital1")
        self.show_editor("digital2")
        self.show_editor("drums")
        self.show_editor("analog")
        self.show_editor("arpeggio")
        self.show_editor("midi_file")
        self.show_editor("pattern")
        self.show_editor("effects")
        self.show_editor("vocal_fx")
        self.editor_tab_widget.setCurrentIndex(1)

    def show_editor(self, editor_type: str) -> None:
        """
        Show editor of given type
        :param editor_type: str
        :return: None
        """

        config = self.jdxi_main_window.editor_registry.get(editor_type)
        if not config:
            log.warning(f"Unknown editor type: {editor_type}")
            return

        title, editor_class, synth_type, midi_channel, kwargs = (
            (*config, {}) if len(config) == 4 else config
        )

        if synth_type:
            self.jdxi_main_window.current_synth_type = synth_type
        if midi_channel:
            self.jdxi_main_window.channel = midi_channel

        self._show_editor_tab(title, editor_class, **kwargs)

    def _show_editor_tab(self, title: str, editor_class, **kwargs) -> None:
        """
        Show the editor tab with the specified title and editor class.
        :param title: str Editor title
        :param editor_class: class Editor class to be shown
        :param kwargs: Additional arguments for the editor class
        :return: None
        """
        try:
            existing_editor = self.jdxi_main_window.get_existing_editor(editor_class)
            print(self.jdxi_main_window.editors)
            log.parameter("Existing editor", existing_editor)
            # instance_attr = f"{editor_class.__name__.lower()}_instance"
            # existing_editor = getattr(self.jdxi_main_window, instance_attr, None)

            if existing_editor:
                index = self.editor_tab_widget.indexOf(existing_editor)
                if index != -1:
                    self.editor_tab_widget.setCurrentIndex(index)
                    return

            preset_helper = (
                self.jdxi_main_window.get_preset_helper_for_current_synth()
                if editor_class in {
                    ArpeggioEditor, DigitalSynthEditor, DigitalSynth2Editor,
                    AnalogSynthEditor, DrumCommonEditor, PatternSequenceEditor,
                    ProgramEditor, PresetEditor, MidiFileEditor,
                    VocalFXEditor, EffectsCommonEditor,
                }
                else None
            )

            editor = (
                editor_class(
                    midi_helper=self.jdxi_main_window.midi_helper,
                    preset_helper=preset_helper,
                    parent=self,
                    **kwargs,
                )
                if preset_helper
                else editor_class(
                    midi_out=self.jdxi_main_window.midi_helper.midi_out,
                    parent=self,
                    **kwargs,
                )
            )
            editor.setWindowTitle(title)

            self.editor_tab_widget.addTab(editor, title)
            self.editor_tab_widget.setCurrentWidget(editor)

            setattr(self, instance_attr, editor)
            self.jdxi_main_window.register_editor(editor)

            if hasattr(editor, "preset_helper"):
                editor.preset_helper.update_display.connect(self.jdxi_main_window.update_display_callback)

            if hasattr(editor, "partial_editors"):
                for partial in editor.partial_editors.values():
                    self.jdxi_main_window.register_editor(partial)

        except Exception as ex:
            log.error(f"Error showing {title} editor", exception=ex)

    def _close_editor_tab(self, index: int) -> None:
        """
        Close the editor tab at the specified index.
        :param index: int Index of the tab to close
        :return: None
        """
        widget = self.editor_tab_widget.widget(index)
        if widget:
            self.editor_tab_widget.removeTab(index)
            """
            widget.deleteLater()
            # Optional: clear the corresponding instance_attr
            for key in list(self.__dict__):
                if self.__dict__[key] is widget:
                    delattr(self, key)
                    break"""
