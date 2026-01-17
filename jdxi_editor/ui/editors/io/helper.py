from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.jdxi.style.icons import IconRegistry


def create_placeholder_icon(e: Exception, error_message: str, icon_name: str) -> tuple[
    QWidget, QIcon]:
    """Create a placeholder widget so the tab still appears"""
    placeholder_widget = QWidget()
    placeholder_layout = QVBoxLayout(placeholder_widget)
    placeholder_label = QLabel(f"{error_message} {e}")
    placeholder_layout.addWidget(placeholder_label)
    playlist_icon = IconRegistry.get_icon(icon_name, color=JDXiStyle.GREY)
    return placeholder_widget, playlist_icon


def create_placeholder_(e: Exception) -> tuple[QWidget, QIcon]:
    """Create a placeholder widget so the tab still appears"""
    placeholder_widget = QWidget()
    placeholder_layout = QVBoxLayout(placeholder_widget)
    placeholder_label = QLabel(f"Error loading user programs: {e}")
    placeholder_layout.addWidget(placeholder_label)
    user_programs_icon = IconRegistry.get_icon("mdi.account-music", color=JDXiStyle.GREY)
    return placeholder_widget, user_programs_icon
