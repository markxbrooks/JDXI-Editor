"""
The Audio Monitor panel: device, the three instruments, and one timer.
"""

from typing import Optional

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.audio.analysers.waveform_analyser import TIMEBASE_MS
from jdxi_editor.audio.audio_analyser import AudioAnalyser
from jdxi_editor.audio.audio_buffer import SampleRing
from jdxi_editor.audio.audio_snapshot import REFRESH_HZ, SAMPLE_RATE, AudioSnapshot
from jdxi_editor.audio.audio_source import InputDeviceSource
from jdxi_editor.ui.style.rack_skin import active_skin
from jdxi_editor.ui.editors.helpers.widgets import create_jdxi_button, create_jdxi_row
from jdxi_editor.ui.widgets.audio.oscilloscope import Oscilloscope
from jdxi_editor.ui.widgets.audio.spectrum_display import SpectrumDisplay
from jdxi_editor.ui.widgets.audio.vu_meter import VUMeter


class _Readout(QWidget):
    """A short heading and one instrument, on the chassis surface."""

    def __init__(self, title: str, body: QWidget, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.heading = QLabel(title)
        self.heading.setObjectName("readoutHeading")
        self.body = body
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 8)
        layout.setSpacing(4)
        layout.addWidget(self.heading)
        layout.addWidget(body, 1)
        self.apply_skin()

    def apply_skin(self) -> None:
        skin = active_skin()
        self.setStyleSheet(
            "_Readout {"
            f"background-color: {skin.chassis.surface};"
            "border-radius: 4px;"
            "}"
            "_Readout QLabel#readoutHeading {"
            f"color: {_heading_colour(skin)};"
            "background: transparent;"
            "}"
        )
        # A skin can change the instrument's shape (bars, dials, VU faces)
        fit = getattr(self.body, "_fit_height", None)
        if fit is not None:
            fit()
        self.body.update()


