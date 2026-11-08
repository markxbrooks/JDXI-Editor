"""
Icon registry.

Provides centralized icons definitions and retrieval with fallback support.
"""

import sys
from pathlib import Path

import qtawesome as qta
from decologr import Decologr as log
from picoui.dimensions import PicoUiDimensions
from PySide6.QtGui import QIcon, QPixmap


def resource_path(path: Path) -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / path
    return path


class IconRegistryPixmaps:
    SLURM = "slurm_93.png"


class IconRegistry:
    """Centralized icons definitions and retrieval"""

    _base_dir = Path(__file__).resolve().parent / "images"

    pixmaps = IconRegistryPixmaps

    dashboard = "mdi.view-dashboard-variant"
    map = "mdi.map"

    # Action icons
    RUN = "msc.run"
    REFRESH = "ei.refresh"
    SETTINGS = "msc.settings"
    EXPORT = "fa5s.file-export"
    HELP = "mdi.help-rhombus-outline"
    QUIT = "mdi6.exit-to-app"

    # File icons
    FOLDER = "ph.folders-light"
    FOLDER_OPENED = "msc.folder-opened"
    FILE_TEXT = "ph.file-text-light"
    FILE_BINARY = "msc.file-binary"
    FILE_TABLE1 = "mdi.book-information-variant"
    FILE_DOCUMENT = "mdi6.file-document-check-outline"
    FILE_NEW = "msc.new-file"
    SAVE = "msc.save"
    SAVE_AS = "msc.save-as"
    FETCH_PDB = "ph.database"
    FETCH_ALPHAFOLD = "ri.google-fill"
    RECENTER_VIEW = "mdi.image-filter-center-focus"
    INFO = "ph.info"
    FILE_SEARCH = "ph.file-search"
    EXCEL = "mdi.microsoft-excel"
    FILE_MTZ = "mdi.data-matrix-edit"
    FILE_MOLECULE = "mdi.molecule"
    NUCLEIC = "mdi.dna"
    REPORT = "msc.report"

    # Tab icons
    SEARCH_WEB = "mdi6.search-web"
    DATASET_PROCESSING = "mdi.database"  # For "dataset processing for pandda"
    PROCESSED_DATASETS = "mdi.database-check"  # For "pandda processed datasets"
    MODELLED_STRUCTURES = "mdi.molecule"  # For "modelled structures"
    RHOFIT_PIPELINE = "mdi.pipe"  # For "rhofit pipeline"

    # Navigation icons
    BACK = "ri.arrow-go-back-fill"
    FORWARD = "ri.arrow-go-forward-fill"

    # Other
    FORK = "ei.fork"
    CPU = "mdi6.cpu-64-bit"
    PANDA = "mdi6.panda"
    DATASETS = "mdi.image-edit-outline"
    DATABASE = "mdi.database"
    SHIELD = "mdi.shield-account"
    TRASH = "mdi.delete"
    CLEANUP = "mdi.broom"
    CANCEL = "mdi.cancel"
    STOP = "mdi.stop"
    ADD = "mdi.plus"
    DELETE = "mdi.delete"
    PAUSE = "mdi.pause"
    SERVER_PROCESS = "msc.server-process"

    # ElMo main window / viewer (tabs, menus, toolbar)
    DELETE_SWEEP = "mdi.delete-sweep"
    DOWNLOAD = "ph.download"
    SEARCH = "fa5s.search"
    ALIGN_LEFT = "fa5s.align-left"
    MDI_REFRESH = "mdi.refresh"
    MDI_GRID = "mdi.grid"
    MDI_MAGNIFY = "mdi.magnify"
    CAMERA = "mdi.camera"
    FULLSCREEN = "mdi.fullscreen"
    TOOLS = "mdi.tools"
    CHART_SCATTER_PLOT = "mdi.chart-scatter-plot"
    INTER_CHAIN_CONTACTS = "mdi.call-split"
    MAP_TAB = "mdi.map"
    VIEW_DASHBOARD = "mdi.view-dashboard-variant"
    DIALS_TAB = "mdi.tune"
    MIDI_TAB = "mdi.midi"
    SYMMETRY_MATES_TAB = "mdi.crystal-ball"
    TERMINAL_TAB = "fa5s.terminal"
    PREFERENCES = "mdi.cog"
    TABLE_GRID = "fa5s.table"
    MSC_FILE_TEXT = "msc.file-text"
    CLIP_SLICE = "ri.slice-fill"
    FOG_LINE = "ri.foggy-line"
    PICK_ATOM = "fa5s.mouse-pointer"
    SECOND_LIGHT = "mdi6.ceiling-light-multiple"
    BACKGROUND_TOGGLE = "fa5s.yin-yang"
    AUTO_ROTATE = "mdi.axis-z-rotate-clockwise"

    # Biotoolkit
    OUTPUT = "msc.output"
    SEARCH_LINE = "ri.search-2-line"
    SEARCH_RI = "ri.search-line"
    DATABASE_SEARCH = "mdi.database-search-outline"
    FA_DATABASE = "fa5s.database"
    EXIT = "mdi.exit-to-app"
    CUT = "mdi.content-cut"
    COPY = "msc.copy"
    FIND = "mdi6.file-find-outline"
    PASTE = "mdi6.content-paste"
    SELECT_ALL = "mdi6.arrow-expand-all"
    REDO = "mdi6.redo-variant"
    UNDO = "mdi6.undo-variant"
    FONT = "mdi6.format-font"
    COLOR = "msc.symbol-color"
    NUMBERED_LIST = "mdi.format-list-numbered-rtl"
    CONVERT = "ri.exchange-box-line"
    HELP_RHOMBUS = "mdi6.help-rhombus-outline"
    ZOOM_IN = "msc.zoom-in"
    ZOOM_OUT = "msc.zoom-out"
    SCREEN_NORMAL = "msc.screen-normal"
    FIT_TO_PAGE = "mdi.fit-to-page-outline"
    FILE_DOCUMENT_EDIT = "mdi6.file-document-edit-outline"
    PAINT_BRUSH = "fa5s.paint-brush"
    HIGHLIGHTER = "fa5s.highlighter"
    FONT_SIZE = "ei.fontsize"
    TEXT_BOX_PLUS = "mdi6.text-box-plus-outline"
    WEIGHT = "fa5s.weight"
    TEXT_ALIGN_LEFT = "ph.text-align-left"
    USER_SECRET = "fa5s.user-secret"
    PALETTE = "fa5s.palette"
    TABLE_ROW_ADD = "mdi.table-row-plus-after"
    TABLE_ROW_REMOVE = "mdi.table-row-remove"
    TABLE_ROW_HEIGHT = "mdi6.table-row-height"
    INSERT_ROW = "ri.insert-row-top"
    DELETE_ROW = "ri.delete-row"
    FILE_CSV = "fa5s.file-csv"
    DATABASE_SYNC = "mdi6.database-sync-outline"
    FILTER = "msc.filter-filled"
    TABLE_COLUMN = "mdi.table-column"
    MSC_REFRESH = "msc.refresh"
    ARROW_RIGHT = "mdi.arrow-right"
    CHART_GANTT = "mdi6.chart-gantt"
    FLASK = "fa5s.flask"
    TEST_TUBE = "ri.test-tube-fill"
    CUBE = "fa5s.cube"
    CHROME = "fa5b.chrome"
    DEBUG_BREAKPOINT = "msc.debug-breakpoint-data-unverified"
    FOLDER_MARKER = "mdi6.folder-marker-outline"
    FOLDER_MULTIPLE_PLUS = "mdi6.folder-multiple-plus-outline"
    FILE_DOCUMENT_MULTIPLE = "mdi.file-document-multiple"
    FOLDER_OPEN_THIN = "ph.folder-notch-open-thin"
    FA_INFO = "fa5s.info-circle"
    LICENSE = "fa5s.id-card"
    EI_ALIGN_LEFT = "ei.align-left"

    @staticmethod
    def get_pixmap(icon_name: str) -> QPixmap:
        filename = IconRegistry.pixmaps.get(icon_name)
        if not filename:
            return QPixmap()

        path = resource_path(IconRegistry._base_dir / filename)

        if not path.exists():
            raise FileNotFoundError(f"Missing icons: {path}")

        return QPixmap(str(path))

    @staticmethod
    def get_icon(icon_name: str, fallback: str = None) -> QPixmap:
        """
        Get icons with fallback support.

        :param icon_name: Icon identifier (e.g., "msc.run")
        :param fallback: Fallback icons if primary fails
        :return: QIcon or None if both fail
        """
        try:
            icon = qta.icon(icon_name).pixmap(PicoUiDimensions.ICON_SIZE)
            if icon.isNull():
                raise ValueError(f"Icon {icon_name} is null")
            return icon

        except Exception as ex:
            log.debug(f"Failed to load icons {icon_name}: {ex}")
            if fallback:
                try:
                    icon = qta.icon(fallback)
                    if not icon.isNull():
                        log.info(f"Using fallback icons {fallback} for {icon_name}")
                        return icon

                except Exception as fallback_ex:
                    log.exception(f"Failed to load fallback icons {fallback_ex}")
            log.warning(f"Could not load icons {icon_name}")
            return None

    @staticmethod
    def get_icon_safe(icon_name: str, fallback: str = None) -> QIcon:
        """
        Get a QIcon with fallback support. Always returns a QIcon (may be empty).

        :param icon_name: Icon identifier
        :param fallback: Fallback icons if primary fails
        :return: QIcon (may be empty if all fail)
        """
        pixmap = IconRegistry.get_icon(icon_name, fallback)
        if pixmap is None or pixmap.isNull():
            return QIcon()
        if isinstance(pixmap, QIcon):
            return pixmap
        return QIcon(pixmap)
