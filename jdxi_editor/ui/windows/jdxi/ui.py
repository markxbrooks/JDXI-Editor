"""
JD-Xi Editor UI setup.

This class defines the main user interface for the JD-Xi Editor application, inheriting from QMainWindow. It handles the creation of the UI elements, including the main layout, menus, status bar, and MIDI indicators. It also provides functionality for displaying and managing synth presets, favorites, and MIDI connectivity.

Key Features:
- Sets up a frameless window with a customizable layout.
- Initializes MIDI helper and indicators for MIDI input/output.
- Loads and displays a digital font for instrument displays.
- Allows users to manage and load favorite presets.
- Displays a virtual piano keyboard in the status bar.
- Integrates with MIDIHelper for MIDI communication.
- Loads and saves application settings and preferences.

Methods:
    - __init__: Initializes the UI, settings, MIDI components, and layout.
    - _create_main_layout: Sets up the central layout for displaying instrument images and overlays.

"""


import re
from typing import Callable, Optional, Union

from decologr import Decologr as log
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLayout, QMainWindow, QMessageBox

from jdxi_editor.core.synth.factory import create_synth_data
from jdxi_editor.core.synth.type import JDXiSynth
from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.sysex.request.midi_requests import MidiRequests
from jdxi_editor.project import __package_name__, __program__
from jdxi_editor.ui.common import JDXi, QVBoxLayout, QWidget
from jdxi_editor.ui.editors.helpers.preset import get_preset_list_number_by_name
from jdxi_editor.ui.editors.helpers.program import get_program_name_by_id
from jdxi_editor.ui.image.instrument import draw_instrument_pixmap
from jdxi_editor.ui.preset.manager import JDXiPresetManager
from jdxi_editor.ui.widgets.button.favorite import FavoriteButton
from jdxi_editor.ui.widgets.button.sequencer import SequencerSquare
from jdxi_editor.ui.widgets.indicator.led import LEDIndicator
from jdxi_editor.ui.widgets.piano.keyboard import PianoKeyboard
from jdxi_editor.ui.widgets.rack import RackStatusBar
from jdxi_editor.ui.windows.jdxi.containers import build_wheel_label_row, build_wheel_row
from jdxi_editor.ui.windows.jdxi.panel import build_faceplate
from picoui.helpers.layout import create_layout_with_items


