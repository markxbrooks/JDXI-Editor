"""
Starting without a MIDI backend.

python-rtmidi raises from ``MidiIn()`` / ``MidiOut()`` when it cannot reach
the platform's MIDI service at all. On Linux that is whenever ``/dev/snd/seq``
is missing, because the kernel's ``snd-seq`` module is not loaded -- the
normal state in a container, on a minimal install, and on a CI runner, where
it reads:

    MidiInAlsa::initialize: error creating ALSA sequencer client object

An unguarded construction makes that fatal: the editor cannot be built at
all, and the user is shown a traceback rather than a message. But the editor
is useful without a JD-Xi attached, and already opens its MIDI configuration
dialog when it finds no ports, so an absent backend should look like "no
ports" rather than a crash.

:class:`NoMidiBackend` answers every method the editor calls on a port, so
callers need no special case and nothing has to tolerate ``None``. rtmidi's
own dummy API would have done this, but the published wheels are not built
with it: ``get_compiled_api()`` offers only the platform's real backend.
"""

from __future__ import annotations

from decologr import Decologr as log


class NoMidiBackend:
    """A MIDI port that is always closed and has nothing to offer."""

    def get_ports(self) -> list:
        return []

    def open_port(self, *_args, **_kwargs) -> None:
        return None

    def close_port(self) -> None:
        return None

    def is_port_open(self) -> bool:
        return False

    def set_callback(self, *_args, **_kwargs) -> None:
        return None

    def cancel_callback(self) -> None:
        return None

    def ignore_types(self, *_args, **_kwargs) -> None:
        return None

    def send_message(self, *_args, **_kwargs) -> None:
        return None


def open_rtmidi(factory, kind: str):
    """
    Build an rtmidi port, or a stand-in when there is no MIDI backend.

    :param factory: ``rtmidi.MidiIn`` or ``rtmidi.MidiOut``
    :param kind: str what the port is for, for the log line
    :return: the rtmidi port, or :class:`NoMidiBackend`
    """
    try:
        return factory()
    except Exception as ex:  # rtmidi raises its own SystemError here
        log.warning(
            scope="MIDI",
            message=(
                f"No MIDI {kind} backend ({ex}). Starting without MIDI: no "
                f"ports will be listed. On Linux, load the kernel sequencer "
                f"with 'sudo modprobe snd-seq'."
            ),
        )
        return NoMidiBackend()
