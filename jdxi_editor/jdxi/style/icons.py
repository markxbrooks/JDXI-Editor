"""
Icon registry for JD-Xi Editor.

Provides centralized icon definitions and retrieval with fallback support.
"""

import qtawesome as qta
from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel

from decologr import Decologr as log
from jdxi_editor.jdxi.style import JDXiStyle


class IconRegistry:
    """Centralized icon definitions and retrieval"""

    # Action icons
    CLEAR = "ei.broom"
    RUN = "msc.run"
    SAVE = "fa5.save"
    DELETE = "mdi.delete-empty-outline"
    REFRESH = "ei.refresh"
    SETTINGS = "msc.settings"
    EXPORT = "fa5s.file-export"
    HELP = "mdi.help-rhombus-outline"
    HELP_RHOMBUS = "mdi6.help-rhombus-outline"
    QUIT = "mdi6.exit-to-app"

    # File icons
    FOLDER = "ph.folders-light"
    FOLDER_OPENED = "msc.folder-opened"
    FOLDER_NOTCH_OPEN = "ph.folder-notch-open-fill"
    FILE_TEXT = "ph.file-text-light"
    FILE_TABLE1 = "mdi.book-information-variant"
    FILE_DOCUMENT = "mdi6.file-document-check-outline"
    FILE_SEARCH = "ph.file-search"
    EXCEL = "mdi.microsoft-excel"
    FILE_MTZ = "mdi.data-matrix-edit"
    FILE_MOLECULE = "mdi.molecule"
    FLOPPY_DISK = "ph.floppy-disk-fill"

    # MIDI icons
    MIDI_PORT = "mdi.midi-port"
    MUSIC = "mdi.file-music-outline"
    KEYBOARD = "mdi6.keyboard-settings-outline"

    # Playback icons
    PLAY = "ri.play-line"
    STOP = "ri.stop-line"
    PAUSE = "ri.pause-line"
    MUTE = "msc.mute"

    # Instrument icons
    PIANO = "msc.piano"
    DRUM = "fa5s.drum"
    DISTORTION = "mdi6.signal-distance-variant"

    # Effect icons
    EFFECT = "mdi.effect"
    DELAY = "mdi.timer-outline"
    REVERB = "mdi.wave"
    MICROPHONE = "mdi.microphone"
    EQUALIZER = "mdi.equalizer"

    # Control icons
    TUNE = "mdi.tune"
    CLOCK = "mdi.clock-outline"
    MUSIC_NOTE = "mdi.music-note"
    MUSIC_NOTE_MULTIPLE = "mdi.music-note-multiple"
    CODE_BRACES = "mdi.code-braces"
    CIRCLE_OUTLINE = "mdi.circle-outline"
    VOLUME_HIGH = "mdi.volume-high"
    COG_OUTLINE = "mdi.cog-outline"
    DOTS_HORIZONTAL = "mdi.dots-horizontal"
    PAN_HORIZONTAL = "mdi.pan-horizontal"

    # Tab icons
    SEARCH_WEB = "mdi6.search-web"
    DATASET_PROCESSING = "mdi.database"
    PROCESSED_DATASETS = "mdi.database-check"
    MODELLED_STRUCTURES = "mdi.molecule"
    RHOFIT_PIPELINE = "mdi.pipe"

    # Navigation icons
    BACK = "ri.arrow-go-back-fill"
    FORWARD = "ri.arrow-go-forward-fill"

    # Control icons
    FORK = "ei.fork"
    CPU = "mdi6.cpu-64-bit"
    PANDA = "mdi6.panda"
    DATASETS = "mdi.image-edit-outline"
    DATABASE = "mdi.database"
    SHIELD = "mdi.shield-account"
    TRASH = "mdi.delete"
    TRASH_FILL = "ph.trash-fill"
    CLEANUP = "mdi.broom"
    CANCEL = "mdi.cancel"
    ADD = "mdi.plus"
    PLUS_CIRCLE = "ph.plus-circle-fill"
    DELETE = "mdi.delete"
    PAUSE_ICON = "mdi.pause"
    SERVER_PROCESS = "msc.server-process"
    REPORT: str = "msc.report"

    # Waveform/Synth icons
    TRIANGLE_WAVE = "mdi.triangle-wave"
    SINE_WAVE = "mdi.sine-wave"
    FILTER = "ri.filter-3-fill"
    AMPLIFIER = "mdi.amplifier"
    WAVEFORM = "mdi.waveform"

    @staticmethod
    def get_icon(
        icon_name: str, color: str = None, size: int = None, fallback: str = None
    ) -> QIcon:
        """
        Get icon with fallback support.

        :param icon_name: Icon identifier (e.g., "msc.run")
        :param color: Optional color string (e.g., "#FF0000" or JDXiStyle.FOREGROUND)
        :param size: Optional size in pixels (defaults to JDXiStyle.ICON_SIZE)
        :param fallback: Fallback icon if primary fails
        :return: QIcon or None if both fail
        """
        try:
            kwargs = {}
            if color:
                kwargs["color"] = color

            icon = qta.icon(icon_name, **kwargs)
            if icon.isNull():
                raise ValueError(f"Icon {icon_name} is null")
            return icon

        except Exception as ex:
            log.debug(f"Failed to load icon {icon_name}: {ex}")
            if fallback:
                try:
                    kwargs = {}
                    if color:
                        kwargs["color"] = color
                    icon = qta.icon(fallback, **kwargs)
                    if not icon.isNull():
                        log.info(f"Using fallback icon {fallback} for {icon_name}")
                        return icon

                except Exception as fallback_ex:
                    log.debug(f"Failed to load fallback icon {fallback}: {fallback_ex}")
            log.warning(f"Could not load icon {icon_name}")
            return None

    @staticmethod
    def get_icon_pixmap(
        icon_name: str, color: str = None, size: int = None, fallback: str = None
    ):
        """
        Get icon as QPixmap with fallback support.

        :param icon_name: Icon identifier
        :param color: Optional color string
        :param size: Optional size in pixels (defaults to JDXiStyle.ICON_SIZE)
        :param fallback: Fallback icon if primary fails
        :return: QPixmap or None if all fail
        """
        icon = IconRegistry.get_icon(icon_name, color=color, fallback=fallback)
        if icon is None:
            return None

        icon_size = size or JDXiStyle.ICON_SIZE
        return icon.pixmap(icon_size, icon_size)

    @staticmethod
    def get_icon_safe(
        icon_name: str, color: str = None, size: int = None, fallback: str = None
    ) -> QIcon:
        """
        Get icon with fallback support, returns empty QIcon if all fail.

        This version always returns a QIcon object (may be empty).

        :param icon_name: Icon identifier
        :param color: Optional color string
        :param size: Optional size in pixels (unused, kept for compatibility)
        :param fallback: Fallback icon if primary fails
        :return: QIcon (may be empty if all fail)
        """
        icon = IconRegistry.get_icon(icon_name, color=color, fallback=fallback)
        if icon is None:
            # Return empty icon
            return qta.icon("")
        return icon

    @staticmethod
    def create_adsr_icons_row() -> QHBoxLayout:
        """Create ADSR icons row"""
        icon_hlayout = QHBoxLayout()
        for icon in [
            "mdi.triangle-wave",
            "mdi.sine-wave",
            "fa5s.wave-square",
            "mdi.cosine-wave",
            "mdi.triangle-wave",
            "mdi.waveform",
        ]:
            icon_label = QLabel()
            icon_pixmap = qta.icon(icon, color=JDXiStyle.GREY).pixmap(30, 30)
            icon_label.setPixmap(icon_pixmap)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            icon_hlayout.addWidget(icon_label)
        return icon_hlayout

    @staticmethod
    def create_oscillator_icons_row() -> QHBoxLayout:
        """Create oscillator/waveform icons row for oscillator sections"""
        icon_hlayout = QHBoxLayout()
        for icon in [
            "mdi.triangle-wave",
            "mdi.sine-wave",
            "fa5s.wave-square",
            "mdi.sawtooth-wave",
            "mdi.waveform",
            "mdi.sine-wave",
        ]:
            icon_label = QLabel()
            icon_pixmap = qta.icon(icon, color=JDXiStyle.GREY).pixmap(30, 30)
            icon_label.setPixmap(icon_pixmap)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            icon_hlayout.addWidget(icon_label)
        return icon_hlayout

    @staticmethod
    def create_generic_musical_icon_row() -> QHBoxLayout:
        # Icons
        icons_hlayout = QHBoxLayout()
        for icon_name in [
            "ph.bell-ringing-bold",
            "mdi.call-merge",
            "mdi.account-voice",
            "ri.voiceprint-fill",
            "mdi.piano",
        ]:
            icon_label = QLabel()
            icon = qta.icon(icon_name, color=JDXiStyle.GREY)
            pixmap = icon.pixmap(24, 24)  # Using fixed icon size
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignHCenter)
            icons_hlayout.addWidget(icon_label)
        return icons_hlayout

    @classmethod
    def get_icon_by_qta_name(cls, name, color, scale_factor=1):
        """get icon by qta name"""
        try:
            return qta.icon(name, color, scale_factor)
        except Exception as ex:
            return qta.icon("mdi.piano")
