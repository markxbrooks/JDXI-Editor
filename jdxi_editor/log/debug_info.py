"""
Log Debug info
"""

from decologr import Decologr as log


def log_debug_info(successes: list[str], failures: list[str]) -> None:
    """
    Logs debug information about the parsed SysEx data.

    :param successes: list[str] – Parameters successfully decoded.
    :param failures: list[str] – Parameters that failed decoding.
    """
    for listing in [successes, failures]:
        try:
            listing.remove("SYNTH_TONE")
        except ValueError:
            pass  # or handle the error

    total = len(successes) + len(failures)
    success_rate = (len(successes) / total * 100) if total else 0.0

    log.message(f"Successes ({len(successes)}): {successes}", stacklevel=3)
    log.message(f"Failures ({len(failures)}): {failures}", stacklevel=3)
    log.message(f"Success Rate: {success_rate:.1f}%", stacklevel=3)
    log.message("=" * 100, stacklevel=3)
