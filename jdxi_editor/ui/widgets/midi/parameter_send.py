"""
Send a control-change or NRPN value the way the faceplate knobs and the
editor sliders both do.

The map is partial number to CC number, or to NRPN LSB. Partial 1, 2, and 3
are sent on every change, which is what the performance controls have always
done.
"""

from typing import Iterable, Mapping


def send_control_change_map(
    midi_helper,
    nrpn_map: Mapping,
    value: int,
    channels: Iterable[int],
) -> None:
    """
    Send one control-change value for every partial in the map.

    :param midi_helper: MidiIOHelper
    :param nrpn_map: dict partial number to control-change number
    :param value: int 0–127
    :param channels: MIDI channels to send on
    """
    for partial in (1, 2, 3):
        cc_number = nrpn_map.get(partial)
        if cc_number is None:
            raise ValueError("Invalid partial number")
        for channel in channels:
            midi_helper.send_control_change(cc_number, value, channel=channel)


def send_nrpn_map(
    midi_helper,
    nrpn_map: Mapping,
    value: int,
    nrpn_msb: int,
    param_type: str,
    channels: Iterable[int] = (0, 1, 2),
) -> None:
    """
    Send one NRPN or RPN value for every partial in the map.

    :param midi_helper: MidiIOHelper
    :param nrpn_map: dict partial number to parameter LSB
    :param value: int
    :param nrpn_msb: int parameter MSB
    :param param_type: str "nrpn" or "rpn"
    :param channels: MIDI channels to send on
    """
    for partial in (1, 2, 3):
        param_lsb = nrpn_map.get(partial)
        if param_lsb is None:
            raise ValueError(f"Invalid partial number: {partial}")
        parameter = (nrpn_msb << 7) | param_lsb
        for channel in channels:
            if param_type == "nrpn":
                midi_helper.send_nrpn(parameter=parameter, value=value, channel=channel)
            elif param_type == "rpn":
                midi_helper.send_rpn(parameter=parameter, value=value, channel=channel)
            else:
                raise ValueError(f"Unsupported parameter type: {param_type}")
