"""
5. Parameter Address Map
========================

Example usage:
>>> system_common = ParameterAddress.from_str("01 00 00 00")

>>> print(PARAMETER_ADDRESS_MAP[ParameterAreas.SYSTEM][BYTE_GROUPS_4][system_common])
SETUP

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

from jdxi_editor.midi.data.address.address import (
    AddressOffsetDrumKitLMB,
    AddressOffsetProgramLMB,
    AddressOffsetSuperNATURALLMB,
    AddressOffsetSystemLMB,
    AddressOffsetTemporaryToneUMB,
    AddressStartMSB,
)
from jdxi_editor.midi.data.parameter.address.name import ParameterAddressName
from jdxi_editor.midi.data.parameter.address.table import parameter_address_table, PARAMETER_ADDRESS_TABLE
from jdxi_editor.midi.data.parameter.areas.name import ParameterAreas
from jdxi_editor.midi.data.parameter.offset.name import ParameterOffsetName
from jdxi_editor.midi.data.parameter.offset.table import parameter_offset_table, PARAMETER_OFFSET_TABLE
from picomidi.core.parameter.address import ParameterAddress
from picomidi.core.parameter.factory import AddressFactory

BYTE_GROUPS_4 = "4-byte-addresses"
BYTE_GROUPS_3 = "3-byte-offsets"

parameter_address_map = {}
parameter_offset_map = {}

for param, address in parameter_address_table:
    print(f"{param.name}: {address}")
    parameter_address_map[param.name] = AddressFactory.from_str(address)
    print(f"{param.name}: {parameter_address_map[param.name]}")

for param, offset in parameter_offset_table:
    print(f"{param.name}: {offset}")
    parameter_offset_map[param.name] = AddressFactory.from_str(offset)
    print(f"{param.name}: {parameter_offset_map[param.name]}")

PARAMETER_ADDRESS_MAP = {
    ParameterAreas.SYSTEM: {
        BYTE_GROUPS_4: {
            PARAMETER_ADDRESS_TABLE[ParameterAddressName.SETUP]: AddressStartMSB.SETUP.name,  # "Setup",
            PARAMETER_ADDRESS_TABLE[ParameterAddressName.SYSTEM]: AddressStartMSB.SYSTEM.name,  # "System"
        },
        BYTE_GROUPS_3: {
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.SYSTEM_COMMON]: AddressOffsetSystemLMB.COMMON.name,  # "System Common",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.SYSTEM_CONTROLLER]: AddressOffsetSystemLMB.CONTROLLER.name,  # "System Controller"
        },
    },
    ParameterAreas.TEMPORARY_TONE: {
        BYTE_GROUPS_4: {
            PARAMETER_ADDRESS_TABLE[ParameterAddressName.TEMPORARY_PROGRAM]: AddressStartMSB.TEMPORARY_PROGRAM.name,  # Temporary Program
            PARAMETER_ADDRESS_TABLE[ParameterAddressName.TEMPORARY_TONE_DIGITAL1]: AddressOffsetTemporaryToneUMB.DIGITAL_SYNTH_1.name,
            # "Temporary Tone (Digital Synth Part 1)",
            PARAMETER_ADDRESS_TABLE[ParameterAddressName.TEMPORARY_TONE_DIGITAL2]: AddressOffsetTemporaryToneUMB.DIGITAL_SYNTH_2.name,
            # "Temporary Tone (Digital Synth Part 2)",
            PARAMETER_ADDRESS_TABLE[ParameterAddressName.TEMPORARY_TONE_ANALOG]: AddressOffsetTemporaryToneUMB.ANALOG_SYNTH.name,
            # "Temporary Tone (Analog Synth Part)",
            PARAMETER_ADDRESS_TABLE[ParameterAddressName.TEMPORARY_DRUM_KIT]: AddressOffsetTemporaryToneUMB.DRUM_KIT.name,  # "Temporary Tone (Drums Part)"
        },
        BYTE_GROUPS_3: {
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.TEMPORARY_SUPERNATURAL_SYNTH_TONE]: AddressOffsetTemporaryToneUMB.DIGITAL_SYNTH_1.name,  # "Temporary SuperNATURAL Synth Tone",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.TEMPORARY_ANALOG_SYNTH_TONE]: AddressOffsetTemporaryToneUMB.ANALOG_SYNTH.name,  #  "Temporary Analog Synth Tone",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.TEMPORARY_DRUM_KIT]: AddressOffsetTemporaryToneUMB.DRUM_KIT.name,  #  "Temporary Drum Kit"
        },
    },
    ParameterAreas.PROGRAM: {
        BYTE_GROUPS_3: {
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.PROGRAM_COMMON]: AddressOffsetProgramLMB.COMMON.name,  # "Program Common",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.PROGRAM_VOCAL_EFFECT]: AddressOffsetProgramLMB.VOCAL_EFFECT.name,  # "Program Vocal Effect",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.PROGRAM_EFFECT_1]: AddressOffsetProgramLMB.EFFECT_1.name,  # "Program Effect 1",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.PROGRAM_EFFECT_2]: AddressOffsetProgramLMB.EFFECT_2.name,  # "Program Effect 2",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.PROGRAM_DELAY]: AddressOffsetProgramLMB.DELAY.name,  # "Program Delay",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.PROGRAM_REVERB]: AddressOffsetProgramLMB.REVERB.name,  # "Program Reverb",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.PROGRAM_PART_DIGITAL1]: AddressOffsetProgramLMB.PART_DIGITAL_SYNTH_1.name,  # "Program Part (Digital Synth Part 1)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.PROGRAM_PART_DIGITAL2]: AddressOffsetProgramLMB.PART_DIGITAL_SYNTH_2.name,  # "Program Part (Digital Synth Part 2)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.PROGRAM_PART_ANALOG]: AddressOffsetProgramLMB.PART_ANALOG.name,  # "Program Part (Analog Synth Part)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.PROGRAM_PART_DRUMS]: AddressOffsetProgramLMB.PART_DRUM.name,  # "Program Part (Drums Part)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.PROGRAM_ZONE_DIGITAL1]: AddressOffsetProgramLMB.ZONE_DIGITAL_SYNTH_1.name,  # "Program Zone (Digital Synth Part 1)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.PROGRAM_ZONE_DIGITAL2]: AddressOffsetProgramLMB.ZONE_DIGITAL_SYNTH_2.name,  # "Program Zone (Digital Synth Part 2)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.PROGRAM_ZONE_ANALOG]: AddressOffsetProgramLMB.ZONE_ANALOG.name,  # "Program Zone (Analog Synth Part)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.PROGRAM_ZONE_DRUMS]: AddressOffsetProgramLMB.ZONE_DRUM.name,  # "Program Zone (Drums Part)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.PROGRAM_CONTROLLER]: AddressOffsetProgramLMB.CONTROLLER.name,
        }
    },
    ParameterAreas.SUPERNATURAL_SYNTH_TONE: {
        BYTE_GROUPS_3: {
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.SUPERNATURAL_SYNTH_TONE_COMMON]: AddressOffsetSuperNATURALLMB.COMMON.name,  # "SuperNATURAL Synth Tone Common",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.SUPERNATURAL_SYNTH_TONE_PARTIAL1]: AddressOffsetSuperNATURALLMB.PARTIAL_1.name,  # "SuperNATURAL Synth Tone Partial (1)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.SUPERNATURAL_SYNTH_TONE_PARTIAL2]: AddressOffsetSuperNATURALLMB.PARTIAL_2.name,  # "SuperNATURAL Synth Tone Partial (2)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.SUPERNATURAL_SYNTH_TONE_PARTIAL3]: AddressOffsetSuperNATURALLMB.PARTIAL_3.name,  # "SuperNATURAL Synth Tone Partial (3)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.SUPERNATURAL_SYNTH_TONE_MODIFY]: AddressOffsetSuperNATURALLMB.MODIFY.name,  # "SuperNATURAL Synth Tone Modify"
        }
    },
    ParameterAreas.ANALOG_SYNTH_TONE: {
        BYTE_GROUPS_3: {
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.ANALOG_SYNTH_TONE]: AddressOffsetProgramLMB.COMMON.name  # "Analog Synth Tone"
        }
    },
    ParameterAreas.DRUM_KIT: {
        BYTE_GROUPS_3: {
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_COMMON]: AddressOffsetDrumKitLMB.COMMON.name,  # "Drum Kit Common",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL1]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_1.name,  # "Drum Kit Partial (Key # 36)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL2]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_2.name,  # "Drum Kit Partial (Key # 37)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL3]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_3.name,  # "Drum Kit Partial (Key # 38)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL4]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_4.name,  # "Drum Kit Partial (Key # 39)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL5]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_5.name,  # "Drum Kit Partial (Key # 40)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL6]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_6.name,  # "Drum Kit Partial (Key # 41)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL7]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_7.name,  # "Drum Kit Partial (Key # 42)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL8]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_8.name,  # "Drum Kit Partial (Key # 43)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL9]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_9.name,  # "Drum Kit Partial (Key # 44)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL10]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_10.name,  # "Drum Kit Partial (Key # 45)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL11]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_11.name,  # "Drum Kit Partial (Key # 46)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL12]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_12.name,  # "Drum Kit Partial (Key # 47)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL13]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_13.name,  # "Drum Kit Partial (Key # 48)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL14]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_14.name,  # "Drum Kit Partial (Key # 49)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL15]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_15.name,  # "Drum Kit Partial (Key # 50)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL16]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_16.name,  # "Drum Kit Partial (Key # 51)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL17]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_17.name,  # "Drum Kit Partial (Key # 52)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL18]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_18.name,  # "Drum Kit Partial (Key # 53)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL19]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_19.name,  # "Drum Kit Partial (Key # 54)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL20]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_20.name,  # "Drum Kit Partial (Key # 55)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL21]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_21.name,  # "Drum Kit Partial (Key # 56)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL22]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_22.name,  # "Drum Kit Partial (Key # 57)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL23]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_23.name,  # "Drum Kit Partial (Key # 58)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL24]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_24.name,  # "Drum Kit Partial (Key # 59)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL25]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_25.name,  # "Drum Kit Partial (Key # 60)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL26]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_26.name,  # "Drum Kit Partial (Key # 61)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL27]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_27.name,  # "Drum Kit Partial (Key # 62)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL28]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_28.name,  # "Drum Kit Partial (Key # 63)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL29]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_29.name,  # "Drum Kit Partial (Key # 64)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL30]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_30.name,  # "Drum Kit Partial (Key # 65)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL31]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_31.name,  # "Drum Kit Partial (Key # 66)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL32]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_32.name,  # "Drum Kit Partial (Key # 67)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL33]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_33.name,  # "Drum Kit Partial (Key # 68)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL34]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_34.name,  # "Drum Kit Partial (Key # 69)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL35]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_35.name,  # "Drum Kit Partial (Key # 70)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL36]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_36.name,  # "Drum Kit Partial (Key # 71)",
            PARAMETER_OFFSET_TABLE[ParameterOffsetName.DRUM_KIT_PARTIAL37]: AddressOffsetDrumKitLMB.DRUM_KIT_PART_37.name,  # "Drum Kit Partial (Key # 72)"
        }
    },
}
