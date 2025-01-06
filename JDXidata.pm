package JDXidata;

use warnings;
use strict;

use Exporter;
our @ISA=qw(Exporter);
our @EXPORT=qw(
  $ROL_ID
  $JDXI_ID
  $DR1
  $DT1
  $Xi_header
  @coarse_tune
  @ENV_labels
  @rnd_pdepth
  @sync_notes
  @dly_notes
  @tone_cats
  @mute_grp
  @rev_type
  @hf_damp
  @ratio
  @comp_att
  @comp_rel
  @fx1_type
  @fx2_type
  @fx_type
  @arp_grid
  @arp_duration
  @arp_motif
  @arp_type
  @ap_key
  @vc_hpf
  @PCMwaves
  @DRMwaves
  @ANdata
  %AN
  @AN_rnd
  @SN_COM
  @SN_MOD
  @SN_PL
  %SN1
  %SN2
  @SN
  @DRdata
  %DR
  @ARPdata
  %ARP
  @VFXdata
  %VFX
  @FXdata
  %FX
  @FX_send
  @Part
);

# default JD-Xi MIDI strings
our $ROL_ID="\x41";
our $JDXI_ID="\x00\x00\x00\x0E";
our $DR1="\x11";
our $DT1="\x12";
# Header Format: F0 41 xx 00 00 00 0E 12
our $Xi_header  ='\xF0'.$ROL_ID.'[\x01-\x10]'.$JDXI_ID.$DT1;

our @coarse_tune=();
my $pval=0;
my @notes=('C ','C#','D ','Eb','E ','F ','F#','G ','G#','A ','Bb','B ');
for my $o (-1..9) {
    for my $n (0..11) {
        if ($pval<128) {$coarse_tune[$pval]=$notes[$n].$o;}
        $pval++;
    }
}

our @ENV_labels=('    PITCH ENV    ', '     TVF ENV     ', '     TVA ENV     ');

our @rnd_pdepth=(0..10, 20, 30 ,40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200);

our @sync_notes=('16','12','8','4','2','1','3/4','2/3','1/2','3/8','1/3',
                '1/4','3/16','1/6','1/8','3/32','1/12','1/16','1/24','1/32');

our @dly_notes=('1/96', '1/64', '1/48', '1/32', '1/24', '3/64', '1/16', '1/12', '3/32', '1/8',
                '1/6', '3/16', '1/4', '1/3', '3/8', '1/2', '2/3', '3/4', '1', '4/3', '3/2', '2');

our @tone_cats=('00: not assigned', '09: Keyboard', '21: Bass', '34: Lead',
               '35: Brass', '36: Strings/Pad', '39: FX/Other', '40: Seq');

our @mute_grp=('OFF', 1..31);

our @rev_type=('Room 1','Room 2','Stage 1','Stage 2','Hall 1','Hall 2');

our @hf_damp=('200Hz', '250Hz', '315Hz', '400Hz', '500Hz', '630Hz', '800Hz', '1000Hz', '1250Hz', '1600Hz', '2000Hz',
             '2500Hz', '3150Hz', '4000Hz', '5000Hz', '6300Hz', '8000Hz', 'BYPASS');

our @ratio=('  1:1','  2:1','  3:1','  4:1','  5:1','  6:1','  7:1','  8:1','  9:1',' 10:1',
           ' 20:1',' 30:1',' 40:1',' 50:1',' 60:1',' 70:1',' 80:1',' 90:1','100:1',' inf:1');

our @comp_att=(0.05,0.06,0.07,0.08,0.09,0.10,0.20,0.30,0.40,0.50,0.60,0.70,0.80,0.90, 1.0, 2.0,
               3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0,10.0,15.0,20.0,25.0,30.0,35.0,40.0,45.0,50.0);

our @comp_rel=(0.05,0.07,0.10,0.50,1,5,10,17,25,50,75,100,200,300,400,500,600,700,800,900,1000,1200,1500,2000);

our @fx1_type=('00: Thru','01: Distortion','02: Fuzz','03: Compressor','04: Bit Crusher');

our @fx2_type=('00: Thru','05: Flanger','06: Phaser','07: Ring Mod','08: Slicer');

our @fx_type=(@fx1_type, @fx2_type[1,2,3,4]);

our @arp_grid=('1/4', '1/8', '1/8 L', '1/8 H', '1/12', '1/16', '1/16 L', '1/16 H', '1/24');

our @arp_duration=('30%', '40%', '50%', '60%', '70%', '80%', '90%', '100%', '120%', 'Full');

our @arp_motif=('Up  (L)',      'Up  (L&H)',      'Up  (_)',
                'Down  (L)',    'Down  (L&H)',    'Down  (_)',
                'Up/Down  (L)', 'Up/Down  (L&H)', 'Up/Down  (_)',
                'Random  (L)',                    'Random  (_)', 'Phrase');

our @arp_type=('001: Basic 1 (a)',      '002: Basic 2 (a)',      '003: Basic 3 (a)',    '004: Basic 4 (a)',    '005: Basic 5 (a)',    '006: Basic 6 (a)',
               '007: Seq Ptn 1 (2)',    '008: Seq Ptn 2 (2)',    '009: Seq Ptn 3 (2)',  '010: Seq Ptn 4 (2)',  '011: Seq Ptn 5 (2)',
               '012: Seq Ptn 6 (3)',    '013: Seq Ptn 7 (3)',    '014: Seq Ptn 8 (3)',  '015: Seq Ptn 9 (3)',  '016: Seq Ptn 10 (3)', '017: Seq Ptn 11 (3)',
               '018: Seq Ptn 12 (3)',   '019: Seq Ptn 13 (3)',   '020: Seq Ptn 14 (3)', '021: Seq Ptn 15 (3)', '022: Seq Ptn 16 (3)', '023: Seq Ptn 17 (3)',
               '024: Seq Ptn 18 (4)',   '025: Seq Ptn 19 (4)',   '026: Seq Ptn 20 (4)', '027: Seq Ptn 21 (4)', '028: Seq Ptn 22 (4)', '029: Seq Ptn 23 (4)',
               '030: Seq Ptn 24 (4)',   '031: Seq Ptn 25 (4)',   '032: Seq Ptn 26 (4)', '033: Seq Ptn 27 (4)', '034: Seq Ptn 28 (4)', '035: Seq Ptn 29 (4)',
               '036: Seq Ptn 30 (5)',   '037: Seq Ptn 31 (5)',
               '038: Seq Ptn 32 (6)',
               '039: Seq Ptn 33 (p)',   '040: Seq Ptn 34 (p)',   '041: Seq Ptn 35 (p)', '042: Seq Ptn 36 (p)', '043: Seq Ptn 37 (p)', '044: Seq Ptn 38 (p)',
               '045: Seq Ptn 39 (p)',   '046: Seq Ptn 40 (p)',   '047: Seq Ptn 41 (p)', '048: Seq Ptn 42 (p)', '049: Seq Ptn 43 (p)', '050: Seq Ptn 44 (p)',
               '051: Seq Ptn 45 (p)',   '052: Seq Ptn 46 (p)',   '053: Seq Ptn 47 (p)', '054: Seq Ptn 48 (p)', '055: Seq Ptn 49 (p)', '056: Seq Ptn 50 (p)',
               '057: Seq Ptn 51 (p)',   '058: Seq Ptn 52 (p)',   '059: Seq Ptn 53 (p)', '060: Seq Ptn 54 (p)', '061: Seq Ptn 55 (p)', '062: Seq Ptn 56 (p)',
               '063: Seq Ptn 57 (p)',   '064: Seq Ptn 58 (p)',   '065: Seq Ptn 59 (p)', '066: Seq Ptn 60 (p)',
               '067: Bassline 1 (1)',   '068: Bassline 2 (1)',   '069: Bassline 3 (1)', '070: Bassline 4 (1)', '071: Bassline 5 (1)', '072: Bassline 6 (1)',
               '073: Bassline 7 (1)',   '074: Bassline 8 (1)',   '075: Bassline 9 (1)',
               '076: Bassline 10 (2)',  '077: Bassline 11 (2)',  '078: Bassline 12 (2)','079: Bassline 13 (2)','080: Bassline 14 (2)','081: Bassline 15 (2)',
               '082: Bassline 16 (3)',  '083: Bassline 17 (3)',  '084: Bassline 18 (3)','085: Bassline 19 (3)','086: Bassline 20 (3)','087: Bassline 21 (3)',
               '088: Bassline 22 (p)',  '089: Bassline 23 (p)',  '090: Bassline 24 (p)','091: Bassline 25 (p)','092: Bassline 26 (p)','093: Bassline 27 (p)',
               '094: Bassline 28 (p)',  '095: Bassline 29 (p)',  '096: Bassline 30 (p)','097: Bassline 31 (p)','098: Bassline 32 (p)','099: Bassline 33 (p)',
               '100: Bassline 34 (p)',  '101: Bassline 35 (p)',  '102: Bassline 36 (p)','103: Bassline 37 (p)','104: Bassline 38 (p)','105: Bassline 39 (p)',
               '106: Bassline 40 (p)',  '107: Bassline 41 (p)',
               '108: Sliced 1 (a)',     '109: Sliced 2 (a)',     '110: Sliced 3 (a)',   '111: Sliced 4 (a)',   '112: Sliced 5 (a)',   '113: Sliced 6 (a)',
               '114: Sliced 7 (a)',     '115: Sliced 8 (a)',     '116: Sliced 9 (a)',   '117: Sliced 10 (a)',
               '118: Gtr Arp 1 (4)',    '119: Gtr Arp 2 (5)',    '120: Gtr Arp 3 (6)',
               '121: Gtr Backing 1 (a)','122: Gtr Backing 2 (a)',
               '123: Key Backing 1 (a)','124: Key Backing 2 (a)','125: Key Backing 3 (1-3)',
               '126: 1/1 Note Trg (1)', '127: 1/2 Note Trg (1)', '128: 1/4 Note Trg (1)');

