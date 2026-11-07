"""
Playback activity

Whether any transport (the MIDI File Player's or the Pattern Editor's) is
playing. Editors use it to hold back device requests (RQ1) while playback is
sending MIDI, and to make them once it stops.

Example:
    >>> activity = playback_activity()
    >>> activity.playing_changed.connect(lambda playing: print(playing))
    >>> activity.is_playing
    False
    >>> refresher = DeviceRefresher(editor.data_request, editor.isVisible, parent=editor)
    >>> refresher.schedule()  # after a parameter change on the JD-Xi
"""

from typing import Callable, Optional

from PySide6.QtCore import QObject, QTimer, Signal

# Wait for changes (e.g. a knob being turned) to settle before requesting
REFRESH_DELAY_MS = 400


class PlaybackActivity(QObject):
    """
    Which transports are playing.

    Signals:
        playing_changed(bool): True when the first transport starts playing,
            False when the last one stops or pauses
    """

    playing_changed = Signal(bool)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._playing: set[int] = set()

    @property
    def is_playing(self) -> bool:
        return bool(self._playing)

    def set_playing(self, source: object, playing: bool) -> None:
        """*source* (a transport) has started (True) or stopped/paused (False)."""
        was_playing = self.is_playing
        if playing:
            self._playing.add(id(source))
        else:
            self._playing.discard(id(source))
        if self.is_playing != was_playing:
            self.playing_changed.emit(self.is_playing)


_activity: Optional[PlaybackActivity] = None


def playback_activity() -> PlaybackActivity:
    """The application's PlaybackActivity."""
    global _activity
    if _activity is None:
        _activity = PlaybackActivity()
    return _activity


class DeviceRefresher(QObject):
    """
    Asks the JD-Xi for an editor's values so its UI follows parameter changes
    made on the instrument: once a burst of changes has settled, and never
    while playback is sending MIDI (it asks once playback stops instead).
    """

    def __init__(
        self,
        request: Callable[[], None],
        is_wanted: Callable[[], bool] = lambda: True,
        delay_ms: int = REFRESH_DELAY_MS,
        parent: Optional[QObject] = None,
    ):
        """
        :param request: Sends the editor's requests (e.g. its data_request)
        :param is_wanted: False when the request can be skipped (e.g. the
            editor is hidden and will request when shown)
        :param delay_ms: Quiet time after the last change before requesting
        :param parent: Optional QObject parent (the editor)
        """
        super().__init__(parent)
        self._request = request
        self._is_wanted = is_wanted
        self._pending = False  # held back by playback
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(delay_ms)
        self._timer.timeout.connect(self._refresh)
        playback_activity().playing_changed.connect(self._on_playing_changed)

    @property
    def is_pending(self) -> bool:
        """A request is waiting for playback to stop."""
        return self._pending

    def schedule(self, *_args) -> None:
        """A parameter changed: request after *delay_ms* without further changes."""
        if playback_activity().is_playing:
            self._pending = True
            return
        self._timer.start()

    def request_now(self) -> None:
        """Request straight away (e.g. the editor was shown), unless playing."""
        self._timer.stop()
        self._refresh()

    def _refresh(self) -> None:
        if playback_activity().is_playing:
            self._pending = True
            return
        self._pending = False
        if self._is_wanted():
            self._request()

    def _on_playing_changed(self, playing: bool) -> None:
        if not playing and self._pending:
            self._timer.start()
