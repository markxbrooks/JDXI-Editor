import logging

from jdxi_editor.globals import logger, LOGGING
from jdxi_editor.log.emoji import LEVEL_EMOJIS
from jdxi_editor.midi.data.address.address import AddressOffsetTemporaryToneUMB, AddressOffsetSuperNATURALLMB
from jdxi_editor.midi.data.parameter.synth import AddressParameter
from jdxi_editor.ui.windows.midi.debugger import parse_sysex_byte


def log_slider_parameters(umb: int,
                          lmb: int,
                          param: AddressParameter,
                          value: int,
                          slider_value: int,
                          level: int = logging.INFO):
    """Log slider parameters for debugging."""
    synth_umb = f"0x{int(umb):02X}"
    part_lmb = f"0x{int(lmb):02X}"

    synth_name_umb = parse_sysex_byte(int(synth_umb, 16), AddressOffsetTemporaryToneUMB)
    if part_lmb != "0x00":
        part_name_lmb = parse_sysex_byte(int(part_lmb, 16), AddressOffsetSuperNATURALLMB)
    else:
        part_name_lmb = "COMMON"

    message = (
        f"Updating synth umb {synth_umb:<2} \t {synth_name_umb:<20} "
        f"part lmb {part_lmb:<2} \t {part_name_lmb:<20} "
        f"{param.name:<30} "
        f"MIDI {value:<4} -> Slider {slider_value}"
    )

    emoji = LEVEL_EMOJIS.get(level, "🔔")

    # Add MIDI flair if message seems MIDI-related
    midi_tag = "🎵" if "midi" in message.lower() or "sysex" in message.lower() else ""
    qc_passed_tag = "✅" if "updat" in message.lower() else ""
    message = f"{emoji} {qc_passed_tag} {midi_tag} {message}"
    if LOGGING:
        if level == logging.DEBUG:
            logger.debug(message, stacklevel=2)
        elif level == logging.INFO:
            logger.info(message, stacklevel=2)
        elif level == logging.WARNING:
            logger.warning(message, stacklevel=2)
        elif level == logging.ERROR:
            logger.error(message, stacklevel=2)
        elif level == logging.CRITICAL:
            logger.critical(message, stacklevel=2)
        else:
            # fallback for non-standard levels
            logger.log(message, stacklevel=2)
