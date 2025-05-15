address_map = {
    "System": {
        "4-byte-addresses": {
            "01 00 00 00": "Setup",
            "02 00 00 00": "System"
        },
        "3-byte-offsets": {
            "00 00 00": "System Common",
            "00 03 00": "System Controller"
        }
    },
    "Temporary Tone": {
        "4-byte-addresses": {
            "18 00 00 00": "Temporary Program",
            "19 00 00 00": "Temporary Tone (Digital Synth Part 1)",
            "19 20 00 00": "Temporary Tone (Digital Synth Part 2)",
            "19 40 00 00": "Temporary Tone (Analog Synth Part)",
            "19 60 00 00": "Temporary Tone (Drums Part)"
        },
        "3-byte-offsets": {
            "01 00 00": "Temporary SuperNATURAL Synth Tone",
            "02 00 00": "Temporary Analog Synth Tone",
            "10 00 00": "Temporary Drum Kit"
        }
    },
    "Program": {
        "3-byte-offsets": {
            "00 00 00": "Program Common",
            "00 01 00": "Program Vocal Effect",
            "00 02 00": "Program Effect 1",
            "00 04 00": "Program Effect 2",
            "00 06 00": "Program Delay",
            "00 08 00": "Program Reverb",
            "00 20 00": "Program Part (Digital Synth Part 1)",
            "00 21 00": "Program Part (Digital Synth Part 2)",
            "00 22 00": "Program Part (Analog Synth Part)",
            "00 23 00": "Program Part (Drums Part)",
            "00 30 00": "Program Zone (Digital Synth Part 1)",
            "00 31 00": "Program Zone (Digital Synth Part 2)",
            "00 32 00": "Program Zone (Analog Synth Part)",
            "00 33 00": "Program Zone (Drums Part)",
            "00 40 00": "Program Controller"
        }
    },
    "SuperNATURAL Synth Tone": {
        "3-byte-offsets": {
            "00 00 00": "SuperNATURAL Synth Tone Common",
            "00 20 00": "SuperNATURAL Synth Tone Partial (1)",
            "00 21 00": "SuperNATURAL Synth Tone Partial (2)",
            "00 22 00": "SuperNATURAL Synth Tone Partial (3)",
            "00 50 00": "SuperNATURAL Synth Tone Modify"
        }
    }
}