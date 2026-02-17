from dataclasses import dataclass
from typing import Any, Optional

from picomidi.sysex.parameter.address import AddressParameter

from jdxi_editor.ui.widgets.envelope.parameter import EnvelopeParameter


@dataclass
class EnvControlSpec:
    param: AddressParameter
    env_param: str  # ← REQUIRED
    label: str
    min_value: int = 0
    max_value: int = 5000
    default_value: int = 0
    units: str = " ms"
    enabled: bool = True