our @ap_key=('C',  'Db',  'D',  'Eb',  'E',  'F',  'F#',  'G',  'Ab',  'A',  'Bb',  'B',
             'Cm', 'C#m', 'Dm', 'D#m', 'Em', 'Fm', 'F#m', 'Gm', 'G#m', 'Am', 'Bbm', 'Bm');

our @vc_hpf=('BYPASS', '1000 Hz', '1250 Hz', '1600 Hz', '2000 Hz', '2500 Hz', '3150 Hz',
             '4000 Hz', '5000 Hz', '6300 Hz', '8000 Hz', '10000 Hz', '12500 Hz', '16000 Hz');

my @AN_presets=(
'001: Toxic Bass 1', '002: Sub Bass 1',   '003: Backwards 1',  '004: Fat as That1', '005: Saw+Sub Bs 1', '006: Saw Bass 1',   '007: Pulse Bass 1',
'008: ResoSaw Bs 1', '009: ResoSaw Bs 2', '010: AcidSaw SEQ1', '011: Psy Bass 1',   '012: Dist TB Bs 1', '013: Sqr Bass 1',   '014: Tri Bass 1',
'015: Snake Glide1', '016: Soft Bass 1',  '017: Tear Drop 1',  '018: Slo worn 1',   '019: Dist LFO Bs1', '020: ResoPulseBs1', '021: Squelchy 1',
'022: DnB Wobbler1', '023: OffBeat Wob1', '024: Chilled Wob',  '025: Bouncy Bass1', '026: PulseOfLife1', '027: PWM Base 1',   '028: Pumper Bass1',
'029: ClickerBass1', '030: Psy Bass 2',   '031: HooverSuprt1', '032: Celoclip 1',   '033: Tri Fall Bs1', '034: 808 Bass 1',   '035: House Bass 1',
'036: Psy Bass 3',   '037: Reel 1',       '038: PortaSaw Ld1', '039: Porta Lead 1', '040: Analog Tp 1',  '041: Tri Lead 1',   '042: Sine Lead 1',
'043: Saw Buzz 1',   '044: Buzz Saw Ld1', '045: Laser Lead 1', '046: Saw & Per 1',  '047: Insect 1',     '048: Sqr SEQ 1',    '049: ZipPhase 1',
'050: Stinger 1',    '051: 3 Oh 3',       '052: Sus Zap 1',    '053: Bowouch 1',    '054: Resocut 1',    '055: LFO FX',       '056: Fall Synth 1',
'057: Twister 1',    '058: Analog Kick1', '059: Zippers 1',    '060: Zippers 2',    '061: Zippers 3',    '062: Siren Hell 1', '063: SirenFX/Mod1');

my @SN_presets=(
'001: JP8 Strings1', '002: Soft Pad 1',   '003: JP8 Strings2', '004: JUNO Str 1',   '005: Oct Strings',  '006: Brite Str 1',  '007: Boreal Pad',
'008: JP8 Strings3', '009: JP8 Strings4', '010: Hollow Pad 1', '011: LFO Pad 1',    '012: Hybrid Str',   '013: Awakening 1',  '014: Cincosoft 1',
'015: Bright Pad 1', '016: Analog Str 1', '017: Soft ResoPd1', '018: HPF Poly 1',   '019: BPF Poly',     '020: Sweep Pad 1',  '021: Soft Pad 2',
'022: Sweep JD 1',   '023: FltSweep Pd1', '024: HPF Pad',      '025: HPF SweepPd1', '026: KOff Pad',     '027: Sweep Pad 2',  '028: TrnsSweepPad',
'029: Revalation 1', '030: LFO CarvePd1', '031: RETROX 139 1', '032: LFO ResoPad1', '033: PLS Pad 1',    '034: PLS Pad 2',    '035: Trip 2 Mars1',
'036: Reso S&H Pd1', '037: SideChainPd1', '038: PXZoon 1',     '039: Psychoscilo1', '040: Fantasy 1',    '041: D-50 Stack 1', '042: Organ Pad',
'043: Bell Pad',     '044: Dreaming 1',   '045: Syn Sniper 1', '046: Strings 1',    '047: D-50 Pizz 1',  '048: Super Saw 1',  '049: S-SawStacLd1',
'050: Tekno Lead 1', '051: Tekno Lead 2', '052: Tekno Lead 3', '053: OSC-SyncLd 1', '054: WaveShapeLd1', '055: JD RingMod 1', '056: Buzz Lead 1',
'057: Buzz Lead 2',  '058: SawBuzz Ld 1', '059: Sqr Buzz Ld1', '060: Tekno Lead 4', '061: Dist Flt TB1', '062: Dist TB Sqr1', '063: Glideator 1',
'064: Vintager 1',   '065: Hover Lead 1', '066: Saw Lead 1',   '067: Saw+Tri Lead', '068: PortaSaw Ld1', '069: Reso Saw Ld',  '070: SawTrap Ld 1',
'071: Fat GR Lead',  '072: Pulstar Ld',   '073: Slow Lead',    '074: AnaVox Lead',  '075: Square Ld 1',  '076: Square Ld 2',  '077: Sqr Lead 1',
'078: Sqr Trap Ld1', '079: Sine Lead 1',  '080: Tri Lead',     '081: Tri Stac Ld1', '082: 5th SawLead1', '083: Sweet 5th 1',  '084: 4th Syn Lead',
'085: Maj Stack Ld', '086: MinStack Ld1', '087: Chubby Lead1', '088: CuttingLead1', '089: Seq Bass 1',   '090: Reso Bass 1',  '091: TB Bass 1',
'092: 106 Bass 1',   '093: FilterEnvBs1', '094: JUNO Sqr Bs1', '095: Reso Bass 2',  '096: JUNO Bass',    '097: MG Bass 1',    '098: 106 Bass 3',
'099: Reso Bass 3',  '100: Detune Bs 1',  '101: MKS-50 Bass1', '102: Sweep Bass',   '103: MG Bass 2',    '104: MG Bass 3',    '105: ResRubber Bs',
'106: R&B Bass 1',   '107: Reso Bass 4',  '108: Wide Bass 1',  '109: Chow Bass 1',  '110: Chow Bass 2',  '111: SqrFilterBs1', '112: Reso Bass 5',
'113: Syn Bass 1',   '114: ResoSawSynBs', '115: Filter Bass1', '116: SeqFltEnvBs',  '117: DnB Bass 1',   '118: UnisonSynBs1', '119: Modular Bs',
'120: Monster Bs 1', '121: Monster Bs 2', '122: Monster Bs 3', '123: Monster Bs 4', '124: Square Bs 1',  '125: 106 Bass 2',   '126: 5th Stac Bs1',
'127: SqrStacSynBs', '128: MC-202 Bs',    '129: TB Bass 2',    '130: Square Bs 2',  '131: SH-101 Bs',    '132: R&B Bass 2',   '133: MG Bass 4',
'134: Seq Bass 2',   '135: Tri Bass 1',   '136: BPF Syn Bs 2', '137: BPF Syn Bs 1', '138: Low Bass 1',   '139: Low Bass 2',   '140: Kick Bass 1',
'141: SinDetuneBs1', '142: Organ Bass 1', '143: Growl Bass 1', '144: Talking Bs 1', '145: LFO Bass 1',   '146: LFO Bass 2',   '147: Crack Bass',
'148: Wobble Bs 1',  '149: Wobble Bs 2',  '150: Wobble Bs 3',  '151: Wobble Bs 4',  '152: SideChainBs1', '153: SideChainBs2', '154: House Bass 1',
'155: FM Bass',      '156: 4Op FM Bass1', '157: Ac. Bass',     '158: Fingerd Bs 1', '159: Picked Bass',  '160: Fretless Bs',  '161: Slap Bass 1',
'162: JD Piano 1',   '163: E. Grand 1',   '164: Trem EP 1',    '165: FM E.Piano 1', '166: FM E.Piano 2', '167: Vib Wurly 1',  '168: Pulse Clav',
'169: Clav',         '170: 70\'s E.Organ','171: House Org 1',  '172: House Org 2',  '173: Bell 1',       '174: Bell 2',       '175: Organ Bell',
'176: Vibraphone 1', '177: Steel Drum',   '178: Harp 1',       '179: Ac. Guitar',   '180: Bright Strat', '181: Funk Guitar1', '182: Jazz Guitar',
'183: Dist Guitar1', '184: D. Mute Gtr1', '185: E. Sitar',     '186: Sitar Drone',  '187: FX 1',         '188: FX 2',         '189: FX 3',
'190: Tuned Winds1', '191: Bend Lead 1',  '192: RiSER 1',      '193: Rising SEQ 1', '194: Scream Saw',   '195: Noise SEQ 1',  '196: Syn Vox 1',
'197: JD SoftVox',   '198: Vox Pad',      '199: VP-330 Chr',   '200: Orch Hit',     '201: Philly Hit',   '202: House Hit',    '203: O\'Skool Hit1',
'204: Punch Hit',    '205: Tao Hit',      '206: SEQ Saw 1',    '207: SEQ Sqr',      '208: SEQ Tri 1',    '209: SEQ 1',        '210: SEQ 2',
'211: SEQ 3',        '212: SEQ 4',        '213: Sqr Reso Plk', '214: Pluck Synth1', '215: Paperclip 1',  '216: Sonar Pluck1', '217: SqrTrapPlk 1',
'218: TB Saw Seq 1', '219: TB Sqr Seq 1', '220: JUNO Key',     '221: Analog Poly1', '222: Analog Poly2', '223: Analog Poly3', '224: Analog Poly4',
'225: JUNO Octavr1', '226: EDM Synth 1',  '227: Super Saw 2',  '228: S-Saw Poly',   '229: Trance Key 1', '230: S-Saw Pad 1',  '231: 7th Stac Syn',
'232: S-SawStc Syn', '233: Trance Key 2', '234: Analog Brass', '235: Reso Brass',   '236: Soft Brass 1', '237: FM Brass',     '238: Syn Brass 1',
'239: Syn Brass 2',  '240: JP8 Brass',    '241: Soft SynBrs1', '242: Soft SynBrs2', '243: EpicSlow Brs', '244: JUNO Brass',   '245: Poly Brass',
'246: Voc:Ensemble', '247: Voc:5thStack', '248: Voc:Robot',    '249: Voc:Saw',      '250: Voc:Sqr',      '251: Voc:Rise Up',  '252: Voc:Auto Vib',
'253: Voc:PitchEnv', '254: Voc:VP-330',   '255: Voc:Noise');

