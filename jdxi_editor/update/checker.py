"""
Update checker

Asks GitHub Releases whether a newer JD-Xi Editor has been published, with one
unauthenticated request (GitHub allows 60 an hour per IP address; the automatic
check runs at most once a day). Drafts, pre-releases and releases without a
build for this platform are ignored.

Example:
    >>> checker = UpdateChecker(parent)
    >>> checker.update_available.connect(on_update)  # (ReleaseInfo, manual)
    >>> checker.check(manual=True)
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable, Iterable, Optional

from PySide6.QtCore import QObject, QSettings, QUrl, Signal
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest

from jdxi_editor.project import __organization_name__, __program__, __version__

REPOSITORY = "markxbrooks/JDXI-Editor"
RELEASES_API_URL = f"https://api.github.com/repos/{REPOSITORY}/releases?per_page=10"
RELEASES_PAGE_URL = f"https://github.com/{REPOSITORY}/releases"
PIP_UPGRADE_COMMAND = "pip install -U jdxi-editor"

AUTO_CHECK_KEY = "update/auto_check"
LAST_CHECK_KEY = "update/last_check"
SKIPPED_VERSION_KEY = "update/skipped_version"
AUTO_CHECK_DEFAULT = True  # on by default; said so in the dialog and Preferences

CHECK_INTERVAL = timedelta(days=1)
STARTUP_DELAY_MS = 10_000
TRANSFER_TIMEOUT_MS = 15_000

# Install kinds, and the release assets that suit each, in order of preference
MACOS, WINDOWS, APPIMAGE, DEB, LINUX, PIP = (
    "macos",
    "windows",
    "appimage",
    "deb",
    "linux",
    "pip",
)
ASSET_SUFFIXES: dict[str, tuple[str, ...]] = {
    MACOS: (".pkg", ".app.zip", ".dmg"),
    WINDOWS: (".exe",),
    APPIMAGE: (".appimage",),
    DEB: (".deb", ".appimage"),
    LINUX: (".appimage", ".deb"),
    PIP: (),  # upgraded from PyPI, no download needed
}


@dataclass(frozen=True)
class ReleaseInfo:
    """A published release, with the download that suits this install."""

    version: str
    tag: str
    name: str
    notes: str  # Markdown
    page_url: str
    asset_name: Optional[str] = None
    asset_url: Optional[str] = None


def parse_version(text: str) -> Optional[tuple[int, ...]]:
    """'v0.9.10' or '0.9.10' -> (0, 9, 10); None if there is no version."""
    match = re.match(r"^\s*[vV]?(\d+(?:\.\d+)*)", text or "")
    if not match:
        return None
    return tuple(int(part) for part in match.group(1).split("."))


def is_newer(candidate: str, current: str) -> bool:
    """True if candidate is a later version than current (0.9.10 > 0.9.9)."""
    new, old = parse_version(candidate), parse_version(current)
    if new is None or old is None:
        return False
    width = max(len(new), len(old))
    return new + (0,) * (width - len(new)) > old + (0,) * (width - len(old))


def install_kind() -> str:
    """How this copy was installed, which decides the download offered."""
    if not getattr(sys, "frozen", False):  # py2app and PyInstaller set this
        return PIP
    if sys.platform == "darwin":
        return MACOS
    if sys.platform.startswith("win"):
        return WINDOWS
    if os.environ.get("APPIMAGE"):
        return APPIMAGE
    if sys.executable.startswith("/opt/"):  # where the .deb installs
        return DEB
    return LINUX


def _pick_asset(assets: Iterable[dict], kind: str) -> Optional[dict]:
    assets = list(assets)
    for suffix in ASSET_SUFFIXES.get(kind, ()):
        for asset in assets:
            if str(asset.get("name", "")).lower().endswith(suffix):
                return asset
    return None


def pick_release(releases: Iterable[dict], kind: str) -> Optional[ReleaseInfo]:
    """The newest published release with a build for this kind of install."""
    candidates = []
    for release in releases:
        if release.get("draft") or release.get("prerelease"):
            continue
        tag = str(release.get("tag_name", ""))
        version = parse_version(tag)
        if version is None:
            continue
        candidates.append((version, release))
    for version, release in sorted(candidates, key=lambda c: c[0], reverse=True):
        asset = _pick_asset(release.get("assets") or [], kind)
        if asset is None and kind != PIP:
            continue  # e.g. published before its builds were uploaded
        return ReleaseInfo(
            version=".".join(str(part) for part in version),
            tag=str(release.get("tag_name", "")),
            name=str(release.get("name") or release.get("tag_name", "")),
            notes=str(release.get("body") or ""),
            page_url=str(release.get("html_url") or RELEASES_PAGE_URL),
            asset_name=asset.get("name") if asset else None,
            asset_url=asset.get("browser_download_url") if asset else None,
        )
    return None


def settings_bool(settings: QSettings, key: str, default: bool) -> bool:
    value = settings.value(key, default)
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("true", "1", "yes")


def app_settings() -> QSettings:
    return QSettings(__organization_name__, __program__)


def should_auto_check(
    settings: Optional[QSettings] = None, now: Optional[datetime] = None
) -> bool:
    """Automatic checks are on and the last one was over a day ago."""
    settings = settings or app_settings()
    if not settings_bool(settings, AUTO_CHECK_KEY, AUTO_CHECK_DEFAULT):
        return False
    now = now or datetime.now(timezone.utc)
    try:
        last = datetime.fromisoformat(str(settings.value(LAST_CHECK_KEY, "")))
    except ValueError:
        return True
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    return now - last >= CHECK_INTERVAL


class UpdateChecker(QObject):
    """Checks GitHub Releases asynchronously; never blocks the UI."""

    update_available = Signal(object, bool)  # ReleaseInfo, manual
    up_to_date = Signal(str, bool)  # newest version found ("" if none), manual
    failed = Signal(str, bool)  # error message, manual

    def __init__(
        self,
        parent: Optional[QObject] = None,
        url: str = RELEASES_API_URL,
        current_version: str = __version__,
        kind: Optional[str] = None,
        settings: Optional[QSettings] = None,
        now: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    ):
        super().__init__(parent)
        self.url = url
        self.current_version = current_version
        self.kind = kind or install_kind()
        self.settings = settings or app_settings()
        self._now = now
        self._manager = QNetworkAccessManager(self)
        self._reply: Optional[QNetworkReply] = None

    @property
    def is_checking(self) -> bool:
        return self._reply is not None

    def check(self, manual: bool = False) -> None:
        """Start a check; the result arrives as one of the signals."""
        if self._reply is not None:
            return  # one at a time
        request = QNetworkRequest(QUrl(self.url))
        request.setRawHeader(b"Accept", b"application/vnd.github+json")
        request.setRawHeader(b"X-GitHub-Api-Version", b"2022-11-28")
        request.setRawHeader(
            b"User-Agent", f"JDXI-Editor/{self.current_version}".encode()
        )
        request.setTransferTimeout(TRANSFER_TIMEOUT_MS)
        reply = self._manager.get(request)
        self._reply = reply
        reply.finished.connect(lambda: self._on_finished(reply, manual))

    def _on_finished(self, reply: QNetworkReply, manual: bool) -> None:
        self._reply = None
        try:
            if reply.error() != QNetworkReply.NetworkError.NoError:
                self.failed.emit(reply.errorString(), manual)
                return
            try:
                releases = json.loads(bytes(reply.readAll()).decode("utf-8"))
            except (ValueError, UnicodeDecodeError) as ex:
                self.failed.emit(f"Unexpected reply from GitHub: {ex}", manual)
                return
            if not isinstance(releases, list):
                message = (
                    releases.get("message") if isinstance(releases, dict) else None
                )
                self.failed.emit(message or "Unexpected reply from GitHub", manual)
                return
            self.settings.setValue(LAST_CHECK_KEY, self._now().isoformat())
            self._report(pick_release(releases, self.kind), manual)
        finally:
            reply.deleteLater()

    def _report(self, release: Optional[ReleaseInfo], manual: bool) -> None:
        if release is None or not is_newer(release.version, self.current_version):
            self.up_to_date.emit(release.version if release else "", manual)
            return
        skipped = str(self.settings.value(SKIPPED_VERSION_KEY, ""))
        if not manual and skipped == release.version:
            self.up_to_date.emit(release.version, manual)  # the user skipped it
            return
        self.update_available.emit(release, manual)