class AudioMonitor(QWidget):
    """
    Captures an input, analyses it once, and paints whichever instruments
    are switched on.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.ring = SampleRing(SAMPLE_RATE * 2)
        self.analyser = AudioAnalyser(self.ring)
        self.source = InputDeviceSource(self.ring)
        self.scope = Oscilloscope()
        self.vu = VUMeter()
        self.spectrum = SpectrumDisplay()
        self.scope_panel = _Readout("Oscilloscope", self.scope)
        self.meter_panel = _Readout("Meters", self.vu)
        self.spectrum_panel = _Readout("Spectrum", self.spectrum)
        self._skin_id = active_skin().skin_id

        self.device = QComboBox()
        self.status = QLabel("Stopped")
        # Round transport buttons: Start stays lit while listening, Stop is
        # live only then
        self.listen_button, start_label = _round_button(
            "PLAY", "Start", "Listen to the chosen input"
        )
        self.listen_button.setCheckable(True)
        self.listen_button.clicked.connect(self._on_listen_clicked)
        self.stop_button, stop_label = _round_button(
            "STOP", "Stop", "Stop listening and release the input"
        )
        self.stop_button.clicked.connect(self.stop)
        self.stop_button.setEnabled(False)

        self.show_scope = QCheckBox("Oscilloscope")
        self.show_vu = QCheckBox("Meters")
        self.show_spectrum = QCheckBox("Spectrum")
        for box, panel in (
            (self.show_scope, self.scope_panel),
            (self.show_vu, self.meter_panel),
            (self.show_spectrum, self.spectrum_panel),
        ):
            box.setChecked(True)
            box.toggled.connect(panel.setVisible)

        self.timebase = QComboBox()
        for ms in TIMEBASE_MS:
            self.timebase.addItem(f"{ms} ms", ms)
        self.timebase.setCurrentIndex(TIMEBASE_MS.index(20))
        self.timebase.currentIndexChanged.connect(self._timebase_changed)

        inputs = QHBoxLayout()
        inputs.addWidget(self.device, 1)
        inputs.addWidget(self.status)
        inputs.addWidget(self.listen_button)
        inputs.addWidget(start_label)
        inputs.addSpacing(6)
        inputs.addWidget(self.stop_button)
        inputs.addWidget(stop_label)

        display = QGroupBox("Display")
        choices = QHBoxLayout(display)
        choices.addWidget(self.show_scope)
        choices.addWidget(self.show_vu)
        choices.addWidget(self.show_spectrum)
        choices.addStretch(1)
        choices.addWidget(self.timebase)

        layout = QVBoxLayout(self)
        layout.addLayout(inputs)
        layout.addWidget(display)
        layout.addWidget(self.scope_panel, 1)
        layout.addWidget(self.meter_panel, 0)
        layout.addWidget(self.spectrum_panel, 1)

        self._timer = QTimer(self)
        self._timer.setInterval(int(1000 / REFRESH_HZ))
        self._timer.timeout.connect(self.refresh_display)
        self._populate_devices()

    def _populate_devices(self) -> None:
        self.device.clear()
        if not InputDeviceSource.available():
            self.device.addItem("sounddevice is not installed", None)
            self.listen_button.setEnabled(False)
            self.status.setText("sounddevice is not installed")
            return
        self.device.addItem("(Default)", None)
        for name, index in InputDeviceSource.input_devices():
            self.device.addItem(name, index)

    def _timebase_changed(self, _index: int) -> None:
        ms = self.timebase.currentData()
        if ms is not None:
            self.analyser.set_timebase(int(ms))

    def _on_listen_clicked(self, _checked: bool) -> None:
        # Start only starts; Stop is its own button. Clicking a lit Start
        # leaves it lit rather than stopping.
        if self._timer.isActive():
            self._set_listening(True)
            return
        self.start()

    def _set_listening(self, listening: bool) -> None:
        self.listen_button.blockSignals(True)
        self.listen_button.setChecked(listening)
        self.listen_button.blockSignals(False)
        self.stop_button.setEnabled(listening)

    def start(self) -> None:
        """
        Open the chosen input and start the refresh timer.

        :return: None
        """
        device = self.device.currentData()
        try:
            self.analyser.start()
            self.source.start(None if device is None else int(device))
        except Exception as ex:
            self.source.stop()
            self.analyser.stop()
            self._set_listening(False)
            self.status.setText(str(ex))
            return
        self._timer.start()
        self._set_listening(True)
        self.status.setText("Listening")

    def stop(self) -> None:
        """
        Close the input and stop analysis.

        :return: None
        """
        self._timer.stop()
        self.source.stop()
        self.analyser.stop()
        self._set_listening(False)
        if InputDeviceSource.available():
            self.status.setText("Stopped")

    def refresh_display(self) -> None:
        """
        Paint the latest snapshot, if one has been published.

        :return: None
        """
        self._apply_panel_skin()
        self.show_snapshot(self.analyser.latest_snapshot())

    def show_snapshot(self, snapshot: Optional[AudioSnapshot]) -> None:
        """
        Hand one snapshot to the three instruments.

        :param snapshot: Optional[AudioSnapshot]
        :return: None
        """
        if snapshot is None:
            return
        self.vu.set_levels(
            snapshot.peak_left,
            snapshot.peak_right,
            snapshot.vu_left,
            snapshot.vu_right,
            snapshot.peak_hold_left,
            snapshot.peak_hold_right,
        )
        self.spectrum.set_spectrum(snapshot.spectrum)
        self.scope.set_waveform(snapshot.waveform_left, snapshot.waveform_right)

    def _apply_panel_skin(self) -> None:
        skin_id = active_skin().skin_id
        if skin_id == self._skin_id:
            return
        self._skin_id = skin_id
        for panel in (self.scope_panel, self.meter_panel, self.spectrum_panel):
            panel.apply_skin()

    def closeEvent(self, event) -> None:
        self.stop()
        super().closeEvent(event)


def _round_button(icon: str, text: str, tooltip: str):
    """
    A round JD-Xi button and its icon + text label, as on the Transport.

    :param icon: str name of a JDXi.UI.Icon constant
    :param text: str label
    :param tooltip: str
    :return: (QPushButton, QWidget label row)
    """
    from jdxi_editor.core.jdxi import JDXi

    button = create_jdxi_button(tooltip)
    pixmap = JDXi.UI.Icon.get_icon_pixmap(
        getattr(JDXi.UI.Icon, icon), color=JDXi.UI.Style.FOREGROUND, size=20
    )
    row, _label = create_jdxi_row(text, icon_pixmap=pixmap)
    row.setToolTip(tooltip)
    return button, row


def _luminance(colour: str) -> float:
    from PySide6.QtGui import QColor

    def channel(value: float) -> float:
        return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4

    c = QColor(colour)
    return (
        0.2126 * channel(c.redF()) + 0.7152 * channel(c.greenF()) + 0.0722 * channel(c.blueF())
    )


def _contrast(first: str, second: str) -> float:
    high, low = sorted((_luminance(first), _luminance(second)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def _heading_colour(skin) -> str:
    """
    The readout headings sit on the chassis's dark control surface, not on
    the faceplate. A pale skin's faceplate ink (dark) would vanish there, so
    it is used only when it reads on the surface; otherwise the display's
    colours, which are made for a dark ground, and failing those a light grey.
    """
    surface = skin.chassis.surface
    for colour in (skin.foreground.text_secondary, skin.lcd.text_dim, skin.lcd.text):
        if _contrast(colour, surface) >= 3.0:
            return colour
    return "#B4B4B0"