my @DR_presets=(
'001: TR-909 Kit 1', '002: TR-808 Kit 1', '003: 707&727 Kit1', '004: CR-78 Kit 1',  '005: TR-606 Kit 1', '006: TR-626 Kit 1', '007: EDM Kit 1',
'008: Drum&Bs Kit1', '009: Techno Kit 1', '010: House Kit 1',  '011: Hiphop Kit 1', '012: R&B Kit 1',    '013: TR-909 Kit 2', '014: TR-909 Kit 3',
'015: TR-808 Kit 2', '016: TR-808 Kit 3', '017: TR-808 Kit 4', '018: 808&909 Kit1', '019: 808&909 Kit2', '020: 707&727 Kit2', '021: 909&7*7 Kit1',
'022: 808&7*7 Kit1', '023: EDM Kit 2',    '024: Techno Kit 2', '025: Hiphop Kit 2', '026: 80\'s Kit 1',  '027: 90\'s Kit 1',  '028: Noise Kit 1',
'029: Pop Kit 1',    '030: Pop Kit 2',    '031: Rock Kit',     '032: Jazz Kit',     '033: Latin Kit');

our @PCMwaves=( '000: --- OFF ---',
'001: Calc.Saw',     '002: DistSaw Wave', '003: GR-300 Saw',   '004: Lead Wave 1',  '005: Lead Wave 2',  '006: Unison Saw',   '007: Saw+Sub Wave',
'008: SqrLeadWave',  '009: SqrLeadWave+', '010: FeedbackWave', '011: Bad Axe',      '012: Cutting Lead', '013: DistTB Sqr',   '014: Sync Sweep',
'015: Saw Sync',     '016: Unison Sync+', '017: Sync Wave',    '018: Cutters',      '019: Nasty',        '020: Bagpipe Wave', '021: Wave Scan',
'022: Wire String',  '023: Lead Wave 3',  '024: PWM Wave 1',   '025: PWM Wave 2',   '026: MIDI Clav',    '027: Huge MIDI',    '028: Wobble Bs 1',
'029: Wobble Bs 2',  '030: Hollow Bass',  '031: SynBs Wave',   '032: Solid Bass',   '033: House Bass',   '034: 4OP FM Bass',  '035: Fine Wine',
'036: Bell Wave 1',  '037: Bell Wave 1+', '038: Bell Wave 2',  '039: Digi Wave 1',  '040: Digi Wave 2',  '041: Org Bell',     '042: Gamelan',
'043: Crystal',      '044: Finger Bell',  '045: DipthongWave', '046: DipthongWv +', '047: Hollo Wave1',  '048: Hollo Wave2',  '049: Hollo Wave2+',
'050: Heaven Wave',  '051: Doo',          '052: MMM Vox',      '053: Eeh Formant',  '054: Iih Formant',  '055: Syn Vox 1',    '056: Syn Vox 2',
'057: Org Vox',      '058: Male Ooh',     '059: LargeChrF 1',  '060: LargeChrF 2',  '061: Female Oohs',  '062: Female Aahs',  '063: Atmospheric',
'064: Air Pad 1',    '065: Air Pad 2',    '066: Air Pad 3',    '067: VP-330 Choir', '068: SynStrings 1', '069: SynStrings 2', '070: SynStrings 3',
'071: SynStrings 4', '072: SynStrings 5', '073: SynStrings 6', '074: Revalation',   '075: Alan\'s Pad',  '076: LFO Poly',     '077: Boreal Pad L',
'078: Boreal Pad R', '079: HPF Pad L',    '080: HPF Pad R',    '081: Sweep Pad',    '082: Chubby Ld',    '083: Fantasy Pad',  '084: Legend Pad',
'085: D-50 Stack',   '086: ChrdOfCnadaL', '087: ChrdOfCnadaR', '088: Fireflies',    '089: JazzyBubbles', '090: SynthFx 1',    '091: SynthFx 2',
'092: X-Mod Wave 1', '093: X-Mod Wave 2', '094: SynVox Noise', '095: Dentist Nz',   '096: Atmosphere',   '097: Anklungs',     '098: Xylo Seq',
'099: O\'Skool Hit', '100: Orch. Hit',    '101: Punch Hit',    '102: Philly Hit',   '103: ClassicHseHt', '104: Tao Hit',      '105: Smear Hit',
'106: 808 Kick 1Lp', '107: 808 Kick 2Lp', '108: 909 Kick Lp',  '109: JD Piano',     '110: E.Grand',      '111: Stage EP',     '112: Wurly',
'113: EP Hard',      '114: FM EP 1',      '115: FM EP 2',      '116: FM EP 3',      '117: Harpsi Wave',  '118: Clav Wave 1',  '119: Clav Wave 2',
'120: Vibe Wave',    '121: Organ Wave 1', '122: Organ Wave 2', '123: PercOrgan 1',  '124: PercOrgan 2',  '125: Vint.Organ',   '126: Harmonica',
'127: Ac. Guitar',   '128: Nylon Gtr',    '129: Brt Strat',    '130: Funk Guitar',  '131: Jazz Guitar',  '132: Dist Guitar',  '133: D.Mute Gtr',
'134: FatAc. Bass',  '135: Fingerd Bass', '136: Picked Bass',  '137: Fretless Bs',  '138: Slap Bass',    '139: Strings 1',    '140: Strings 2',
'141: Strings 3 L',  '142: Strings 3 R',  '143: Pizzagogo',    '144: Harp Harm',    '145: Harp Wave',    '146: PopBrsAtk',    '147: PopBrass',
'148: Tp Section',   '149: Studio Tp',    '150: Tp Vib Mari',  '151: Tp Hrmn Mt',   '152: FM Brass',     '153: Trombone',     '154: Wide Sax',
'155: Flute Wave',   '156: Flute Push',   '157: E.Sitar',      '158: Sitar Drone',  '159: Agogo',        '160: Steel Drums');

