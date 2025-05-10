from jdxi_editor.log.message import log_message


def log_debug_info(data: dict, successes: list, failures: list) -> None:
    """
    Logs debug information about the parsed SysEx data.

    :param data: dict – Parsed SysEx data.
    :param successes: list – Parameters successfully decoded.
    :param failures: list – Parameters that failed decoding.
    """
    total = len(successes) + len(failures)
    success_rate = (len(successes) / total * 100) if total else 0.0

    log_message(f"✅ Successes ({len(successes)}): {successes}")
    log_message(f"❌ Failures ({len(failures)}): {failures}")
    log_message(f"📊 Success Rate: {success_rate:.1f}%")
    log_message("=" * 100)
