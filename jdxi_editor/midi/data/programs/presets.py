import json
import csv
from io import StringIO
import pandas as pd

# Raw data as a string
RAW_PRESETS_CSV = """
id,name,category,msb,lsb,pc
001,JP8 Strings1,Strings/Pad,95,64,1
002,Soft Pad 1,Strings/Pad,95,64,2
003,JP8 Strings2,Strings/Pad,95,64,3
004,JUNO Str 1,Strings/Pad,95,64,4
005,Oct Strings,Strings/Pad,95,64,5
006,Brite Str 1,Strings/Pad,95,64,6
007,Boreal Pad,Strings/Pad,95,64,7
008,JP8 Strings3,Strings/Pad,95,64,8
009,JP8 Strings4,Strings/Pad,95,64,9
010,Hollow Pad 1,Strings/Pad,95,64,10
011,LFO Pad 1,Strings/Pad,95,64,11
012,Hybrid Str,Strings/Pad,95,64,12
013,Awakening 1,Strings/Pad,95,64,13
014,Cincosoft 1,Strings/Pad,95,64,14
015,Bright Pad 1,Strings/Pad,95,64,15
016,Analog Str 1,Strings/Pad,95,64,16
017,Soft ResoPd1,Strings/Pad,95,64,17
018,HPF Poly 1,Strings/Pad,95,64,18
019,BPF Poly,Strings/Pad,95,64,19
020,Sweep Pad 1,Strings/Pad,95,64,20
021,Soft Pad 2,Strings/Pad,95,64,21
022,Sweep JD 1,Strings/Pad,95,64,22
023,FltSweep Pd1,Strings/Pad,95,64,23
024,HPF Pad,Strings/Pad,95,64,24
025,HPF SweepPd1,Strings/Pad,95,64,25
026,KO Pad,Strings/Pad,95,64,26
027,Sweep Pad 2,Strings/Pad,95,64,27
028,TrnsSweepPad,Strings/Pad,95,64,28
029,Revalation 1,Strings/Pad,95,64,29
030,LFO CarvePd1,Strings/Pad,95,64,30
031,RETROX 139 1,Strings/Pad,95,64,31
032,LFO ResoPad1,Strings/Pad,95,64,32
033,PLS Pad 1,Strings/Pad,95,64,33
034,PLS Pad 2,Strings/Pad,95,64,34
035,Trip 2 Mars1,Strings/Pad,95,64,35
036,Reso S&H Pd1,Strings/Pad,95,64,36
037,SideChainPd1,Strings/Pad,95,64,37
038,PXZoon 1,Strings/Pad,95,64,38
039,Psychoscilo1,Strings/Pad,95,64,39
040,Fantasy 1,Strings/Pad,95,64,40
041,D-50 Stack 1,Strings/Pad,95,64,41
042,Organ Pad,Strings/Pad,95,64,42
043,Bell Pad,Strings/Pad,95,64,43
044,Dreaming 1,Strings/Pad,95,64,44
045,Syn Sniper 1,Strings/Pad,95,64,45
046,Strings 1,Strings/Pad,95,64,46
047,D-50 Pizz 1,Strings/Pad,95,64,47
048,Super Saw 1 Lead,Strings/Pad,95,64,48
049,S-SawStacLd1,Lead,95,64,49
050,Tekno Lead 1,Lead,95,64,50
051,Tekno Lead 2,Lead,95,64,51
052,Tekno Lead 3,Lead,95,64,52
053,OSC-SyncLd 1,Lead,95,64,53
054,WaveShapeLd1,Lead,95,64,54
055,JD RingMod 1 Lead,Lead,95,64,55
056,Buzz Lead 1,Lead,95,64,56
057,Buzz Lead 2,Lead,95,64,57
058,SawBuzz Ld 1,Lead,95,64,58
059,Sqr Buzz Ld1,Lead,95,64,59
060,Tekno Lead 4,Lead,95,64,60
061,Dist Flt TB1,Lead,95,64,61
062,Dist TB Sqr1,Lead,95,64,62
063,Glideator 1,Lead,95,64,63
064,Vintager 1,Lead,95,64,64
065,Hover Lead 1,Lead,95,64,65
066,Saw Lead 1,Lead,95,64,66
067,Saw+Tri Lead,Lead,95,64,67
068,PortaSaw Ld1,Lead,95,64,68
069,Reso Saw Ld,Lead,95,64,69
070,4th Syn Lead,Lead,95,64,84
071,Maj Stack Ld,Lead,95,64,85
072,MinStack Ld1,Lead,95,64,86
073,Chubby Lead1,Lead,95,64,87
074,CuttingLead1,Lead,95,64,88
089,Seq Bass 1,Bass,95,64,89
090,Reso Bass 1,Bass,95,64,90
091,TB Bass 1,Bass,95,64,91
092,106 Bass 1,Bass,95,64,92
093,FilterEnvBs1,Bass,95,64,93
094,JUNO Sqr Bs1,Bass,95,64,94
095,Reso Bass 2,Bass,95,64,95
096,JUNO Bass,Bass,95,64,96
097,MG Bass 1,Bass,95,64,97
098,106 Bass 3,Bass,95,64,98
099,Reso Bass 3,Bass,95,64,99
100,Detune Bs 1,Bass,95,64,100
101,MKS-50 Bass1,Bass,95,64,101
102,Sweep Bass,Bass,95,64,102
103,MG Bass 2,Bass,95,64,103
104,MG Bass 3,Bass,95,64,104
105,ResRubber Bs,Bass,95,64,105
106,R&B Bass 1,Bass,95,64,106
107,Reso Bass 4,Bass,95,64,107
108,Wide Bass 1,Bass,95,64,108
109,Chow Bass 1,Bass,95,64,109
110,Chow Bass 2,Bass,95,64,110
111,SqrFilterBs1,Bass,95,64,111
112,Reso Bass 5,Bass,95,64,112
113,Syn Bass 1,Bass,95,64,113
114,ResoSawSynBs,Bass,95,64,114
115,Filter Bass1,Bass,95,64,115
116,SeqFltEnvBs,Bass,95,64,116
117,DnB Bass 1,Bass,95,64,117
118,UnisonSynBs1,Bass,95,64,118
119,Modular Bs,Bass,95,64,119
120,Monster Bs 1,Bass,95,64,120
121,Monster Bs 2,Bass,95,64,121
122,Monster Bs 3,Bass,95,64,122
123,Monster Bs 4,Bass,95,64,123
124,Square Bs 1,Bass,95,64,124
125,106 Bass 2,Bass,95,64,125
126,5th Stac Bs1,Bass,95,64,126
127,SqrStacSynBs,Bass,95,64,127
128,MC-202 Bs,Bass,95,64,128
129,TB Bass 2,Bass,95,65,1
130,Square Bs 2,Bass,95,65,2
131,SH-101 Bs,Bass,95,65,3
132,R&B Bass 2,Bass,95,65,4
133,MG Bass 4,Bass,95,65,5
134,Seq Bass 2,Bass,95,65,6
135,Tri Bass 1,Bass,95,65,7
136,BPF Syn Bs 2,Bass,95,65,8
137,BPF Syn Bs 1,Bass,95,65,9
138,Low Bass 1,Bass,95,65,10
139,Low Bass 2,Bass,95,65,11
140,Kick Bass 1,Bass,95,65,12
141,SinDetuneBs1,Bass,95,65,13
142,Organ Bass 1,Bass,95,65,14
143,Growl Bass 1,Bass,95,65,15
144,Talking Bs 1,Bass,95,65,16
145,LFO Bass 1,Bass,95,65,17
146,LFO Bass 2,Bass,95,65,18
147,Crack Bass,Bass,95,65,19
148,Wobble Bs 1,Bass,95,65,20
149,Wobble Bs 2,Bass,95,65,21
150,Wobble Bs 3,Bass,95,65,22
151,Wobble Bs 4,Bass,95,65,23
152,SideChainBs1,Bass,95,65,24
153,SideChainBs2,Bass,95,65,25
154,House Bass 1,Bass,95,65,26
155,FM Bass,Bass,95,65,27
156,4Op FM Bass1,Bass,95,65,28
157,Ac. Bass,Bass,95,65,29
158,Fingerd Bs 1,Bass,95,65,30
159,Picked Bass,Bass,95,65,31
160,Fretless Bs,Bass,95,65,32
161,Slap Bass 1,Bass,95,65,33
162,JD Piano 1,Keyboard,95,65,34
163,E. Grand 1,Keyboard,95,65,35
164,Trem EP 1,Keyboard,95,65,36
165,FM E. Piano 1,Keyboard,95,65,37
166,FM E. Piano 2,Keyboard,95,65,38
167,Vib Wurly 1,Keyboard,95,65,39
168,Pulse Clav,Keyboard,95,65,40
169,Clav,Keyboard,95,65,41
170,70's E. Organ,Keyboard,95,65,42
171,House Org 1,Keyboard,95,65,43
172,House Org 2,Keyboard,95,65,44
173,Bell 1,Keyboard,95,65,45
174,Bell 2,Keyboard,95,65,46
175,Organ Bell,Keyboard,95,65,47
176,Vibraphone 1,Keyboard,95,65,48
177,Steel Drum,Keyboard,95,65,49
178,Harp 1,Keyboard,95,65,50
179,Ac. Guitar,Keyboard,95,65,51
180,Bright Strat,Keyboard,95,65,52
181,Funk Guitar1,Keyboard,95,65,53
182,Jazz Guitar,Keyboard,95,65,54
183,Dist Guitar1,Keyboard,95,65,55
184,D. Mute Gtr1,Keyboard,95,65,56
185,E. Sitar,Keyboard,95,65,57
186,Sitar Drone,Keyboard,95,65,58
187,FX 1,FX/Other,95,65,59
188,FX 2,FX/Other,95,65,60
189,FX 3,FX/Other,95,65,61
190,Tuned Winds1,FX/Other,95,65,62
191,Bend Lead 1,FX/Other,95,65,63
192,RiSER 1,FX/Other,95,65,64
193,Rising SEQ 1,FX/Other,95,65,65
194,Scream Saw,FX/Other,95,65,66
195,Noise SEQ 1,FX/Other,95,65,67
196,Syn Vox 1,FX/Other,95,65,68
197,JD SoftVox,FX/Other,95,65,69
198,Vox Pad,FX/Other,95,65,70
199,VP-330 Chr,FX/Other,95,65,71
200,Orch Hit,FX/Other,95,65,72
201,Philly Hit,FX/Other,95,65,73
202,House Hit,FX/Other,95,65,74
203,O'Skool Hit1,FX/Other,95,65,75
204,Punch Hit,FX/Other,95,65,76
205,Tao Hit,FX/Other,95,65,77
206,SEQ Saw 1,Seq,95,65,78
207,SEQ Sqr,Seq,95,65,79
208,SEQ Tri 1,Seq,95,65,80
209,SEQ 1,Seq,95,65,81
210,SEQ 2,Seq,95,65,82
211,SEQ 3,Seq,95,65,83
212,SEQ 4,Seq,95,65,84
213,Sqr Reso Plk,Seq,95,65,85
214,Pluck Synth1,Seq,95,65,86
215,Paperclip 1,Seq,95,65,87
216,Sonar Pluck1,Seq,95,65,88
217,SqrTrapPlk 1,Seq,95,65,89
218,TB Saw Seq 1,Seq,95,65,90
219,TB Sqr Seq 1,Seq,95,65,91
220,JUNO Key Seq,Seq,95,65,92
221,Analog Poly1,Seq,95,65,93
222,Analog Poly2,Seq,95,65,94
223,Analog Poly3,Seq,95,65,95
224,Analog Poly4,Seq,95,65,96
225,JUNO Octavr1,Seq,95,65,97
226,EDM Synth 1,Seq,95,65,98
227,Super Saw 2,Seq,95,65,99
228,S-Saw Poly,Seq,95,65,100
229,Trance Key 1,Seq,95,65,101
230,S-Saw Pad 1,Seq,95,65,102
231,7th Stac Syn,Seq,95,65,103
232,S-SawStc Syn,Seq,95,65,104
233,Trance Key 2,Seq,95,65,105
234,Analog Brass,Brass,95,65,106
235,Reso Brass,Brass,95,65,107
236,Soft Brass 1,Brass,95,65,108
237,FM Brass,Brass,95,65,109
238,Syn Brass 1,Brass,95,65,110
239,Syn Brass 2,Brass,95,65,111
240,JP8 Brass,Brass,95,65,112
241,Soft SynBrs1,Brass,95,65,113
242,Soft SynBrs2,Brass,95,65,114
243 EpicSlow Brs Brass 95 65 115
244,JUNO Brass,Brass,95,65,116
245,Poly Brass,Brass,95,65,117
246,Voc:Ensemble,FX/Other,95,65,118
247,Voc:5thStack,FX/Other,95,65,119
248,Voc:Robot,FX/Other,95,65,120
249,Voc:Saw,FX/Other,95,65,121
250,Voc:Sqr,FX/Other,95,65,122
251,Voc:Rise Up,FX/Other,95,65,123
252,Voc:Auto Vib,FX/Other,95,65,124
253,Voc:PitchEnv,FX/Other,95,65,125
254,Voc:VP-330,FX/Other,95,65,126
255,Voc:Noise,FX/Other,95,65,127
256,Init Tone,FX/Other,95,65,128
"""


