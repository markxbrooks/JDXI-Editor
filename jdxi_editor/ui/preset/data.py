"""
JDXi preset data

This module defines the `JDXIPresetData` class, which provides methods to retrieve
structured preset data for different JD-Xi synth types, including Analog, Digital1,
Digital2, and Drum. It calculates MIDI bank and program values for use in MIDI Program
Change messages.

Classes:
    - JDXIPresetData: Provides static methods for looking up JD-Xi presets by synth type
      and index.

Constants and Enums (from imports):
    - JDXISynth: Enum representing synth types (ANALOG, DIGITAL_1, DIGITAL_2, DRUM).
    - JDXIPresets: Named preset lists for each synth type.

Example usage:
=============
>>> from jdxi_editor.synth.type import JDXiSynth
>>> preset_data = JDXiPresetData.get_preset_details(JDXiSynth.DIGITAL_SYNTH_1, 10)
>>> print(preset_data)
JDXiPresetData(name='011: LFO Pad 1', presets=['001: JP8 Strings1', '002: Soft Pad 1', '003: JP8 Strings2', '004: JUNO Str 1', '005: Oct Strings', '006: Brite Str 1', '007: Boreal Pad', '008: JP8 Strings3', '009: JP8 Strings4', '010: Hollow Pad 1', '011: LFO Pad 1', '012: Hybrid Str', '013: Awakening 1', '014: Cincosoft 1', '015: Bright Pad 1', '016: Analog Str 1', '017: Soft ResoPd1', '018: HPF Poly 1', '019: BPF Poly', '020: Sweep Pad 1', '021: Soft Pad 2', '022: Sweep JD 1', '023: FltSweep Pd1', '024: HPF Pad', '025: HPF SweepPd1', '026: KOff Pad', '027: Sweep Pad 2', '028: TrnsSweepPad', '029: Revalation 1', '030: LFO CarvePd1', '031: RETROX 139 1', '032: LFO ResoPad1', '033: PLS Pad 1', '034: PLS Pad 2', '035: Trip 2 Mars1', '036: Reso S&H Pd1', '037: SideChainPd1', '038: PXZoon 1', '039: Psychoscilo1', '040: Fantasy 1', '041: D-50 Stack 1', '042: Organ Pad', '043: Bell Pad', '044: Dreaming 1', '045: Syn Sniper 1', '046: Strings 1', '047: D-50 Pizz 1', '048: Super Saw 1', '049: S-SawStacLd1', '050: Tekno Lead 1', '051: Tekno Lead 2', '052: Tekno Lead 3', '053: OSC-SyncLd 1', '054: WaveShapeLd1', '055: JD RingMod 1', '056: Buzz Lead 1', '057: Buzz Lead 2', '058: SawBuzz Ld 1', '059: Sqr Buzz Ld1', '060: Tekno Lead 4', '061: Dist Flt TB1', '062: Dist TB Sqr1', '063: Glideator 1', '064: Vintager 1', '065: Hover Lead 1', '066: Saw Lead 1', '067: Saw+Tri Lead', '068: PortaSaw Ld1', '069: Reso Saw Ld', '070: SawTrap Ld 1', '071: Fat GR Lead', '072: Pulstar Ld', '073: Slow Lead', '074: AnaVox Lead', '075: Square Ld 1', '076: Square Ld 2', '077: Sqr Lead 1', '078: Sqr Trap Ld1', '079: Sine Lead 1', '080: Tri Lead', '081: Tri Stac Ld1', '082: 5th SawLead1', '083: Sweet 5th 1', '084: 4th Syn Lead', '085: Maj Stack Ld', '086: MinStack Ld1', '087: Chubby Lead1', '088: CuttingLead1', '089: Seq Bass 1', '090: Reso Bass 1', '091: TB Bass 1', '092: 106 Bass 1', '093: FilterEnvBs1', '094: JUNO Sqr Bs1', '095: Reso Bass 2', '096: JUNO Bass', '097: MG Bass 1', '098: 106 Bass 3', '099: Reso Bass 3', '100: Detune Bs 1', '101: MKS-50 Bass1', '102: Sweep Bass', '103: MG Bass 2', '104: MG Bass 3', '105: ResRubber Bs', '106: R&B Bass 1', '107: Reso Bass 4', '108: Wide Bass 1', '109: Chow Bass 1', '110: Chow Bass 2', '111: SqrFilterBs1', '112: Reso Bass 5', '113: Syn Bass 1', '114: ResoSawSynBs', '115: Filter Bass1', '116: SeqFltEnvBs', '117: DnB Bass 1', '118: UnisonSynBs1', '119: Modular Bs', '120: Monster Bs 1', '121: Monster Bs 2', '122: Monster Bs 3', '123: Monster Bs 4', '124: Square Bs 1', '125: 106 Bass 2', '126: 5th Stac Bs1', '127: SqrStacSynBs', '128: MC-202 Bs', '129: TB Bass 2', '130: Square Bs 2', '131: SH-101 Bs', '132: R&B Bass 2', '133: MG Bass 4', '134: Seq Bass 2', '135: Tri Bass 1', '136: BPF Syn Bs 2', '137: BPF Syn Bs 1', '138: Low Bass 1', '139: Low Bass 2', '140: Kick Bass 1', '141: SinDetuneBs1', '142: Organ Bass 1', '143: Growl Bass 1', '144: Talking Bs 1', '145: LFO Bass 1', '146: LFO Bass 2', '147: Crack Bass', '148: Wobble Bs 1', '149: Wobble Bs 2', '150: Wobble Bs 3', '151: Wobble Bs 4', '152: SideChainBs1', '153: SideChainBs2', '154: House Bass 1', '155: FM Bass', '156: 4Op FM Bass1', '157: Ac. Bass', '158: Fingerd Bs 1', '159: Picked Bass', '160: Fretless Bs', '161: Slap Bass 1', '162: JD Piano 1', '163: E. Grand 1', '164: Trem EP 1', '165: FM E.Piano 1', '166: FM E.Piano 2', '167: Vib Wurly 1', '168: Pulse Clav', '169: Clav', "170: 70's E.Organ", '171: House Org 1', '172: House Org 2', '173: Bell 1', '174: Bell 2', '175: Organ Bell', '176: Vibraphone 1', '177: Steel Drum', '178: Harp 1', '179: Ac. Guitar', '180: Bright Strat', '181: Funk Guitar1', '182: Jazz Guitar', '183: Dist Guitar1', '184: D. Mute Gtr1', '185: E. Sitar', '186: Sitar Drone', '187: FX 1', '188: FX 2', '189: FX 3', '190: Tuned Winds1', '191: Bend Lead 1', '192: RiSER 1', '193: Rising SEQ 1', '194: Scream Saw', '195: Noise SEQ 1', '196: Syn Vox 1', '197: JD SoftVox', '198: Vox Pad', '199: VP-330 Chr', '200: Orch Hit', '201: Philly Hit', '202: House Hit', "203: O'Skool Hit1", '204: Punch Hit', '205: Tao Hit', '206: SEQ Saw 1', '207: SEQ Sqr', '208: SEQ Tri 1', '209: SEQ 1', '210: SEQ 2', '211: SEQ 3', '212: SEQ 4', '213: Sqr Reso Plk', '214: Pluck Synth1', '215: Paperclip 1', '216: Sonar Pluck1', '217: SqrTrapPlk 1', '218: TB Saw Seq 1', '219: TB Sqr Seq 1', '220: JUNO Key', '221: Analog Poly1', '222: Analog Poly2', '223: Analog Poly3', '224: Analog Poly4', '225: JUNO Octavr1', '226: EDM Synth 1', '227: Super Saw 2', '228: S-Saw Poly', '229: Trance Key 1', '230: S-Saw Pad 1', '231: 7th Stac Syn', '232: S-SawStc Syn', '233: Trance Key 2', '234: Analog Brass', '235: Reso Brass', '236: Soft Brass 1', '237: FM Brass', '238: Syn Brass 1', '239: Syn Brass 2', '240: JP8 Brass', '241: Soft SynBrs1', '242: Soft SynBrs2', '243: EpicSlow Brs', '244: JUNO Brass', '245: Poly Brass', '246: Voc:Ensemble', '247: Voc:5thStack', '248: Voc:Robot', '249: Voc:Saw', '250: Voc:Sqr', '251: Voc:Rise Up', '252: Voc:Auto Vib', '253: Voc:PitchEnv', '254: Voc:VP-330', '255: Voc:Noise'], bank_msb=16, bank_lsb=0, program=10)
>>> import json
>>> from dataclasses import asdict
...
>>> preset = JDXiPresetData.get_preset_details(JDXiSynth.ANALOG_SYNTH, 5)
...
>>> with open("preset.json", "w") as f:
...    json.dump(asdict(preset), f, indent=2)
...
>>> with open("preset.json", "r") as f:
...    data = json.load(f)
...    preset = JDXiPresetData(**data)
"""