our @DRMwaves=('000: --- OFF ---',
'001: 78 Kick P',    '002: 606 Kick P',   '003: 808 Kick 1aP', '004: 808 Kick 1bP', '005: 808 Kick 1cP', '006: 808 Kick 2aP', '007: 808 Kick 2bP',
'008: 808 Kick 2cP', '009: 808 Kick 3aP', '010: 808 Kick 3bP', '011: 808 Kick 3cP', '012: 808 Kick 4aP', '013: 808 Kick 4bP', '014: 808 Kick 4cP',
'015: 808 Kick 1Lp', '016: 808 Kick 2Lp', '017: 909 Kick 1aP', '018: 909 Kick 1bP', '019: 909 Kick 1cP', '020: 909 Kick 2bP', '021: 909 Kick 2cP',
'022: 909 Kick 3P',  '023: 909 Kick 4',   '024: 909 Kick 5',   '025: 909 Kick 6',   '026: 909 DstKickP', '027: 909 Kick Lp',  '028: 707 Kick 1 P',
'029: 707 Kick 2 P', '030: 626 Kick 1 P', '031: 626 Kick 2 P', '032: Analog Kick1', '033: Analog Kick2', '034: Analog Kick3', '035: Analog Kick4',
'036: Analog Kick5', '037: PlasticKick1', '038: PlasticKick2', '039: Synth Kick 1', '040: Synth Kick 2', '041: Synth Kick 3', '042: Synth Kick 4',
'043: Synth Kick 5', '044: Synth Kick 6', '045: Synth Kick 7', '046: Synth Kick 8', '047: Synth Kick 9', '048: Synth Kick10', '049: Synth Kick11',
'050: Synth Kick12', '051: Synth Kick13', '052: Synth Kick14', '053: Synth Kick15', '054: Vint Kick P',  '055: Jungle KickP', '056: HashKick 1 P',
'057: HashKick 2 P', '058: Lite Kick P',  '059: Dry Kick 1',   '060: Dry Kick 2',   '061: Tight Kick P', '062: Old Kick',     '063: Warm Kick P',
'064: Hush Kick P',  '065: Power Kick',   '066: Break Kick',   '067: Turbo Kick',   '068: TM-2 Kick 1',  '069: TM-2 Kick 2',  '070: PurePhatKckP',
'071: Bright KickP', '072: LoBit Kick1P', '073: LoBit Kick2P', '074: Dance Kick P', '075: Hip Kick P',   '076: HipHop Kick',  '077: Mix Kick 1',
'078: Mix Kick 2',   '079: Wide Kick P',  '080: LD Kick P',    '081: SF Kick 1 P',  '082: SF Kick 2 P',  '083: TY Kick P',    '084: WD Kick P',
'085: Reg.Kick P',   '086: Rock Kick P',  '087: Jz Dry Kick',  '088: Jazz Kick P',  '089: 78 Snr',       '090: 606 Snr 1 P',  '091: 606 Snr 2 P',
'092: 808 Snr 1a P', '093: 808 Snr 1b P', '094: 808 Snr 1c P', '095: 808 Snr 2a P', '096: 808 Snr 2b P', '097: 808 Snr 2c P', '098: 808 Snr 3a P',
'099: 808 Snr 3b P', '100: 808 Snr 3c P', '101: 909 Snr 1a P', '102: 909 Snr 1b P', '103: 909 Snr 1c P', '104: 909 Snr 1d P', '105: 909 Snr 2a P',
'106: 909 Snr 2b P', '107: 909 Snr 2c P', '108: 909 Snr 2d P', '109: 909 Snr 3a P', '110: 909 Snr 3b P', '111: 909 Snr 3c P', '112: 909 Snr 3d P',
'113: 909 DstSnr1P', '114: 909 DstSnr2P', '115: 909 DstSnr3P', '116: 707 Snr 1a P', '117: 707 Snr 2a P', '118: 707 Snr 1b P', '119: 707 Snr 2b P',
'120: 626 Snr 1',    '121: 626 Snr 2',    '122: 626 Snr 3',    '123: 626 Snr 1a P', '124: 626 Snr 3a P', '125: 626 Snr 1b P', '126: 626 Snr 2 P',
'127: 626 Snr 3b P', '128: Analog Snr 1', '129: Analog Snr 2', '130: Analog Snr 3', '131: Synth Snr 1',  '132: Synth Snr 2',  '133: 106 Snr',
'134: Sim Snare',    '135: Jungle Snr 1', '136: Jungle Snr 2', '137: Jungle Snr 3', '138: Lite Snare',   '139: Lo-Bit Snr1P', '140: Lo-Bit Snr2P',
'141: HphpJazzSnrP', '142: PurePhatSnrP', '143: DRDisco SnrP', '144: Ragga Snr',    '145: Lo-Fi Snare',  '146: DR Snare',     '147: DanceHallSnr',
'148: Break Snr',    '149: Piccolo SnrP', '150: TM-2 Snr 1',   '151: TM-2 Snr 2',   '152: WoodSnr RS',   '153: LD Snr',       '154: SF Snr P',
'155: TY Snr',       '156: WD Snr P',     '157: Tight Snr',    '158: Reg.Snr1 P',   '159: Reg.Snr2 P',   '160: Ballad Snr P', '161: Rock Snr1 P',
'162: Rock Snr2 P',  '163: LD Rim',       '164: SF Rim',       '165: TY Rim',       '166: WD Rim P',     '167: Jazz Snr P',   '168: Jazz Rim P',
'169: Jz BrshSlapP', '170: Jz BrshSwshP', '171: Swish&Trn P',  '172: 78 Rimshot',   '173: 808 RimshotP', '174: 909 RimshotP', '175: 707 Rimshot',
'176: 626 Rimshot',  '177: Vint Stick P', '178: Lo-Bit Stk P', '179: Hard Stick P', '180: Wild Stick P', '181: LD Cstick',    '182: TY Cstick',
'183: WD Cstick',    '184: 606 H.Tom P',  '185: 808 H.Tom P',  '186: 909 H.Tom P',  '187: 707 H.Tom P',  '188: 626 H.Tom 1',  '189: 626 H.Tom 2',
'190: SimV Tom 1 P', '191: LD H.Tom P',   '192: SF H.Tom P',   '193: TY H.Tom P',   '194: 808 M.Tom P',  '195: 909 M.Tom P',  '196: 707 M.Tom P',
'197: 626 M.Tom 1',  '198: 626 M.Tom 2',  '199: SimV Tom 2 P', '200: LD M.Tom P',   '201: SF M.Tom P',   '202: TY M.Tom P',   '203: 606 L.Tom P',
'204: 808 L.Tom P',  '205: 909 L.Tom P',  '206: 707 L.Tom P',  '207: 626 L.Tom 1',  '208: 626 L.Tom 2',  '209: SimV Tom 3 P', '210: SimV Tom 4 P',
'211: LD L.Tom P',   '212: SF L.Tom P',   '213: TY L.Tom P',   '214: 78 CHH',       '215: 606 CHH',      '216: 808 CHH',      '217: 909 CHH 1',
'218: 909 CHH 2',    '219: 909 CHH 3',    '220: 909 CHH 4',    '221: 707 CHH',      '222: 626 CHH',      '223: HipHop CHH',   '224: Lite CHH',
'225: Reg.CHH',      '226: Rock CHH',     '227: S13 CHH Tip',  '228: S14 CHH Tip',  '229: 606 C&OHH',    '230: 808 C&OHH S',  '231: 808 C&OHH L',
'232: Hip PHH',      '233: Reg.PHH',      '234: Rock PHH',     '235: S13 PHH',      '236: S14 PHH',      '237: 606 OHH',      '238: 808 OHH S',
'239: 808 OHH L',    '240: 909 OHH 1',    '241: 909 OHH 2',    '242: 909 OHH 3',    '243: 707 OHH',      '244: 626 OHH',      '245: HipHop OHH',
'246: Lite OHH',     '247: Reg.OHH',      '248: Rock OHH',     '249: S13 OHH Shft', '250: S14 OHH Shft', '251: 78 Cymbal',    '252: 606 Cymbal',
'253: 808 Cymbal 1', '254: 808 Cymbal 2', '255: 808 Cymbal 3', '256: 909 CrashCym', '257: 909 Rev Cym',  '258: MG Nz Cym',    '259: 707 CrashCym',
'260: 626 CrashCym', '261: Crash Cym 1',  '262: Crash Cym 2',  '263: Rock Crash 1', '264: Rock Crash 2', '265: P17 CrashTip', '266: S18 CrashTip',
'267: Z18kCrashSft', '268: Jazz Crash',   '269: 909 RideCym',  '270: 707 RideCym',  '271: 626 RideCym',  '272: Ride Cymbal',  '273: 626 ChinaCym',
'274: China Cymbal', '275: Splash Cym',   '276: 626 Cup',      '277: Rock Rd Cup',  '278: 808 ClapS1 P', '279: 808 ClapS2 P', '280: 808 ClapL1 P',
'281: 808 ClapL2 P', '282: 909 Clap 1 P', '283: 909 Clap 2 P', '284: 909 Clap 3 P', '285: 909 DstClapP', '286: 707 Clap P',   '287: 626 Clap',
'288: R8 Clap',      '289: Cheap Clap',   '290: Old Clap P',   '291: Hip Clap',     '292: Dist Clap',    '293: Hand Clap',    '294: Club Clap',
'295: Real Clap',    '296: Funk Clap',    '297: Bright Clap',  '298: TM-2 Clap',    '299: Amb Clap',     '300: Disc Clap',    '301: Claptail',
'302: Gospel Clap',  '303: 78 Tamb',      '304: 707 Tamb P',   '305: 626 Tamb',     '306: TM-2 Tamb',    '307: Tamborine 1',  '308: Tamborine 2',
'309: Tamborine 3',  '310: 808 CowbellP', '311: 707 Cowbell',  '312: 626 Cowbell',  '313: Cowbell Mute', '314: 78 H.Bongo P', '315: 727 H.Bongo',
'316: Bongo Hi Mt',  '317: Bongo Hi Slp', '318: Bongo Hi Op',  '319: 78 L.Bongo P', '320: 727 L.Bongo',  '321: Bongo Lo Op',  '322: Bongo Lo Slp',
'323: 808 H.CongaP', '324: 727 H.CngOpP', '325: 727 H.CngMtP', '326: 626 H.CngaOp', '327: 626 H.CngaMt', '328: Conga Hi Mt',  '329: Conga 2H Mt',
'330: Conga Hi Slp', '331: Conga 2H Slp', '332: Conga Hi Op',  '333: Conga 2H Op',  '334: 808 M.CongaP', '335: 78 L.Conga P', '336: 808 L.CongaP',
'337: 727 L.CongaP', '338: 626 L.Conga',  '339: Conga Lo Mt',  '340: Conga Lo Slp', '341: Conga Lo Op',  '342: Conga 2L Mt',  '343: Conga 2L Op',
'344: Conga Slp Op', '345: Conga Efx',    '346: Conga Thumb',  '347: 727 H.Timbal', '348: 626 H.Timbal', '349: 727 L.Timbal', '350: 626 L.Timbal',
'351: Timbale 1',    '352: Timbale 2',    '353: Timbale 3',    '354: Timbale 4',    '355: Timbles LoOp', '356: Timbles LoMt', '357: TimbalesHand',
'358: Timbales Rim', '359: TmbSideStick', '360: 727 H.Agogo',  '361: 626 H.Agogo',  '362: 727 L.Agogo',  '363: 626 L.Agogo',  '364: 727 Cabasa P',
'365: Cabasa Up',    '366: Cabasa Down',  '367: Cabasa Cut',   '368: 78 Maracas P', '369: 808 MaracasP', '370: 727 MaracasP', '371: Maracas',
'372: 727 WhistleS', '373: 727 WhistleL', '374: Whistle',      '375: 78 Guiro S',   '376: 78 Guiro L',   '377: Guiro',        '378: Guiro Long',
'379: 78 Claves P',  '380: 808 Claves P', '381: 626 Claves',   '382: Claves',       '383: Wood Block',   '384: Triangle',     '385: 78 MetalBt P',
'386: 727 StrChime', '387: 626 Shaker',   '388: Shaker',       '389: Finger Snap',  '390: Club FinSnap', '391: Snap',         '392: Group Snap',
'393: Op Pandeiro',  '394: Mt Pandeiro',  '395: PandeiroOp',   '396: PandeiroMt',   '397: PandeiroHit',  '398: PandeiroRim',  '399: PandeiroCrsh',
'400: PandeiroRoll', '401: 727 Quijada',  '402: TablaBayam 1', '403: TablaBayam 2', '404: TablaBayam 3', '405: TablaBayam 4', '406: TablaBayam 5',
'407: TablaBayam 6', '408: TablaBayam 7', '409: Udo',          '410: Udu Pot Hi',   '411: Udu Pot Slp',  '412: Scratch 1',    '413: Scratch 2',
'414: Scratch 3',    '415: Scratch 4',    '416: Scratch 5',    '417: Dance M',      '418: Ahh M',        '419: Let\'s Go M',  '420: Hah F',
'421: Yeah F',       '422: C\'mon Baby F','423: Wooh F',       '424: White Noise',  '425: Pink Noise',   '426: Atmosphere',   '427: PercOrgan 1',
'428: PercOrgan 2',  '429: TB Blip',      '430: D.Mute Gtr',   '431: Flute Fx',     '432: Pop Brs Atk',  '433: Strings Hit',  '434: Smear Hit',
'435: O\'Skool Hit', '436: Orch. Hit',    '437: Punch Hit',    '438: Philly Hit',   '439: ClassicHseHt', '440: Tao Hit',      '441: MG S Zap 1',
'442: MG S Zap 2',   '443: MG S Zap 3',   '444: SH2 S Zap 1',  '445: SH2 S Zap 2',  '446: SH2 S Zap 3',  '447: SH2 S Zap 4',  '448: SH2 S Zap 5',
'449: SH2 U Zap 1',  '450: SH2 U Zap 2',  '451: SH2 U Zap 3',  '452: SH2 U Zap 4',  '453: SH2 U Zap 5');

