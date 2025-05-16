"""
5. Parameter Address Map
========================

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

from jdxi_editor.midi.data.address.address import AddressMemoryAreaMSB, \
    AddressOffsetSystemUMB, AddressOffsetSuperNATURALLMB, AddressOffsetAnalogLMB, AddressOffsetTemporaryToneUMB, \
    AddressOffsetProgramLMB

PARAMETER_ADDRESS_MAP = {
    "System": {
        "4-byte-addresses": {
            "01 00 00 00": AddressMemoryAreaMSB.SETUP.name,  # "Setup",
            "02 00 00 00": AddressMemoryAreaMSB.SYSTEM.name,  # "System"
        },
        "3-byte-offsets": {
            "00 00 00": AddressOffsetSystemUMB.COMMON.name,  # "System Common",
            "00 03 00": AddressOffsetSystemUMB.CONTROLLER.name,  # "System Controller"
        }
    },
    "Temporary Tone": {
        "4-byte-addresses": {
            "18 00 00 00": AddressMemoryAreaMSB.TEMPORARY_PROGRAM.name,  # Temporary Program
            "19 00 00 00": AddressOffsetTemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_1_AREA.name,  # "Temporary Tone (Digital Synth Part 1)",
            "19 20 00 00": AddressOffsetTemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_2_AREA.name,  # "Temporary Tone (Digital Synth Part 2)",
            "19 40 00 00": AddressOffsetTemporaryToneUMB.ANALOG_PART.name,  # "Temporary Tone (Analog Synth Part)",
            "19 60 00 00": AddressOffsetTemporaryToneUMB.DRUM_KIT_PART.name,  # "Temporary Tone (Drums Part)"
        },
        "3-byte-offsets": {
            "01 00 00": AddressOffsetTemporaryToneUMB.TEMPORARY_DIGITAL_SYNTH_1_AREA.name,  # "Temporary SuperNATURAL Synth Tone",
            "02 00 00": AddressOffsetTemporaryToneUMB.ANALOG_PART.name,  #  "Temporary Analog Synth T one",
            "10 00 00": AddressOffsetTemporaryToneUMB.DRUM_KIT_PART.name,  #  "Temporary Drum Kit"
        }
    },
    "Program": {
        "3-byte-offsets": {
            "00 00 00": AddressOffsetProgramLMB.COMMON.name,  # "Program Common",
            "00 01 00": AddressOffsetProgramLMB.VOCAL_EFFECT.name,  # "Program Vocal Effect",
            "00 02 00": AddressOffsetProgramLMB.EFFECT_1.name,  # "Program Effect 1",
            "00 04 00": AddressOffsetProgramLMB.EFFECT_2.name,  # "Program Effect 2",
            "00 06 00": AddressOffsetProgramLMB.DELAY.name, # "Program Delay",
            "00 08 00": AddressOffsetProgramLMB.REVERB.name, # "Program Reverb",
            "00 20 00": AddressOffsetProgramLMB.PART_DIGITAL_SYNTH_1.name,  # "Program Part (Digital Synth Part 1)",
            "00 21 00": AddressOffsetProgramLMB.PART_DIGITAL_SYNTH_2.name,  # "Program Part (Digital Synth Part 2)",
            "00 22 00": AddressOffsetProgramLMB.PART_ANALOG.name,  # "Program Part (Analog Synth Part)",
            "00 23 00": AddressOffsetProgramLMB.PART_DRUM.name,  # "Program Part (Drums Part)",
            "00 30 00": AddressOffsetProgramLMB.ZONE_DIGITAL_SYNTH_1.name,  # "Program Zone (Digital Synth Part 1)",
            "00 31 00": AddressOffsetProgramLMB.ZONE_DIGITAL_SYNTH_2.name,  # "Program Zone (Digital Synth Part 2)",
            "00 32 00": AddressOffsetProgramLMB.ZONE_ANALOG.name,  # "Program Zone (Analog Synth Part)",
            "00 33 00": AddressOffsetProgramLMB.ZONE_DRUM.name , # "Program Zone (Drums Part)",
            "00 40 00": AddressOffsetProgramLMB.CONTROLLER.name,
        }
    },
    "SuperNATURAL Synth Tone": {
        "3-byte-offsets": {
            "00 00 00": AddressOffsetSuperNATURALLMB.COMMON.name,  # "SuperNATURAL Synth Tone Common",
            "00 20 00": AddressOffsetSuperNATURALLMB.PARTIAL_1.name,  # "SuperNATURAL Synth Tone Partial (1)",
            "00 21 00": AddressOffsetSuperNATURALLMB.PARTIAL_2.name,  # "SuperNATURAL Synth Tone Partial (2)",
            "00 22 00": AddressOffsetSuperNATURALLMB.PARTIAL_3.name,  # "SuperNATURAL Synth Tone Partial (3)",
            "00 50 00": AddressOffsetSuperNATURALLMB.MODIFY.name  # "SuperNATURAL Synth Tone Modify"
        }
    },
    "Analog Synth Tone": {
        "3-byte-offsets": {
            "00 00 00": AddressOffsetAnalogLMB.COMMON.name  # "Analog Synth Tone"
        }
    },
    "Drum Kit": {
        "3-byte-offsets": {
            "00 00 00": "Drum Kit Common",
            "00 2E 00": "Drum Kit Partial (Key # 36)",
            "00 30 00": "Drum Kit Partial (Key # 37)",
            "00 32 00": "Drum Kit Partial (Key # 38)",
            "00 34 00": "Drum Kit Partial (Key # 39)",
            "00 36 00": "Drum Kit Partial (Key # 40)",
            "00 38 00": "Drum Kit Partial (Key # 41)",
            "00 3A 00": "Drum Kit Partial (Key # 42)",
            "00 3C 00": "Drum Kit Partial (Key # 43)",
            "00 3E 00": "Drum Kit Partial (Key # 44)",
            "00 40 00": "Drum Kit Partial (Key # 45)",
            "00 42 00": "Drum Kit Partial (Key # 46)",
            "00 44 00": "Drum Kit Partial (Key # 47)",
            "00 46 00": "Drum Kit Partial (Key # 48)",
            "00 48 00": "Drum Kit Partial (Key # 49)",
            "00 4A 00": "Drum Kit Partial (Key # 50)",
            "00 4C 00": "Drum Kit Partial (Key # 51)",
            "00 4E 00": "Drum Kit Partial (Key # 52)",
            "00 50 00": "Drum Kit Partial (Key # 53)",
            "00 52 00": "Drum Kit Partial (Key # 54)",
            "00 54 00": "Drum Kit Partial (Key # 55)",
            "00 56 00": "Drum Kit Partial (Key # 56)",
            "00 58 00": "Drum Kit Partial (Key # 57)",
            "00 5A 00": "Drum Kit Partial (Key # 58)",
            "00 5C 00": "Drum Kit Partial (Key # 59)",
            "00 5E 00": "Drum Kit Partial (Key # 60)",
            "00 60 00": "Drum Kit Partial (Key # 61)",
            "00 62 00": "Drum Kit Partial (Key # 62)",
            "00 64 00": "Drum Kit Partial (Key # 63)",
            "00 66 00": "Drum Kit Partial (Key # 64)",
            "00 68 00": "Drum Kit Partial (Key # 65)",
            "00 6A 00": "Drum Kit Partial (Key # 66)",
            "00 6C 00": "Drum Kit Partial (Key # 67)",
            "00 6E 00": "Drum Kit Partial (Key # 68)",
            "00 70 00": "Drum Kit Partial (Key # 69)",
            "00 72 00": "Drum Kit Partial (Key # 70)",
            "00 74 00": "Drum Kit Partial (Key # 71)",
            "00 76 00": "Drum Kit Partial (Key # 72)"
        }
    }
}
