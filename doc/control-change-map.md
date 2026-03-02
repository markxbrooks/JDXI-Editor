# JD-Xi Control Change / NRPN Map

Reference for MIDI Control Change (CC) and NRPN parameters. Source: `doc/midi_parameters.txt`.

## Null Reset Values

To avoid unintentional parameter changes when switching patches:

- **Null NRPN:** CC 98 (MSB) = 127, CC 99 (LSB) = 127
- **Null RPN:** CC 100 (MSB) = 127, CC 101 (LSB) = 127
- **Data Entry:** CC 6 (MSB), CC 38 (LSB)

---

## Effects (Global)

| CC# | Parameter        | Value   |
|-----|------------------|---------|
| 12  | Reverb           | 0–127   |
| 13  | Delay            | 0–127   |
| 14  | Effect 1         | 0–127   |
| 15  | Effect 2         | 0–127   |
| 83  | Vocoder (Level)  | 0–127   |
| 91  | Reverb Send Level| 0–127   |
| 94  | Delay Send Level | 0–127   |

---

## SuperNATURAL Synth Tone (Digital, Part 1–3)

| Parameter       | Partial | CC# or NRPN LSB | Value   |
|----------------|---------|-----------------|---------|
| Cutoff         | 1–3     | 102–104         | 0–127   |
| Resonance      | 1–3     | 105–107         | 0–127   |
| Level          | 1–3     | 117–119         | 0–127   |
| Envelope       | 1–3     | NRPN LSB 124–126| 0–127   |
| LFO Shape      | 1–3     | NRPN LSB 3–5    | 0–5     |
| LFO Rate       | 1–3     | 16–18           | 0–127   |
| LFO Pitch Depth| 1–3     | NRPN LSB 15–17  | 0–127   |
| LFO Filter Depth| 1–3    | NRPN LSB 18–20  | 0–127   |
| LFO Amp Depth  | 1–3     | NRPN LSB 21–23  | 0–127   |

---

## Analog Synth Tone

| Parameter       | CC# or NRPN LSB | Value   |
|----------------|-----------------|---------|
| Cutoff         | 102             | 0–127   |
| Resonance      | 105             | 0–127   |
| Level          | 117             | 0–127   |
| Envelope       | NRPN LSB 124    | 0–127   |
| LFO Shape      | NRPN LSB 3      | 0–5     |
| LFO Rate       | 16              | 0–127   |
| LFO Pitch Depth| NRPN LSB 15     | 0–127   |
| LFO Filter Depth| NRPN LSB 18    | 0–127   |
| LFO Amp Depth  | NRPN LSB 21     | 0–127   |
| Pulse Width    | NRPN LSB 37     | 0–127   |

---

## Drum Kit

Per-note parameters: NRPN MSB + Note (36–72) as LSB.

| Parameter  | NRPN MSB | LSB      | Value   |
|-----------|----------|----------|---------|
| Cutoff    | 89       | Note     | 0–127   |
| Resonance | 92       | Note     | 0–127   |
| Level     | 64       | Note     | 0–127   |
| Envelope  | 119      | Note     | 0–127   |

---

## NRPN LSB Map (Analog / Digital)

With NRPN MSB = 0 unless noted. Part 1/Analog, Part 2, Part 3 use different LSB ranges per partial.

| LSB Range | Parameter           | Notes                          |
|-----------|---------------------|--------------------------------|
| 2         | Unison (Digi)       | off/on                         |
| 3–5       | LFO Shape           | 0–5: TRI SIN SAW SQR S&H RND   |
| 6–8       | LFO Rate            | (see also CC16–18)             |
| 9–11      | LFO Tempo Sync      | off/on                         |
| 12–14     | LFO Fade Time       |                                |
| 15–17     | LFO Pitch Depth     | bipolar                        |
| 18–20     | LFO Filter Depth    | bipolar                        |
| 21–23     | LFO Amp Depth       | bipolar                        |
| 24–26     | OSC Waveform        | Analog: 0–2, Digi: 0–7         |
| 27–29     | Pitch               | bipolar                        |
| 30–32     | Detune              | bipolar                        |
| 33        | Digi: Wave shape    | common                         |
| 34        | Digi: RING          | off/on                         |
| 37–39     | Pulse Width         |                                |
| 40–42     | PWM Depth           |                                |
| 43–45     | Digi: Pitch Depth   | -63/+64                        |
| 46–48     | Digi: Pitch Attack  |                                |
| 49–51     | Digi: Pitch Decay   |                                |
| 56–58     | Filter type         | Analog: 0–1, Digi: 0–7         |
| 59–61     | Cutoff              |                                |
| 62–64     | Resonance           | partial                        |
| 65–67     | Filter Depth        | bipolar                        |
| 68–70     | Cutoff Key Follow   | bipolar                        |
| 71–73     | Digi: HPF Cutoff    |                                |
| 74–76     | Filter Attack       |                                |
| 77–79     | Filter Decay        |                                |
| 80–82     | Filter Sustain      |                                |
| 83–85     | Filter Release      |                                |
| 86–88     | Amp Level           |                                |
| 89–91     | Amp Attack          |                                |
| 92–94     | Amp Decay           |                                |
| 95–97     | Amp Sustain         |                                |
| 98–100    | Amp Release         |                                |
| 124–126   | Envelope            |                                |

---

## Standard CC (Part Level)

| CC# | Parameter        | Value   |
|-----|------------------|---------|
| 1   | Modulation       | 0–127   |
| 5   | Portamento Time  | 0–127   |
| 7   | Volume           | 0–127   |
| 10  | Pan              | 0–64–127 (L–C–R) |
| 11  | Expression       | 0–127   |
| 64  | Hold             | off/on  |
| 65  | Portamento       | off/on  |
| 71  | Resonance        | bipolar |
| 72  | Release Time     | bipolar |
| 73  | Attack Time      | bipolar |
| 74  | Cutoff           | bipolar |
| 75  | Decay Time       | bipolar |
| 76  | Vibrato Rate     | bipolar |
| 77  | Vibrato Depth    | bipolar |
| 78  | Vibrato Delay    | bipolar |
| 121 | Reset Controllers| (on MIDI channel) |
