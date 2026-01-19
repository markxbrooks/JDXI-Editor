from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from jdxi_editor.core.jdxi import JDXi


def create_placeholder_icon(
    e: Exception, error_message: str, icon_name: str
) -> tuple[QWidget, QIcon]:
    """Create a placeholder widget so the tab still appears"""
    placeholder_widget = QWidget()
    placeholder_layout = QVBoxLayout(placeholder_widget)
    placeholder_label = QLabel(f"{error_message} {e}")
    placeholder_layout.addWidget(placeholder_label)
    playlist_icon = JDXi.UI.IconRegistry.get_icon(icon_name, color=JDXi.UI.Style.GREY)
    return placeholder_widget, playlist_icon


def create_placeholder_(e: Exception) -> tuple[QWidget, QIcon]:
    """Create a placeholder widget so the tab still appears"""
    placeholder_widget = QWidget()
    placeholder_layout = QVBoxLayout(placeholder_widget)
    placeholder_label = QLabel(f"Error loading user programs: {e}")
    placeholder_layout.addWidget(placeholder_label)
    user_programs_icon = JDXi.UI.IconRegistry.get_icon(
        "mdi.account-music", color=JDXi.UI.Style.GREY
    )
    return placeholder_widget, user_programs_icon
