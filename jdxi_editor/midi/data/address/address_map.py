"""
5. Parameter Address Map
========================

Example usage:
>>> from picomidi.core.parameter.factory import AddressFactory
>>> system_common = AddressFactory.from_str("01 00 00 00")

>>> print(PARAMETER_ADDRESS_MAP[ParameterAreas.SYSTEM][ByteGroupKind.ADDRESS_4][system_common])
AddressStartMSB.SETUP: 0x02

**Transmission of “#” marked address is divided to some packets. For
example, ABH in hexadecimal notation will be divided to 0AH and
0BH, and is sent/received in this order.
**“<*>” marked address

For reference:
JD-Xi (ModelID = 00H 00H 00H 0EH)
+------------------------------------------------------------------------------+
| Start       |                                                                |
| Address     |               Description                                      |
|-------------+----------------------------------------------------------------|
| 01 00 00 00 | Setup                                                          |
|-------------+----------------------------------------------------------------|
| 02 00 00 00 | System                                                         |
|-------------+----------------------------------------------------------------|
| 18 00 00 00 | Temporary Program                                              |
| 19 00 00 00 | Temporary Tone (Digital Synth Part 1)                          |
| 19 20 00 00 | Temporary Tone (Digital Synth Part 2)                          |
| 19 40 00 00 | Temporary Tone (Analog Synth Part)                             |
| 19 60 00 00 | Temporary Tone (Drums Part)                                    |
+------------------------------------------------------------------------------+
**System
+------------------------------------------------------------------------------+
| Offset      |                                                                |
| Offset      |                                                                |
|-------------+----------------------------------------------------------------|
|    00 00 00 | System Common                                                  |
|    00 03 00 | System Controller                                              |
+------------------------------------------------------------------------------+
**Temporary Tone
+------------------------------------------------------------------------------+
| Offset      |                                                                |
| Address     | Description                                                    |
|-------------+----------------------------------------------------------------|
|    01 00 00 | Temporary SuperNATURAL Synth Tone                              |
|    02 00 00 | Temporary Analog Synth Tone                                    |
|    10 00 00 | Temporary Drum Kit                                             |
+------------------------------------------------------------------------------+
**Program
+------------------------------------------------------------------------------+
| Offset      |                                                                |
| Address     | Description                                                    |
|-------------+----------------------------------------------------------------|
|    00 00 00 | Program Common                                                 |
|    00 01 00 | Program Vocal Effect                                           |
|    00 02 00 | Program Effect 1                                               |
|    00 04 00 | Program Effect 2                                               |
|    00 06 00 | Program Delay                                                  |
|    00 08 00 | Program Reverb                                                 |
|    00 20 00 | Program Part (Digital Synth Part 1)                            |
|    00 21 00 | Program Part (Digital Synth Part 2)                            |
|    00 22 00 | Program Part (Analog Synth Part)                               |
|    00 23 00 | Program Part (Drums Part)                                      |
|    00 30 00 | Program Zone (Digital Synth Part 1)                            |
|    00 31 00 | Program Zone (Digital Synth Part 2)                            |
|    00 32 00 | Program Zone (Analog Synth Part)                               |
|    00 33 00 | Program Zone (Drums Part)                                      |
|    00 40 00 | Program Controller                                             |
+------------------------------------------------------------------------------+
**SuperNATURAL Synth Tone
+------------------------------------------------------------------------------+
| Offset      |                                                                |
| Address     | Description                                                    |
|-------------+----------------------------------------------------------------|
|    00 00 00 | SuperNATURAL Synth Tone Common                                 |
|    00 20 00 | SuperNATURAL Synth Tone Partial (1)                            |
|    00 21 00 | SuperNATURAL Synth Tone Partial (2)                            |
|    00 22 00 | SuperNATURAL Synth Tone Partial (3)                            |
|    00 50 00 | SuperNATURAL Synth Tone Modify                                 |
+------------------------------------------------------------------------------+
**Analog Synth Tone
+------------------------------------------------------------------------------+
| Offset      |                                                                |
| Address     | Description                                                    |
|-------------+----------------------------------------------------------------|
|    00 00 00 | Analog Synth Tone                                              |
+------------------------------------------------------------------------------+
**Drum Kit
+------------------------------------------------------------------------------+
| Offset      |                                                                |
| Address     | Description                                                    |
|-------------+----------------------------------------------------------------|
|    00 00 00 | Drum Kit Common                                                |
|    00 2E 00 | Drum Kit Partial (Key # 36)                                    |
|    00 30 00 | Drum Kit Partial (Key # 37)                                    |
|        :    |                                                                |
|    00 76 00 | Drum Kit Partial (Key # 72)                                    |
+------------------------------------------------------------------------------+
"""

