"""
Rack panel
==========

A container that paints a faceplate behind whatever it is given, in the style
of a rack-mounted synth. The widget is picoui's
:class:`~picoui.skin.widgets.RackPanel`; importing it from here also sets up
the editor's skins (:data:`jdxi_editor.ui.style.rack_skin.REGISTRY`), which
it follows unless pinned::

    panel = RackPanel(my_controls)                     # follows the setting
    panel = RackPanel(my_controls, skin="jdxi_rack")   # ears, screws, stripe
"""

import jdxi_editor.ui.style.rack_skin  # noqa: F401  registers the editor's skins
from picoui.skin.widgets import RackPanel

__all__ = ["RackPanel"]
