"""log.debug() logs at DEBUG (Decologr's own debug is message(), at INFO)."""

import logging

import jdxi_editor  # noqa: F401  (installs the DEBUG-level log.debug)
from decologr import Decologr as log


def test_debug_logs_at_debug_level(monkeypatch):
    calls = []
    import decologr

    real = log.message
    monkeypatch.setattr(
        decologr.Decologr,
        "message",
        staticmethod(lambda *a, **k: calls.append(k.get("level"))),
    )
    jdxi_editor._debug_at_debug_level()
    try:
        log.debug("text")
        log.debug("text", 1)
        log.debug(message="text", scope="test")
    finally:
        monkeypatch.setattr(decologr.Decologr, "message", staticmethod(real))
        jdxi_editor._debug_at_debug_level()
    assert calls == [logging.DEBUG] * 3
