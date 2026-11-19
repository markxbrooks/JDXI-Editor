"""
Rack ears
=========

The active skin's rack ears at each end of a horizontal strip: the upper and
lower bands of the MIDI player, where a full RackPanel would paint a second
faceplate behind one that is already there. The widget is picoui's
:class:`~picoui.skin.widgets.RackEars`, following the editor's skins.
"""

import jdxi_editor.ui.style.rack_skin  # noqa: F401  registers the editor's skins
from picoui.skin.widgets import RackEars

__all__ = ["RackEars"]
