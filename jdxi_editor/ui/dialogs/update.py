"""
Update dialog

Offers a newer JD-Xi Editor found on GitHub Releases: its release notes, and
buttons to download it, view the release, skip this version or decide later.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QSettings, Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.project import __program__, __version__
from jdxi_editor.update.checker import (
    PIP,
    PIP_UPGRADE_COMMAND,
    SKIPPED_VERSION_KEY,
    ReleaseInfo,
    app_settings,
)

AUTO_CHECK_NOTICE = (
    f"{__program__} checks GitHub for new releases automatically, at most once "
    "a day. You can turn this off in Help → Preferences."
)


class UpdateDialog(QDialog):
    """Shows a newer release and how to get it."""

    def __init__(
        self,
        release: ReleaseInfo,
        kind: str,
        parent: Optional[QWidget] = None,
        settings: Optional[QSettings] = None,
        current_version: str = __version__,
    ):
        super().__init__(parent)
        self.release = release
        self.settings = settings or app_settings()
        self.setWindowTitle("Update available")
        self.resize(560, 460)

        layout = QVBoxLayout(self)
        heading = QLabel(
            f"<b>{__program__} {release.version}</b> is available "
            f"(you have {current_version})."
        )
        layout.addWidget(heading)

        if kind == PIP:
            how = QLabel(f"To upgrade, run: <code>{PIP_UPGRADE_COMMAND}</code>")
            how.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            layout.addWidget(how)
        elif release.asset_name:
            layout.addWidget(QLabel(f"Download: {release.asset_name}"))

        self.notes = QTextBrowser()
        self.notes.setOpenExternalLinks(True)
        self.notes.setMarkdown(release.notes or "_No release notes._")
        layout.addWidget(self.notes, 1)

        notice = QLabel(AUTO_CHECK_NOTICE)
        notice.setWordWrap(True)
        notice.setObjectName("UpdateNotice")
        layout.addWidget(notice)

        buttons = QDialogButtonBox()
        if release.asset_url and kind != PIP:
            self.download_button = QPushButton("Download")
            self.download_button.setDefault(True)
            self.download_button.clicked.connect(self.on_download)
            buttons.addButton(self.download_button, QDialogButtonBox.ButtonRole.AcceptRole)
        view = QPushButton("View release")
        view.clicked.connect(self.on_view_release)
        buttons.addButton(view, QDialogButtonBox.ButtonRole.ActionRole)
        skip = QPushButton("Skip this version")
        skip.clicked.connect(self.on_skip)
        buttons.addButton(skip, QDialogButtonBox.ButtonRole.DestructiveRole)
        later = QPushButton("Later")
        later.clicked.connect(self.reject)
        buttons.addButton(later, QDialogButtonBox.ButtonRole.RejectRole)
        layout.addWidget(buttons)

    def on_download(self) -> None:
        QDesktopServices.openUrl(QUrl(self.release.asset_url))
        self.accept()

    def on_view_release(self) -> None:
        QDesktopServices.openUrl(QUrl(self.release.page_url))

    def on_skip(self) -> None:
        """Don't offer this version again automatically (a manual check still will)."""
        self.settings.setValue(SKIPPED_VERSION_KEY, self.release.version)
        self.reject()
