"""
Helpers
"""

from typing import Literal

from PySide6.QtGui import QIcon

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.analog.oscillator import AnalogWaveOsc
from jdxi_editor.ui.image.utils import base64_to_pixmap
from jdxi_editor.ui.image.waveform import generate_waveform_icon
from jdxi_editor.ui.widgets.button.waveform.analog import AnalogWaveformButton


def generate_analog_wave_button(
    icon_name: str,
    waveform: Literal[AnalogWaveOsc.PULSE, AnalogWaveOsc.TRIANGLE, AnalogWaveOsc.SAW],
) -> AnalogWaveformButton:
    """generate analog wave button"""
    btn = AnalogWaveformButton(waveform)
    # AnalogWaveformButton already sets BUTTON_WAVEFORM_ANALOG style with blue border
    # No need to override with BUTTON_RECT_ANALOG
    icon_base64 = generate_waveform_icon(icon_name, JDXi.UI.Style.WHITE, 0.7)
    btn.setIcon(QIcon(base64_to_pixmap(icon_base64)))
    btn.setFixedSize(
        JDXi.UI.Dimensions.WAVEFORM_ICON.WIDTH,
        JDXi.UI.Dimensions.WAVEFORM_ICON.HEIGHT,
    )
    return btn


def generate_analog_waveform_icon_name(waveform: AnalogWaveOsc) -> str:
    """generate analog waveform icon name"""
    # --- Set icons
    icon_name = (
        "upsaw"
        if waveform == AnalogWaveOsc.SAW
        else "triangle" if waveform == AnalogWaveOsc.TRIANGLE else "pwsqu"
    )
    return icon_name
