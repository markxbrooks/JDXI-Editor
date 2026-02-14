from typing import Callable, Optional

from picomidi.sysex.parameter.address import AddressParameter
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy, QPushButton

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import JDXiSysExAddress
from jdxi_editor.ui.style.dimensions import JDXiUIDimensions
from jdxi_editor.ui.style.factory import generate_sequencer_button_style


class ChannelStrip(QWidget):
    """Single mixer channel strip with level slider and MIDI-enabled mute button."""

    muteToggled = Signal(bool)

    def __init__(
        self,
        title: str,
        slider: QWidget | None,
        value_label: QLabel | None,
        icon: QLabel | None,
        param: Optional[AddressParameter] = None,
        address: Optional[JDXiSysExAddress] = None,
        send_midi_callback: Optional[
            Callable[[AddressParameter, int, JDXiSysExAddress], bool]
        ] = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self._slider = slider
        self._param = param
        self._address = address
        self._send_midi = send_midi_callback
        self._previous_slider_value: int | None = None

        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(4, 4, 4, 4)

        center = Qt.AlignmentFlag.AlignHCenter

        self.title = QLabel(title)
        self.title.setAlignment(Qt.AlignCenter)
        # layout.addWidget(self.title, 0, center) Another title is superfluous

        if slider:
            slider.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            layout.addWidget(slider, 1, center)

        if value_label:
            value_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(value_label, 0, center)

        if icon:
            icon.setAlignment(Qt.AlignCenter)
            layout.addWidget(icon, 0, center)

        self.mute = QPushButton()
        mute_icon = JDXi.UI.Icon.get_icon(
            JDXi.UI.Icon.MUTE, color=JDXi.UI.Style.FOREGROUND
        )
        self.mute.setIcon(mute_icon)
        self.mute.setIconSize(QSize(18, 18))
        self.mute.setCheckable(True)
        self.mute.setFixedWidth(JDXiUIDimensions.SEQUENCER.SQUARE_SIZE)
        self.mute.setFixedHeight(JDXiUIDimensions.SEQUENCER.SQUARE_SIZE)
        self.mute.setToolTip(f"Mute {title} channel")
        self._update_mute_button_style(self.mute.isChecked())

        self.mute.toggled.connect(self._on_mute_toggled)

        layout.addWidget(self.mute, 0, center)

    def _update_mute_button_style(self, is_muted: bool) -> None:
        """Apply JD-Xi sequencer-style visual for mute toggle."""
        self.mute.setStyleSheet(generate_sequencer_button_style(not is_muted))

    def _on_mute_toggled(self, checked: bool) -> None:
        """Handle mute toggling: send MIDI 0 when muted, restore stored value when unmuted."""
        self._update_mute_button_style(checked)
        self.muteToggled.emit(checked)

        if (
            not self._slider
            or not self._param
            or not self._address
            or not self._send_midi
        ):
            return

        try:
            if checked:
                # Store current slider value (only once when muting)
                if self._previous_slider_value is None:
                    self._previous_slider_value = self._slider.value()

                # Send MIDI value 0 to mute the channel
                self._send_midi(self._param, 0, self._address)

                # Disable slider to prevent user changes while muted
                self._slider.setEnabled(False)
            else:
                # Restore previous slider value and re-enable slider
                if self._previous_slider_value is not None:
                    # Re-send the stored MIDI value to unmute
                    self._send_midi(
                        self._param, self._previous_slider_value, self._address
                    )
                    self._previous_slider_value = None

                self._slider.setEnabled(True)
        except Exception:
            # Fail silently if slider doesn't support value interface or MIDI send fails
            pass