from dataclasses import asdict, dataclass
from typing import List

from jdxi_editor.synth.type import JDXiSynth
from jdxi_editor.ui.preset.tone.lists import JDXiPresetToneList


@dataclass
class JDXiPresetData:
    name: str
    presets: List[str]
    bank_msb: int
    bank_lsb: int
    program: int

    @staticmethod
    def from_dict(data: dict) -> "JDXiPresetData":
        return JDXiPresetData(
            name=data.get("name", "Unnamed"),
            presets=data.get("presets", []),
            bank_msb=data.get("bank_msb", 0),
            bank_lsb=data.get("bank_lsb", 0),
            program=data.get("program", 0),
        )

    @staticmethod
    def get_preset_details(synth_type: str, preset_number: int) -> "JDXiPresetData":
        if synth_type == JDXiSynth.ANALOG_SYNTH:
            presets = JDXiPresetToneList.Analog.ENUMERATED
            bank_msb = 0x10  # JD-Xi MSB for Analog (example)
            bank_lsb = preset_number // 7
            program = preset_number % 7
        elif synth_type == JDXiSynth.DIGITAL_SYNTH_1:
            presets = JDXiPresetToneList.Digital.ENUMERATED
            bank_msb = 0x10
            bank_lsb = preset_number // 16
            program = preset_number % 16
        elif synth_type == JDXiSynth.DIGITAL_SYNTH_2:
            presets = JDXiPresetToneList.Digital.ENUMERATED
            bank_msb = 0x10
            bank_lsb = preset_number // 16
            program = preset_number % 16
        elif synth_type == JDXiSynth.DRUM_KIT:
            presets = JDXiPresetToneList.Drum.ENUMERATED
            bank_msb = 0x10
            bank_lsb = preset_number // 16
            program = preset_number % 16
        else:
            raise ValueError(f"Unknown synth type: {synth_type}")

        # Make sure preset_number is within range
        try:
            name = presets[preset_number]
        except IndexError:
            name = f"Unknown {synth_type} preset {preset_number}"

        return JDXiPresetData(
            name=name,
            presets=presets,
            bank_msb=bank_msb,
            bank_lsb=bank_lsb,
            program=program,
        )

    def to_dict(self):
        return {
            "name": self.name,
            # "presets": self.presets,
            "bank_msb": self.bank_msb,
            "bank_lsb": self.bank_lsb,
            "program": self.program,
        }
