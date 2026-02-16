from dataclasses import dataclass
from typing import Optional, Any

from jdxi_editor.ui.widgets.envelope.parameter import EnvelopeParameter
from picomidi.sysex.parameter.address import AddressParameter


@dataclass
class EnvControlSpec:
    param: AddressParameter
    env_param: str   # ← REQUIRED
    label: str
    min_value: int = 0
    max_value: int = 5000
    default_value: int = 0
    units: str = " ms"
    enabled: bool = True
