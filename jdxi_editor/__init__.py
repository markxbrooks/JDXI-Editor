# Package initialization


def _debug_at_debug_level() -> None:
    """Decologr.debug() logs at INFO (it is the same function as message()):
    the 60-odd log.debug() calls here meant DEBUG. Fixed once, for every module."""
    import logging

    try:
        from decologr import Decologr
    except ImportError:  # pragma: no cover
        return
    message = Decologr.message

    def debug(*args, level: int = logging.DEBUG, stacklevel: int = 4, **kwargs):
        # called as debug("text"), debug("text", value) and debug(message="text")
        return message(*args, level=level, stacklevel=stacklevel, **kwargs)

    Decologr.debug = staticmethod(debug)

    # the successes and failures of each SysEx applied to an editor: also debug
    # (one block for every reply, and the window reads the JD-Xi every 2 s)
    def debug_info(successes, failures, stacklevel: int = 3, scope=None):
        for listing in (successes, failures):
            if "SYNTH_TONE" in listing:
                listing.remove("SYNTH_TONE")
        total = len(successes) + len(failures)
        rate = (len(successes) / total * 100) if total else 0.0
        for text in (
            f"Successes ({len(successes)}): {successes}",
            f"Failures ({len(failures)}): {failures}",
            f"Success Rate: {rate:.1f}%",
        ):
            message(text, level=logging.DEBUG, stacklevel=stacklevel, scope=scope)

    Decologr.debug_info = staticmethod(debug_info)


_debug_at_debug_level()