# Analog part data structure
our @ANdata;
our %AN=(
type     => 'AN',
key      => ['AN'],
msb      => '1942',
addr     => ["\x19\x42\x00\x00"],                                # Sysex start address of tone data
rqlen    => ["\x00\x00\x00\x40"],                                # Length of sysex tone data to request
transf64 => ['(18|19|20|23|24|27|30|36|41|44|52|56|57|58|59)'],  # AN tone parameters with 64 transformation
transf10 => ['(34|43)'],                                         # AN tone parameters with 64/10 transformation
transf4  => [''],
transf_01=> [''],
transf_10=> [''],
MIDIch   => 2,                                                   # default MIDI channel 3 for AN synth part
pattern  => [''],
name     => ['AN Name'],
filename => '',
fnprefix => 'JDXi-AN-',
filetype => 'Analog Synth Tone',
okedext  => 'as',
filelen  => 78,
modified => 0,
ct       => {a=>0},                    # Hash of flags to avoid sending MIDI messages when sliders are initialised
titlestr => 'JDXi Manager - Analog Synth Editor',
window   => '',
geometry => '900x612',
data     => [\@ANdata],
datalen  => [64],
presets  => \@AN_presets,
selpreset=> $AN_presets[0],
dumpto   => '',
readfrom => '',
storeto  => '',
inittone => ["\x49\x6E\x69\x74\x20\x54\x6F\x6E\x65\x20\x20\x20\x00\x00\x35\x00".
             "\x00\x11\x40\x40\x40\x01\x00\x40\x40\x00\x00\x40\x00\x00\x40\x00".
             "\x01\x7F\x40\x00\x40\x00\x00\x7F\x00\x40\x7F\x40\x40\x00\x00\x7F".
             "\x00\x00\x28\x00\x40\x02\x02\x00\x50\x40\x40\x52\x00\x00\x00\x00"]
);
# AN Tone Format: F0 41 xx 00 00 00 0E 12 <4 byte addr> <64 bytes of patch data> <checksum> F7
$AN{pattern}[0]=$Xi_header.$AN{addr}[0].                                                                          # 12 header + addr
                '[\x00,\x0D,\x20-\x7E]{12}\x00'.                                                                  # 13 tone name + reserve
                '[\x00-\x05][\x00-\x7F]{2}[\x00-\x01][\x00-\x13][\x01-\x7F]{3}[\x00-\x01]'.                       #  9 LFO
                '[\x00-\x02][\x28-\x58][\x0E-\x72][\x00-\x7F]{2}[\x01-\x7F][\x00-\x7F]{2}[\x01-\x7F][\x00-\x02]'. # 10 OSC
                '[\x00-\x01][\x00-\x7F][\x36-\x4A][\x00-\x7F][\x01-\x7F][\x00-\x7F]{4}[\x01-\x7F]'.               # 10 Filter
                '[\x00-\x7F][\x36-\x4A][\x01-\x7F][\x00-\x7F]{4}'.                                                #  7 AMP
                '[\x00-\x01][\x00-\x7F][\x00-\x01][\x3D-\x43][\x00-\x18]{2}\x00'.                                 #  7 Common + reserve
                '[\x01-\x7F]{4}\x00{4}'.                                                                          #  8 LFO Mod Ctrl + reserve
                '[\x00-\x7F]\xF7';                                                                                #  2 checksum + F7