from picomidi.core.parameter.factory import AddressFactory
from picomidi.core.parameter.kind import ByteGroupKind

from jdxi_editor.midi.data.address.address import (
    JDXiSysExAddressStartMSB,
    JDXiSysExOffsetDrumKitLMB,
    JDXiSysExOffsetProgramLMB,
    JDXiSysExOffsetSuperNATURALLMB,
    JDXiSysExOffsetSystemLMB,
    JDXiSysExOffsetTemporaryToneUMB,
)
from jdxi_editor.midi.data.parameter.address.name import (
    ParameterAddressName as AddressName,
)
from jdxi_editor.midi.data.parameter.address.table import (
    PARAMETER_ADDRESS_TABLE as ADDRESSES,
)
from jdxi_editor.midi.data.parameter.address.table import (
    parameter_address_table,
)
from jdxi_editor.midi.data.parameter.areas.name import ParameterAreas
from jdxi_editor.midi.data.parameter.offset.name import (
    ParameterOffsetName as OffsetName,
)
from jdxi_editor.midi.data.parameter.offset.table import (
    PARAMETER_OFFSET_TABLE as OFFSETS,
)
from jdxi_editor.midi.data.parameter.offset.table import (
    parameter_offset_table,
)

parameter_address_map = {}
parameter_offset_map = {}

for param, address in parameter_address_table:
    print(f"{param}: {address}")
    parameter_address_map[param] = AddressFactory.from_str(address)
    print(f"{param}: {parameter_address_map[param]}")

for param, offset in parameter_offset_table:
    print(f"{param}: {offset}")
    parameter_offset_map[param] = AddressFactory.from_str(offset)
    print(f"{param}: {parameter_offset_map[param]}")

