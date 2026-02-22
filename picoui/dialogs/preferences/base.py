"""
Preferences Dialog

Sets settings for various biotoolkit features
"""

from __future__ import annotations

from PySide6.QtCore import QSettings, QSize
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QCheckBox, QDialog,
                               QHBoxLayout, QLineEdit,
                               QTabWidget, QVBoxLayout, QWidget, QComboBox, QLabel)

from decologr import Decologr as log
from picoui.icons import IconRegistry
from picoui.settings import PicoUISettings
from picoui.dialogs.preferences.helper import (
    create_checkbox_from_spec,
    create_settings_line_edit,
)
from picoui.specs.widgets import TabWidgetSpec, WindowSpec
from picoui.tooltip.manager import TooltipManager


class BasePreferencesDialog(QDialog):
    """BasePreferencesDialog"""

    spec: TabWidgetSpec = None
    window_spec: WindowSpec = None

    def __init__(self, parent):
        super().__init__(parent)
        self.expected_values: dict[str, str] = {}
        self._widgets: dict[str, QWidget] = {}
        self._layouts: dict[str, QHBoxLayout] = {}
        self.button_box: QWidget = None
        self.reset_button: QWidget = None
        self.font: QFont = None
        self.icon_size: QSize = None
        self.settings: QSettings = None
        log_settings()

    def ui_setup(self, parent: QWidget = None):
        """
        ui_setup
        :param parent: QWidget
        :return: None
        """
        self.icon_size = QSize(40, 40)
        self.font = self.settings.value("font")
        if self.window_spec is not None:
            self.setWindowTitle(self.window_spec.title)
            self.resize(self.window_spec.width, self.window_spec.height)
            if self.window_spec.icon and self.window_spec.icon.name:
                from picoui.icons import IconRegistry
                icon = IconRegistry.get_icon(self.window_spec.icon.name)
                if icon and not icon.isNull():
                    self.setWindowIcon(icon)
        else:
            self.resize(750, 400)

        main_layout = QVBoxLayout(self)
        self._create_log_level_combo(self.settings, self.log_levels)

        specs = self._build_specs()

        self._build_widgets_from_specs(specs)

        self._setup_connections()

        self._create_tab_widget(main_layout)
        main_layout.addWidget(self.button_box)
        self.setLayout(main_layout)

    def _build_widgets_from_specs(self, specs: dict[str, SettingsFieldSpec]):
        """Build widgets from specs dictionary."""
        for key, spec in specs.items():
            if spec.widget_type == WidgetType.LINEEDIT:
                key_name, line_edit, layout = self._create_line_edit_from_spec(spec)
                self._widgets[key_name] = line_edit
                self._layouts[key_name] = layout
            elif spec.widget_type == WidgetType.CHECKBOX:
                check_box = create_checkbox_from_spec(spec)
                self._widgets[key] = check_box
                self._layouts[key] = QHBoxLayout()
                self._layouts[key].addWidget(check_box)
            elif spec.widget_type == WidgetType.PUSHBUTTON:
                self._create_special_buttons(specs)

    def _create_special_buttons(self, specs):
        """Create special buttons"""
        raise NotImplementedError(
            "Not implemented - should be implemented in child classes"
        )

    def _build_specs(self):
        """Build line edit specs from settings file"""
        raise NotImplementedError(
            "Not implemented - should be implemented in child classes"
        )

    def get_settings_value(self, setting_name: str, default_value=""):
        """Get settings value from settings file"""
        value = self.settings.value(setting_name, default_value, type=str)
        # Allow empty values - additional arguments are optional
        if value is None:
            value = ""
        log.debug(f"Loading {setting_name} value from settings: '{value}'")
        return value

    def _create_line_edit_from_spec(
            self,
            spec: SettingsFieldSpec,
    ) -> tuple[str, QLineEdit, QHBoxLayout]:
        """Create QLineEdit and layout from SettingsFieldSpec."""

        line_edit = create_settings_line_edit(
            key=spec.key,
            default=spec.default,
            placeholder=spec.placeholder,
            tooltip=spec.tooltip,
            settings=self.settings,
        )

        layout = create_row(
            icon_name=spec.icon,
            label_text=spec.label,
            widget=line_edit,
        )

        return spec.key, line_edit, layout

    def _setup_connections(self):
        """setup connections"""
        raise NotImplementedError(
            "Not implemented - should be implemented in child classes"
        )

    def _create_tab_widget(self, main_layout):
        """create tab widget"""
        main_tabwidget = QTabWidget()
        main_layout.addWidget(main_tabwidget)
        self._add_tabs(main_tabwidget)

    def _add_tabs(self, tabwidget: QTabWidget):
        """add tabs to tab widget"""
        for tab in self.spec.tabs:
            if not tab.widget_attr:
                raise ValueError(f"Tab '{tab.name}' missing widget_attr")

            widget = getattr(self, tab.widget_attr, None)

            if widget is None:
                raise AttributeError(
                    f"Widget attribute '{tab.widget_attr}' not found on {type(self).__name__}"
                )

            icon = IconRegistry.get_icon(tab.icon) if tab.icon else None

            if icon:
                tabwidget.addTab(widget, icon, tab.name)
            else:
                tabwidget.addTab(widget, tab.name)

    def on_reset_to_defaults(self):
        """
        Reset all preferences to their default values.
        Updates the UI widgets but does not save to QSettings until user clicks OK.
        :return: None
        """
        raise NotImplementedError(
            "Not implemented - should be implemented in child classes"
        )

    def on_save_settings(self):
        """
        on_save_settings
        :return: None
        """
        raise NotImplementedError(
            "Not implemented - should be implemented in child classes"
        )

    def save_checkbox_settings(
            self, value_name: str, checkbox_widget: QCheckBox = None
    ):
        """save checkbox settings"""
        self.settings.setValue(value_name, checkbox_widget.isChecked())

    def sync_settings(self, settings_file):
        """Force sync to ensure settings are written to disk"""
        try:
            sync_result = self.settings.sync()
            self.validate_settings_written(self.expected_values)
            if sync_result:
                log.info("Settings synced successfully")
            else:
                # --- Check settings status for more details
                status = self.settings.status()
                # QSettings.Status enum values: NoError=0, AccessError=1, FormatError=2
                if status == 0:  # NoError
                    log.error("Settings sync failed, but no error reported")
                elif status == 1:  # AccessError
                    log.error(
                        f"Settings sync failed: Access Error - cannot write to {settings_file}. "
                        "Check file permissions."
                    )
                elif status == 2:  # FormatError
                    log.error(
                        f"Settings sync failed: Format Error - invalid format in {settings_file}"
                    )
                else:
                    log.warning(
                        f"Settings sync returned False (status: {status}) - settings may not be saved"
                    )

        except Exception as ex:
            log.error(f"Failed to sync settings to disk: {ex}")

    def validate_settings_written(self, expected_values: dict[str, str | bool]) -> None:
        """Validate that all expected settings were written to disk"""
        verify = QSettings(PicoUISettings.PROJECT, PicoUISettings.PROGRAM)

        for key, expected in expected_values.items():
            saved = verify.value(key, type=type(expected))
            if saved != expected:
                log.error(
                    f"Settings verification failed for '{key}'. "
                    f"Expected '{expected}', got '{saved}'"
                )
            else:
                log.debug(f"Verified '{key}' successfully.")

    def save_line_edit_settings_value(self, value_name: str, line_edit: QLineEdit):
        """save_line_edit_settings_value"""
        value = str(line_edit.text().strip())
        log.info(f"Saving {value_name}: '{value}'")
        self.settings.setValue(value_name, str(line_edit.text().strip()))
        self.expected_values[value_name] = value

    def update_log_level(self, index):
        """
        update_log_level
        :param index: int
        :return:
        """
        raise NotImplementedError(
            "Not implemented - should be implemented in child classes"
        )

    def _create_log_level_combo(self, settings, item_list: dict[int, str]):
        """Create a log level QComboBox"""
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(item_list.values())
        # --- Load the log level from QSettings
        log_level = int(settings.value(PicoUISettings.LOG_LEVEL, logging.DEBUG))
        index = list(item_list.keys()).index(log_level)
        if index >= 0:
            self.log_level_combo.setCurrentIndex(index)
        # --- Connect the combo box to a function that updates QSettings
        self.log_level_combo.currentIndexChanged.connect(self.update_log_level)
        self.log_level_combo.setToolTip(TooltipManager.PREF_LOG_LEVEL_COMBO)
        self.log_level_layout_layout = QHBoxLayout(self)
        self.log_level_icon = QLabel()
        self.log_level_icon.setPixmap(IconRegistry.get_icon(IconRegistry.REPORT))
        self.log_level_label = QLabel("Log file error reporting level:")
        log_level_widgets = [
            self.log_level_icon,
            self.log_level_label,
            self.log_level_combo,
        ]
        for widget in log_level_widgets:
            self.log_level_layout_layout.addWidget(widget)
