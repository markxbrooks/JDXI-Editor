"""
Preferences Dialog

Sets settings for various biotoolkit features
"""

import logging

from decologr import Decologr as log
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QSettings, QSize
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.project import (
    __organization_name__,
    __package_name__,
    __program__,
)


def log_settings() -> None:
    settings = QSettings(__organization_name__, __program__)
    print(f'log_level {settings.value("log_level", logging.DEBUG, type=int)}')
    print(f'logging {settings.value("logging", True, type=bool)}')


class UiPreferencesDialog(QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.icon_size = None
        self.settings = QSettings(__organization_name__, __program__)

    def ui_setup(self, parent: QWidget = None):
        """
        ui_setup
        :param parent: QWidget
        :return: None
        """
        self.icon_size = QSize(40, 40)
        """if darkdetect.isLight():
            theme = "light"
        else:
            theme = "dark"""
        log_settings()
        self.resize(508, 300)

        self.setWindowTitle("JD-XI Editor settings")
        main_layout = QVBoxLayout(self)

        # Create a QComboBox
        self.log_level_combo = QComboBox()
        self.log_levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        self.log_level_combo.addItems(self.log_levels.keys())
        # Load the log level from QSettings
        # self.load_log_level_from_settings()
        log_level = int(self.settings.value("log_level", logging.DEBUG))
        # Reverse lookup: find the key name for the numeric value
        try:
            level_name = next((k for k, v in self.log_levels.items() if v == log_level))
        except StopIteration:
            level_name = "DEBUG"  # default
        index = list(self.log_levels.keys()).index(level_name)
        if index >= 0:
            self.log_level_combo.setCurrentIndex(index)
        # Connect the combo box to a function that updates QSettings
        self.log_level_combo.currentIndexChanged.connect(self.update_log_level)

        self.log_level_layout = QHBoxLayout(self)
        self.log_icon = QLabel()
        self.log_icon.setPixmap(
            JDXi.UI.Icon.get_icon(JDXi.UI.Icon.REPORT).pixmap(self.icon_size)
        )
        self.log_level_label = QLabel("Log file error reporting level:")
        self.log_level_layout.addWidget(self.log_icon)
        self.log_level_layout.addWidget(self.log_level_label)
        self.log_level_layout.addWidget(self.log_level_combo)

        self.logging_layout = QHBoxLayout(self)
        self.logging_icon = QLabel()
        self.logging_checkbox = QCheckBox("Enable Logging?")
        self.logging_checkbox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.logging_checkbox.setChecked(
            bool(self.settings.value("logging", type=bool))
        )
        self.logging_icon.setPixmap(
            JDXi.UI.Icon.get_icon(JDXi.UI.Icon.REPORT).pixmap(self.icon_size)
        )
        self.logging_label = QLabel("Logging On or Off:")
        self.logging_layout.addWidget(self.logging_icon)
        self.logging_layout.addWidget(self.logging_label)
        self.logging_layout.addWidget(self.logging_checkbox)

        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(150, 250, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
        )
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.rejected.connect(self.close)
        self.buttonBox.accepted.connect(self.on_save_settings)
        self.buttonBox.accepted.connect(self.close)
        QtCore.QMetaObject.connectSlotsByName(self)

        main_widget = QWidget()
        main_layout.addWidget(main_widget)

        main_content_layout = QVBoxLayout()
        main_content_layout.addLayout(self.log_level_layout)
        main_content_layout.addLayout(self.logging_layout)
        main_widget.setLayout(main_content_layout)
        main_layout.addWidget(self.buttonBox)
        self.setLayout(main_layout)

    def load_log_level_from_settings(self):
        """
        Load and migrate log level from settings (handles legacy string values).
        """
        value = self.settings.value("log_level", logging.DEBUG)

        # Case 1: Value already an integer (new style)
        if isinstance(value, int):
            log_level = value

        # Case 2: Legacy value stored as string (e.g., "CRITICAL")
        elif isinstance(value, str):
            # Try to parse as integer first
            try:
                log_level = int(value)
            except ValueError:
                # Convert known string names
                log_level = self.log_levels.get(value.upper(), logging.DEBUG)
                # Migrate: store the numeric version back
                self.settings.setValue("log_level", log_level)

        else:
            # Fallback
            log_level = logging.DEBUG

        # Set combo box to correct index
        level_name = next(
            (k for k, v in self.log_levels.items() if v == log_level), "DEBUG"
        )
        index = list(self.log_levels.keys()).index(level_name)
        self.log_level_combo.setCurrentIndex(index)

        # Set the logger level immediately
        logging.getLogger(__package_name__).setLevel(log_level)

    def update_log_level(self, level):
        """
        Update log level for the current logger and all handlers
        """
        log.parameter("level", level)
        logger = logging.getLogger(__package_name__)
        logger.setLevel(level)

        for handler in logger.handlers:
            handler.setLevel(level)

        # Also apply to root logger and its handlers (optional, if you use root logging)
        logging.root.setLevel(level)
        for handler in logging.root.handlers:
            handler.setLevel(level)

        self.settings.setValue("log_level", level)
        self.settings.sync()
        print(f"✅ Updated log level to {logging.getLevelName(level)}")

    def on_save_settings(self):
        """
        on_save_settings
        :return: None
        """
        settings = self.settings
        try:
            settings.setValue("logging", bool(self.logging_checkbox.isChecked()))
            settings.sync()
            log_settings()
        except Exception as ex:
            print(f"Error {ex} occurred saving settings")
