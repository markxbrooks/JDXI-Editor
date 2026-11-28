"""
macOS: tell the system that the app is doing latency-critical work.

macOS throttles the timers of an app it thinks is idle (App Nap, timer
coalescing): a timed wait ends late, by tens of milliseconds — notes of a
MIDI file or a pattern off their beat, a reading's timeouts reached early.
While playing, the editor holds an NSProcessInfo activity "user initiated,
latency critical", as audio and MIDI applications do; Windows has
timeBeginPeriod for the same purpose. Elsewhere, and if anything goes wrong,
nothing happens.

Done through the Objective-C runtime with ctypes (no PyObjC needed).
objc_msgSend is called with the exact prototype of each method: on Apple
silicon it must not be called as a variadic function.
"""

from __future__ import annotations

import ctypes
import ctypes.util
import sys
from typing import Optional

# NSActivityOptions
USER_INITIATED = 0x00FFFFFF
LATENCY_CRITICAL = 0xFF00000000
OPTIONS = USER_INITIATED | LATENCY_CRITICAL

_runtime = None


def _objc():
    global _runtime
    if _runtime is None:
        objc = ctypes.cdll.LoadLibrary(ctypes.util.find_library("objc"))
        ctypes.cdll.LoadLibrary(ctypes.util.find_library("Foundation"))  # NSProcessInfo, NSString
        objc.objc_getClass.restype = ctypes.c_void_p
        objc.objc_getClass.argtypes = [ctypes.c_char_p]
        objc.sel_registerName.restype = ctypes.c_void_p
        objc.sel_registerName.argtypes = [ctypes.c_char_p]
        _runtime = objc
    return _runtime


def _send(restype, *argtypes):
    """objc_msgSend with this prototype: (receiver, selector, *argtypes) -> restype."""
    prototype = ctypes.CFUNCTYPE(restype, ctypes.c_void_p, ctypes.c_void_p, *argtypes)
    return prototype(("objc_msgSend", _objc()))


def _sel(name: str):
    return _objc().sel_registerName(name.encode())


def begin(reason: str) -> Optional[int]:
    """Start the activity; its token (to give to end()), or None if not on macOS or not possible."""
    if sys.platform != "darwin":
        return None
    try:
        objc = _objc()
        process_info = _send(ctypes.c_void_p)(objc.objc_getClass(b"NSProcessInfo"), _sel("processInfo"))
        cf = ctypes.cdll.LoadLibrary(ctypes.util.find_library("CoreFoundation"))
        cf.CFStringCreateWithCString.restype = ctypes.c_void_p
        cf.CFStringCreateWithCString.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint32]
        # an owned CFString (toll-free bridged to NSString): no autorelease pool needed
        text = cf.CFStringCreateWithCString(None, reason.encode(), 0x08000100)  # kCFStringEncodingUTF8
        activity = _send(ctypes.c_void_p, ctypes.c_uint64, ctypes.c_void_p)(
            process_info, _sel("beginActivityWithOptions:reason:"), OPTIONS, text)
        if not activity:
            return None
        _send(ctypes.c_void_p)(activity, _sel("retain"))  # ours until end(): not left to an autorelease pool
        return activity
    except Exception:  # an older system, no runtime: the timers stay as they are
        return None


def end(token: Optional[int]) -> None:
    """End the activity begun with begin()."""
    if not token or sys.platform != "darwin":
        return
    try:
        process_info = _send(ctypes.c_void_p)(_objc().objc_getClass(b"NSProcessInfo"), _sel("processInfo"))
        _send(None, ctypes.c_void_p)(process_info, _sel("endActivity:"), token)
        _send(None)(token, _sel("release"))
    except Exception:
        pass
