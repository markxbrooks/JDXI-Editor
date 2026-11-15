"""
Filter remote control
=====================

Moves the filter controls of the open synth editor from a hardware
controller's knobs and faders. Each value moves the editor's own slider, so
the slider, its spin box and envelope plot update and the editor sends the
parameter to the JD-Xi exactly as if the slider had been dragged.

The target is the Digital Synth editor's selected partial or the Analog Synth
editor, whichever tab is showing; on any other tab the last synth editor shown
keeps receiving.
"""

from __future__ import annotations

from typing import Callable, Optional

from decologr import Decologr as log
from PySide6.QtWidgets import QWidget

from jdxi_editor.midi.io.controller_map import MINILAB3_FILTER_MAP, FilterControl
from jdxi_editor.ui.widgets.slider.slider import Slider

MIDI_MAX = 127


def controls_for_editor(editor: Optional[QWidget]) -> Optional[dict]:
    """
    Parameter -> widget controls that the filter remote drives in ``editor``.

    :param editor: Optional[QWidget] a tab of the main editor
    :return: Optional[dict] the Digital editor's selected partial's controls, the
        Analog editor's controls, or None for any other widget
    """
    from jdxi_editor.ui.editors.analog.editor import AnalogSynthEditor
    from jdxi_editor.ui.editors.digital.editor import DigitalSynthEditor

    if isinstance(editor, DigitalSynthEditor):
        panel = editor._current_partial_panel()
        return panel.all_controls() if panel is not None else None
    if isinstance(editor, AnalogSynthEditor):
        return editor.all_controls()
    return None


def slider_for(controls: dict, control: FilterControl) -> Optional[Slider]:
    """
    The :class:`Slider` that sets ``control`` among ``controls``.

    Cutoff and the envelope stages are composite widgets holding a ``slider``.

    :param controls: dict AddressParameter -> widget
    :param control: FilterControl
    :return: Optional[Slider]
    """
    widget = next(
        (w for param, w in controls.items() if param.name == control.value), None
    )
    if isinstance(widget, Slider):
        return widget
    inner = getattr(widget, "slider", None)
    return inner if isinstance(inner, Slider) else None


def scale_to_slider(slider: Slider, midi_value: int) -> int:
    """
    Map a 0-127 controller value onto the slider's whole range.

    :param slider: Slider
    :param midi_value: int 0-127
    :return: int slider value
    """
    low, high = slider.slider.minimum(), slider.slider.maximum()
    return low + round(max(0, min(MIDI_MAX, midi_value)) * (high - low) / MIDI_MAX)


class FilterRemote:
    """Applies controller CCs to the open synth editor's filter."""

    def __init__(
        self,
        current_editor: Callable[[], Optional[QWidget]],
        cc_map: Optional[dict[int, FilterControl]] = None,
        channel: Optional[int] = None,
    ) -> None:
        """
        :param current_editor: Callable returning the main editor's current tab
        :param cc_map: dict CC number -> FilterControl; defaults to the MiniLab 3 map
        :param channel: Optional[int] only accept this MIDI channel (0-15); None accepts all
        """
        self.current_editor = current_editor
        self.cc_map = dict(MINILAB3_FILTER_MAP if cc_map is None else cc_map)
        self.channel = channel
        self._last_editor: Optional[QWidget] = None

    def target_controls(self) -> Optional[dict]:
        """
        Controls of the editor that receives controller moves.

        :return: Optional[dict] AddressParameter -> widget, or None if no synth editor is open
        """
        editor = self.current_editor()
        controls = controls_for_editor(editor)
        if controls is not None:
            self._last_editor = editor
            return controls
        try:
            return controls_for_editor(self._last_editor)
        except RuntimeError:  # the last editor's tab was closed
            self._last_editor = None
            return None

    def on_control_change(self, channel: int, control: int, value: int) -> bool:
        """
        Move the filter slider mapped to ``control``.

        :param channel: int MIDI channel 0-15
        :param control: int CC number
        :param value: int CC value 0-127
        :return: bool True if a slider was moved
        """
        if self.channel is not None and channel != self.channel:
            return False
        filter_control = self.cc_map.get(control)
        if filter_control is None:
            return False
        controls = self.target_controls()
        if controls is None:
            log.message(
                f"CC{control} ({filter_control.name}): open a Digital or Analog Synth editor",
                scope=self.__class__.__name__,
                silent=True,
            )
            return False
        slider = slider_for(controls, filter_control)
        if slider is None:
            return False
        target = scale_to_slider(slider, value)
        if slider.value() != target:
            slider.setValue(target)  # sends the parameter through the editor
        return True