our @AN_rnd=([ 48, 57],[ 48, 57],[ 48, 57],[ 48, 57],[ 48, 57],[  0,  0],
             [  0,  5],[  0,127],[  0,127],[  0,  1],[  0, 19],[  1,127],[  1,127],[  1,127],[  0,  1],
             [  0,  2],[ 64, 64],[ 64, 64],[  0,127],[  0,127],[  1,127],[  0,127],[  0,127],[  1,127],[  0,  2],
             [  0,  1],[  0,127],[ 54, 74],[  0,127],[  1,127],[  0,127],[  0,127],[  0,127],[  0,127],[  1,127],
             [120,120],[ 64, 64],[ 64, 64],[  0,127],[  0,127],[  0,127],[  0,127],
             [  0,  1],[  0,127],[  0,  1],[ 64, 64],[  0, 24],[  0, 24],[  0,  0],
             [  1,127],[  1,127],[  1,127],[  1,127]);

# initialise SN data arrays
our @SN_COM; our @SN_MOD; our @SN_PL;
for my $i (1..2) { $SN_COM[$i][0]=0; $SN_MOD[$i][0]=0; for my $n (0..2) { $SN_PL[$i][$n][0]=0 } }

# Digital Synth 1 part data structure
our %SN1=(
type     => 'SN1',
key      => ['COM','P1','P2','P3','MOD'],
msb      => '1901',
addr     => ["\x19\x01\x00\x00", "\x19\x01\x20\x00", "\x19\x01\x21\x00", "\x19\x01\x22\x00", "\x19\x01\x50\x00"],
rqlen    => ["\x00\x00\x00\x40", ("\x00\x00\x00\x3D")x3, "\x00\x00\x00\x25"],
transf64 => ['(21)', ('(3|4|9|14|20|22|27|34|35|36|37|44|45|46|47|48|49|59)')x3, ''],
transf10 => ['', ('(13|60)')x3, ''],
transf4  => ['', ('53')x3, ''],
transf_01=> ['', ('')x3, ''],
transf_10=> ['', ('')x3, ''],
MIDIch   => 0,
pattern  => [('')x5 ],
name     => ['SN1 Name', ("\x00")x4 ],
filename => '',
fnprefix => 'JDXi-SN-',
filetype => 'Digital Synth Tone',
okedext  => 'ds',
filelen  => 354,
modified => 0,
ct       => {a=>0},
curpart  => '',
titlestr => 'JDXi Manager - Digital Synth 1 Editor',
window   => '',
geometry => '1150x740',
data     => [$SN_COM[1], $SN_PL[1][0], $SN_PL[1][1], $SN_PL[1][2], $SN_MOD[1]],
datalen  => [64, (61)x3, 37],
presets  => \@SN_presets,
selpreset=> $SN_presets[0],
dumpto   => '',
readfrom => '',
storeto  => '',
ldprwgt  => ['',''],
inittone => ["\x49\x6E\x69\x74\x20\x54\x6F\x6E\x65\x20\x20\x20\x64\x00\x07\x08\x00\x00\x00\x14\x00\x40\x02\x02\x00\x01\x01\x00\x00\x00\x00\x00".
             "\x00\x00\x00\x00\x18\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x01\x01\x00\x00\x27\x00\x00\x00\x00\x40\x03\x40\x40\x40",
             "\x00\x00\x00\x40\x40\x00\x00\x00\x00\x40\x01\x01\x7F\x40\x40\x00\x00\x24\x00\x00\x40\x64\x53\x00\x00\x7F\x00\x40\x00\x51\x00\x11".
             "\x00\x00\x40\x40\x40\x40\x00\x58\x00\x11\x7F\x00\x50\x40\x40\x40\x49\x4A\x40\x40\x01\x00\x00\x00\x0E\x00\x00\x52\x40",
             "\x01\x00\x00\x40\x40\x00\x00\x00\x00\x40\x01\x01\x7F\x40\x40\x00\x00\x24\x00\x00\x40\x64\x53\x00\x00\x7F\x00\x40\x00\x51\x00\x11".
             "\x00\x00\x40\x40\x40\x40\x00\x58\x00\x11\x7F\x00\x50\x40\x40\x40\x49\x4A\x40\x40\x01\x00\x00\x00\x0E\x00\x00\x52\x40",
             "\x07\x00\x00\x40\x40\x00\x00\x00\x00\x40\x01\x01\x7F\x40\x40\x00\x00\x24\x00\x00\x40\x64\x53\x00\x00\x7F\x00\x40\x00\x51\x00\x11".
             "\x00\x00\x40\x40\x40\x40\x00\x58\x00\x11\x7F\x00\x50\x40\x40\x40\x49\x4A\x40\x40\x01\x00\x00\x00\x0E\x00\x00\x52\x40",
             "\x07\x00\x00\x00\x00\x0B\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00".
             "\x00\x00\x00\x00\x00"]
);

# Digital Synth 2 part data structure
our %SN2=(
type     => 'SN2',
key      => ['COM','P1','P2','P3','MOD'],
msb      => '1921',
addr     => ["\x19\x21\x00\x00", "\x19\x21\x20\x00", "\x19\x21\x21\x00", "\x19\x21\x22\x00", "\x19\x21\x50\x00"],
rqlen    => ["\x00\x00\x00\x40", ("\x00\x00\x00\x3D")x3, "\x00\x00\x00\x25"],
transf64 => ['(21)', ('(3|4|9|14|20|22|27|34|35|36|37|44|45|46|47|48|49|59)')x3, ''],
transf10 => ['', ('(13|60)')x3, ''],
transf4  => ['', ('53')x3, ''],
transf_01=> ['', ('')x3, ''],
transf_10=> ['', ('')x3, ''],
MIDIch   => 1,
pattern  => [('')x5 ],
name     => ['SN2 Name', ("\x00")x4 ],
filename => '',
fnprefix => 'JDXi-SN-',
filetype => 'Digital Synth Tone',
okedext  => 'ds',
filelen  => 354,
modified => 0,
ct       => {a=>0},
curpart  => '',
titlestr => 'JDXi Manager - Digital Synth 2 Editor',
window   => '',
geometry => '1150x740',
data     => [$SN_COM[2], $SN_PL[2][0], $SN_PL[2][1], $SN_PL[2][2], $SN_MOD[2]],
datalen  => [64, (61)x3, 37],
presets  => \@SN_presets,
selpreset=> $SN_presets[0],
dumpto   => '',
readfrom => '',
storeto  => '',
ldprwgt  => ['',''],
inittone => [$SN1{inittone}[0], $SN1{inittone}[1], $SN1{inittone}[2], $SN1{inittone}[3], $SN1{inittone}[4]]
);
our @SN=('', \%SN1, \%SN2);