# Preset data as structured JSON
DIGITAL_PRESET_LIST = [
  {
    "id":"001",
    "name":"JP8 Strings1",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":1.0
  }
,
  {
    "id":"002",
    "name":"Soft Pad 1",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":2.0
  }
,
  {
    "id":"003",
    "name":"JP8 Strings2",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":3.0
  }
,
  {
    "id":"004",
    "name":"JUNO Str 1",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":4.0
  }
,
  {
    "id":"005",
    "name":"Oct Strings",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":5.0
  }
,
  {
    "id":"006",
    "name":"Brite Str 1",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":6.0
  }
,
  {
    "id":"007",
    "name":"Boreal Pad",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":7.0
  }
,
  {
    "id":"008",
    "name":"JP8 Strings3",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":8.0
  }
,
  {
    "id":"009",
    "name":"JP8 Strings4",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":9.0
  }
,       
  {
    "id":"010",
    "name":"Hollow Pad 1",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":10.0
  }
,
  {
    "id":"011",
    "name":"LFO Pad 1",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":11.0
  }
,
  {
    "id":"012",
    "name":"Hybrid Str",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":12.0
  }
,
  {
    "id":"013",
    "name":"Awakening 1",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":13.0
  }
,
  {
    "id":"014",
    "name":"Cincosoft 1",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":14.0
  }
,       
  {
    "id":"015",
    "name":"Bright Pad 1",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":15.0
  }
,       
  {
    "id":"016",
    "name":"Analog Str 1",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":16.0
  }
,       
  {
    "id":"017",
    "name":"Soft ResoPd1",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":17.0
  }
,       
  {
    "id":"018",
    "name":"HPF Poly 1",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":18.0
  }
,       
  {
    "id":"019",
    "name":"BPF Poly",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":19.0
  }
,       
  {
    "id":"020",
    "name":"Sweep Pad 1",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":20.0
  }
,       
  {
    "id":"021",
    "name":"Soft Pad 2",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":21.0
  }
,       
  {
    "id":"022",
    "name":"Sweep JD 1",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":22.0
  }
,       
  {
    "id":"023",
    "name":"FltSweep Pd1",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":23.0
  }
,       
  {
    "id":"024",
    "name":"HPF Pad",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":24.0
  }
,       
  {
    "id":"025",
    "name":"HPF SweepPd1",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":25.0
  }
,       
  {
    "id":"026",
    "name":"KO Pad",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":26.0
  }
,       
  {
    "id":"027",
    "name":"Sweep Pad 2",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":27.0
  }
,       
  {
    "id":"028",
    "name":"TrnsSweepPad",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":28.0
  }
,               
  {
    "id":"029",
    "name":"Revalation 1",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":29.0
  }
,       
  {
    "id":"030",
    "name":"LFO CarvePd1",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":30.0
  }
,       
  {
    "id":"031",
    "name":"RETROX 139 1",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":31.0
  }
,       
  {
    "id":"032",
    "name":"LFO ResoPad1",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":32.0
  }
,       
  {
    "id":"033",
    "name":"PLS Pad 1",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":33.0
  }
,       
  {
    "id":"034",
    "name":"PLS Pad 2",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":34.0
  }
,       
  {
    "id":"035",
    "name":"Trip 2 Mars1",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":35.0
  }
,       
  {
    "id":"036",
    "name":"Reso S&H Pd1",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":36.0
  }
,       
  {
    "id":"037",
    "name":"SideChainPd1",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":37.0
  }
,       
  {
    "id":"038",
    "name":"PXZoon 1",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":38.0
  }
,       
  {
    "id":"039",
    "name":"Psychoscilo1",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":39.0
  }
,       
  {
    "id":"040",
    "name":"Fantasy 1",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":40.0
  }
,       
  {
    "id":"041",
    "name":"D-50 Stack 1",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":41.0
  }
,       
  {
    "id":"042",
    "name":"Organ Pad",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":42.0
  }
,            
  {
    "id":"043",
    "name":"Bell Pad",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":43.0
  }
,            
  {
    "id":"044",
    "name":"Dreaming 1",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":44.0
  }
,            
  {
    "id":"045",
    "name":"Syn Sniper 1",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":45.0
  }
,
  {
    "id":"046",
    "name":"Strings 1",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":46.0
  }
,
  {
    "id":"047",
    "name":"D-50 Pizz 1",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":47.0
  }
,
  {
    "id":"048",
    "name":"Super Saw 1 Lead",
    "category":"Strings\/Pad",
    "msb":95.0,
    "lsb":64.0,
    "pc":48.0
  }
,
  {
    "id":"049",
    "name":"S-SawStacLd1",
    "category":"Lead",
    "msb":95.0,
    "lsb":64.0,
    "pc":49.0
  }
,
  {
    "id":"050",
    "name":"Tekno Lead 1",
    "category":"Lead",
    "msb":95.0,
    "lsb":64.0,
    "pc":50.0
  }
,
  {
    "id":"051",
    "name":"Tekno Lead 2",
    "category":"Lead",
    "msb":95.0,
    "lsb":64.0,
    "pc":51.0
  }
,
  {
    "id":"052",
    "name":"Tekno Lead 3",
    "category":"Lead",
    "msb":95.0,
    "lsb":64.0,
    "pc":52.0
  }
,
  {
    "id":"053",
    "name":"OSC-SyncLd 1",
    "category":"Lead",
    "msb":95.0,
    "lsb":64.0,
    "pc":53.0
  }
,
  {
    "id":"054",
    "name":"WaveShapeLd1",
    "category":"Lead",
    "msb":95.0,
    "lsb":64.0,
    "pc":54.0
  }
,
  {
    "id":"055",
    "name":"JD RingMod 1 Lead",
    "category":"Lead",
    "msb":95.0,
    "lsb":64.0,
    "pc":55.0
  }
,
  {
    "id":"056",
    "name":"Buzz Lead 1",
    "category":"Lead",
    "msb":95.0,
    "lsb":64.0,
    "pc":56.0
  }
,
  {
    "id":"057",
    "name":"Buzz Lead 2",
    "category":"Lead",
    "msb":95.0,
    "lsb":64.0,
    "pc":57.0
  }
,
  {
    "id":"058",
    "name":"SawBuzz Ld 1",
    "category":"Lead",
    "msb":95.0,
    "lsb":64.0,
    "pc":58.0
  }
,
  {
    "id":"059",
    "name":"Sqr Buzz Ld1",
    "category":"Lead",
    "msb":95.0,
    "lsb":64.0,
    "pc":59.0
  }
,
  {
    "id":"060",
    "name":"Tekno Lead 4",
    "category":"Lead",
    "msb":95.0,
    "lsb":64.0,
    "pc":60.0
  }
,
  {
    "id":"061",
    "name":"Dist Flt TB1",
    "category":"Lead",
    "msb":95.0,
    "lsb":64.0,
    "pc":61.0
  }
,
  {
    "id":"062",
    "name":"Dist TB Sqr1",
    "category":"Lead",
    "msb":95.0,
    "lsb":64.0,
    "pc":62.0
  }
,
  {
    "id":"063",
    "name":"Glideator 1",
    "category":"Lead",
    "msb":95.0,
    "lsb":64.0,
    "pc":63.0
  }
,
  {
    "id":"064",
    "name":"Vintager 1",
    "category":"Lead",
    "msb":95.0,
    "lsb":64.0,
    "pc":64.0
  }
,
  {
    "id":"065",
    "name":"Hover Lead 1",
    "category":"Lead",
    "msb":95.0,
    "lsb":64.0,
    "pc":65.0
  }
,
  {
    "id":"066",
    "name":"Saw Lead 1",
    "category":"Lead",
    "msb":95.0,
    "lsb":64.0,
    "pc":66.0
  }
,
  {
    "id":"067",
    "name":"Saw+Tri Lead",
    "category":"Lead",
    "msb":95.0,
    "lsb":64.0,
    "pc":67.0
  }
,
  {
    "id":"068",
    "name":"PortaSaw Ld1",
    "category":"Lead",
    "msb":95.0,
    "lsb":64.0,
    "pc":68.0
  }
,
  {
    "id":"069",
    "name":"Reso Saw Ld",
    "category":"Lead",
    "msb":95.0,
    "lsb":64.0,
    "pc":69.0
  }
,
  {
    "id":"070",
    "name":"4th Syn Lead",
    "category":"Lead",
    "msb":95.0,
    "lsb":64.0,
    "pc":84.0
  }
,               
  {
    "id":"071",
    "name":"Maj Stack Ld",
    "category":"Lead",
    "msb":95.0,
    "lsb":64.0,
    "pc":85.0
  }
,
  {
    "id":"072",
    "name":"MinStack Ld1",
    "category":"Lead",
    "msb":95.0,
    "lsb":64.0,
    "pc":86.0
  }
,
  {
    "id":"073",
    "name":"Chubby Lead1",
    "category":"Lead",
    "msb":95.0,
    "lsb":64.0,
    "pc":87.0
  }
,
  {
    "id":"074",
    "name":"CuttingLead1",
    "category":"Lead",
    "msb":95.0,
    "lsb":64.0,
    "pc":88.0
  }
,
  {
    "id":"089",
    "name":"Seq Bass 1",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":89.0
  }
,
  {
    "id":"090",
    "name":"Reso Bass 1",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":90.0
  }
,
  {
    "id":"091",
    "name":"TB Bass 1",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":91.0
  }
,
  {
    "id":"092",
    "name":"106 Bass 1",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":92.0
  }
,
  {
    "id":"093",
    "name":"FilterEnvBs1",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":93.0
  }
,
  {
    "id":"094",
    "name":"JUNO Sqr Bs1",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":94.0
  }
,
  {
    "id":"095",
    "name":"Reso Bass 2",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":95.0
  }
,
  {
    "id":"096",
    "name":"JUNO Bass",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":96.0
  }
,
  {
    "id":"097",
    "name":"MG Bass 1",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":97.0
  }
,
  {
    "id":"098",
    "name":"106 Bass 3",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":98.0
  }
,
  {
    "id":"099",
    "name":"Reso Bass 3",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":99.0
  }
,
  {
    "id":"100",
    "name":"Detune Bs 1",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":100.0
  }
,
  {
    "id":"101",
    "name":"MKS-50 Bass1",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":101.0
  }
,
  {
    "id":"102",
    "name":"Sweep Bass",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":102.0
  }
,
  {
    "id":"103",
    "name":"MG Bass 2",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":103.0
  }
,
  {
    "id":"104",
    "name":"MG Bass 3",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":104.0
  }
,
  {
    "id":"105",
    "name":"ResRubber Bs",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":105.0
  }
,
  {
    "id":"106",
    "name":"R&B Bass 1",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":106.0
  }
,
  {
    "id":"107",
    "name":"Reso Bass 4",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":107.0
  }
,           
  {
    "id":"108",
    "name":"Wide Bass 1",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":108.0
  }
,           
  {
    "id":"109",
    "name":"Chow Bass 1",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":109.0
  }
,           
  {
    "id":"110",
    "name":"Chow Bass 2",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":110.0
  }
,           
  {
    "id":"111",
    "name":"SqrFilterBs1",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":111.0
  }
,           
  {
    "id":"112",
    "name":"Reso Bass 5",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":112.0
  }
,           
  {
    "id":"113",
    "name":"Syn Bass 1",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":113.0
  }
,                       
  {
    "id":"114",
    "name":"ResoSawSynBs",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":114.0
  }
,                       
  {
    "id":"115",
    "name":"Filter Bass1",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":115.0
  }
,                       
  {
    "id":"116",
    "name":"SeqFltEnvBs",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":116.0
  }
,
  {
    "id":"117",
    "name":"DnB Bass 1",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":117.0
  }
,
  {
    "id":"118",
    "name":"UnisonSynBs1",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":118.0
  }
,
  {
    "id":"119",
    "name":"Modular Bs",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":119.0
  }
,
  {
    "id":"120",
    "name":"Monster Bs 1",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":120.0
  }
,
  {
    "id":"121",
    "name":"Monster Bs 2",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":121.0
  }
,
  {
    "id":"122",
    "name":"Monster Bs 3",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":122.0
  }
,
  {
    "id":"123",
    "name":"Monster Bs 4",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":123.0
  }
,
  {
    "id":"124",
    "name":"Square Bs 1",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":124.0
  }
,
        {
    "id":"125",
    "name":"106 Bass 2",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":125.0
  }
,   
  {
    "id":"126",
    "name":"5th Stac Bs1",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":126.0
  }
,
  {
    "id":"127",
    "name":"SqrStacSynBs",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":127.0
  }
,
  {
    "id":"128",
    "name":"MC-202 Bs",
    "category":"Bass",
    "msb":95.0,
    "lsb":64.0,
    "pc":128.0
  }
,
  {
    "id":"129",
    "name":"TB Bass 2",
    "category":"Bass",
    "msb":95.0,
    "lsb":65.0,
    "pc":1.0
  }
,
  {
    "id":"130",
    "name":"Square Bs 2",
    "category":"Bass",
    "msb":95.0,
    "lsb":65.0,
    "pc":2.0
  }
,
  {
    "id":"131",
    "name":"SH-101 Bs",
    "category":"Bass",
    "msb":95.0,
    "lsb":65.0,
    "pc":3.0
  }
,
  {
    "id":"132",
    "name":"R&B Bass 2",
    "category":"Bass",
    "msb":95.0,
    "lsb":65.0,
    "pc":4.0
  }
,
  {
    "id":"133",
    "name":"MG Bass 4",
    "category":"Bass",
    "msb":95.0,
    "lsb":65.0,
    "pc":5.0
  }
,
  {
    "id":"134",
    "name":"Seq Bass 2",
    "category":"Bass",
    "msb":95.0,
    "lsb":65.0,
    "pc":6.0
  }
,
  {
    "id":"135",
    "name":"Tri Bass 1",
    "category":"Bass",
    "msb":95.0,
    "lsb":65.0,
    "pc":7.0
  }
,       
  {
    "id":"136",
    "name":"BPF Syn Bs 2",
    "category":"Bass",
    "msb":95.0,
    "lsb":65.0,
    "pc":8.0
  }
,       
  {
    "id":"137",
    "name":"BPF Syn Bs 1",
    "category":"Bass",
    "msb":95.0,
    "lsb":65.0,
    "pc":9.0
  }
,       
  {
    "id":"138",
    "name":"Low Bass 1",
    "category":"Bass",
    "msb":95.0,
    "lsb":65.0,
    "pc":10.0
  }
,
  {
    "id":"139",
    "name":"Low Bass 2",
    "category":"Bass",
    "msb":95.0,
    "lsb":65.0,
    "pc":11.0
  }
,
  {
    "id":"140",
    "name":"Kick Bass 1",
    "category":"Bass",
    "msb":95.0,
    "lsb":65.0,
    "pc":12.0
  }
,
  {
    "id":"141",
    "name":"SinDetuneBs1",
    "category":"Bass",
    "msb":95.0,
    "lsb":65.0,
    "pc":13.0
  }
,
  {
    "id":"142",
    "name":"Organ Bass 1",
    "category":"Bass",
    "msb":95.0,
    "lsb":65.0,
    "pc":14.0
  }
,
  {
    "id":"143",
    "name":"Growl Bass 1",
    "category":"Bass",
    "msb":95.0,
    "lsb":65.0,
    "pc":15.0
  }
,
  {
    "id":"144",
    "name":"Talking Bs 1",
    "category":"Bass",
    "msb":95.0,
    "lsb":65.0,
    "pc":16.0
  }
,
  {
    "id":"145",
    "name":"LFO Bass 1",
    "category":"Bass",
    "msb":95.0,
    "lsb":65.0,
    "pc":17.0
  }
,
  {
    "id":"146",
    "name":"LFO Bass 2",
    "category":"Bass",
    "msb":95.0,
    "lsb":65.0,
    "pc":18.0
  }
,
  {
    "id":"147",
    "name":"Crack Bass",
    "category":"Bass",
    "msb":95.0,
    "lsb":65.0,
    "pc":19.0
  }
,
  {
    "id":"148",
    "name":"Wobble Bs 1",
    "category":"Bass",
    "msb":95.0,
    "lsb":65.0,
    "pc":20.0
  }
,
  {
    "id":"149",
    "name":"Wobble Bs 2",
    "category":"Bass",
    "msb":95.0,
    "lsb":65.0,
    "pc":21.0
  }
,
  {
    "id":"150",
    "name":"Wobble Bs 3",
    "category":"Bass",
    "msb":95.0,
    "lsb":65.0,
    "pc":22.0
  }
,
  {
    "id":"151",
    "name":"Wobble Bs 4",
    "category":"Bass",
    "msb":95.0,
    "lsb":65.0,
    "pc":23.0
  }
,
  {
    "id":"152",
    "name":"SideChainBs1",
    "category":"Bass",
    "msb":95.0,
    "lsb":65.0,
    "pc":24.0
  }
,
  {
    "id":"153",
    "name":"SideChainBs2",
    "category":"Bass",
    "msb":95.0,
    "lsb":65.0,
    "pc":25.0
  }
,
  {
    "id":"154",
    "name":"House Bass 1",
    "category":"Bass",
    "msb":95.0,
    "lsb":65.0,
    "pc":26.0
  }
,
  {
    "id":"155",
    "name":"FM Bass",
    "category":"Bass",
    "msb":95.0,
    "lsb":65.0,
    "pc":27.0
  }
,       
  {
    "id":"156",
    "name":"4Op FM Bass1",
    "category":"Bass",
    "msb":95.0,
    "lsb":65.0,
    "pc":28.0
  }
,       
  {
    "id":"157",
    "name":"Ac. Bass",
    "category":"Bass",
    "msb":95.0,
    "lsb":65.0,
    "pc":29.0
  }
,       
  {
    "id":"158",
    "name":"Fingerd Bs 1",
    "category":"Bass",
    "msb":95.0,
    "lsb":65.0,
    "pc":30.0
  }
,       
  {
    "id":"159",
    "name":"Picked Bass",
    "category":"Bass",
    "msb":95.0,
    "lsb":65.0,
    "pc":31.0
  }
,       
  {
    "id":"160",
    "name":"Fretless Bs",
    "category":"Bass",
    "msb":95.0,
    "lsb":65.0,
    "pc":32.0
  }
,       
  {
    "id":"161",
    "name":"Slap Bass 1",
    "category":"Bass",
    "msb":95.0,
    "lsb":65.0,
    "pc":33.0
  }
,       
  {
    "id":"162",
    "name":"JD Piano 1",
    "category":"Keyboard",
    "msb":95.0,
    "lsb":65.0,
    "pc":34.0
  }
,       
  {
    "id":"163",
    "name":"E. Grand 1",
    "category":"Keyboard",
    "msb":95.0,
    "lsb":65.0,
    "pc":35.0
  }
,       
  {
    "id":"164",
    "name":"Trem EP 1",
    "category":"Keyboard",
    "msb":95.0,
    "lsb":65.0,
    "pc":36.0
  }
,       
  {
    "id":"165",
    "name":"FM E. Piano 1",
    "category":"Keyboard",
    "msb":95.0,
    "lsb":65.0,
    "pc":37.0
  }
,       
  {
    "id":"166",
    "name":"FM E. Piano 2",
    "category":"Keyboard",
    "msb":95.0,
    "lsb":65.0,
    "pc":38.0
  }
,       
  {
    "id":"167",
    "name":"Vib Wurly 1",
    "category":"Keyboard",
    "msb":95.0,
    "lsb":65.0,
    "pc":39.0
  }
,       
  {
    "id":"168",
    "name":"Pulse Clav",
    "category":"Keyboard",
    "msb":95.0,
    "lsb":65.0,
    "pc":40.0
  }
,       
  {
    "id":"169",
    "name":"Clav",
    "category":"Keyboard",
    "msb":95.0,
    "lsb":65.0,
    "pc":41.0
  }
,       
  {
    "id":"170",
    "name":"70's E. Organ",
    "category":"Keyboard",
    "msb":95.0,
    "lsb":65.0,
    "pc":42.0
  }
,       
  {
    "id":"171",
    "name":"House Org 1",
    "category":"Keyboard",
    "msb":95.0,
    "lsb":65.0,
    "pc":43.0
  }
,       
  {
    "id":"172",
    "name":"House Org 2",
    "category":"Keyboard",
    "msb":95.0,
    "lsb":65.0,
    "pc":44.0
  }
,       
  {
    "id":"173",
    "name":"Bell 1",
    "category":"Keyboard",
    "msb":95.0,
    "lsb":65.0,
    "pc":45.0
  }
,       
  {
    "id":"174",
    "name":"Bell 2",
    "category":"Keyboard",
    "msb":95.0,
    "lsb":65.0,
    "pc":46.0
  }
,       
  {
    "id":"175",
    "name":"Organ Bell",
    "category":"Keyboard",
    "msb":95.0,
    "lsb":65.0,
    "pc":47.0
  }
,       
  {
    "id":"176",
    "name":"Vibraphone 1",
    "category":"Keyboard",
    "msb":95.0,
    "lsb":65.0,
    "pc":48.0
  }
,       
  {
    "id":"177",
    "name":"Steel Drum",
    "category":"Keyboard",
    "msb":95.0,
    "lsb":65.0,
    "pc":49.0
  }
,       
  {
    "id":"178",
    "name":"Harp 1",
    "category":"Keyboard",
    "msb":95.0,
    "lsb":65.0,
    "pc":50.0
  }
,       
  {
    "id":"179",
    "name":"Ac. Guitar",
    "category":"Keyboard",
    "msb":95.0,
    "lsb":65.0,
    "pc":51.0
  }
,       
  {
    "id":"180",
    "name":"Bright Strat",
    "category":"Keyboard",
    "msb":95.0,
    "lsb":65.0,
    "pc":52.0
  }
,       
  {
    "id":"181",
    "name":"Funk Guitar1",
    "category":"Keyboard",
    "msb":95.0,
    "lsb":65.0,
    "pc":53.0
  }
,       
  {
    "id":"182",
    "name":"Jazz Guitar",
    "category":"Keyboard",
    "msb":95.0,
    "lsb":65.0,
    "pc":54.0
  }
,       
  {
    "id":"183",
    "name":"Dist Guitar1",
    "category":"Keyboard",
    "msb":95.0,
    "lsb":65.0,
    "pc":55.0
  }
,       
  {
    "id":"184",
    "name":"D. Mute Gtr1",
    "category":"Keyboard",
    "msb":95.0,
    "lsb":65.0,
    "pc":56.0
  }
,       
  {
    "id":"185",
    "name":"E. Sitar",
    "category":"Keyboard",
    "msb":95.0,
    "lsb":65.0,
    "pc":57.0
  }
,       
  {
    "id":"186",
    "name":"Sitar Drone",
    "category":"Keyboard",
    "msb":95.0,
    "lsb":65.0,
    "pc":58.0
  }
,       
  {
    "id":"187",
    "name":"FX 1",
    "category":"FX\/Other",
    "msb":95.0,
    "lsb":65.0,
    "pc":59.0
  }
,       
  {
    "id":"188",
    "name":"FX 2",
    "category":"FX\/Other",
    "msb":95.0,
    "lsb":65.0,
    "pc":60.0
  }
,
  {
    "id":"189",
    "name":"FX 3",
    "category":"FX\/Other",
    "msb":95.0,
    "lsb":65.0,
    "pc":61.0
  }
,
  {
    "id":"190",
    "name":"Tuned Winds1",
    "category":"FX\/Other",
    "msb":95.0,
    "lsb":65.0,
    "pc":62.0
  }
,
  {
    "id":"191",
    "name":"Bend Lead 1",
    "category":"FX\/Other",
    "msb":95.0,
    "lsb":65.0,
    "pc":63.0
  }
,
  {
    "id":"192",
    "name":"RiSER 1",
    "category":"FX\/Other",
    "msb":95.0,
    "lsb":65.0,
    "pc":64.0
  }
,
  {
    "id":"193",
    "name":"Rising SEQ 1",
    "category":"FX\/Other",
    "msb":95.0,
    "lsb":65.0,
    "pc":65.0
  }
,       
  {
    "id":"194",
    "name":"Scream Saw",
    "category":"FX\/Other",
    "msb":95.0,
    "lsb":65.0,
    "pc":66.0
  }
,       
  {
    "id":"195",
    "name":"Noise SEQ 1",
    "category":"FX\/Other",
    "msb":95.0,
    "lsb":65.0,
    "pc":67.0
  }
,       
  {
    "id":"196",
    "name":"Syn Vox 1",
    "category":"FX\/Other",
    "msb":95.0,
    "lsb":65.0,
    "pc":68.0
  }
,
  {
    "id":"197",
    "name":"JD SoftVox",
    "category":"FX\/Other",
    "msb":95.0,
    "lsb":65.0,
    "pc":69.0
  }
,
  {
    "id":"198",
    "name":"Vox Pad",
    "category":"FX\/Other",
    "msb":95.0,
    "lsb":65.0,
    "pc":70.0
  }
,
  {
    "id":"199",
    "name":"VP-330 Chr",
    "category":"FX\/Other",
    "msb":95.0,
    "lsb":65.0,
    "pc":71.0
  }
,
  {
    "id":"200",
    "name":"Orch Hit",
    "category":"FX\/Other",
    "msb":95.0,
    "lsb":65.0,
    "pc":72.0
  }
,
  {
    "id":"201",
    "name":"Philly Hit",
    "category":"FX\/Other",
    "msb":95.0,
    "lsb":65.0,
    "pc":73.0
  }
,
  {
    "id":"202",
    "name":"House Hit",
    "category":"FX\/Other",
    "msb":95.0,
    "lsb":65.0,
    "pc":74.0
  }
,
  {
    "id":"203",
    "name":"O'Skool Hit1",
    "category":"FX\/Other",
    "msb":95.0,
    "lsb":65.0,
    "pc":75.0
  }
,
  {
    "id":"204",
    "name":"Punch Hit",
    "category":"FX\/Other",
    "msb":95.0,
    "lsb":65.0,
    "pc":76.0
  }
,
  {
    "id":"205",
    "name":"Tao Hit",
    "category":"FX\/Other",
    "msb":95.0,
    "lsb":65.0,
    "pc":77.0
  }
,
  {
    "id":"206",
    "name":"SEQ Saw 1",
    "category":"Seq",
    "msb":95.0,
    "lsb":65.0,
    "pc":78.0
  }
,
  {
    "id":"207",
    "name":"SEQ Sqr",
    "category":"Seq",
    "msb":95.0,
    "lsb":65.0,
    "pc":79.0
  }
,       
  {
    "id":"208",
    "name":"SEQ Tri 1",
    "category":"Seq",
    "msb":95.0,
    "lsb":65.0,
    "pc":80.0
  }
,       
  {
    "id":"209",
    "name":"SEQ 1",
    "category":"Seq",
    "msb":95.0,
    "lsb":65.0,
    "pc":81.0
  }
,       
  {
    "id":"210",
    "name":"SEQ 2",
    "category":"Seq",
    "msb":95.0,
    "lsb":65.0,
    "pc":82.0
  }
,       
  {
    "id":"211",
    "name":"SEQ 3",
    "category":"Seq",
    "msb":95.0,
    "lsb":65.0,
    "pc":83.0
  }
,       
  {
    "id":"212",
    "name":"SEQ 4",
    "category":"Seq",
    "msb":95.0,
    "lsb":65.0,
    "pc":84.0
  }
,       
  {
    "id":"213",
    "name":"Sqr Reso Plk",
    "category":"Seq",
    "msb":95.0,
    "lsb":65.0,
    "pc":85.0
  }
,
  {
    "id":"214",
    "name":"Pluck Synth1",
    "category":"Seq",
    "msb":95.0,
    "lsb":65.0,
    "pc":86.0
  }
,
  {
    "id":"215",
    "name":"Paperclip 1",
    "category":"Seq",
    "msb":95.0,
    "lsb":65.0,
    "pc":87.0
  }
,       
  {
    "id":"216",
    "name":"Sonar Pluck1",
    "category":"Seq",
    "msb":95.0,
    "lsb":65.0,
    "pc":88.0
  }
,       
  {
    "id":"217",
    "name":"SqrTrapPlk 1",
    "category":"Seq",
    "msb":95.0,
    "lsb":65.0,
    "pc":89.0
  }
,       
  {
    "id":"218",
    "name":"TB Saw Seq 1",
    "category":"Seq",
    "msb":95.0,
    "lsb":65.0,
    "pc":90.0
  }
,
  {
    "id":"219",
    "name":"TB Sqr Seq 1",
    "category":"Seq",
    "msb":95.0,
    "lsb":65.0,
    "pc":91.0
  }
,
  {
    "id":"220",
    "name":"JUNO Key Seq",
    "category":"Seq",
    "msb":95.0,
    "lsb":65.0,
    "pc":92.0
  }
,       
  {
    "id":"221",
    "name":"Analog Poly1",
    "category":"Seq",
    "msb":95.0,
    "lsb":65.0,
    "pc":93.0
  }
,       
  {
    "id":"222",
    "name":"Analog Poly2",
    "category":"Seq",
    "msb":95.0,
    "lsb":65.0,
    "pc":94.0
  }
,       
  {
    "id":"223",
    "name":"Analog Poly3",
    "category":"Seq",
    "msb":95.0,
    "lsb":65.0,
    "pc":95.0
  }
,       
  {
    "id":"224",
    "name":"Analog Poly4",
    "category":"Seq",
    "msb":95.0,
    "lsb":65.0,
    "pc":96.0
  }
,       
  {
    "id":"225",
    "name":"JUNO Octavr1",
    "category":"Seq",
    "msb":95.0,
    "lsb":65.0,
    "pc":97.0
  }
,       
  {
    "id":"226",
    "name":"EDM Synth 1",
    "category":"Seq",
    "msb":95.0,
    "lsb":65.0,
    "pc":98.0
  }
,       
  {
    "id":"227",
    "name":"Super Saw 2",
    "category":"Seq",
    "msb":95.0,
    "lsb":65.0,
    "pc":99.0
  }
,       
  {
    "id":"228",
    "name":"S-Saw Poly",
    "category":"Seq",
    "msb":95.0,
    "lsb":65.0,
    "pc":100.0
  }
,       
  {
    "id":"229",
    "name":"Trance Key 1",
    "category":"Seq",
    "msb":95.0,
    "lsb":65.0,
    "pc":101.0
  }
,       
  {
    "id":"230",
    "name":"S-Saw Pad 1",
    "category":"Seq",
    "msb":95.0,
    "lsb":65.0,
    "pc":102.0
  }
,       
  {
    "id":"231",
    "name":"7th Stac Syn",
    "category":"Seq",
    "msb":95.0,
    "lsb":65.0,
    "pc":103.0
  }
,       
  {
    "id":"232",
    "name":"S-SawStc Syn",
    "category":"Seq",
    "msb":95.0,
    "lsb":65.0,
    "pc":104.0
  }
,       
  {
    "id":"233",
    "name":"Trance Key 2",
    "category":"Seq",
    "msb":95.0,
    "lsb":65.0,
    "pc":105.0
  }
,       
  {
    "id":"234",
    "name":"Analog Brass",
    "category":"Brass",
    "msb":95.0,
    "lsb":65.0,
    "pc":106.0
  }
,       
  {
    "id":"235",
    "name":"Reso Brass",
    "category":"Brass",
    "msb":95.0,
    "lsb":65.0,
    "pc":107.0
  }
,       
  {
    "id":"236",
    "name":"Soft Brass 1",
    "category":"Brass",
    "msb":95.0,
    "lsb":65.0,
    "pc":108.0
  }
,       
  {
    "id":"237",
    "name":"FM Brass",
    "category":"Brass",
    "msb":95.0,
    "lsb":65.0,
    "pc":109.0
  }
,       
  {
    "id":"238",
    "name":"Syn Brass 1",
    "category":"Brass",
    "msb":95.0,
    "lsb":65.0,
    "pc":110.0
  }
,       
  {
    "id":"239",
    "name":"Syn Brass 2",
    "category":"Brass",
    "msb":95.0,
    "lsb":65.0,
    "pc":111.0
  }
,       
  {
    "id":"240",
    "name":"JP8 Brass",
    "category":"Brass",
    "msb":95.0,
    "lsb":65.0,
    "pc":112.0
  }
,       
  {
    "id":"241",
    "name":"Soft SynBrs1",
    "category":"Brass",
    "msb":95.0,
    "lsb":65.0,
    "pc":113.0
  }
,       
  {
    "id":"242",
    "name":"Soft SynBrs2",
    "category":"Brass",
    "msb":95.0,
    "lsb":65.0,
    "pc":114.0
  }
,       
  {
    "id":"243",
    "name":"EpicSlow Brs",
    "category":"Brass",
    "msb":95.0,
    "lsb":65.0,
    "pc":115.0
  }
,       
  {
    "id":"244",
    "name":"JUNO Brass",
    "category":"Brass",
    "msb":95.0,
    "lsb":65.0,
    "pc":116.0
  }
,       
  {
    "id":"245",
    "name":"Poly Brass",
    "category":"Brass",
    "msb":95.0,
    "lsb":65.0,
    "pc":117.0
  }
,       
  {
    "id":"246",
    "name":"Voc:Ensemble",
    "category":"FX\/Other",
    "msb":95.0,
    "lsb":65.0,
    "pc":118.0
  }
,       
  {
    "id":"247",
    "name":"Voc:5thStack",
    "category":"FX\/Other",
    "msb":95.0,
    "lsb":65.0,
    "pc":119.0
  }
,       
  {
    "id":"248",
    "name":"Voc:Robot",
    "category":"FX\/Other",
    "msb":95.0,
    "lsb":65.0,
    "pc":120.0
  }
,       
  {
    "id":"249",
    "name":"Voc:Saw",
    "category":"FX\/Other",
    "msb":95.0,
    "lsb":65.0,
    "pc":121.0
  }
,       
  {
    "id":"250",
    "name":"Voc:Sqr",
    "category":"FX\/Other",
    "msb":95.0,
    "lsb":65.0,
    "pc":122.0
  }
,       
  {
    "id":"251",
    "name":"Voc:Rise Up",
    "category":"FX\/Other",
    "msb":95.0,
    "lsb":65.0,
    "pc":123.0
  }
,       
  {
    "id":"252",
    "name":"Voc:Auto Vib",
    "category":"FX\/Other",
    "msb":95.0,
    "lsb":65.0,
    "pc":124.0
  }
,       
  {
    "id":"253",
    "name":"Voc:PitchEnv",
    "category":"FX\/Other",
    "msb":95.0,
    "lsb":65.0,
    "pc":125.0
  }
,       
  {
    "id":"254",
    "name":"Voc:VP-330",
    "category":"FX\/Other",
    "msb":95.0,
    "lsb":65.0,
    "pc":126.0
  }
,       
  {
    "id":"255",
    "name":"Voc:Noise",
    "category":"FX\/Other",
    "msb":95.0,
    "lsb":65.0,
    "pc":127.0
  }
,       
  {
    "id":"256",
    "name":"Init Tone",
    "category":"FX\/Other",
    "msb":95.0,
    "lsb":65.0,
    "pc":128.0
  }

]

