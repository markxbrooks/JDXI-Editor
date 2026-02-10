from dataclasses import dataclass

from jdxi_editor.ui.widgets.spec import ComboBoxSpec, SliderSpec, SwitchSpec


@dataclass
class DigitalToneModifySpecs:
    """Digital Tone Modify"""

    interval_sens: list[SliderSpec] = None
    envelope_loop_mode: list[ComboBoxSpec] = None
    envelope_loop_sync_note: list[ComboBoxSpec] = None
    chromatic_portamento: list[SwitchSpec] = None