#$SN1{pattern}[0]=$Xi_header.$SN1{addr}[0].
#                 '[\x00,\x0D,\x20-\x7E]{12}[\x00-\x7F]\x00{5}[\x00-\x01][\x00-\x7F][\x00-\x01][\x3D-\x43][\x00-\x18]{2}\x00[\x00-\x01]{6}[\x00-\x02]'.
#                 '\x00{3}[\x00-\x01]\x00{2}[\x00-\x01]{2}\x00[\x00-\x7F]{3}\x00{5}[\x00-\x03][\x00-\x7F]{3}'.
#                 '[\x00-\x7F]\xF7';
$SN1{pattern}[0]=$Xi_header.'('.$SN1{addr}[0].'|'.$SN2{addr}[0].')[\x00,\x0D,\x20-\x7E]{12}[\x00-\x7F]{53}\xF7';
$SN1{pattern}[1]=$Xi_header.'('.$SN1{addr}[1].'|'.$SN2{addr}[1].')[\x00-\x7F]{62}\xF7';
$SN1{pattern}[2]=$Xi_header.'('.$SN1{addr}[2].'|'.$SN2{addr}[2].')[\x00-\x7F]{62}\xF7';
$SN1{pattern}[3]=$Xi_header.'('.$SN1{addr}[3].'|'.$SN2{addr}[3].')[\x00-\x7F]{62}\xF7';
$SN1{pattern}[4]=$Xi_header.'('.$SN1{addr}[4].'|'.$SN2{addr}[4].')[\x00-\x7F]{38}\xF7';
for my $n (0..4) { $SN2{pattern}[$n]=$SN1{pattern}[$n]; }

# Drums part data structure
our @DRdata;
for my $n (0..38) { $DRdata[$n][0]=''; }
our %DR=(
type     => 'DR',
key      => ['COM',  'BD1',  'RIM',  'BD2',  'CLAP', 'BD3',  'SD1',  'CHH',  'SD2',  'PHH',  'SD3', 'OHH',  'SD4', 'TOM1',
             'PRC1', 'TOM2', 'PRC2', 'TOM3', 'PRC3', 'CYM1', 'PRC4', 'CYM2', 'PRC5', 'CYM3', 'HIT', 'OTH1', 'OTH2',
             'D4', 'Eb4', 'E4', 'F4', 'F#4', 'G4', 'G#4', 'A4', 'Bb4', 'B4', 'C5', 'C#5'],
msb      => '1970',
addr     => ["\x19\x70\x00\x00", "\x19\x70\x2E\x00", "\x19\x70\x30\x00", "\x19\x70\x32\x00", "\x19\x70\x34\x00", "\x19\x70\x36\x00", "\x19\x70\x38\x00",
             "\x19\x70\x3A\x00", "\x19\x70\x3C\x00", "\x19\x70\x3E\x00", "\x19\x70\x40\x00", "\x19\x70\x42\x00", "\x19\x70\x44\x00", "\x19\x70\x46\x00",
             "\x19\x70\x48\x00", "\x19\x70\x4A\x00", "\x19\x70\x4C\x00", "\x19\x70\x4E\x00", "\x19\x70\x50\x00", "\x19\x70\x52\x00", "\x19\x70\x54\x00",
             "\x19\x70\x56\x00", "\x19\x70\x58\x00", "\x19\x70\x5A\x00", "\x19\x70\x5C\x00", "\x19\x70\x5E\x00", "\x19\x70\x60\x00", "\x19\x70\x62\x00",
             "\x19\x70\x64\x00", "\x19\x70\x66\x00", "\x19\x70\x68\x00", "\x19\x70\x6A\x00", "\x19\x70\x6C\x00", "\x19\x70\x6E\x00", "\x19\x70\x70\x00",
             "\x19\x70\x72\x00", "\x19\x70\x74\x00", "\x19\x70\x76\x00", "\x19\x70\x78\x00" ],
rqlen    => ["\x00\x00\x00\x12", ("\x00\x00\x01\x43")x38 ],
transf64 => ['', ('(16|18|20|52|53|54|81|82|83|110|111|112|139|140|141|149|150|151|152|157|158|159|160|161|165|167|168|170|171|172|183|184|185|194)')x38 ],
transf10 => ['', ('')x38 ],
transf4  => ['', ('(39|43|68|72|97|101|126|130)')x38 ],
transf_01=> ['', ('')x38 ],
transf_10=> ['', ('')x38 ],
MIDIch   => 9,
pattern  => ['', ('')x38 ],
name     => ['KIT Name', 'BD1', 'RIM', 'BD2', 'CLAP', 'BD3', 'SD1', 'CHH', 'SD2', 'PHH', 'SD3', 'OHH', 'SD4', 'TOM1',
             'PRC1', 'TOM2', 'PRC2', 'TOM3', 'PRC3', 'CYM1', 'PRC4', 'CYM2', 'PRC5', 'CYM3', 'HIT', 'OTH1', 'OTH2',
             'D4', 'Eb4', 'E4', 'F4', 'F#4', 'G4', 'G#4', 'A4', 'Bb4', 'B4', 'C5', 'C#5'],
filename => '',
fnprefix => 'JDXi-DR-',
filetype => 'Drum Kit',
okedext  => 'dk',
filelen  => 7974,
modified => 0,
ct       => {a=>0},
curpart  => '',
titlestr => 'JDXi Manager - Drum Kit Editor',
window   => '',
geometry => '1246x710',
data     => [$DRdata[0],  $DRdata[1],  $DRdata[2],  $DRdata[3],  $DRdata[4],  $DRdata[5],  $DRdata[6],  $DRdata[7],  $DRdata[8],  $DRdata[9],
             $DRdata[10], $DRdata[11], $DRdata[12], $DRdata[13], $DRdata[14], $DRdata[15], $DRdata[16], $DRdata[17], $DRdata[18], $DRdata[19],
             $DRdata[20], $DRdata[21], $DRdata[22], $DRdata[23], $DRdata[24], $DRdata[25], $DRdata[26], $DRdata[27], $DRdata[28], $DRdata[29],
             $DRdata[30], $DRdata[31], $DRdata[32], $DRdata[33], $DRdata[34], $DRdata[35], $DRdata[36], $DRdata[37], $DRdata[38] ],
datalen  => [18, (195)x38 ],
presets  => \@DR_presets,
selpreset=> $DR_presets[0],
dumpto   => '',
readfrom => '',
storeto  => '',
ldprwgt  => ['',''],
inittone => ["\x49\x6E\x69\x74\x20\x4B\x69\x74\x20\x20\x20\x20\x7F\x00\x00\x00\x00\x0D",
    ("\x49\x6E\x69\x74\x20\x50\x61\x72\x74\x69\x61\x6C\x00\x00\x7F\x3C\x40\x00\x40\x00\x40\x01\x7F\x00\x00\x00\x40\x03\x02\x01\x01\x00\x01\x01\x00\x00".
     "\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x40\x40\x40\x01\x01\x7F\x01\x7F\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00".
     "\x00\x00\x00\x00\x01\x00\x00\x00\x00\x40\x40\x40\x01\x01\x7F\x01\x7F\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00".
     "\x00\x00\x40\x40\x40\x01\x01\x7F\x01\x7F\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x40\x40\x40\x01\x01".
     "\x7F\x01\x7F\x00\x00\x40\x40\x40\x40\x00\x28\x50\x28\x40\x22\x5E\x40\x40\x01\x7F\x01\x40\x00\x40\x40\x01\x40\x40\x40\x00\x0A\x0A\x40\x00\x7F\x7F".
     "\x7F\x00\x01\x60\x40\x40\x00\x0A\x0A\x0A\x7F\x7F\x7F\x00\x40")x38 ]
);
$DR{pattern}[0]=$Xi_header.$DR{addr}[0].'[\x00,\x0D,\x20-\x7E]{12}[\x00-\x7F]{7}\xF7';
for my $n (1..38) { $DR{pattern}[$n]=$Xi_header.quotemeta($DR{addr}[$n]).'[\x00,\x0D,\x20-\x7E]{12}[\x00-\x7F]{184}\xF7'; }