def generate_preset_list():
    """Generate a list of presets from RAW_PRESETS_CSV data."""
    presets = []
    csv_file = StringIO(RAW_PRESETS_CSV)
    reader = csv.DictReader(csv_file)
    
    for row in reader:
        print(row)
        # Convert numeric fields to integers
        msb = int(row['msb'])
        lsb = int(row['lsb'])
        pc = int(row['pc'])
        
        presets.append({
            "id": row['id'].zfill(3),
            "name": row['name'],
            "category": row['category'],
            "msb": msb,
            "lsb": lsb,
            "pc": pc
        })
    return presets


def get_preset_by_program_number(program_number):
    """Get preset information by program number.
    
    Args:
        program_number (str): The program number (e.g., '090')
        
    Returns:
        dict: Preset information containing msb, lsb, pc, and other details
        None: If preset not found
    """
    program_number = str(program_number).zfill(3)
    return next((preset for preset in DIGITAL_PRESET_LIST if preset["id"] == program_number), None)


def get_preset_parameters(program_number):
    """Get MSB, LSB, and PC values for a given program number.
    
    Args:
        program_number (str): The program number (e.g., '090')
        
    Returns:
        tuple: (msb, lsb, pc) values as integers
        None: If preset not found
    """
    preset = get_preset_by_program_number(program_number)
    if preset:
        return preset["msb"], preset["lsb"], preset["pc"]  # Already integers
    return None

    