PARAMETER_ADDRESS_MAP = {
    ParameterAreas.SYSTEM: {
        ByteGroupKind.ADDRESS_4: {
            ADDRESSES[AddressName.SETUP]: JDXiSysExAddressStartMSB.SETUP,  # "Setup",
            ADDRESSES[AddressName.SYSTEM]: JDXiSysExAddressStartMSB.SYSTEM,  # "System"
        },
        ByteGroupKind.OFFSET_3: {
            OFFSETS[
                OffsetName.SYSTEM_COMMON
            ]: JDXiSysExOffsetSystemLMB.COMMON,  # "System Common",
            OFFSETS[
                OffsetName.SYSTEM_CONTROLLER
            ]: JDXiSysExOffsetSystemLMB.CONTROLLER,  # "System Controller"
        },
    },
    ParameterAreas.TEMPORARY_TONE: {
        ByteGroupKind.ADDRESS_4: {
            ADDRESSES[
                AddressName.TEMPORARY_PROGRAM
            ]: JDXiSysExAddressStartMSB.TEMPORARY_PROGRAM,  # Temporary Program
            ADDRESSES[
                AddressName.TEMPORARY_TONE_DIGITAL1
            ]: JDXiSysExOffsetTemporaryToneUMB.DIGITAL_SYNTH_1,
            # "Temporary Tone (Digital Synth Part 1)",
            ADDRESSES[
                AddressName.TEMPORARY_TONE_DIGITAL2
            ]: JDXiSysExOffsetTemporaryToneUMB.DIGITAL_SYNTH_2,
            # "Temporary Tone (Digital Synth Part 2)",
            ADDRESSES[
                AddressName.TEMPORARY_TONE_ANALOG
            ]: JDXiSysExOffsetTemporaryToneUMB.ANALOG_SYNTH,
            # "Temporary Tone (Analog Synth Part)",
            ADDRESSES[
                AddressName.TEMPORARY_DRUM_KIT
            ]: JDXiSysExOffsetTemporaryToneUMB.DRUM_KIT,  # "Temporary Tone (Drums Part)"
        },
        ByteGroupKind.OFFSET_3: {
            OFFSETS[
                OffsetName.TEMPORARY_SUPERNATURAL_SYNTH_TONE
            ]: JDXiSysExOffsetTemporaryToneUMB.DIGITAL_SYNTH_1,  # "Temporary SuperNATURAL Synth Tone",
            OFFSETS[
                OffsetName.TEMPORARY_ANALOG_SYNTH_TONE
            ]: JDXiSysExOffsetTemporaryToneUMB.ANALOG_SYNTH,  #  "Temporary Analog Synth Tone",
            OFFSETS[
                OffsetName.TEMPORARY_DRUM_KIT
            ]: JDXiSysExOffsetTemporaryToneUMB.DRUM_KIT,  #  "Temporary Drum Kit"
        },
    },
    ParameterAreas.PROGRAM: {
        ByteGroupKind.OFFSET_3: {
            OFFSETS[
                OffsetName.PROGRAM_COMMON
            ]: JDXiSysExOffsetProgramLMB.COMMON,  # "Program Common",
            OFFSETS[
                OffsetName.PROGRAM_VOCAL_EFFECT
            ]: JDXiSysExOffsetProgramLMB.VOCAL_EFFECT,  # "Program Vocal Effect",
            OFFSETS[
                OffsetName.PROGRAM_EFFECT_1
            ]: JDXiSysExOffsetProgramLMB.EFFECT_1,  # "Program Effect 1",
            OFFSETS[
                OffsetName.PROGRAM_EFFECT_2
            ]: JDXiSysExOffsetProgramLMB.EFFECT_2,  # "Program Effect 2",
            OFFSETS[
                OffsetName.PROGRAM_DELAY
            ]: JDXiSysExOffsetProgramLMB.DELAY,  # "Program Delay",
            OFFSETS[
                OffsetName.PROGRAM_REVERB
            ]: JDXiSysExOffsetProgramLMB.REVERB,  # "Program Reverb",
            OFFSETS[
                OffsetName.PROGRAM_PART_DIGITAL1
            ]: JDXiSysExOffsetProgramLMB.PART_DIGITAL_SYNTH_1,  # "Program Part (Digital Synth Part 1)",
            OFFSETS[
                OffsetName.PROGRAM_PART_DIGITAL2
            ]: JDXiSysExOffsetProgramLMB.PART_DIGITAL_SYNTH_2,  # "Program Part (Digital Synth Part 2)",
            OFFSETS[
                OffsetName.PROGRAM_PART_ANALOG
            ]: JDXiSysExOffsetProgramLMB.PART_ANALOG,  # "Program Part (Analog Synth Part)",
            OFFSETS[
                OffsetName.PROGRAM_PART_DRUMS
            ]: JDXiSysExOffsetProgramLMB.PART_DRUM,  # "Program Part (Drums Part)",
            OFFSETS[
                OffsetName.PROGRAM_ZONE_DIGITAL1
            ]: JDXiSysExOffsetProgramLMB.ZONE_DIGITAL_SYNTH_1,  # "Program Zone (Digital Synth Part 1)",
            OFFSETS[
                OffsetName.PROGRAM_ZONE_DIGITAL2
            ]: JDXiSysExOffsetProgramLMB.ZONE_DIGITAL_SYNTH_2,  # "Program Zone (Digital Synth Part 2)",
            OFFSETS[
                OffsetName.PROGRAM_ZONE_ANALOG
            ]: JDXiSysExOffsetProgramLMB.ZONE_ANALOG,  # "Program Zone (Analog Synth Part)",
            OFFSETS[
                OffsetName.PROGRAM_ZONE_DRUMS
            ]: JDXiSysExOffsetProgramLMB.ZONE_DRUM,  # "Program Zone (Drums Part)",
            OFFSETS[
                OffsetName.PROGRAM_CONTROLLER
            ]: JDXiSysExOffsetProgramLMB.CONTROLLER,
        }
    },
    ParameterAreas.SUPERNATURAL_SYNTH_TONE: {
        ByteGroupKind.OFFSET_3: {
            OFFSETS[
                OffsetName.SUPERNATURAL_SYNTH_TONE_COMMON
            ]: JDXiSysExOffsetSuperNATURALLMB.COMMON,  # "SuperNATURAL Synth Tone Common",
            OFFSETS[
                OffsetName.SUPERNATURAL_SYNTH_TONE_PARTIAL1
            ]: JDXiSysExOffsetSuperNATURALLMB.PARTIAL_1,  # "SuperNATURAL Synth Tone Partial (1)",
            OFFSETS[
                OffsetName.SUPERNATURAL_SYNTH_TONE_PARTIAL2
            ]: JDXiSysExOffsetSuperNATURALLMB.PARTIAL_2,  # "SuperNATURAL Synth Tone Partial (2)",
            OFFSETS[
                OffsetName.SUPERNATURAL_SYNTH_TONE_PARTIAL3
            ]: JDXiSysExOffsetSuperNATURALLMB.PARTIAL_3,  # "SuperNATURAL Synth Tone Partial (3)",
            OFFSETS[
                OffsetName.SUPERNATURAL_SYNTH_TONE_MODIFY
            ]: JDXiSysExOffsetSuperNATURALLMB.MODIFY,  # "SuperNATURAL Synth Tone Modify"
        }
    },
    ParameterAreas.ANALOG_SYNTH_TONE: {
        ByteGroupKind.OFFSET_3: {
            OFFSETS[
                OffsetName.ANALOG_SYNTH_TONE
            ]: JDXiSysExOffsetProgramLMB.COMMON  # "Analog Synth Tone"
        }
    },
    ParameterAreas.DRUM_KIT: {
        ByteGroupKind.OFFSET_3: {
            OFFSETS[
                OffsetName.DRUM_KIT_COMMON
            ]: JDXiSysExOffsetDrumKitLMB.COMMON,  # "Drum Kit Common",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL1
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_1,  # "Drum Kit Partial (Key # 36)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL2
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_2,  # "Drum Kit Partial (Key # 37)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL3
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_3,  # "Drum Kit Partial (Key # 38)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL4
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_4,  # "Drum Kit Partial (Key # 39)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL5
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_5,  # "Drum Kit Partial (Key # 40)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL6
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_6,  # "Drum Kit Partial (Key # 41)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL7
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_7,  # "Drum Kit Partial (Key # 42)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL8
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_8,  # "Drum Kit Partial (Key # 43)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL9
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_9,  # "Drum Kit Partial (Key # 44)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL10
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_10,  # "Drum Kit Partial (Key # 45)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL11
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_11,  # "Drum Kit Partial (Key # 46)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL12
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_12,  # "Drum Kit Partial (Key # 47)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL13
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_13,  # "Drum Kit Partial (Key # 48)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL14
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_14,  # "Drum Kit Partial (Key # 49)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL15
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_15,  # "Drum Kit Partial (Key # 50)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL16
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_16,  # "Drum Kit Partial (Key # 51)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL17
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_17,  # "Drum Kit Partial (Key # 52)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL18
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_18,  # "Drum Kit Partial (Key # 53)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL19
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_19,  # "Drum Kit Partial (Key # 54)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL20
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_20,  # "Drum Kit Partial (Key # 55)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL21
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_21,  # "Drum Kit Partial (Key # 56)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL22
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_22,  # "Drum Kit Partial (Key # 57)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL23
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_23,  # "Drum Kit Partial (Key # 58)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL24
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_24,  # "Drum Kit Partial (Key # 59)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL25
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_25,  # "Drum Kit Partial (Key # 60)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL26
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_26,  # "Drum Kit Partial (Key # 61)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL27
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_27,  # "Drum Kit Partial (Key # 62)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL28
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_28,  # "Drum Kit Partial (Key # 63)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL29
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_29,  # "Drum Kit Partial (Key # 64)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL30
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_30,  # "Drum Kit Partial (Key # 65)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL31
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_31,  # "Drum Kit Partial (Key # 66)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL32
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_32,  # "Drum Kit Partial (Key # 67)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL33
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_33,  # "Drum Kit Partial (Key # 68)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL34
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_34,  # "Drum Kit Partial (Key # 69)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL35
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_35,  # "Drum Kit Partial (Key # 70)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL36
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_36,  # "Drum Kit Partial (Key # 71)",
            OFFSETS[
                OffsetName.DRUM_KIT_PARTIAL37
            ]: JDXiSysExOffsetDrumKitLMB.DRUM_KIT_PART_37,  # "Drum Kit Partial (Key # 72)"
        }
    },
}