class JDXiWindow(QMainWindow):
    """JD-Xi UI setup, with as little as possible functionality, which is to be super-classed"""

    def __init__(self):
        super().__init__()
        self.digital_font_family = None
        self.editor_registry = None
        self.editors = []
        self.log_viewer = None
        self.midi_debugger = None
        self.midi_message_monitor = None
        self.audio_monitor = None
        self.midi_controller_config = None
        self.old_pos = None
        # JDXi.UI.Theme.apply_dark_theme()
        self.preset_helpers = None
        self.slot_number = None
        self.sequencer_buttons = []
        self.current_program_bank_letter = "A"
        # --- Set up programs
        self.current_program_id = "A01"
        self.current_program_number = int(self.current_program_id[1:])
        self.current_program_name = get_program_name_by_id(self.current_program_id)
        # --- Set up presets
        self.preset_manager = JDXiPresetManager()
        # Initialize synth preset_type
        self.current_synth_type: JDXiSynth = JDXiSynth.DIGITAL_SYNTH_1
        # --- Initialize octave
        self.current_octave = 0  # Initialize octave tracking first
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle(__program__)
        self.setMinimumSize(
            JDXi.UI.Dimensions.INSTRUMENT.WIDTH, JDXi.UI.Dimensions.INSTRUMENT.HEIGHT
        )

        # --- Initialize MIDI helper
        self.midi_helper = MidiIOHelper()
        #  --- Initialize MIDI connectivity
        if self.midi_helper:
            self.midi_helper.close_ports()
        self.channel = MidiChannel.DIGITAL_SYNTH_1
        self.midi_helper.midi_program_changed.connect(self._handle_program_change)
        self.midi_key_hold_latched = False
        self.midi_requests = MidiRequests.PROGRAM_TONE_NAME_PARTIAL

        # --- Load custom font
        self._load_digital_font()

        # --- Create UI
        # The bottom strip is part of the instrument, ears and all. It has to
        # be installed before anything asks for statusBar(): setStatusBar
        # deletes the bar it replaces, and everything inside it with it.
        self.setStatusBar(RackStatusBar(self))
        self._create_menu_bar()
        self._create_status_bar()
        self._create_main_layout()
        self._create_parts_menu()
        self._create_effects_menu()
        self._create_playback_menu()
        self._create_help_menu()

        # --- Load settings
        self.settings = QSettings("mabsoft", __package_name__)

        # --- Add piano keyboard at bottom
        self.piano_keyboard = PianoKeyboard(parent=self)
        self.statusBar().addPermanentWidget(self.piano_keyboard)

        # --- Load saved favorites
        self._load_saved_favorites()

    def _create_main_layout(self) -> None:
        """Create the main dashboard"""
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.faceplate = build_faceplate(self)
        layout.addWidget(self.faceplate)

        # --- Initialize current preset index
        self.current_preset_index = 0

    def _menu_action(
        self,
        text: str,
        slot: Callable,
        shortcut: Optional[Union[QKeySequence, QKeySequence.StandardKey, str]] = None,
        icon: Optional[QIcon] = None,
        status_tip: Optional[str] = None,
    ) -> QAction:
        """Menu item with a shortcut that works while any editor window is focused."""
        action = QAction(icon, text, self) if icon is not None else QAction(text, self)
        if shortcut is not None:
            action.setShortcut(QKeySequence(shortcut))
            action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        if status_tip:
            action.setStatusTip(status_tip)
        action.triggered.connect(slot)
        return action

    def _add_skin_menu(self, menu) -> None:
        """
        A "JDXiSkin" submenu: the faceplate the panels and displays wear, the
        Skin Editor, and the folder of the user's own skins.

        :param menu: QMenu the menu to add the submenu to
        :return: None
        """
        self._skin_submenu = menu.addMenu("&JDXiSkin")
        self._populate_skin_menu()

    def _populate_skin_menu(self) -> None:
        """
        Fill the JDXiSkin submenu, again after a skin is added.

        :return: None
        """
        from PySide6.QtGui import QActionGroup

        from jdxi_editor.ui.style.rack_skin import SKINS, active_skin

        submenu = self._skin_submenu
        submenu.clear()
        group = QActionGroup(submenu)
        group.setExclusive(True)
        current = active_skin().skin_id
        for skin_id, skin in SKINS.items():
            action = QAction(skin.label, submenu)
            action.setCheckable(True)
            action.setChecked(skin_id == current)
            action.triggered.connect(
                lambda _checked=False, chosen=skin_id: self._apply_skin(chosen)
            )
            group.addAction(action)
            submenu.addAction(action)
        submenu.addSeparator()
        submenu.addAction(
            self._menu_action(
                "Skin &Editor...",
                self._show_skin_editor,
                status_tip="Make a skin of your own from any skin",
            )
        )
        submenu.addAction(
            self._menu_action(
                "Open User Skins &Folder",
                self._open_user_skins_folder,
                status_tip="Where your skin files are kept",
            )
        )

    def showEvent(self, event) -> None:
        """
        Give the instrument its proportions once the window is laid out.

        :param event: QShowEvent
        :return: None
        """
        super().showEvent(event)
        self.apply_instrument_proportions()

    def resizeEvent(self, event) -> None:
        """
        Keep the instrument in proportion as the window changes width.

        The JD-Xi is 2.37 : 1, and its panel and keys are a fixed share of
        its width, so both follow the window rather than staying at the size
        that happened to be right at 1000 px.

        :param event: QResizeEvent
        :return: None
        """
        super().resizeEvent(event)
        self.apply_instrument_proportions()

    def apply_instrument_proportions(self) -> None:
        """
        Size the panel and the keys for the instrument's current width.

        :return: None
        """
        width = self.width()
        central = self.centralWidget()
        dimensions = JDXi.UI.Dimensions.INSTRUMENT
        faceplate = getattr(self, "faceplate", None)
        panel = dimensions.panel_height_for(width)
        if faceplate is not None:
            # it may need more than the ratio asks for, to fit its controls
            panel = faceplate.apply_width(width)
        depth = round(width * dimensions.DEPTH_RATIO)
        keys = max(dimensions.keys_height_for(width) // 2, depth - panel)
        keyboard = getattr(self, "piano_keyboard", None)
        if keyboard is not None:
            # The strip keeps ear_width at each end for the skin's cheeks and
            # lays the keys out between them, so the keys have that much less
            # than the window to fill. Sized to the window instead, the keys
            # alone ask for more than the strip can be given, Qt hands the
            # strip its minimum anyway, and the surplus hangs over the right
            # edge of the window -- taking the right cheek, painted at the
            # strip's far end, out of sight. The left one starts at x=0
            # whatever happens, so the pair goes lopsided rather than absent.
            from jdxi_editor.ui.style.rack_skin import active_skin

            keyboard.set_instrument_width(width - 2 * active_skin().ear_width, keys)

        # Reserve the depth the instrument needs. Without this the window
        # opens shorter than the panel and the keys together, and Qt squeezes
        # the panel below its own minimum -- 215 px of a 230 px faceplate,
        # with the step buttons pushed off the bottom edge.
        # sizeHint, not height: during the first resize the menu bar is not
        # shown yet and reports 0, which left the window 20 px short and the
        # panel squeezed for the rest of the session
        menu = self.menuBar()
        chrome = menu.sizeHint().height() if menu is not None else 0
        wanted = chrome + panel + keys + self._status_bar_padding()
        # Fixed, not merely a minimum: the instrument is a shape, and a saved
        # geometry or a drag on the bottom edge would otherwise leave it
        # floating in a band of empty body. The width stays free and the
        # depth follows it.
        #
        # The shortfall is measured rather than predicted: adding up the menu
        # bar, the panel, the keys and the status bar's margins was always a
        # few pixels out, and the panel paid for it by being squeezed past
        # its own edge. Asking the central widget how short it is converges
        # in a pass or two and cannot drift.
        if central is not None:
            wanted = self.height() + (panel - central.height())
        if self.minimumHeight() != wanted or self.maximumHeight() != wanted:
            self.setFixedHeight(wanted)

    def _status_bar_padding(self) -> int:
        """
        What the status bar adds around the keyboard.

        :return: int px
        """
        status = self.statusBar()
        if status is None:
            return 0
        # From the margins, not from the live heights: measured while the
        # layout is still settling, the difference is whatever the keyboard
        # happened to be a moment ago, and the window ends up that much too
        # tall for good.
        margins = status.contentsMargins()
        return margins.top() + margins.bottom()

    def _apply_skin(self, skin, remember: bool = True) -> None:
        """
        Wear ``skin`` everywhere: chrome, and the picture of the instrument.

        The instrument is drawn once into a pixmap, so it has to be drawn
        again; the chrome follows the skin by itself.

        :param skin: str | JDXiSkin a key of rack_skin.SKINS, or a skin (one
            the Skin Editor is trying on)
        :param remember: bool store the choice for next time
        :return: None
        """
        from jdxi_editor.ui.style.rack_skin import set_active_skin

        set_active_skin(skin, remember=remember)
        self.refresh_instrument_image()
        self.apply_keyboard_area_skin()
        # Cheeks of a different width leave the keys a different width
        self.apply_instrument_proportions()

    def _show_skin_editor(self) -> None:
        """Open the Skin Editor, or bring it forward."""
        from jdxi_editor.ui.windows.skin.editor import SkinEditorWindow

        editor = getattr(self, "skin_editor", None)
        if editor is None:
            editor = SkinEditorWindow(
                parent=self,
                wear=lambda skin, remember: self._apply_skin(skin, remember=remember),
                saved=self._skin_saved,
            )
            editor.setAttribute(Qt.WA_DeleteOnClose)
            editor.destroyed.connect(lambda: setattr(self, "skin_editor", None))
            self.skin_editor = editor
        editor.show()
        editor.raise_()

    def _skin_saved(self, skin) -> None:
        """A skin saved in the Skin Editor: offer it, and wear it."""
        self._apply_skin(skin.skin_id)
        self._populate_skin_menu()

    def _open_user_skins_folder(self) -> None:
        """Show the folder of the user's skin files, making it if need be."""
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QDesktopServices

        from jdxi_editor.ui.style.user_skins import USER_SKIN_DIR

        USER_SKIN_DIR.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(USER_SKIN_DIR)))

    def refresh_instrument_image(self) -> None:
        """
        Draw the instrument again in the current skin.

        :return: None
        """
        if getattr(self, "image_label", None) is None:
            return
        self.image_label.setPixmap(draw_instrument_pixmap())

    def _create_menu_bar(self) -> None:
        menubar = self.menuBar()

        # --- File menu
        file_menu = menubar.addMenu("&File")

        file_menu.addAction(
            self._menu_action(
                "&Load MIDI file",
                self._midi_file_load,
                QKeySequence.StandardKey.Open,
            )
        )
        file_menu.addAction(
            self._menu_action(
                "&Save MIDI file",
                self._midi_file_save,
                QKeySequence.StandardKey.Save,
            )
        )
        file_menu.addAction(
            self._menu_action(
                "Save MIDI file &As...",
                self._midi_file_save_as,
                QKeySequence.StandardKey.SaveAs,
            )
        )
        from jdxi_editor.globals import lilypond_enabled

        self.open_midi_as_pdf_action = self._menu_action(
            "Open current MIDI as &PDF",
            self._open_current_midi_as_pdf,
            "Ctrl+P",
            status_tip="Export the current MIDI file to PDF via LilyPond (Advanced preference)",
        )
        self.open_midi_as_pdf_action.setVisible(lilypond_enabled())
        file_menu.addAction(self.open_midi_as_pdf_action)

        file_menu.addSeparator()

        file_menu.addAction(
            self._menu_action(
                "Load P&rogram...",
                lambda: self.show_editor("program"),
                "Ctrl+Shift+O",
                JDXi.UI.Icon.get_icon(JDXi.UI.Icon.FOLDER_OPENED),
            )
        )

        load_preset_action = QAction("Load Preset...", self)
        load_preset_action.triggered.connect(lambda: self.show_editor("preset"))
        # file_menu.addAction(load_preset_action)

        file_menu.addAction(
            self._menu_action("Load &Patch...", self._patch_load, "Ctrl+Alt+O")
        )
        file_menu.addAction(
            self._menu_action("Save Patc&h...", self._patch_save, "Ctrl+Alt+S")
        )

        file_menu.addSeparator()

        file_menu.addAction(
            self._menu_action(
                "&Dump Settings to Synth",
                self._dump_settings_to_synth,
                "Ctrl+Shift+D",
            )
        )

        file_menu.addSeparator()

        file_menu.addAction(self._menu_action("&Quit", self.close, "Ctrl+Q"))

        # --- Edit menu
        edit_menu = menubar.addMenu("&Edit")

        edit_menu.addAction(
            self._menu_action(
                "&MIDI Configuration...",
                self._show_midi_config,
                "Ctrl+Shift+M",
            )
        )

        edit_menu.addAction(
            self._menu_action(
                "MIDI &Controller...",
                self._show_midi_controller_config,
                "Ctrl+Shift+K",
                status_tip="Set up a hardware controller to drive the filter",
            )
        )

        edit_menu.addSeparator()

        self._add_skin_menu(edit_menu)

        edit_menu.addSeparator()

        edit_menu.addAction(
            self._menu_action(
                "&Update User Program Database",
                self._update_user_program_database,
                "Ctrl+Shift+U",
            )
        )

    def _create_parts_menu(self) -> None:
        """Create editors menu"""
        self.parts_menu = self.menuBar().addMenu("&Parts")

        self.parts_menu.addAction(
            self._menu_action(
                "Digital Synth &1", lambda: self.show_editor("digital1"), "Ctrl+1"
            )
        )
        self.parts_menu.addAction(
            self._menu_action(
                "Digital Synth &2", lambda: self.show_editor("digital2"), "Ctrl+2"
            )
        )
        self.parts_menu.addAction(
            self._menu_action("&Drums", lambda: self.show_editor("drums"), "Ctrl+4")
        )
        self.parts_menu.addAction(
            self._menu_action(
                "&Analog Synth", lambda: self.show_editor("analog"), "Ctrl+5"
            )
        )

    def _create_effects_menu(self) -> None:
        """Create editors menu"""
        self.effects_menu = self.menuBar().addMenu("Effe&cts")

        self.effects_menu.addAction(
            self._menu_action("&Effects", lambda: self.show_editor("effects"), "Ctrl+6")
        )
        self.effects_menu.addAction(
            self._menu_action(
                "&Vocal FX", lambda: self.show_editor("vocal_fx"), "Ctrl+7"
            )
        )

    def _create_playback_menu(self) -> None:
        # --- Create editors menu
        playback_menu = self.menuBar().addMenu("P&layback")

        playback_menu.addAction(
            self._menu_action(
                "&MIDI File", lambda: self.show_editor("midi_player"), "Ctrl+8"
            )
        )
        playback_menu.addAction(
            self._menu_action(
                "&Arpeggiator", lambda: self.show_editor("arpeggio"), "Ctrl+9"
            )
        )
        playback_menu.addAction(
            self._menu_action(
                "&Pattern Sequencer", lambda: self.show_editor("pattern"), "Ctrl+0"
            )
        )

    def _create_debug_menu(self) -> None:
        # --- Add debug menu
        self.debug_menu = self.menuBar().addMenu("Debug")

        # --- Add MIDI debugger action (SysEx decoder)
        midi_debugger_action = QAction("MIDI SysEx Debugger", self)
        midi_debugger_action.triggered.connect(self._show_midi_debugger)
        self.debug_menu.addAction(midi_debugger_action)

        # --- Add MIDI message monitor action
        midi_monitor_action = QAction("MIDI Monitor", self)
        midi_monitor_action.triggered.connect(self._show_midi_message_monitor)
        self.debug_menu.addAction(midi_monitor_action)

        audio_monitor_action = QAction("Audio Monitor", self)
        audio_monitor_action.triggered.connect(self._show_audio_monitor)
        self.debug_menu.addAction(audio_monitor_action)

        # --- Add log viewer action
        log_viewer_action = QAction("Log Viewer", self)
        log_viewer_action.triggered.connect(self._show_log_viewer)
        self.debug_menu.addAction(log_viewer_action)

        # --- Add About window action
        about_help_action = QAction("About", self)
        about_help_action.triggered.connect(self._show_about_help)
        self.debug_menu.addAction(about_help_action)

    def _create_help_menu(self) -> None:
        menubar = self.menuBar()

        # --- Help menu
        self.help_menu = menubar.addMenu("&Help")
        self.help_menu.addAction(
            self._menu_action("&Log Viewer", self._show_log_viewer, "Ctrl+Shift+L")
        )
        self.help_menu.addAction(
            self._menu_action(
                "MIDI &SysEx Debugger", self._show_midi_debugger, "Ctrl+Shift+Y"
            )
        )
        self.help_menu.addAction(
            self._menu_action(
                "MIDI &Monitor", self._show_midi_message_monitor, "Ctrl+Alt+M"
            )
        )
        self.help_menu.addAction(
            self._menu_action(
                "Audio &Monitor", self._show_audio_monitor, "Ctrl+Alt+A"
            )
        )
        self.help_menu.addAction(
            self._menu_action("&About", self._show_about_help, "Ctrl+Shift+A")
        )
        self.help_menu.addAction(
            self._menu_action(
                "&Preferences",
                self.on_preferences,
                "Ctrl+,",
                JDXi.UI.Icon.get_icon(JDXi.UI.Icon.SETTINGS),
                "Show the Preferences window",
            )
        )
        self.help_menu.addAction(
            self._menu_action(
                "Check for &Updates…",
                self.on_check_for_updates,
                "Ctrl+Alt+U",
                status_tip="Look for a newer release on GitHub",
            )
        )
        self.help_menu.addAction(
            self._menu_action(
                "&Documentation",
                self.on_documentation,
                QKeySequence.StandardKey.HelpContents,
                JDXi.UI.Icon.get_icon(JDXi.UI.Icon.HELP_RHOMBUS),
                f"Show {__program__} documentation",
            )
        )

        # --- Add Main Editor window action
        main_editor_action = QAction("Main Editor", self)
        main_editor_action.triggered.connect(self._show_main_editor)
        # self.help_menu.addAction(main_editor_action)

    def _create_status_bar(self):
        """Create status bar with MIDI indicators"""
        status_bar = self.statusBar()

        JDXi.UI.Theme.apply_transparent(status_bar)

        midi_indicator_container = QWidget()
        midi_indicator_container.setLayout(self._build_status_layout())
        status_bar.addPermanentWidget(midi_indicator_container)

        # --- Set initial indicator states
        self.midi_in_indicator.set_state(self.midi_helper.is_input_open)
        self.midi_out_indicator.set_state(self.midi_helper.is_output_open)
        self.apply_keyboard_area_skin()

    def apply_keyboard_area_skin(self) -> None:
        """
        Dress the keyboard area in the active skin.

        The wheels, indicators and keys sit on the instrument's body, so the
        strip behind them is the skin's body colour, as it is around the
        panel above.

        :return: None
        """
        from jdxi_editor.ui.style.rack_skin import active_skin

        skin = active_skin()
        self.statusBar().setStyleSheet(
            f"QStatusBar {{ background-color: {skin.chassis.body}; }}"
            f"QStatusBar QLabel {{ color: {skin.foreground.text}; }}"
        )
        if getattr(self, "piano_keyboard", None) is not None:
            self.piano_keyboard.apply_skin()
        status_bar = self.statusBar()
        if isinstance(status_bar, RackStatusBar):
            status_bar.apply_skin()

    def _build_status_layout(self) -> QLayout:
        layout_items = [build_wheel_label_row(), build_wheel_row(midi_helper=self.midi_helper), self._build_midi_indicator_row()]
        layout = create_layout_with_items(vertical=True, items=layout_items)
        return layout

    def _build_midi_indicator_row(self) -> QLayout:
        self.midi_in_indicator = LEDIndicator()
        self.midi_out_indicator = LEDIndicator()

        row_widgets = [QLabel("MIDI"), QLabel("IN:"), self.midi_in_indicator, QLabel("OUT:"), self.midi_out_indicator]
        row = create_layout_with_items(row_widgets, vertical=False)
        return row

    def _update_display(self):
        """Update the digital with the current preset information"""
        if not self.current_synth_type:
            log.warning("No Synth type, defaulting to DIGITAL_1.", scope="JDXiWindow")
            self.current_synth_type = JDXiSynth.DIGITAL_SYNTH_1
        try:
            synth_data = create_synth_data(self.current_synth_type)
            log.message(
                f"Creating synth data for type: {self.current_synth_type}",
                scope="JDXiWindow",
            )
            if not synth_data:
                synth_data = create_synth_data(JDXiSynth.DIGITAL_SYNTH_1)

            self.preset_manager.current_preset_name = (
                self.preset_manager.get_preset_name_by_type(self.current_synth_type)
            )
            log.message(
                f"Current preset name: {self.preset_manager.current_preset_name}",
                scope="JDXiWindow",
            )
            # Update preset number
            # synth_data.preset_list might be a dict (PROGRAM_CHANGE) or a list
            # Use presets (ENUMERATED list) to find the index instead
            if hasattr(synth_data, "presets") and isinstance(synth_data.presets, list):
                # Search through the ENUMERATED list to find the preset name
                preset_name = self.preset_manager.current_preset_name
                try:
                    # Try to find the preset in the list
                    preset_index = next(
                        (
                            i
                            for i, p in enumerate(synth_data.presets)
                            if preset_name in p or p in preset_name
                        ),
                        None,
                    )
                    if preset_index is not None:
                        # Convert 0-based index to 1-based preset number
                        self.preset_manager.current_preset_number = preset_index + 1
                    else:
                        # Fallback: try get_preset_list_number_by_name if preset_list is a list
                        if isinstance(synth_data.preset_list, list):
                            self.preset_manager.current_preset_number = (
                                get_preset_list_number_by_name(
                                    preset_name, synth_data.preset_list
                                )
                            )
                        else:
                            # Default to 1 if we can't find it
                            self.preset_manager.current_preset_number = 1
                except Exception as ex:
                    log.warning(
                        f"Error finding preset number: {ex}, defaulting to 1",
                        scope="JDXiWindow",
                    )
                    self.preset_manager.current_preset_number = 1
            elif isinstance(synth_data.preset_list, list):
                # preset_list is already a list, use the existing function
                self.preset_manager.current_preset_number = (
                    get_preset_list_number_by_name(
                        self.preset_manager.current_preset_name, synth_data.preset_list
                    )
                )
            else:
                # preset_list is a dict or something else, default to 1
                log.warning(
                    f"preset_list is not a list (type: {type(synth_data.preset_list)}), ",
                    f"defaulting preset number to 1",
                    scope="JDXiWindow",
                )
                self.preset_manager.current_preset_number = 1
            log.message(
                f"Current preset number: {self.preset_manager.current_preset_number}",
                scope="JDXiWindow",
            )

            self.digital_display.repaint_display(
                current_octave=self.current_octave,
                tone_number=self.preset_manager.current_preset_number,
                tone_name=self.preset_manager.get_preset_name_by_type(
                    self.current_synth_type
                ),
                program_name=self.current_program_name,
                active_synth=synth_data.display_prefix,
            )
        except Exception as ex:
            log.error(f"Error updating digital: {ex}", scope="JDXiWindow")

    def _load_digital_font(self) -> None:
        """Load the digital LCD font for the instrument display."""
        from jdxi_editor.ui.widgets.digital.base import get_lcd_font_family, load_lcd_font

        self.digital_font_family = load_lcd_font() or get_lcd_font_family()
        log.message(
            f"Using LCD font family: {self.digital_font_family}",
            scope="JDXiWindow",
        )

    def update_preset_display(self, preset_number: int, preset_name: str):
        """Update the current preset digital"""
        self.preset_manager.current_preset_number = preset_number
        self.preset_manager.current_preset_name = preset_name
        self._update_display()

    def _update_display_preset(
        self, preset_number: int, preset_name: str, channel: int
    ):
        """Update the digital with the new preset information."""
        log.message(
            f"Updating digital preset: # {preset_number}, name: {preset_name}, channel: {channel}",
            scope="JDXiWindow",
        )
        self.current_preset_index = preset_number
        self.channel = channel

        try:
            # --- Extract actual number and name if the preset_name is like '123:Some Name'
            match = re.match(r"^(\d{3}):(.*)", preset_name)
            if match:
                preset_number = int(match.group(1))
                preset_name = match.group(2).strip()

            self.preset_manager.current_preset_number = preset_number
            self.preset_manager.current_preset_name = preset_name
            self._update_display()

            # --- Update piano keyboard MIDI channel if available
            if hasattr(self, "piano_keyboard"):
                self.piano_keyboard.set_midi_channel(channel)

            log.message(
                f"Updated digital: {preset_number:03d}:{preset_name} (channel {channel})",
                scope="JDXiWindow",
            )

        except Exception as ex:
            log.error(f"Error updating digital: {ex}", scope="JDXiWindow")

    def show_error(self, title: str, message: str):
        """Show error message dialog

        Args:
            title: Dialog title
            message: Error message
        """
        QMessageBox.critical(self, title, message)

    def show_warning(self, title: str, message: str):
        """Show warning message dialog

        Args:
            title: Dialog title
            message: Warning message
        """
        QMessageBox.warning(self, title, message)

    def show_info(self, title: str, message: str):
        """Show info message dialog

        Args:
            title: Dialog title
            message: Info message
        """
        QMessageBox.information(self, title, message)

    def _load_settings(self):
        raise NotImplementedError("to be implemented in subclass")

    def on_documentation(self):
        raise NotImplementedError("to be implemented in subclass")

    def on_preferences(self):
        raise NotImplementedError("to be implemented in subclass")

    def on_check_for_updates(self):
        raise NotImplementedError("to be implemented in subclass")

    def show_editor(self, param: str):
        raise NotImplementedError("to be implemented in subclass")

    def _show_midi_debugger(self):
        raise NotImplementedError("Should be implemented in subclass")

    def _show_main_editor(self):
        raise NotImplementedError("Should be implemented in subclass")

    def _show_about_help(self):
        raise NotImplementedError("Should be implemented in subclass")

    def _show_midi_message_monitor(self):
        raise NotImplementedError("Should be implemented in subclass")

    def _show_audio_monitor(self):
        raise NotImplementedError("Should be implemented in subclass")

    def _show_log_viewer(self):
        raise NotImplementedError("Should be implemented in subclass")

    def _show_midi_config(self):
        raise NotImplementedError("Should be implemented in subclass")

    def _midi_send_octave(self, _):
        raise NotImplementedError("Should be implemented in subclass")

    def _preset_previous(self):
        raise NotImplementedError("Should be implemented in subclass")

    def _preset_next(self):
        raise NotImplementedError("Should be implemented in subclass")

    def _load_saved_favorites(self):
        raise NotImplementedError("Should be implemented in subclass")

    def _select_synth(self, synth_type):
        raise NotImplementedError("Should be implemented in subclass")

    def _show_favorite_context_menu(
        self, pos, button: Union[FavoriteButton, SequencerSquare]
    ):
        raise NotImplementedError("Should be implemented in subclass")

    def _save_favorite(self, button, idx):
        raise NotImplementedError("to be implemented in subclass")

    def _midi_file_load(self):
        raise NotImplementedError("to be implemented in subclass")

    def _midi_file_save(self):
        raise NotImplementedError("to be implemented in subclass")

    def _midi_file_save_as(self):
        raise NotImplementedError("to be implemented in subclass")

    def _open_current_midi_as_pdf(self):
        raise NotImplementedError("to be implemented in subclass")

    def _patch_load(self):
        raise NotImplementedError("to be implemented in subclass")

    def _patch_save(self):
        raise NotImplementedError("to be implemented in subclass")

    def _dump_settings_to_synth(self):
        raise NotImplementedError("to be implemented in subclass")

    def _handle_program_change(self, bank_letter: str, program_number: int):
        raise NotImplementedError("to be implemented in subclass")
