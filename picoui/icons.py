"""
Icon registry.

Provides centralized icon definitions and retrieval with fallback support.
"""

import sys
from pathlib import Path

import qtawesome as qta
from PySide6.QtGui import QPixmap

from decologr import Decologr as log

from picoui.dimensions import PicoUiDimensions


def resource_path(path: Path) -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / path
    return path


class IconRegistryPixmaps:
    SLURM = "slurm_93.png"


class IconRegistry:
    """Centralized icon definitions and retrieval"""

    _base_dir = Path(__file__).resolve().parent / "images"

    pixmaps = IconRegistryPixmaps

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
    FILE_SEARCH = "ph.file-search"
    EXCEL = "mdi.microsoft-excel"
    FILE_MTZ = "mdi.data-matrix-edit"
    FILE_MOLECULE = "mdi.molecule"
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

    @staticmethod
    def get_pixmap(icon_name: str) -> QPixmap:
        filename = IconRegistry.pixmaps.get(icon_name)
        if not filename:
            return QPixmap()

        path = resource_path(IconRegistry._base_dir / filename)

        if not path.exists():
            raise FileNotFoundError(f"Missing icon: {path}")

        return QPixmap(str(path))

    @staticmethod
    def get_icon(icon_name: str, fallback: str = None):
        """
        Get icon with fallback support.

        :param icon_name: Icon identifier (e.g., "msc.run")
        :param fallback: Fallback icon if primary fails
        :return: QIcon or None if both fail
        """
        try:
            icon = qta.icon(icon_name).pixmap(PicoUiDimensions.ICON_SIZE)
            if icon.isNull():
                raise ValueError(f"Icon {icon_name} is null")
            return icon

        except Exception as ex:
            log.debug(f"Failed to load icon {icon_name}: {ex}")
            if fallback:
                try:
                    icon = qta.icon(fallback)
                    if not icon.isNull():
                        log.info(f"Using fallback icon {fallback} for {icon_name}")
                        return icon

                except Exception as fallback_ex:
                    log.exception(f"Failed to load fallback icon {fallback_ex}")
            log.warning(f"Could not load icon {icon_name}")
            return None

    @staticmethod
    def get_icon_safe(icon_name: str, fallback: str = None):
        """
        Get icon with fallback support, returns empty QIcon if all fail.

        This version always returns a QIcon object (may be empty).

        :param icon_name: Icon identifier
        :param fallback: Fallback icon if primary fails
        :return: QIcon (may be empty if all fail)
        """
        icon = IconRegistry.get_icon(icon_name, fallback)
        if icon is None:
            # Return empty icon
            return qta.icon("")
        return icon
