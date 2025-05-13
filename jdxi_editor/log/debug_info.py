from jdxi_editor.log.message import log_message


def log_debug_info(successes: list, failures: list) -> None:
    """
    Logs debug information about the parsed SysEx data.

    :param successes: list – Parameters successfully decoded.
    :param failures: list – Parameters that failed decoding.
    """
    for listing in [successes, failures]:
        try:
            listing.remove("SYNTH_TONE")
        except ValueError:
            pass  # or handle the error

    total = len(successes) + len(failures)
    success_rate = (len(successes) / total * 100) if total else 0.0

    log_message(f"Successes ({len(successes)}): {successes}", stacklevel=3)
    log_message(f"Failures ({len(failures)}): {failures}", stacklevel=3)
    log_message(f"Success Rate: {success_rate:.1f}%", stacklevel=3)
    log_message("=" * 100, stacklevel=3)