# Arpeggio part data structure
our @ARPdata;
our %ARP=(
type     => 'AR',
key      => ['Arp'],
msb      => '1800',
addr     => ["\x18\x00\x40\x00"],
rqlen    => ["\x00\x00\x00\x0C"],
transf64 => ['(7)'],
transf10 => [''],
transf4  => [''],
transf_01=> [''],
transf_10=> [''],
MIDIch   => 0,
pattern  => [''],
name     => ["\x00"],
filename => '',
fnprefix => 'JDXi-AR-',
filetype => 'Arpeggio',
okedext  => '',
filelen  => 26,
modified => 0,
ct       => {a=>0},
titlestr => 'JDXi Manager - Arpeggio Editor',
window   => '',
geometry => '480x340',
data     => [\@ARPdata],
datalen  => [12],
dumpto   => '',
readfrom => '',
storeto  => '',
inittone => ["\x00\x05\x05\x00\x01\x00\x02\x40\x00\x64\x00\x00"]
);
$ARP{pattern}[0]=$Xi_header.$ARP{addr}[0].'[\x00-\x7F]{13}\xF7';

# Vocal FX part data structure
our @VFXdata;
our %VFX=(
type     => 'VC',
key      => ['Vocal FX'],
msb      => '1800',
addr     => ["\x18\x00\x01\x00"],
rqlen    => ["\x00\x00\x00\x18"],
transf64 => ['(1)'],
transf10 => [''],
transf4  => [''],
transf_01=> ['(11)'],
transf_10=> ['(10)'],
MIDIch   => 0,
pattern  => [''],
name     => ["\x00"],
filename => '',
fnprefix => 'JDXi-VC-',
filetype => 'Vocal Effects',
okedext  => '',
filelen  => 38,
modified => 0,
ct       => {a=>0},
titlestr => 'JDXi Manager - Vocal Effects Editor',
window   => '',
geometry => '750x340',
data     => [\@VFXdata],
datalen  => [24],
dumpto   => '',
readfrom => '',
storeto  => '',
inittone => ["\x7F\x40\x00\x00\x02\x01\x00\x01\x00\x00\x0A\x01\x64\x01\x00\x00\x50\x50\x00\x00\x40\x01\x40\x40"]
);
$VFX{pattern}[0]=$Xi_header.$VFX{addr}[0].'[\x00-\x7F]{25}\xF7';

# Effects part data structure
our @FXdata;
for my $n (0..3) { $FXdata[$n][0]=''; }
our %FX=(
type     => 'FX',
key      => ['Effect 1','Effect 2','Delay','Reverb'],
msb      => '1800',
addr     => ["\x18\x00\x02\x00", "\x18\x00\x04\x00", "\x18\x00\x06\x00", "\x18\x00\x08\x00"],
rqlen    => [("\x00\x00\x01\x11")x2, "\x00\x00\x00\x64", "\x00\x00\x00\x63"],
transf64 => [('')x4 ],
transf10 => [('')x4 ],
transf4  => [('(17|21|25|29|33|37|41|45|49|53|57|61|65|69)')x2, '(4|8|12|16|20|24|28|32)', '(3|7|11|15)'],
transf_01=> [('')x4 ],
transf_10=> [('')x4 ],
MIDIch   => 0,
pattern  => [('')x4 ],
name     => [("\x00")x4 ],
filename => '',
fnprefix => 'JDXi-FX-',
filetype => 'Effects',
okedext  => '',
filelen  => 545,
modified => 0,
ct       => {a=>0},
titlestr => 'JDXi Manager - Effects Editor',
window   => '',
geometry => '740x610',
data     => [$FXdata[0], $FXdata[1], $FXdata[2], $FXdata[3]],
datalen  => [145, 145, 100, 99],
dumpto   => '',
readfrom => '',
storeto  => '',
inittone => [("\x00\x7F\x32\x32\x01\x00\x40\x00\x40\x00\x40\x00\x40\x00\x00\x00\x00"."\x08\x00\x00\x00"x32)x2,
              "\x01\x7F\x00\x00\x08\x00\x00\x01\x08\x00\x00\x01\x08\x00\x0C\x08\x08\x00\x00\x0B\x08\x00\x03\x02".
              "\x08\x00\x03\x02\x08\x00\x00\x0E"."\x08\x00\x00\x00"x17,
              "\x01\x7F\x00\x08\x00\x00\x04\x08\x00\x05\x00\x08\x00\x00\x0E"."\x08\x00\x00\x00"x21 ]
);
for my $n (0..3) { $FX{pattern}[$n]=$Xi_header.quotemeta($FX{addr}[$n]).'[\x00-\x7F]{'.($FX{datalen}[$n]+1).'}\xF7'; }

# sysex string to send when switching FX1 or FX2 type
# all start with: \xF0\x41\x10\x00\x00\x00\x0E\x12  + addr (\x18\x00\x02\x00 or \x18\x00\x04\x00)
our @FX_send=(
"\x00\x7F\x32\x32\x01"."\x00\x40"x4 ."\x00"x4 ."\x08\x00\x00\x00"x32,
"\x01\x7F\x32\x32\x01"."\x00\x40"x4 ."\x00"x4 .
  "\x08\x00\x05\x00\x08\x00\x06\x0E\x08\x00\x00\x02\x08\x00\x07\x0F"."\x08\x00\x00\x00"x28,
"\x02\x7F\x32\x32\x01"."\x00\x40"x4 ."\x00"x4 .
  "\x08\x00\x04\x06\x08\x00\x06\x04\x08\x00\x00\x03\x08\x00\x07\x0F"."\x08\x00\x00\x00"x28,
"\x03\x7F\x32\x32\x01"."\x00\x40"x4 ."\x00"x4 .
  "\x08\x00\x02\x08\x08\x00\x00\x03\x08\x00\x00\x09\x08\x00\x00\x00\x08\x00\x03\x02".
  "\x08\x00\x00\x00\x08\x00\x00\x00\x08\x00\x02\x04\x08\x00\x0F\x0A\x08\x00\x03\x02"."\x08\x00\x00\x00"x22,
"\x04\x7F\x32\x32\x01"."\x00\x40"x4 ."\x00"x4 .
  "\x08\x00\x07\x0F\x08\x00\x04\x0B\x08\x00\x04\x06\x08\x00\x05\x05"."\x08\x00\x00\x00"x28,
"\x05\x7F\x32\x32\x01"."\x00\x40"x4 ."\x00"x4 .
  "\x08\x00\x00\x01\x08\x00\x01\x09\x08\x00\x01\x05\x08\x00\x06\x04\x08\x00\x05\x00\x08\x00\x01\x0E\x08\x00\x03\x02\x08\x00\x07\x0F"."\x08\x00\x00\x00"x24,
"\x06\x7F\x32\x32\x01"."\x00\x40"x4 ."\x00"x4 .
  "\x08\x00\x00\x01\x08\x00\x02\x03\x08\x00\x01\x02\x08\x00\x02\x08\x08\x00\x02\x08\x08\x00\x01\x0E\x08\x00\x06\x04"."\x08\x00\x00\x00"x25,
"\x07\x7F\x32\x32\x01"."\x00\x40"x4 ."\x00"x4 .
  "\x08\x00\x03\x0C\x08\x00\x05\x00\x08\x00\x03\x02\x08\x00\x07\x0F"."\x08\x00\x00\x00"x28,
"\x08\x7F\x32\x32\x01"."\x00\x40"x4 ."\x00"x4 .
  "\x08\x00\x00\x00\x08\x00\x01\x02\x08\x00\x02\x07\x08\x00\x03\x02\x08\x00\x07\x0F"."\x08\x00\x00\x00"x27
);

our @Part=(\%AN, \%SN1, \%SN2, \%DR, \%FX, \%ARP, \%VFX);

1;
