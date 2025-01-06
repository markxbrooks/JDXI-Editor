#!/usr/bin/perl
#
#  JDXi Manager version 0.30 alpha
#
#  Copyright (C) 2016-2024 LinuxTECH.NET
#
#       ALL RIGHTS RESERVED
#
#  Roland is a registered trademark of Roland Corporation
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

use strict;
use warnings;

my $vernr='0.30';
my $version=$vernr.' alpha';
my $year='2016-2024';
my $DEBUG=0;

use Tk;
use Tk::Pane;
use Tk::BrowseEntry;
use Tk::NoteBook;
use Tk::Balloon;
use Tk::PNG;
use Config::Simple '-strict';
use Time::HiRes qw(usleep time);
use LWP::UserAgent ();

# add path of binary to INC so that own libs can be found
use FindBin ();
use lib $FindBin::Bin;
my $binpath=$FindBin::Bin;

# custom perl modules
use LTNicons;
use JDXidata;
use LTNstyle;

# initialize config file handler
my $cfg = new Config::Simple(syntax=>'ini');

# check if OS is Linux or Windows for OS specific sections
our $LINUX;
our $WINDOWS;
BEGIN{ 
    if ($^O eq 'linux') { $LINUX=1; } 
}

use if ($LINUX),   'MIDI::ALSA'     => ('SND_SEQ_EVENT_PORT_UNSUBSCRIBED',
                                        'SND_SEQ_EVENT_SYSEX');

# initialise MIDI on Linux and Windows
my $midi;
my $midiIn;
my $midiOut;
if ($LINUX) {
    MIDI::ALSA::client("JDXi Manager PID_$$",1,1,0);
}

###### Global variables
my $midilast=0;
my $midilock=0;
my $PrgClass='jdxi_manager';
my $vcode=abs(25000-int(time/86400)).((gmtime(time))[6]);
my $webprfx='http://';
my $domain='LinuxTECH.NET';
my $webaddr=$webprfx.'JDXi-Manager.'.$domain;
my @note;
my $oct=60;
my $vel=120;
my $mchan=2; # MIDI ch. 3 (analog synth)
my $dev_nr=16; # default MIDI PRG RX/TX channel
my $umemnr=0;
my $mute=0;
my $dte_vis=0;
my $upd_chk=1;
my %copybuffer=(SN=>'', DR=>'');
my %PDM_val; # Hash of pulldownmenu active values


###### Global Defaults
# slider labels
my $sp=0; # label interval for 0-63 (could be 0,7,9,63)
my $sn=0; # label interval for -63-63 (could be 0,14,63)

# import custom colour, style and font settings and merge with defaults
my %custom;
Config::Simple->import_from('jdxi_colors.ini', \%custom);
my %conf=(SetDefaults(), %custom);

if ($conf{style} eq '3D') {
    $conf{btnstyle}  ='raised';
    $conf{snkstyle}  ='sunken';
    $conf{frmstyle}  ='raised';
    $conf{frmbdwidth}= 1;
    $conf{BEbdwidth} = 1;
    $conf{bdwidth}   = 1;
}

# set element defaults, use like this: %{$D{Btn_defaults}}
my %D=%{SetElemDefaults(\%conf)};

# JD-Xi Analog Init Tone / Preset 064
ReadPatData(\$AN{inittone}[0], \%AN, 0);
$AN{name}[0]=PData2Name($AN{data}[0]);

# JD-Xi SuperNatural Synth Init Tone / Preset 256
for my $n (0..4) {
    ReadPatData(\$SN1{inittone}[$n], \%SN1, $n);
    if ($SN1{name}[$n] ne "\x00") { $SN1{name}[$n]=PData2Name($SN1{data}[$n]) }
    ReadPatData(\$SN2{inittone}[$n], \%SN2, $n);
    if ($SN2{name}[$n] ne "\x00") { $SN2{name}[$n]=PData2Name($SN2{data}[$n]) }
}

# JD-Xi Drums Init Kit
ReadPatData(\$DR{inittone}[0], \%DR, 0);
$DR{name}[0]=PData2Name($DR{data}[0]);
for my $n (1..38) {
    ReadPatData(\$DR{inittone}[$n], \%DR, $n);
    $DR{name}[$n]=PData2Name($DR{data}[$n]);
}

# JD-Xi Init Program FX Data
for my $n (0..3) {
    ReadPatData(\$FX{inittone}[$n], \%FX, $n);
}

# JD-Xi Init Program ARP Data
ReadPatData(\$ARP{inittone}[0], \%ARP, 0);

# JD-Xi Init Program Vocal Effects Data
ReadPatData(\$VFX{inittone}[0], \%VFX, 0);

# selected and available midi in/out devices
my $midi_outdev='';
my $midi_outdev_prev='';
my $midi_indev='';
my $midi_indev_prev='';
my @midi_indevs=MidiPortList('in');
my @midi_outdevs=MidiPortList('out');

# these widgets need to be global
my $midiin;
my $midiout;
my $outtest;
my $panicbtn;
my $midiupload;
my $hidden;
my $donate;
my @FX_frame;

### ---------------------------------------------------------------------------
# set up main program window
my $mw=MainWindow->new(-bg=>$conf{bgcolor}, -class=>$PrgClass);
#$mw->scaling(2.5);
$mw->title('JDXi Manager ('.$version.') - Control Panel');
$mw->resizable(0,0);
$mw->protocol(WM_DELETE_WINDOW => [\&exitProgam, $mw]);
my $ptkdpi=$mw->pixels("1i");
my $zoomfctr=int(($ptkdpi*4)/96)/4;
if ($zoomfctr < 1){$zoomfctr=1} elsif ($zoomfctr > 2.75){$zoomfctr=2.75}
my @darrow_bits=darrow_bits($ptkdpi);
$mw->DefineBitmap('bm:darrow' => @darrow_bits);
SetStyle($mw, \%conf);
my $PrgIcon=$mw->Photo(-format=>'png', -data=>knob_png("$binpath/jdxi_128.png", $zoomfctr) );
$mw->iconimage($PrgIcon);
my $spacer_xpm =$mw->Pixmap(-data => spacer_xpm($conf{btnfcol}) );
my $triang_icon=$mw->Photo(-format=>'png', -data=>triangle_png($conf{btnfcol}, $zoomfctr) );
my $sine_icon  =$mw->Photo(-format=>'png', -data=>    sine_png($conf{btnfcol}, $zoomfctr) );
my $upsaw_icon =$mw->Photo(-format=>'png', -data=>   upsaw_png($conf{btnfcol}, $zoomfctr) );
my $spsaw_icon =$mw->Photo(-format=>'png', -data=>   spsaw_png($conf{btnfcol}, $zoomfctr) );
my $square_icon=$mw->Photo(-format=>'png', -data=>  square_png($conf{btnfcol}, $zoomfctr) );
my $pwsqu_icon =$mw->Photo(-format=>'png', -data=>   pwsqu_png($conf{btnfcol}, $zoomfctr) );
my $noise_icon =$mw->Photo(-format=>'png', -data=>   noise_png($conf{btnfcol}, $zoomfctr) );

my $MBar   =$mw->Frame(%{$D{MBar_defaults}})->pack(-anchor=>'n',  -fill=>'x',    -expand=>1);
my $other  =$mw->Frame(-bg=>$conf{bgcolor} )->pack(-anchor=>'nw', -fill=>'both', -expand=>1, -pady=>1, -side=>'right');
my $midiset=$mw->Frame(-bg=>$conf{bgcolor} )->pack(-anchor=>'n',  -fill=>'both', -expand=>1, -pady=>4, -padx=>4);
my $parts  =$mw->Frame(-bg=>$conf{bgcolor} )->pack(-anchor=>'n',  -fill=>'both', -expand=>1);
topMenubar($mw, $MBar);
MIDI_IOconfig($midiset);
Parts($parts);
Other($other);

# gather basic technical details of system we are running on
my $OSdetails=$mw->server();
my $scrwth=$mw->screenwidth;
my $scrhgt=$mw->screenheight;
my $windpi='';
#my $cpuname='';
#if ($LINUX) {$cpuname=`grep -m 1 "model name" /proc/cpuinfo`}
if ($LINUX) {
    $OSdetails=get_distro();
    my $DskEnv;
    if    ($ENV{'XDG_CURRENT_DESKTOP'}) { $DskEnv=$ENV{'XDG_CURRENT_DESKTOP'} }
    elsif ($ENV{'DESKTOP'})             { $DskEnv=$ENV{'DESKTOP'} }
    elsif ($ENV{'XDG_MENU_PREFIX'})     { $DskEnv=$ENV{'XDG_MENU_PREFIX'} }
    elsif ($ENV{'DESKTOP_SESSION'})     { $DskEnv=$ENV{'DESKTOP_SESSION'} }
    if ($DskEnv) {
        if ($DskEnv=~/.*-$/) { chop $DskEnv }
        if ($DskEnv=~/[ -~]+/) { $OSdetails.='-'.$DskEnv }
    }
}

if ($DEBUG) {print STDOUT 'Window System:['. $mw->windowingsystem .'] Server:['.$OSdetails."]\n".
#             'cpu:['.$cpuname."]\n".
             'Screen res:['.$scrwth.'x'.$scrhgt."] WinDPI:[$windpi] PTkDPI:[$ptkdpi] Zoom:[$zoomfctr]\n";
}

AdjustDefWinRes($ptkdpi);
LoadConfig();

$mw->after(50, sub{ if ($upd_chk){CheckUpdate()} });

MainLoop;


########################################################################################################################
# Subroutines
#############

# add scrollbars to window
sub ScrolledWin {
    my($ref_win)=@_;

    $$ref_win->resizable(1,1);
    my $scfr=$$ref_win->Scrolled( 'Frame',
        -scrollbars => 'osoe',
        -sticky     => 'nsew',
        -background => $conf{divcol}
    );
    return $scfr;
}

# check for updated version
sub CheckUpdate {
    my $wdpi=''; if ($windpi) {$wdpi=$windpi.' / '}
    my $screensz=$scrwth.'x'.$scrhgt.'; '.$wdpi.$ptkdpi.' dpi; zoom '.$zoomfctr.';';
    my $ua = LWP::UserAgent->new();
    $ua->agent("JDXi_Manager/$vernr ($OSdetails.$vcode; $screensz)");
    $ua->timeout(2);
    $ua->env_proxy;
    $mw->Busy();
    my $response=$ua->get($webaddr.'/jmver.txt');
    if ($response->is_success) {
        my $newver=$response->decoded_content;
        my $resp='';
        if ($DEBUG) {print STDOUT "Latest version is: ".$newver." \n";}
        if ($newver=~/^[0-9]+\.[0-9]+$/ && ($newver > $vernr)) {
            $resp=$mw->messageBox(
                -title   =>'New Release Available',
                -icon    => 'info',
                -message =>"A new release of the JDXi Manager is available.\nWould you like to go to the JDXi Manager website now?",
                -type    =>'YesNo',
                -default =>'Yes'
            );
        if ($resp eq 'Yes') { AccessURL("$webaddr/?ref=$vernr#newrel") }
        }
    } else {
        if ($DEBUG) {print STDOUT "Error while checking for newer version: ". $response->status_line ." \n";}
    }
    $mw->Unbusy;
}

# read Linux distro details if available
sub get_distro {
    my $distro='';
    my $lsb=new Config::Simple(syntax=>'simple');
    if ($lsb->read('/etc/lsb-release') and $lsb->param('DISTRIB_DESCRIPTION')) {
        $distro=$lsb->param('DISTRIB_DESCRIPTION');
    } elsif ($lsb->read('/etc/os-release') and $lsb->param('PRETTY_NAME')) {
        $distro=$lsb->param('PRETTY_NAME');
    } else {
        $distro=`uname -smr 2>/dev/null`;
    }
    chomp $distro;
    if ($distro ne '') { return $distro } else { return 'unknown system' }
}


# set up keyboard keys as MIDI keyboard
sub KbdSetup {
    my($win)=@_;

    # Function keys F1-F8 bindings to select octave (F5 => 60=C4)
    for my $n (1..8) {
        my $val=$n*12;
        $win->bind("<Key-F$n>" => [\&SelOct, $val]);
    }
    # Function keys F9-F12 bindings to select Part
    for my $n (9..12) {
        my $val=$n-9;
        if ($val == 3) {$val = 9}
        $win->bind("<Key-F$n>" => [\&SelPart, $val]);
    }

    # key to note mappings for QWERTY, AZERTY and QWERTZ keyboards
    my %key2note=('z'=>0, 'w'=>0, 'y'=>0, 's'=>1, 'x'=>2, 'd'=>3, 'c'=>4, 'v'=>5,
                  'g'=>6, 'b'=>7, 'h'=>8, 'n'=>9, 'j'=>10, 'm'=>11, 'comma'=>11);

    while (my($key, $note) = each %key2note) {
        $win->bind("<Key-$key>"           => [\&NoteOn,  $note]);
        $win->bind("<KeyRelease-$key>"    => [\&NoteOff, $note]);
    }
}

# Called when F1-F8 pressed to select octave
sub SelOct {
    my($button, $nr)=@_;
    $oct=$nr;
}

# Called when F9-F12 pressed to select Part
sub SelPart {
    my($button, $nr)=@_;
    $mchan=$nr;
}

# Called when keyboard note key is pressed
sub NoteOn {
    my($button, $nr)=@_;
    my $nnr=$oct+$nr;
    if ((!($note[$nnr]) or $note[$nnr]==0) and !$mute) {
        $note[$nnr]=1;
        PlayMidiNote($mchan,$nnr,$vel,1);
    }
}

# Called when keyboard note key is released
sub NoteOff {
    my($button, $nr)=@_;
    my $nnr=$oct+$nr;
    PlayMidiNote($mchan,$nnr,0,0);
    $note[$nnr]=0;
}

# Mousewheel bindings for various Elements
sub BindMWheel {
    my($widget, $parent, $target, $var, $incr)=@_;
    if ($LINUX) {
        $$widget->bind('<Button-5>'  =>  sub {$$target->set($$var-$incr)});
        $$widget->bind('<Button-4>'  =>  sub {$$target->set($$var+$incr)});
    }
}

# quit the program, ask for confirmation if unsaved changes
sub exitProgam {
    my ($win)=@_;

    if ($AN{modified} || $SN1{modified} || $SN2{modified} || $DR{modified} || $FX{modified} || $ARP{modified} || $VFX{modified}) {
        my $rtn=UnsavedChanges($win, 'Quit anyway?');
        if ($rtn eq 'Yes') {
            exit;
        }
    } else {
        exit;
    }
}

# close an Editor Window
sub closeSubWin {
    my ($rf_hash)=@_;

    if ($DEBUG) {print STDOUT "[ modified => $$rf_hash{modified} ]\n"}

    if ($$rf_hash{modified} == 1) {
        my $rtn=UnsavedChanges($$rf_hash{window}, 'Close anyway?');
        if ($rtn eq 'Yes') {
            $$rf_hash{geometry}=$$rf_hash{window}->geometry;
            if ($DEBUG) { print STDOUT $$rf_hash{geometry} ."\n" };
            $$rf_hash{window}->destroy;
            $$rf_hash{ct}={a=>0};
            $$rf_hash{modified}=0;
            $$rf_hash{window}='';
            if ($$rf_hash{type} eq 'DR') {$hidden=''}
            return 0;
        }
    } else {
        $$rf_hash{geometry}=$$rf_hash{window}->geometry;
        if ($DEBUG) { print STDOUT $$rf_hash{geometry} ."\n" };
        $$rf_hash{window}->destroy;
            $$rf_hash{ct}={a=>0};
            $$rf_hash{window}='';
            if ($$rf_hash{type} eq 'DR') {$hidden=''}
            return 0;
    }
    return 1;
}

# Do nothing
sub Noop {}

# call as: UnsavedChanges($question), returns: Yes/No
sub UnsavedChanges {
    my ($win, $question)=@_;
    my $rtn=$win->messageBox(
        -title   => 'Unsaved changes',
        -icon    => 'question',
        -message => "There are unsaved changes that will be lost unless you save them first.\n\n$question",
        -type    => 'YesNo',
        -default => 'No'
    );
    return $rtn;
}

# Confirm store patch in JD-Xi user memory, returns: Yes/No
sub StoreConfirm {
    my ($win, $patchnr)=@_;
    my $rtn=$win->messageBox(
        -title   => 'Confirm Patch Overwrite',
        -icon    => 'question',
        -message => "Do you really want to overwrite user patch $patchnr on your JD-Xi with your current patch?\n",
        -type    => 'YesNo',
        -default => 'No'
    );
    return $rtn;
}

# Error popup window
sub Error {
    my ($win, $msg)=@_;
    $win->messageBox(
        -title   =>'Error',
        -icon    => 'warning',
        -message =>"$msg",
        -type    =>'Ok',
        -default =>'Ok'
    );
}

# Success popup window
sub Success {
    my ($win, $msg)=@_;
    $win->messageBox(
        -title   =>'Success',
        -icon    => 'info',
        -message =>"$msg",
        -type    =>'Ok',
        -default =>'Ok'
    );
}

# set up top bar
sub topMenubar {
    my ($win, $frame)=@_;

    # Pulldown Menus
    my $pdmenu=$frame->Frame()->pack(-side=>'left');
    my $btn0=$pdmenu->Menubutton(-text=>'File', -tearoff=>0, -anchor=>'w',
        -menuitems => [['command'=>'Quit',       -accelerator=>'Ctrl+Q', -command=>[\&exitProgam, $win]]]
    )->pack(-side=>'left');

    my $btn1=$pdmenu->Menubutton(-text=>'Edit', -tearoff=>0, -anchor=>'w',
        -menuitems => [['command'=>'Hide/Show Donate Button',            -command=> sub{ if ($donate->ismapped) {$donate->gridForget()}
                                                                          else {$donate->grid(%{$D{GridCfg}}, -padx=>10, -pady=>5, -row=>0, -column=>4)}} ],
                       ['checkbutton'=>'Automatically Check for Updates',-variable=>\$upd_chk, -command=>\&SaveConfig],
                       '-',
                       ['command'=>'Save Settings',                      -command=> \&SaveConfig ]]
    )->pack(-side=>'left');

    my $btn2=$pdmenu->Menubutton(-text=>'Help', -tearoff=>0, -anchor=>'w',
        -menuitems => [['command'=>'Online Documentation',               -command=>[\&AccessURL, "$webaddr/docs/?ref=$vernr"]],
                       ['command'=>'JDXi Manager Website',               -command=>[\&AccessURL, "$webaddr/?ref=$vernr"]],
                       ['command'=>'Roland JD-Xi Manuals',               -command=>[\&AccessURL, "$webaddr/goto/roland_mans?ref=$vernr"]],
                       '-',
                       ['command'=>'About JDXi Manager',                 -command=>[\&About, $win]]]
    )->pack(-side=>'left');

    # global keyboard bindings for Menus
    $win->bind("<Control-q>" => [\&exitProgam, $win]);    $win->bind("<Control-Q>" => [\&exitProgam, $win]);
}

# Menu bar for editor windows
sub FileMenu {
    my ($rf_hash)=@_;

    my $type=substr($$rf_hash{type},0,2);
    my $mbar=$$rf_hash{window}->Frame(-relief=>'raised', -borderwidth=>1);
    my $file=$mbar->Menubutton(-text=>'File', -tearoff=>0, -anchor=>'w',
          -menuitems=>[['command'=>'New',        -command=>sub{   newVoice($rf_hash)}, -accelerator=>'Ctrl+I'],
                       ['command'=>'Open...',    -command=>sub{   loadFile($rf_hash)}, -accelerator=>'Ctrl+O'],
#                      ['command'=>'Browse...',  -command=>sub{ browseFile($rf_hash)}],
                       '-',
                       ['command'=>'Save',       -command=>sub{   saveFile($rf_hash)}, -accelerator=>'Ctrl+S'],
                       ['command'=>'Save As...', -command=>sub{ saveasFile($rf_hash)}, -accelerator=>'Ctrl+A'],
                       '-',
                       ['command'=>'Close',      -command=>sub{closeSubWin($rf_hash)}, -accelerator=>'Ctrl+Q']]
    )->pack(-side=>'left');
    $$rf_hash{window}->bind("<Control-i>"=>sub{   newVoice($rf_hash)} );
    $$rf_hash{window}->bind("<Control-o>"=>sub{   loadFile($rf_hash)} );
    $$rf_hash{window}->bind("<Control-s>"=>sub{   saveFile($rf_hash)} );
    $$rf_hash{window}->bind("<Control-a>"=>sub{ saveasFile($rf_hash)} );
    $$rf_hash{window}->bind("<Control-q>"=>sub{closeSubWin($rf_hash)} );
    # random patch button for analog synth part
    if ($type eq 'AN') {
        $mbar->Button(-text=>'Random Patch', -command=>[\&rndVoice])->pack(-side=>'right');
    }
    # copy and paste partials menu for drums and digital synths parts
    if ($type eq 'DR' || $type eq 'SN') {
        my $file=$mbar->Menubutton(-text=>'Edit', -tearoff=>0, -anchor=>'w',
          -menuitems=>[['command'=>'Copy Partial',  -command=>sub{ copyPart($rf_hash, $type)}, -accelerator=>'Ctrl+C'],
                       ['command'=>'Paste Partial', -command=>sub{pastePart($rf_hash, $type)}, -accelerator=>'Ctrl+V']]
        )->pack(-side=>'left');
        $$rf_hash{window}->bind("<Control-c>"=>sub{ copyPart($rf_hash, $type)} );
        $$rf_hash{window}->bind("<Control-v>"=>sub{pastePart($rf_hash, $type)} );
    }
    my $wins=$mbar->Menubutton(-text=>'Window', -tearoff=>0, -anchor=>'w', -menuitems=>[
        ['command'=>'Digital Synth 1 ', -command=>sub{ if (! $SN1{window}){SN_Edit(1)} else {$SN1{window}->deiconify(); $SN1{window}->raise();} } ],
        ['command'=>'Digital Synth 2 ', -command=>sub{ if (! $SN2{window}){SN_Edit(2)} else {$SN2{window}->deiconify(); $SN2{window}->raise();} } ],
        ['command'=>'Drums',            -command=>sub{ if (!  $DR{window}){DR_Edit()}  else {$DR{window}->deiconify();   $DR{window}->raise();} } ],
        ['command'=>'Analog Synth',     -command=>sub{ if (!  $AN{window}){AN_Edit()}  else {$AN{window}->deiconify();   $AN{window}->raise();} } ],
        ['command'=>'Effects',          -command=>sub{ if (!  $FX{window}){FX_Edit()}  else {$FX{window}->deiconify();   $FX{window}->raise();} } ],
        ['command'=>'Arpeggio',         -command=>sub{ if (! $ARP{window}){ARP_Edit()} else {$ARP{window}->deiconify(); $ARP{window}->raise();} } ],
        ['command'=>'Vocal Effects',    -command=>sub{ if (! $VFX{window}){VFX_Edit()} else {$VFX{window}->deiconify(); $VFX{window}->raise();} } ]]
    )->pack(-side=>'left');
    return $mbar;
}

# copy current partial
sub copyPart {
    my ($rf_hash, $type)=@_;
    my $sysex=\$copybuffer{$type};
    my $n=$$rf_hash{curpart};
    if ($$rf_hash{name}[$n] ne "\x00") { Name2PData(\$$rf_hash{name}[$n], $$rf_hash{data}[$n]) }
    $$sysex=WritePatData($rf_hash, $n);
}

# paste copy into current partial
sub pastePart {
    my ($rf_hash, $type)=@_;
    my $sysex=\$copybuffer{$type};
    my $n=$$rf_hash{curpart};
    if (length($$sysex) == $$rf_hash{datalen}[$n]) {
        ReadPatData($sysex, $rf_hash, $n);
        if ($$rf_hash{name}[$n] ne "\x00") { $$rf_hash{name}[$n]=PData2Name($$rf_hash{data}[$n]) }
        $$rf_hash{modified}=1;
        SysexStrSend($rf_hash, $n);
    } else {
        Error($$rf_hash{window},"Error: copy buffer is empty.\nCopy a partial first before pasting.");
    }
}

# spawn browser with given URL
sub AccessURL {
    my ($url)=@_;
    if($LINUX) { system("xdg-open \"$url\" >/dev/null 2>&1") }
}

# Other Editor Buttons
sub Other {
    my ($frame)=@_;

    $frame->Button(%{$D{PtBtn_defaults}}, -text=>"Effects", -width=>9,
        -command=> sub{ if (! $FX{window}){FX_Edit()} else {$FX{window}->deiconify(); $FX{window}->raise();} }
    )->pack(-padx=>10, -pady=>6);
    $frame->Button(%{$D{PtBtn_defaults}}, -text=>"Vocal FX", -width=>9,
        -command=> sub{ if (! $VFX{window}){VFX_Edit()} else {$VFX{window}->deiconify(); $VFX{window}->raise();} }
    )->pack(-padx=>10, -pady=>0);
    $frame->Button(%{$D{PtBtn_defaults}}, -text=>"Arpeggio", -width=>9,
        -command=> sub{ if (! $ARP{window}){ARP_Edit()} else {$ARP{window}->deiconify(); $ARP{window}->raise();} }
    )->pack(-padx=>10, -pady=>6);
    $frame->Button(%{$D{PtBtn_defaults}}, -text=>"Program", -width=>9, -state=>'disabled',
    )->pack(-padx=>10, -pady=>0);
    $frame->Frame(-bg=>$conf{bgcolor}, -borderwidth=>0, -highlightthickness=>0, -height=>0, -width=>0
    )->pack(-padx=>10, -pady=>2);
}

# Part Editor Buttons
sub Parts {
    my ($frame)=@_;

    my $sfr=StdFrame(\$frame, 'Part Editors', $conf{CFGbgc}, $conf{CFGfgc});

    $sfr->Button(%{$D{PtBtn_defaults}},
        -text             => "Digital\nSynth 1",
        -command          => sub{ if (! $SN1{window}){SN_Edit(1)} else {$SN1{window}->deiconify(); $SN1{window}->raise();} }
    )->grid(
    $sfr->Button(%{$D{PtBtn_defaults}},
        -text             => "Digital\nSynth 2",
        -command          => sub{ if (! $SN2{window}){SN_Edit(2)} else {$SN2{window}->deiconify(); $SN2{window}->raise();} }
    ),
    $sfr->Button(%{$D{PtBtn_defaults}},
        -text             => "Drums",
        -command          => sub{ if (! $DR{window}){DR_Edit()} else {$DR{window}->deiconify(); $DR{window}->raise();} }
    ),
    $sfr->Button(%{$D{PtBtn_defaults}},
        -foreground       => $conf{APtbtncol},
        -activeforeground => $conf{APtbtncol},
        -text             => "Analog\n Synth",
        -command          => sub{ if (! $AN{window}){AN_Edit()} else {$AN{window}->deiconify(); $AN{window}->raise();} }
    ), %{$D{GridCfg}}, -padx=>10, -pady=>5);
    $donate=$sfr->Button(%{$D{PtBtn_defaults}},
        -background       => '#FFB02D',
        -activebackground => '#FFB02D',
        -foreground       => '#01318F',
        -activeforeground => '#01318F',
        -text             => "Donate now\nwith PayPal",
        -command          => sub{ AccessURL($webaddr.'/donate')}
    );
    my $balloon=$sfr->Balloon();
    $balloon->attach($donate, -state => 'balloon', -balloonmsg =>
        "Click here to go to the PayPal donation web page.\n\n". 
        "Your donation is greatly appreciated and will\n".
        "encourage us to continue improving the JDXi Manager.\n");
}

# 'About' information window
sub About {
    my ($win)=@_;

    $win->messageBox(
        -title   => 'About - JDXi Manager',
        -icon    => 'info',
        -message => "            JDXi Manager v. $version\n\n".
                    "            \x{00A9} $year $domain\n".
                    "                  All rights reserved\n\n".
                    "A Patch Editor for the Roland JD-Xi\n\n".
                    "Official Internet Page: $webaddr/\n\n".
                    "Roland is a registered trademark of Roland Corp.\n\n\n".
                    "For personal use only, redistribution strictly prohibited.\n",
        -type    => 'Ok',
        -default => 'Ok'
    );
}

# save config settings to ini file
sub SaveConfig {
    if ($midi_indev  ne '') { $cfg->param('MIDI_IN',  "$midi_indev") }
    if ($midi_outdev ne '') { $cfg->param('MIDI_OUT', "$midi_outdev") }
    $cfg->param('Update_Check', $upd_chk);
    $cfg->param('MIDI_Channel', $dev_nr);
    $cfg->param('Dte_vis', $dte_vis);
    $cfg->param('MW_geometry',($mw->geometry));
    for my $n (0..$#Part) {
        if ($Part[$n]{window} && Exists($Part[$n]{window}) && $Part[$n]{window}->state() eq 'normal') {
            $Part[$n]{geometry}=$Part[$n]{window}->geometry;
            $cfg->param($Part[$n]{type}.'_geometry', $Part[$n]{geometry});
        }
    }
    $cfg->save('jdxi_manager.ini') or Error($mw, $cfg->error());
}

# adjust default resolution of editor windows based on dpi
sub AdjustDefWinRes {
    my ($scrdpi)=@_;
    my $factor=$scrdpi/96;
    for my $n (0..$#Part) {
        my ($resx,$resy)=$Part[$n]{geometry}=~/(\d+)x(\d+)/;
        $Part[$n]{geometry}=int($resx*$factor)."x".int($resy*$factor);
    }
}

# load and apply saved settings from ini file
sub LoadConfig {
    $cfg->read('jdxi_manager.ini') or return;
    if (defined $cfg->param('Dte_vis')) { $dte_vis=$cfg->param('Dte_vis');
    }
    # restore update check setting (0-1)
    if (defined $cfg->param('Update_Check')                  &&
                $cfg->param('Update_Check')=~/^(0|1)$/) { $upd_chk=$cfg->param('Update_Check'); }
    # restore MIDI Channel (1-16)
    if (defined $cfg->param('MIDI_Channel')                  &&
                $cfg->param('MIDI_Channel')=~/^(1[0-6]|[1-9])$/) { $dev_nr=$cfg->param('MIDI_Channel'); }
    # restore main window position only
    if (defined $cfg->param('MW_geometry')                   &&
               ($cfg->param('MW_geometry')=~/\d+x\d+(\+-?\d+\+-?\d+)/)) { my $xypos=$1; $mw->geometry($xypos); }
    # restore part window positions and size
    for my $n (0..$#Part) {
        if (defined $cfg->param($Part[$n]{type}.'_geometry') &&
                   ($cfg->param($Part[$n]{type}.'_geometry')=~/\d+x\d+\+-?\d+\+-?\d+/)) {
            $Part[$n]{geometry}=$cfg->param($Part[$n]{type}.'_geometry');
        }
    }
    # restore MIDI IN config
    if (defined $cfg->param('MIDI_IN')                       &&
               ($cfg->param('MIDI_IN') ne '')) {
        my @midi_indevices=MidiPortList('in');
        my $in_pre=0;
        for (my $n=0; $n<@midi_indevices; $n++) {
            if ($midi_indevices[$n] eq $cfg->param('MIDI_IN')) {
                $midi_indev=$cfg->param('MIDI_IN');
                MidiConSetup('in');
                $in_pre=1;
                last;
            }
        }
        if ($in_pre == 0) {
            Error($mw,'Default MIDI IN device \''. $cfg->param('MIDI_IN') .'\' not available, check connections.');
        }
    }
    # restore MIDI OUT config
    if (defined $cfg->param('MIDI_OUT')                      &&
               ($cfg->param('MIDI_OUT') ne '')) {
        my @midi_outdevices=MidiPortList('out');
        my $out_pre=0;
        for (my $m=0; $m<@midi_outdevices; $m++) {
            if ($midi_outdevices[$m] eq $cfg->param('MIDI_OUT')) {
                $midi_outdev=$cfg->param('MIDI_OUT');
                MidiConSetup('out');
                $out_pre=1;
                last;
            }
        }
        if ($out_pre == 0) {
            Error($mw,'Default MIDI OUT device \''. $cfg->param('MIDI_OUT') .'\' not available, check connections.');
        }
    }
}

# Edit Buffer Operations and Preset Loading
sub EditBufferOps {
    my ($frame, $rf_hash)=@_;

    my $prpos='left'; if ($$rf_hash{type} eq 'AN') {$prpos='top'}
    my $fr1=$frame->Frame(-background=>$conf{bgcolor})->pack(-side=>$prpos, -anchor=>'n', -fill=>'both', -expand=>1);
    my $fr2=$frame->Frame(-background=>$conf{bgcolor})->pack(-side=>$prpos, -anchor=>'n', -fill=>'both', -expand=>1);

    # Edit Buffer Operations Frame
    $fr1->Label(%{$D{Label_defaults}},
        -font         => $conf{midicfgfnt},
        -text         => 'JD-Xi Edit Buffer: ',
        -justify      => 'right'
    )->grid(-row=>1, -column=>1, -padx=>2, -pady=>5);

    $$rf_hash{dumpto}=$fr1->Button(%{$D{Btn_defaults}},
        -text         => 'Dump to',
        -command      => sub{ SysexPatSend($rf_hash); }
    )->grid(-row=>1, -column=>2, -padx=>0, -pady=>5);

    if ($midi_outdev ne '') {
        $$rf_hash{dumpto}->configure(-state=>'normal');
    } else {
        $$rf_hash{dumpto}->configure(-state=>'disabled');
    }

    $$rf_hash{readfrom}=$fr1->Button(%{$D{Btn_defaults}},
        -text         => 'Read from',
        -command      => sub{ SysexPatRcve($rf_hash); }
    )->grid(-row=>1, -column=>3, -padx=>8, -pady=>5);

    if (($midi_indev ne '') && ($midi_outdev ne '')) {
        $$rf_hash{readfrom}->configure(-state=>'normal');
    } else {
        $$rf_hash{readfrom}->configure(-state=>'disabled');
    }

    # Load Presets Frame
    if ($$rf_hash{type}=~/^(AN|SN1|SN2|DR)$/) {
        $fr2->Label(%{$D{Label_defaults}},
            -font         => $conf{midicfgfnt},
            -text         => 'Preset: ',
            -justify      => 'right'
        )->grid(-row=>1, -column=>0, -padx=>2, -pady=>5);

        $$rf_hash{ldprwgt}[0]=$fr2->BrowseEntry(%{$D{BEntry_defaults}},
            -variable     => \$$rf_hash{selpreset},
            -choices      => ["$$rf_hash{selpreset}"],
            -font         => $conf{midicfgfnt},
            -width        => 18,
            -listheight   => 34,
            -listcmd      => sub{ $_[0]->delete(0, 'end');
                                  $_[0]->insert('end', $_) for (@{$$rf_hash{presets}});
                                  $_[0]->Subwidget('slistbox')->see(($$rf_hash{selpreset}=~/^(\d\d\d):.*/)[0]);
                                }
        )->grid(-row=>1, -column=>1, -padx=>0, -pady=>5);
        $$rf_hash{ldprwgt}[0]->Subwidget('choices' )->configure(%{$D{choices_defaults}});
        $$rf_hash{ldprwgt}[0]->Subwidget('arrow'   )->configure(%{$D{arrow_defaults}});
        $$rf_hash{ldprwgt}[0]->Subwidget('slistbox')->configure(-activestyle=>'none');

        if ($LINUX) {
            $$rf_hash{ldprwgt}[0]->bind('<Button-5>'  =>  sub { ChgPreset($rf_hash, 'prev') });
            $$rf_hash{ldprwgt}[0]->bind('<Button-4>'  =>  sub { ChgPreset($rf_hash, 'next') });
            $$rf_hash{ldprwgt}[0]->Subwidget('arrow'  )->bind('<Button-5>'  =>  sub { ChgPreset($rf_hash, 'prev') });
            $$rf_hash{ldprwgt}[0]->Subwidget('arrow'  )->bind('<Button-4>'  =>  sub { ChgPreset($rf_hash, 'next') });
        }

        $$rf_hash{ldprwgt}[1]=$fr2->Button(%{$D{Btn_defaults}},
            -text         => 'Load',
            -command      => sub{ LoadPreset($rf_hash) }
        )->grid(-row=>1, -column=>2, -padx=>8, -pady=>5);
        if ($LINUX) {
            $$rf_hash{ldprwgt}[1]->bind('<Button-5>'  =>  sub { ChgPreset($rf_hash, 'prev') });
            $$rf_hash{ldprwgt}[1]->bind('<Button-4>'  =>  sub { ChgPreset($rf_hash, 'next') });
        }
        if (($midi_indev ne '') && ($midi_outdev ne '') && ($$rf_hash{selpreset} ne '')) {
            $$rf_hash{ldprwgt}[1]->configure(-state=>'normal');
        } else {
            $$rf_hash{ldprwgt}[1]->configure(-state=>'disabled');
        }
    }
    else { $fr2->destroy() }
}

# Load selected preset from JD-Xi
sub LoadPreset {
    my ($rf_hash)=@_;

    my $rtn='';
    if ($$rf_hash{modified} == 1) {
        $rtn=UnsavedChanges($$rf_hash{window}, 'Load selected Preset anyway?');
    }
    if (($rtn eq "Yes") or ($$rf_hash{modified} == 0)) {
        my $addr; my $msb; my $lsb=64;
        my ($prnr)=$$rf_hash{selpreset}=~/^(\d\d\d):.*/;
        if    ($$rf_hash{type} eq 'SN1') { $addr='18002006'; $msb=95; if ($prnr>128) {$lsb=65; $prnr=$prnr-128;}}
        elsif ($$rf_hash{type} eq 'SN2') { $addr='18002106'; $msb=95; if ($prnr>128) {$lsb=65; $prnr=$prnr-128;}}
        elsif ($$rf_hash{type} eq 'AN')  { $addr='18002206'; $msb=94; }
        elsif ($$rf_hash{type} eq 'DR')  { $addr='18002306'; $msb=86; }
        SendPaChMsg($addr,$msb,1);
        SendPaChMsg($addr+1,$lsb,1);
        SendPaChMsg($addr+2,($prnr-1),1);
        SysexPatRcve($rf_hash);
    }
}

# select next/prev choice in presets pulldown menu when mouse wheel is scrolled down/up
sub ChgPreset {
    my ($rf_hash, $chg)=@_;

    if ($$rf_hash{selpreset} eq '') {
        $$rf_hash{selpreset}=${$$rf_hash{presets}}[0];
    }
    my ($prnr)=$$rf_hash{selpreset}=~/^(\d\d\d):.*/;
    if ($chg eq 'prev' && ($prnr > 1)) {
        $$rf_hash{selpreset}=${$$rf_hash{presets}}[$prnr-2];
    }
    elsif ($chg eq 'next' && ($prnr < @{$$rf_hash{presets}})) {
        $$rf_hash{selpreset}=${$$rf_hash{presets}}[$prnr];
    }
}

# Reset Patch to Init Tone
sub newVoice {
    my ($rf_hash)=@_;

    my $rtn='';
    if ($$rf_hash{modified} == 1) {
        $rtn=UnsavedChanges($$rf_hash{window}, 'Reset patch to default values anyway?');
    }
    if (($rtn eq "Yes") or ($$rf_hash{modified} == 0)) {
        for (my $n=0; $n<@{$$rf_hash{data}}; $n++) {
            ReadPatData(\$$rf_hash{inittone}[$n], $rf_hash, $n);
            if ($$rf_hash{name}[$n] ne "\x00") { $$rf_hash{name}[$n]=PData2Name($$rf_hash{data}[$n]) }
        }
        $$rf_hash{modified}=0;
        $$rf_hash{filename}='';
        $$rf_hash{window}->title($$rf_hash{titlestr});
        if ($$rf_hash{type} eq 'FX') { ShowFXCtrls(0); ShowFXCtrls(1); }
        if ($midi_outdev ne '') { SysexPatSend($rf_hash); }
    }
}

# generate randon analog Tone
sub rndVoice {
    my $rtn='';
    if ($AN{modified} == 1) {
        $rtn=UnsavedChanges($AN{window}, 'Generate random patch anyway?');
    }
    if (($rtn eq "Yes") or ($AN{modified} == 0)) {
        my $rndtone="\x52\x61\x6E\x64\x6F\x6D\x20";
        for (my $n=0; $n<@AN_rnd; $n++) {
        my $rndval=int(rand($AN_rnd[$n][1]-$AN_rnd[$n][0]+1))+$AN_rnd[$n][0];
        $rndtone=$rndtone.chr($rndval);
        }
        $rndtone=$rndtone."\x00\x00\x00\x00";
        ReadPatData(\$rndtone,\%AN,0);
        $AN{name}[0]=PData2Name($AN{data}[0]);
        $AN{modified}=0;
        $AN{filename}='';
        $AN{window}->title($AN{titlestr});
        if ($midi_outdev ne '') { SysexPatSend(\%AN); }
    }
}

# browse and load files from a folder with one click
sub browseFile {
    my ($rf_hash)=@_;

    my $brWin=$mw->Toplevel(-bg=>$conf{bgcolor}, -class=>$PrgClass);
    $brWin->title("Browse $$rf_hash{filetype} Sysex Files (JDXi-". substr($$rf_hash{type},0,2) .")");
    $brWin->iconimage($PrgIcon);
    $brWin->geometry("576x480");
    my $Bdir;
    if ($Bdir=$brWin->chooseDirectory) {
        $brWin->messageBox(-message=>"Dir: $Bdir");
    }

}

# load a JD-Xi sysex dump file
sub loadFile {
    my ($rf_hash)=@_;

    my $rtn="";
    if ($$rf_hash{modified} == 1) {
        $rtn=UnsavedChanges($$rf_hash{window}, 'Open patch from file anyway?');
    }
    if (($rtn eq "Yes") or ($$rf_hash{modified} == 0)) {
        my @exts=('.syx', '.SYX');
        if ($$rf_hash{okedext}) { push @exts, ".$$rf_hash{okedext}"; }
        my $types=[ ['Sysex Files', [@exts] ], ['All Files', '*'] ];
        my $gr=''; if ( $$rf_hash{filetype}=~/^[aeiou]/i ) {$gr='n'} # get a/an correct
        my $syx_file=$$rf_hash{window}->getOpenFile(
            -defaultextension => '.syx',
            -filetypes        => $types,
            -title            => "Open a$gr $$rf_hash{filetype} Sysex File (JDXi-". substr($$rf_hash{type},0,2) .")"
        );
        if ($syx_file && -r $syx_file) {
            open my $fh, '<', $syx_file;
            binmode $fh;
            my $sysex = do { local $/; <$fh> };
            close $fh;
            # import okJDXIeditor files
            if ($$rf_hash{okedext} && $syx_file=~/\.$$rf_hash{okedext}$/) {
                if ($sysex=~/^[A-F,a-f,0-9,\x0A]*$/) {
                    $sysex=ascii2tone($sysex);
                    # if no part38 then use part 38 from inittone
                    if (length $sysex == 7765) {
                         my $part38=$DR{addr}[38].$DR{inittone}[38];
                         $sysex.="\xF0".$ROL_ID.chr($dev_nr).$JDXI_ID.$DT1.$part38.chr(chksumCalc(\$part38))."\xF7";
                    }
                } else {
                    Error($$rf_hash{window}, "Error while opening $syx_file\n\nFile format incorrect.");
                    return;
                }
            }
            # check length
            if (length $sysex != $$rf_hash{filelen}) {
                Error($$rf_hash{window}, "Error while opening $syx_file\n\nFile length incorrect.");
                return;
            }
            # split up and check received data
            my $start=0;
            my @tmpsyx;
            for (my $n=0; $n<@{$$rf_hash{data}}; $n++) {
                my $exp_len=(($$rf_hash{datalen}[$n])+14);
                $tmpsyx[$n]=substr($sysex, $start, $exp_len);
                $start+=$exp_len;
                my $check=ValidatePatData(\$tmpsyx[$n], \$$rf_hash{pattern}[$n], $exp_len);
                if ($check ne 'ok') {
                    Error($$rf_hash{window}, "Error while opening $syx_file in section $$rf_hash{key}[$n]\n\n$check");
                    return;
                }
            }
            # All data received and checked successfully
            for (my $n=0; $n<@{$$rf_hash{data}}; $n++) {
                ReadPatData(\substr($tmpsyx[$n],12,($$rf_hash{datalen}[$n])), $rf_hash, $n);
                if ($$rf_hash{name}[$n] ne "\x00") { $$rf_hash{name}[$n]=PData2Name($$rf_hash{data}[$n]) }
            }
            $$rf_hash{modified}=0;
            $$rf_hash{filename}=$syx_file;
            $$rf_hash{window}->title("$$rf_hash{titlestr} - $$rf_hash{filename}");
            if ($$rf_hash{type} eq 'FX') { ShowFXCtrls(0); ShowFXCtrls(1); }
            if ($midi_outdev ne '') { SysexPatSend($rf_hash); }
        } elsif ($syx_file) {
            Error($$rf_hash{window},"Error: could not open $syx_file");
        }
    }
}

# save JD-Xi patch to previously opened sysex dump file
sub saveFile {
    my ($rf_hash)=@_;

    if ($$rf_hash{filename} ne '') {
        saveSub($$rf_hash{filename}, $rf_hash);
    } else {
        saveasFile($rf_hash);
    }
}

# save JD-Xi patch to sysex dump file
sub saveasFile {
    my ($rf_hash)=@_;
    my @exts=('.syx', '.SYX');
    if ($$rf_hash{okedext}) { push @exts, ".$$rf_hash{okedext}"; }
    my $types=[ ['Sysex Files', [@exts] ], ['All Files', '*'] ];
    my $name='unnamed';
    if ($$rf_hash{name}[0] ne "\x00"){ $name=$$rf_hash{name}[0]; }
    $name=~ s/^\s+|\s+$//g;              # removes leading and trailing whitespace
    $name=~ s/\/|'|"|\\|\.|\s/_/gs;      # converts space and other dangerous chars into underscores
    my $syx_file=$$rf_hash{window}->getSaveFile(
        -initialfile      => "$$rf_hash{fnprefix}${name}.syx",
        -defaultextension => '.syx',
        -filetypes        => $types,
        -title            => 'Save as'
    );
    if ($syx_file && ($syx_file ne '')) {
        saveSub($syx_file, $rf_hash);
    }
}

# actual sysex dump file save subroutine
sub saveSub {
    my($fname, $rf_hash)=@_;

    if ($fname eq '') {
        Error($$rf_hash{window},'Error: no file name given.');
        return;
    } else {
        my $fh;
        unless (open $fh, '>', $fname) {
            Error($$rf_hash{window},"Error: cannot save to file $fname\nCheck filesystem permissions.");
            return;
        }

        # prepare sysex string to save
        my $filedata='';
        for (my $n=0; $n<@{$$rf_hash{data}}; $n++) {
            if ($$rf_hash{name}[$n] ne "\x00") { Name2PData(\$$rf_hash{name}[$n], $$rf_hash{data}[$n]) }
            my $sysex=$$rf_hash{addr}[$n].WritePatData($rf_hash, $n);
            my $chksum=chksumCalc(\$sysex);
            if ($fname=~/\.$$rf_hash{okedext}$/) {
                $filedata.=unpack("H*","\xF0".$ROL_ID.chr($dev_nr).$JDXI_ID.$DT1.$sysex.chr($chksum)."\xF7")."\n";
            } else {
                $filedata.="\xF0".$ROL_ID.chr($dev_nr).$JDXI_ID.$DT1.$sysex.chr($chksum)."\xF7";
            }
        }
        if ($fname=~/\.$$rf_hash{okedext}$/) {
            $filedata=~tr/a-f/A-F/;
            chop $filedata;
            if ($$rf_hash{okedext} eq 'dk') {$filedata=substr($filedata, 0, 15567)} # if drum part then chop off part38 
        }
        binmode $fh;
        print $fh $filedata;
        close $fh;
        $$rf_hash{modified}=0;
        $$rf_hash{filename}=$fname;
        $$rf_hash{window}->title("$$rf_hash{titlestr} - $$rf_hash{filename}");
    }
}

# generate binary tone data from ascii data
sub ascii2tone {
    my($ascii)=@_;
    my $tdata='';
    $ascii=~s/\x0A//g;
    $tdata=pack("H*",$ascii);
    return $tdata;
}

# generate ASCII data for patch
sub tone2ascii {
    my($rf_hash)=@_;
    my $filedata='';
    for (my $n=0; $n<@{$$rf_hash{data}}; $n++) {
        if ($$rf_hash{name}[$n] ne "\x00") { Name2PData(\$$rf_hash{name}[$n], $$rf_hash{data}[$n]) }
        my $sysex=$$rf_hash{addr}[$n].WritePatData($rf_hash, $n);
        my $chksum=chksumCalc(\$sysex);
        $filedata.=unpack("H*","\xF0".$ROL_ID.chr($dev_nr).$JDXI_ID.$DT1.$sysex.chr($chksum)."\xF7")."\n";
    }
    $filedata=~tr/a-f/A-F/;
    if ($DEBUG) { print STDOUT $filedata }
    chop $filedata;
    return $filedata;
}

############ AN Synth Editor Window
sub AN_Edit {
    $AN{window}=$mw->Toplevel(-bg=>$conf{bgcolor}, -class=>$PrgClass);
#    $AN{window}=MainWindow->new(-bg=>$conf{bgcolor}, -class=>$PrgClass);
    $AN{window}->protocol(WM_DELETE_WINDOW => [\&closeSubWin, \%AN]);
    $AN{window}->title($AN{titlestr});
    $AN{window}->iconimage($PrgIcon);
    $AN{window}->geometry($AN{geometry});
    my $Fmenu=FileMenu(\%AN)->pack(-anchor=>'n', -fill=>'x');
    my $SCwin=ScrolledWin(\$AN{window})->pack(-anchor=>'n', -fill=>'both', -expand=>1);

    # fill main pane with 5 columns and a bottom right frame
    my $Col_0  =$SCwin->Frame(-background=>$conf{divcol})->pack(-side=>'left',   -anchor=>'n', -fill=>'both', -expand=>1);
    my $Col_3  =$SCwin->Frame(-background=>$conf{divcol})->pack(-side=>'right',  -anchor=>'n', -fill=>'both', -expand=>1);
    my $Col_12b=$SCwin->Frame(-background=>$conf{divcol})->pack(-side=>'bottom', -anchor=>'n', -fill=>'both', -expand=>0);
    my $Col_1  =$SCwin->Frame(-background=>$conf{divcol})->pack(-side=>'left',   -anchor=>'n', -fill=>'both', -expand=>1);
    my $Col_2  =$SCwin->Frame(-background=>$conf{divcol})->pack(-side=>'left',   -anchor=>'n', -fill=>'both', -expand=>1);

    # Column 0
    my $AN_OSC_frame=$Col_0->Frame(%{$D{Frame_defaults}})->pack(%{$D{B_elastic}}); AN_OSC_Frame(\$AN_OSC_frame);
    # Column 1
    my $AN_LFO_frame=$Col_1->Frame(%{$D{Frame_defaults}})->pack(%{$D{B_elastic}}); AN_LFO_Frame(\$AN_LFO_frame);
    # Column 2
    my $AN_VCF_frame=$Col_2->Frame(%{$D{Frame_defaults}})->pack(%{$D{B_elastic}}); AN_VCF_Frame(\$AN_VCF_frame);
    # Column 3
    my $AN_AMP_frame=$Col_3->Frame(%{$D{Frame_defaults}})->pack(%{$D{B_elastic}}); AN_AMP_Frame(\$AN_AMP_frame);
    my $AN_COM_frame=$Col_3->Frame(%{$D{Frame_defaults}})->pack(%{$D{B_elastic}}); AN_COM_Frame(\$AN_COM_frame);
    # Column 1+2 bottom
    my $editbufops=$Col_12b->Frame(%{$D{Frame_defaults}})->pack(%{$D{B_elastic}}); EditBufferOps($editbufops, \%AN);

    # set up keyboard keys as MIDI keyboard on Windows (on Linux Key-Auto-Repeat spoils it)
    KbdSetup($AN{window});
    SysexPatRcve(\%AN);
}

# SN Synth Editor Windows
sub SN_Edit {
    my ($x)=@_;
    $SN[$x]{window}=$mw->Toplevel(-bg=>$conf{bgcolor}, -class=>$PrgClass);
    $SN[$x]{window}->protocol(WM_DELETE_WINDOW => [\&closeSubWin, $SN[$x]]);
    $SN[$x]{window}->title($SN[$x]{titlestr});
    $SN[$x]{window}->iconimage($PrgIcon);
    $SN[$x]{window}->geometry($SN[$x]{geometry});
    my $Fmenu=FileMenu($SN[$x])->pack(-anchor=>'n', -fill=>'x');
    my $SCwin=ScrolledWin(\$SN[$x]{window})->pack(-anchor=>'n', -fill=>'both', -expand=>1);
    # another frame needed to allow dynamic expansion of grid below
    my $sf=$SCwin->Frame(-background=>$conf{divcol})->pack(-anchor=>'n', -fill=>'both', -expand=>1);

    # create left column notebook and bottom row
    my $SN_Col_0=$sf->Frame(-background=>$conf{divcol})->grid(-sticky=>'nsew', -rowspan=>2);
    my $SN_Tabs=$sf->NoteBook(%{$D{NB_defaults}})->grid(-sticky=>'nsew', -row=>0, -column=>1);
    my $SN_Row1=$sf->Frame(-background=>$conf{divcol})->grid(-sticky=>'nsew', -row=>1, -column=>1);
    $sf->gridColumnconfigure(0, -weight=>10);
    $sf->gridColumnconfigure(1, -weight=>30);
    $sf->gridRowconfigure(0, -weight=>40);
    $sf->gridRowconfigure(1, -weight=>0);

    # Common + Misc + EditBufferOps frames
    my $SN_COM_frame=$SN_Col_0->Frame(%{$D{Frame_defaults}})->pack(%{$D{B_elastic}}); SN_COM_Frame($x,\$SN_COM_frame);
    my $SN_MOD_frame=$SN_Col_0->Frame(%{$D{Frame_defaults}})->pack(%{$D{B_elastic}}); SN_MOD_Frame($x,\$SN_MOD_frame);
    my $editbufferops=$SN_Row1->Frame(%{$D{Frame_defaults}})->pack(%{$D{B_elastic}}); EditBufferOps($editbufferops, $SN[$x]);

    # Tabs with Partial 1,2,3
    my @SNtab;        my @SN_LFO_frame; my @SN_MLFO_frame;  my @SN_OSC_frame;
    my @SN_VCF_frame; my @SN_AMP_frame; my @SN_PITCH_frame; my @SN_VCFENV_frame;

    for my $n (0..2) {
        $SNtab[$n]=$SN_Tabs->add("Tab$n", -label=>"  PARTIAL ".($n+1)."  ", -raisecmd=>sub{$SN[$x]{curpart}=($n+1)});
        $SNtab[$n]->configure(-bg=>$conf{bgcolor});
        my $SNP_Col_0   =$SNtab[$n]->Frame(-background=>$conf{divcol})->pack(-side=>'left',   -anchor=>'n', -fill=>'both', -expand=>1);
        my $SNP_Col_1   =$SNtab[$n]->Frame(-background=>$conf{divcol})->pack(-side=>'left',   -anchor=>'n', -fill=>'both', -expand=>1);
        my $SNP_Col_2   =$SNtab[$n]->Frame(-background=>$conf{divcol})->pack(-side=>'left',   -anchor=>'n', -fill=>'both', -expand=>1);
        # Tab Column 0
        $SN_LFO_frame[$n]   =$SNP_Col_0->Frame(%{$D{Frame_defaults}})->pack(%{$D{B_elastic}}); SN_LFO_Frame(   $x, $n,    \$SN_LFO_frame[$n] );
        $SN_MLFO_frame[$n]  =$SNP_Col_0->Frame(%{$D{Frame_defaults}})->pack(%{$D{B_elastic}}); SN_MLFO_Frame(  $x, $n,   \$SN_MLFO_frame[$n] );
        # Tab Column 1
        $SN_OSC_frame[$n]   =$SNP_Col_1->Frame(%{$D{Frame_defaults}})->pack(%{$D{B_elastic}}); SN_OSC_Frame(   $x, $n,    \$SN_OSC_frame[$n] );
        $SN_VCF_frame[$n]   =$SNP_Col_1->Frame(%{$D{Frame_defaults}})->pack(%{$D{B_elastic}}); SN_VCF_Frame(   $x, $n,    \$SN_VCF_frame[$n] );
        $SN_AMP_frame[$n]   =$SNP_Col_1->Frame(%{$D{Frame_defaults}})->pack(%{$D{B_elastic}}); SN_AMP_Frame(   $x, $n,    \$SN_AMP_frame[$n] );
        # Tab Column 2
        $SN_PITCH_frame[$n] =$SNP_Col_2->Frame(%{$D{Frame_defaults}})->pack(%{$D{B_elastic}}); SN_PITCH_Frame( $x, $n,  \$SN_PITCH_frame[$n] );
        $SN_VCFENV_frame[$n]=$SNP_Col_2->Frame(%{$D{Frame_defaults}})->pack(%{$D{B_elastic}}); SN_VCFENV_Frame($x, $n, \$SN_VCFENV_frame[$n] );
    }
    SN_PRT_Frame($x, \$SN_Tabs)->place(-anchor=>'n', -relx=>0.5, -y=>3);
    KbdSetup($SN[$x]{window});
    $SN[$x]{curpart}=1;
    SysexPatRcve($SN[$x]);
}

# Arp Editor Window
sub ARP_Edit {
    $ARP{window}=$mw->Toplevel(-bg=>$conf{bgcolor}, -class => $PrgClass);
    $ARP{window}->protocol(WM_DELETE_WINDOW => [\&closeSubWin, \%ARP]);
    $ARP{window}->title($ARP{titlestr});
    $ARP{window}->iconimage($PrgIcon);
    $ARP{window}->geometry($ARP{geometry});
    my $Fmenu=FileMenu(\%ARP)->pack(-anchor=>'n', -fill=>'x');
    my $SCwin=ScrolledWin(\$ARP{window})->pack(-anchor=>'n', -fill=>'both', -expand=>1);
    # another frame needed to allow dynamic expansion of grid below
    my $sf=$SCwin->Frame(-background=>$conf{divcol})->pack(-anchor=>'n', -fill=>'both', -expand=>1);
    my $Col0=$sf->Frame(-background=>$conf{divcol})->grid(-sticky=>'nsew');
    $sf->gridRowconfigure(0, -weight=>35);
    GridXW1(\$sf);
    my $ARP_frame =$Col0->Frame(%{$D{Frame_defaults}})->pack(%{$D{B_elastic}}); ARP_Frame(\$ARP_frame);
    my $editbufops=$Col0->Frame(%{$D{Frame_defaults}})->pack(%{$D{X_elastic}}); EditBufferOps($editbufops, \%ARP);
    SysexPatRcve(\%ARP);
}

# Vocal Effects Editor Window
sub VFX_Edit {
    $VFX{window}=$mw->Toplevel(-bg=>$conf{bgcolor}, -class => $PrgClass);
    $VFX{window}->protocol(WM_DELETE_WINDOW => [\&closeSubWin, \%VFX]);
    $VFX{window}->title($VFX{titlestr});
    $VFX{window}->iconimage($PrgIcon);
    $VFX{window}->geometry($VFX{geometry});
    my $Fmenu=FileMenu(\%VFX)->pack(-anchor=>'n', -fill=>'x');
    my $SCwin=ScrolledWin(\$VFX{window})->pack(-anchor=>'n', -fill=>'both', -expand=>1);
    # another frame needed to allow dynamic expansion of grid below
    my $sf=$SCwin->Frame(-background=>$conf{divcol})->pack(-anchor=>'n', -fill=>'both', -expand=>1);

    my $Col0=$sf->Frame(-background=>$conf{divcol})->grid(
    my $Col1=$sf->Frame(-background=>$conf{divcol}),
    my $Col2=$sf->Frame(-background=>$conf{divcol}), -sticky=>'nsew');
    my $C01b=$sf->Frame(-background=>$conf{divcol})->grid('-', '^', -sticky=>'nsew');

    $sf->gridRowconfigure(0, -weight=>35);
    GridXW1(\$sf);
    my $VFX_frame=$Col0->Frame(%{$D{Frame_defaults}})->pack(%{$D{B_elastic}}); VFX_Frame(\$VFX_frame);
    my $VC_frame =$Col1->Frame(%{$D{Frame_defaults}})->pack(%{$D{B_elastic}}); VC_Frame(\$VC_frame);
    my $AP_frame =$Col2->Frame(%{$D{Frame_defaults}})->pack(%{$D{B_elastic}}); AP_Frame(\$AP_frame);

    my $editbufops=$C01b->Frame(%{$D{Frame_defaults}})->pack(%{$D{X_elastic}}); EditBufferOps($editbufops, \%VFX);
    SysexPatRcve(\%VFX);
}

# Effects Editor Window
sub FX_Edit {
    $FX{window}=$mw->Toplevel(-bg=>$conf{bgcolor}, -class=>$PrgClass);
    $FX{window}->protocol(WM_DELETE_WINDOW => [\&closeSubWin, \%FX]);
    $FX{window}->title($FX{titlestr});
    $FX{window}->iconimage($PrgIcon);
    $FX{window}->geometry($FX{geometry});
    my $Fmenu=FileMenu(\%FX)->pack(-anchor=>'n', -fill=>'x');
    my $SCwin=ScrolledWin(\$FX{window})->pack(-anchor=>'n', -fill=>'both', -expand=>1);
    # another frame needed to allow dynamic expansion of grid below
    my $sf=$SCwin->Frame(-background=>$conf{divcol})->pack(-anchor=>'n', -fill=>'both', -expand=>1);

    my $FX00=$sf->Frame(-background=>$conf{divcol})->grid(
    my $FX01=$sf->Frame(-background=>$conf{divcol}),
    my $Col2=$sf->Frame(-background=>$conf{divcol}), -sticky=>'nsew');
    $FX_frame[2]=$sf->Frame(-background=>$conf{divcol})->grid(
    $FX_frame[3]=$sf->Frame(-background=>$conf{divcol}),'^', -sticky=>'nsew');
    my $C01b=$sf->Frame(-background=>$conf{divcol})->grid('-', '^', -sticky=>'nsew');

    $sf->gridRowconfigure(0, -weight=>35);
    $sf->gridRowconfigure(1, -weight=>64);
    $sf->gridRowconfigure(2, -weight=>1);
    GridXW1(\$sf);

    my $FX_DEL_frame=$Col2->Frame(%{$D{Frame_defaults}})->pack(%{$D{B_elastic}}); FX_DEL_Frame(\$FX_DEL_frame);
    my $FX_REV_frame=$Col2->Frame(%{$D{Frame_defaults}})->pack(%{$D{B_elastic}}); FX_REV_Frame(\$FX_REV_frame);

    my $FX_FX1_frame=$FX00->Frame(%{$D{Frame_defaults}})->pack(%{$D{B_elastic}}); FX_FX1_Frame(\$FX_FX1_frame);
    my $FX_FX2_frame=$FX01->Frame(%{$D{Frame_defaults}})->pack(%{$D{B_elastic}}); FX_FX2_Frame(\$FX_FX2_frame);
    $FX_frame[0]=$FX_frame[2]->Frame(%{$D{Frame_defaults}})->pack(%{$D{B_elastic}}); ShowFXCtrls(0);
    $FX_frame[1]=$FX_frame[3]->Frame(%{$D{Frame_defaults}})->pack(%{$D{B_elastic}}); ShowFXCtrls(1);

    my $editbufops=$C01b->Frame(%{$D{Frame_defaults}})->pack(%{$D{B_elastic}}); EditBufferOps($editbufops, \%FX);
    SysexPatRcve(\%FX);
}

# show controls for selected FX type
sub ShowFXCtrls {
    my($fxnr)=@_;
    my($ty,$name)=($fx_type[$FXdata[$fxnr][0x00]]=~/^(\d\d): (.*)/);
    $FX_frame[$fxnr]->destroy() if Tk::Exists($FX_frame[$fxnr]);
    $FX_frame[$fxnr]=$FX_frame[$fxnr+2]->Frame(%{$D{Frame_defaults}})->pack(%{$D{B_elastic}});
    if    ($ty == 0) {FX12_Through(\$FX_frame[$fxnr])}
    elsif ($ty == 1) {FXHashDel(2); FX1_DistFuzz_Frame(\$FX_frame[$fxnr])}
    elsif ($ty == 2) {FXHashDel(2); FX1_DistFuzz_Frame(\$FX_frame[$fxnr])}
    elsif ($ty == 3) {FXHashDel(2); FX1_Compressor_Frame(\$FX_frame[$fxnr])}
    elsif ($ty == 4) {FXHashDel(2); FX1_BitCrusher_Frame(\$FX_frame[$fxnr])}
    elsif ($ty == 5) {FXHashDel(4); FX2_Flanger_Frame(\$FX_frame[$fxnr])}
    elsif ($ty == 6) {FXHashDel(4); FX2_Phaser_Frame(\$FX_frame[$fxnr])}
    elsif ($ty == 7) {FXHashDel(4); FX2_RingMod_Frame(\$FX_frame[$fxnr])}
    elsif ($ty == 8) {FXHashDel(4); FX2_Slicer_Frame(\$FX_frame[$fxnr])}
}

# delete hash keys for sliders of FX1 or FX2 before refreshing frame
sub FXHashDel {
    my($n)=@_;
    for my $i (11,15,19,'1D',21,25,29,'2D',31,35,39) {
        if ($FX{ct}{"18000${n}${i}"}) { delete $FX{ct}{"18000${n}${i}"} }
    }
}

# Drums Editor Window
sub DR_Edit {
    $DR{window}=$mw->Toplevel(-bg=>$conf{bgcolor}, -class=>$PrgClass);
    $DR{window}->protocol(WM_DELETE_WINDOW => [\&closeSubWin, \%DR]);
    $DR{window}->title($DR{titlestr});
    $DR{window}->iconimage($PrgIcon);
    $DR{window}->geometry($DR{geometry});
    my $Fmenu=FileMenu(\%DR)->pack(-anchor=>'n', -fill=>'x');
    my $SCwin=ScrolledWin(\$DR{window})->pack(-anchor=>'n', -fill=>'both', -expand=>1);
    # another frame needed to allow dynamic expansion of grid below
    my $sf=$SCwin->Frame(-background=>$conf{divcol})->pack(-anchor=>'n', -fill=>'both', -expand=>1);

    # create top row and notebook
    my $tabnr=1;
    my $DR_Tabs_row =$sf->Frame(-background=>$conf{divcol}  )->grid(-sticky=>'nsew');
    my $bf          =$sf->Frame(-background=>$conf{btnselfg})->grid(-sticky=>'nsew');
    my $DR_Tab_frm  =$bf->Frame(-background=>$conf{divcol}  )->pack(-anchor=>'n', -fill=>'both', -expand=>1, -padx=>2, -pady=>1);
    my $DR_Row_0    =$sf->Frame(-background=>$conf{divcol}  )->grid(-sticky=>'nsew');
    $sf->gridRowconfigure(0, -weight=>0);
    $sf->gridRowconfigure(1, -weight=>30);
    $sf->gridRowconfigure(2, -weight=>0);
    $sf->gridColumnconfigure(0, -weight=>50);

    my $mchan=($DR{MIDIch});
    # create tabs row
    my @DRTabs; my $tprev=0;
    $DR_Tabs_row->Frame(-background=>$conf{divcol}, -width=>50)->pack(-side=> 'right');
    for my $n (1..38) {
        my $lbltxt=$DR{key}[$n];
        $DRTabs[$n]=$DR_Tabs_row->Radiobutton(%{$D{RadioB_defaults}},
            -width     => (length $lbltxt),
            -padx      => 3,
            -height    => 2,
            -value     => $n,
            -text      => $lbltxt,
            -variable  => \$tabnr,
            -font      => $conf{smlbldft},
            -command   => sub{
                                if ($tprev != $n) { 
                                    if ($DR{ct}{'1970000C'}) { $DR{ct}={'1970000C'=>1} } else { $DR{ct}={a=>0} }
                                    Mk_DRTab($n, \$DR_Tab_frm);
                                    $DR{curpart}=$n;
                                    $tprev=$n;
                                }
                          }
        )->pack(-side=> 'left', -fill=>'both', -expand=>1);
        my $dnote=(35+$n);
        $DRTabs[$n]->bind('<Button-3>' => sub { PlayMidiNote($mchan,$dnote,127,1) });
        $DRTabs[$n]->bind('<ButtonRelease-3>' => sub { PlayMidiNote($mchan,$dnote,127,0) });
    }
    $DRTabs[1]->invoke();
    my $DR_COM_frame =$DR_Row_0->Frame(%{$D{Frame_defaults}})->pack(%{$D{Y_elastic}}, -side=>'left'); DR_COM_Frame(\$DR_COM_frame);
    my $editbufferops=$DR_Row_0->Frame(%{$D{Frame_defaults}})->pack(%{$D{B_elastic}}, -side=>'right'); EditBufferOps($editbufferops, \%DR);
    KbdSetup($DR{window});
    SysexPatRcve(\%DR);
}

sub Mk_DRTab {
    my ($n, $DR_Tab)=@_;

    my $LO=ord substr($DR{addr}[$n],2,1);
    my $HI=($LO + 1);
    $LO=sprintf("%02X", $LO);
    $HI=sprintf("%02X", $HI);

    if ($hidden) {$hidden->destroy;}
    $hidden=$$DR_Tab->Frame(-bd=>0, -highlightthickness=>0, -background=>$conf{divcol});
    #first row
    my $DR_MAIN_frame =$hidden->Frame(%{$D{Frame_defaults}})->grid(
    my $DRP_Col_1     =$hidden->Frame(%{$D{Frame_defaults}}), '-',
    my $DR_TVF_frame  =$hidden->Frame(%{$D{Frame_defaults}}),
    my $DR_TVA_frame  =$hidden->Frame(%{$D{Frame_defaults}}), -padx=>$conf{divwidth}, -pady=>$conf{divwidth}, -sticky=>'nsew');
    # second row
    my $DR_PITCH_frame=$hidden->Frame(%{$D{Frame_defaults}})->grid(
    my $DRP_Col_B     =$hidden->Frame(%{$D{Frame_defaults}}), '-', '-',
    my $DR_OUT_frame  =$hidden->Frame(%{$D{Frame_defaults}}), -padx=>$conf{divwidth}, -pady=>$conf{divwidth}, -sticky=>'nsew');
    $hidden->gridRowconfigure(0, -weight=>2);
    $hidden->gridRowconfigure(1, -weight=>1);
    GridXW1(\$hidden);
    # Wave panel
    Header(\$DRP_Col_1, 'WAVE / WMT', $conf{OSCbgc}, $conf{OSCfgc})->pack(-anchor=>'n', -fill=>'x', -expand=>0);
    my $WMT_Tabs=$DRP_Col_1->NoteBook(%{$D{NB2_defaults}})->pack(-anchor=>'n', -fill=>'both', -expand=>1);
    # Envelopes panel
    Header(\$DRP_Col_B, 'ENVELOPES', $conf{LFObgc}, $conf{LFOfgc})->pack(-anchor=>'n', -fill=>'x', -expand=>0);
    my $ENV_Tabs=$DRP_Col_B->NoteBook(%{$D{NB2_defaults}})->pack(-anchor=>'n', -fill=>'both', -expand=>1);

    $hidden->pack(-anchor=>'n', -fill=>'both', -expand=>1);

    # column frames
    DR_MAIN_Frame($n, $LO, $HI, \$DR_MAIN_frame);
    DR_PITCH_Frame($n, $LO, $HI, \$DR_PITCH_frame);
    DR_TVF_Frame($n, $LO, $HI, \$DR_TVF_frame);
    DR_TVA_Frame($n, $LO, $HI, \$DR_TVA_frame);
    DR_OUT_Frame($n, $LO, $HI, \$DR_OUT_frame);
    # Wave tabs
    my @WMTtab;
    for my $t (0..3) {
        $WMTtab[$t]=$WMT_Tabs->add("WMT_${n}_${t}", -label=>'   W'.($t+1).'   ');
        $WMTtab[$t]->configure(-bg=>$conf{bgcolor});
        DR_WMT_Frame($n, $t, $LO, $HI, \$WMTtab[$t]);
    }
    # place wave on/off frame (temporarily change bgcolor)
    $conf{bgtemp}="$conf{bgcolor}"; $conf{bgcolor}="$conf{divcol}";  ${$D{Label_defaults}}{'-background'}="$conf{divcol}";
    DR_PRT_Frame($n, $LO, \$WMT_Tabs)->place(-relx=>0.48, -y=>1);
    $conf{bgcolor}="$conf{bgtemp}"; ${$D{Label_defaults}}{'-background'}="$conf{bgcolor}";
    # Envelopes tabs
    my @ENVtab;
    for my $t (0..2) { 
        $ENVtab[$t]=$ENV_Tabs->add("ENV_${n}_${t}", -label=>$ENV_labels[$t]);
        $ENVtab[$t]->configure(-bg=>$conf{bgcolor});
    }
    DR_PITCHENV_Frame($n, $LO, $HI, \$ENVtab[0]);
    DR_TVFENV_Frame(  $n, $LO, $HI, \$ENVtab[1]);
    DR_TVAENV_Frame(  $n, $LO, $HI, \$ENVtab[2]);
}

# Writes JDXI Analog tone data to sysex data string
sub WritePatData { 
    my ($rf_hash, $n)=@_;

    my $sysex="";
    if ($DEBUG) {print STDOUT "WritePatData $$rf_hash{type}: $$rf_hash{key}[$n]\n"}

    for (my $i=0; $i<$$rf_hash{datalen}[$n]; $i++)
    {
        if (($$rf_hash{name}[$n] ne "\x00") && ($i < 12))  { $sysex.=     $$rf_hash{data}[$n][$i]         }
        elsif  ($i=~/^$$rf_hash{transf64}[$n]$/)           { $sysex.=chr(($$rf_hash{data}[$n][$i])+64)    }
        elsif  ($i=~/^$$rf_hash{transf10}[$n]$/)           { $sysex.=chr(($$rf_hash{data}[$n][$i])/10+64) }
        elsif  ($i=~/^$$rf_hash{transf_01}[$n]$/)          { $sysex.=chr(($$rf_hash{data}[$n][$i])+1)     }
        elsif  ($i=~/^$$rf_hash{transf_10}[$n]$/)          { $sysex.=chr(($$rf_hash{data}[$n][$i])+10)    }
        elsif  ($i=~/^$$rf_hash{transf4}[$n]$/) {
            my $tmpval=$$rf_hash{data}[$n][$i];
            if ($$rf_hash{type} eq 'FX') {$tmpval+=32768}
            my $hex=sprintf("%04X", $tmpval);
            if ($DEBUG) {print STDOUT "WritePatData [$i]: [$tmpval] [$hex]"}
            $hex=~s/\G([0-9A-F])/chr(hex($1))/gei;
            $sysex.=$hex; $i=$i+3;
           if ($DEBUG) {print STDOUT "[$i]\n"}
        }
        else { $sysex.=chr( $$rf_hash{data}[$n][$i]) }
    }
    return $sysex;
}

# Reads JDXI data from sysex data string into @PData
sub ReadPatData { 
    my ($rf_sysex, $rf_hash, $n)=@_;

    my $len=(length $$rf_sysex);
    #if ($DEBUG) {print STDOUT "sysex length $len\n"}
    for (my $i = 0; $i < $len; $i++)
    {
        my $dv=(ord(substr($$rf_sysex,$i,1)));
        if    ($i=~/^$$rf_hash{transf64}[$n]$/)  { $$rf_hash{data}[$n][$i]=( $dv-64) }
        elsif ($i=~/^$$rf_hash{transf_01}[$n]$/) { $$rf_hash{data}[$n][$i]=( $dv-1) }
        elsif ($i=~/^$$rf_hash{transf_10}[$n]$/) { $$rf_hash{data}[$n][$i]=( $dv-10) }
        elsif ($i=~/^$$rf_hash{transf10}[$n]$/)  { $$rf_hash{data}[$n][$i]=(($dv-64)*10) }
        elsif ($i=~/^$$rf_hash{transf4}[$n]$/ )  {
            my $dv1=(ord(substr($$rf_sysex,($i+1),1))); $$rf_hash{data}[$n][$i+1]=$dv1;
            my $dv2=(ord(substr($$rf_sysex,($i+2),1))); $$rf_hash{data}[$n][$i+2]=$dv2;
            my $dv3=(ord(substr($$rf_sysex,($i+3),1))); $$rf_hash{data}[$n][$i+3]=$dv3;
            my $tmpv=((4096*$dv)+(256*$dv1)+(16*$dv2)+$dv3);
            if ($$rf_hash{type} eq 'FX') { $$rf_hash{data}[$n][$i]=($tmpv-32768) }
            else { $$rf_hash{data}[$n][$i]=$tmpv }
            $i=$i+3;
        }
        else { $$rf_hash{data}[$n][$i]=$dv }
        # if ($DEBUG) {print STDOUT "[$i]: $dv -> $$rf_hash{data}[$n][$i]\n"}
    }
    # AN =============================
    if ($$rf_hash{type} eq 'AN') {
        $PDM_val{19420011}=$sync_notes[$$rf_hash{data}[$n][0x11]];
    }
    # SN1/2 - 0 ======================
    elsif ($$rf_hash{type}=~/^SN(1|2)$/ && $n==0) {
        my $msb=$$rf_hash{msb};
        for (my $i=0; $i < @tone_cats; $i++) {
            if ($tone_cats[$i]=~/^($$rf_hash{data}[$n][0x36]):.*/) { $PDM_val{$msb."0036"}=$tone_cats[$i] }
        }
    }
    # SN1/2 - 4 ======================
    elsif ($$rf_hash{type}=~/^SN(1|2)$/ && $n==4) {
        my $msb=$$rf_hash{msb};
        $PDM_val{$msb."5005"}=$sync_notes[$$rf_hash{data}[$n][0x05]];
    }
    # SN1/2 - 1/2/3 ==================
    elsif ($$rf_hash{type}=~/^SN(1|2)$/ && $n>0 && $n<4) {
        my $msb=$$rf_hash{msb};
        my $lsb=$n-1;
        $PDM_val{$msb."2".$lsb."1F"}=$sync_notes[$$rf_hash{data}[$n][0x1F]];
        $PDM_val{$msb."2".$lsb."29"}=$sync_notes[$$rf_hash{data}[$n][0x29]];
        # Wave Number
        my $wavenr=$$rf_hash{data}[$n][0x35];
        #if ($DEBUG) {print STDOUT "Wave Nr: $wavenr \n"}
        if ($wavenr > 160) {
            #Error($$rf_hash{window}, "Sysex data of Partial $n contains invalid PCM Wave Nr. $wavenr. Setting PCM Wave to 'OFF'.");
            $wavenr=0; $$rf_hash{data}[$n][0x35]=$wavenr;
        }
        $PDM_val{$msb."2".$lsb."35"}=$PCMwaves[$wavenr];
    }
    # DR 1-38 ========================
    elsif ($$rf_hash{type} eq 'DR' && $n>0) {
        my $LO=ord substr($$rf_hash{addr}[$n],2,1);
        my $HI=($LO + 1);
        $LO=sprintf("%02X", $LO);
        $HI=sprintf("%02X", $HI);
        $PDM_val{"1970".$LO."0D"}=$mute_grp[$$rf_hash{data}[$n][0x0D]];
        $PDM_val{"1970".$LO."0F"}=$coarse_tune[$$rf_hash{data}[$n][0x0F]];
        $PDM_val{"1970".$LO."11"}=$rnd_pdepth[$$rf_hash{data}[$n][0x11]];
        for my $t (0..3) {
            my $a=(29*$t);
            my $wavenrL=$$rf_hash{data}[$n][0x27+$a];
            my $wavenrR=$$rf_hash{data}[$n][0x2B+$a];
            #if ($DEBUG) {print STDOUT "WMT [$t] Wave L: [$wavenrL] Wave R: [$wavenrR]\n"}
            if ($wavenrL > 453) {
                #Error($$rf_hash{window}, "Sysex data of Partial $n W".($t+1)." contains invalid PCM Wave(L) Nr. $wavenrL. Setting PCM Wave(L) to 'OFF'.");
                $wavenrL=0; $$rf_hash{data}[$n][0x27+$a]=$wavenrL;
            }
            if ($wavenrR > 453) {
                #Error($$rf_hash{window}, "Sysex data of Partial $n W".($t+1)." contains invalid PCM Wave(R) Nr. $wavenrR. Setting PCM Wave(R) to 'OFF'.");
                $wavenrR=0; $$rf_hash{data}[$n][0x2B+$a]=$wavenrR;
            }
            $PDM_val{Addr(0x27+$a,$LO,$HI)}=$DRMwaves[$wavenrL];
            $PDM_val{Addr(0x2B+$a,$LO,$HI)}=$DRMwaves[$wavenrR];
        }
    }
    # FX 0 ================================
    elsif ($$rf_hash{type} eq 'FX' && $n==0) {
        $PDM_val{"18000200"}=$fx_type[$$rf_hash{data}[$n][0]];
        $PDM_val{"1800022D"}=$coarse_tune[$$rf_hash{data}[$n][45]];
        $PDM_val{"18000215"}=$ratio[$$rf_hash{data}[$n][21]];
        $PDM_val{"18000219"}=$comp_att[$$rf_hash{data}[$n][25]];
        $PDM_val{"1800021D"}=$comp_rel[$$rf_hash{data}[$n][29]];
    }
    # FX 1 ================================
    elsif ($$rf_hash{type} eq 'FX' && $n==1) {
        $PDM_val{"18000400"}=$fx_type[$$rf_hash{data}[$n][0]];
        $PDM_val{"18000415"}=$dly_notes[$$rf_hash{data}[$n][21]];
        $PDM_val{"18000419"}=$dly_notes[$$rf_hash{data}[$n][25]];
    }
    # FX 2 (Delay) ========================
    elsif ($$rf_hash{type} eq 'FX' && $n==2) {
        $PDM_val{"18000610"}=$dly_notes[$$rf_hash{data}[$n][16]];
        $PDM_val{"1800061C"}=$hf_damp[$$rf_hash{data}[$n][28]];
    }
    # FX 3 (Reverb) ========================
    elsif ($$rf_hash{type} eq 'FX' && $n==3) {
        $PDM_val{"18000803"}=$rev_type[$$rf_hash{data}[$n][3]];
        $PDM_val{"1800080B"}=$hf_damp[$$rf_hash{data}[$n][11]];
    }
    # ARP =============================
    if ($$rf_hash{type} eq 'AR') {
        $PDM_val{18004005}=$arp_type[$$rf_hash{data}[$n][0x05]];
        $PDM_val{18004006}=$arp_motif[$$rf_hash{data}[$n][0x06]];
    }
    # VFX =============================
    if ($$rf_hash{type} eq 'VC') {
        $PDM_val{18000113}=$vc_hpf[$$rf_hash{data}[$n][0x13]];
        $PDM_val{18000108}=$ap_key[$$rf_hash{data}[$n][0x08]];
    }
}

# Updates @PData with tone name from $name
sub Name2PData { 
    my ($rf_name, $rf_data)=@_;

    for my $i (0..11) {
        if ($i < length $$rf_name) {
            $$rf_data[$i]=substr($$rf_name,$i,1);
        } else {
            $$rf_data[$i]="\x20";
        }
    }
}

# Returns tone name as string from @PData and converts illegal chars to space
sub PData2Name { 
    my ($rf_data)=@_;

    my $name='';
    for my $i (0..11) {
        if ($$rf_data[$i]<32) {$$rf_data[$i]=32}
        $name.=chr($$rf_data[$i]);
    }
    return $name;
}

# Calculate checksum of Roland sysex data
sub chksumCalc { 
    my ($rf_sysex)=@_;

    my $sum=0;
    for (my $i = 0; $i < (length ${$rf_sysex}); $i++) {
        $sum+=(ord(substr(${$rf_sysex},$i,1)));
    }
    return ((128-($sum%128))%128);
}

# Validates JD-Xi sysex format, expects: reference to sysex string, reference to pattern, expected length
sub ValidatePatData {
    my ($ref_sysex, $ref_pattern, $explen)=@_;

    if ($DEBUG) {print STDOUT "received: [".(unpack "H*",${$ref_sysex})."]\n"}
    # check length
    my $len=(length $$ref_sysex);
    ($len == $explen) or return "sysex length mismatch, received $len bytes, expected $explen bytes.";
    # check validity of sysex data
    #if ($DEBUG) {print STDOUT "Pattern: [".${$ref_pattern}."]\n"}
    ${$ref_sysex}=~/^${$ref_pattern}$/ or return "invalid sysex data";
    # calculate checksum
    my $calcsum=chksumCalc(\(substr(${$ref_sysex},8,($explen-10))));
    # expected checksum
    my $syxsum=(ord(substr(${$ref_sysex},($explen-2),1)));
    # compare
    ($calcsum == $syxsum) or return "sysex checksum mismatch, received $syxsum, expected $calcsum.";
    return "ok";
}

#------------------------------------------------------------------------------------------------
# MIDI Subroutines

# Windows: send MIDI string
sub WinMIDIOut { 
    my ($mididata)=@_;
    my $len=length $mididata;

    if ($DEBUG) {print STDOUT "sending parameter change [".(unpack "H*",$mididata)."] len [$len]\n"}

    my $midiouthdr = pack ("PLLLLPLL", $mididata, $len, 0, 0, 0, undef, 0, 0);
    my $lpMidiOutHdr = unpack('L!', pack('P', $midiouthdr));
    $midiOut->PrepareHeader  ($lpMidiOutHdr);
    $midiOut->LongMsg        ($lpMidiOutHdr);
    $midiOut->UnprepareHeader($lpMidiOutHdr);
}

# create an array of available midi ports
sub MidiPortList { 
    my ($dir)=@_;
    my @portlist;

    if ($LINUX) {
        my %clients = MIDI::ALSA::listclients();
        my %portnrs = MIDI::ALSA::listnumports();
        my $tmp=0;
        while (my ($key, $value) = each(%clients)){
            if ($key>15 && $key<128) {
                for (my $i=0; $i<($portnrs{$key}); $i++) {
                    $portlist[$tmp]=$value.":".$i;
                    $tmp++;
                }
            }
        }
    }
    return @portlist;
}

# set up a new midi connection and drop the previous one
sub MidiConSetup { 
    my ($dir)=@_;

    if ($LINUX) {
        if ($dir eq 'out') {
            if ($midi_outdev_prev ne '') {
                MIDI::ALSA::disconnectto(1,"$midi_outdev_prev");
            }
            $midi_outdev_prev=$midi_outdev;
            MIDI::ALSA::connectto(1,"$midi_outdev");
        } elsif ($dir eq 'in') {
            if ($midi_indev_prev ne '') {
                MIDI::ALSA::disconnectfrom(0,"$midi_indev_prev");
            }
            $midi_indev_prev=$midi_indev;
            MIDI::ALSA::connectfrom(0,"$midi_indev");
        }
    }
    ($midi_outdev) ? $outtest->configure(-state=>'normal') : $outtest->configure(-state=>'disabled');
    ($midi_outdev) ? $panicbtn->configure(-state=>'normal') : $panicbtn->configure(-state=>'disabled');
    for my $part (\%SN1, \%SN2, \%AN, \%DR, \%FX, \%ARP, \%VFX) {
        if ($$part{window}) {
            if ($midi_outdev) {
                $$part{dumpto}->configure(-state=>'normal');
#               $$part{storeto}->configure(-state=>'normal');
                ($midi_indev) ? $$part{readfrom}->configure(-state=>'normal') : $$part{readfrom}->configure(-state=>'disabled');
                if (defined $$part{ldprwgt}[1]) {
                    ($midi_indev) ? $$part{ldprwgt}[1]->configure(-state=>'normal') : $$part{ldprwgt}[1]->configure(-state=>'disabled');
                }
            } else {
                $$part{dumpto}->configure(-state=>'disabled');
                $$part{readfrom}->configure(-state=>'disabled');
                $$part{storeto}->configure(-state=>'disabled');
                $$part{ldprwgt}[1]->configure(-state=>'disabled');
            }
        }
    }
}

# MIDI input and output devices selection
sub MIDI_IOconfig { 
    my ($frame)=@_;

    # MIDI OUT device selection
    $frame->Label(%{$D{Label_defaults}},
        -text         => " Output MIDI Device:",
        -font         => $conf{midicfgfnt},
        -justify      => 'right'
    )->grid(-row=>0, -column=>0, -sticky=>'e', -pady=>6);
    $midiout=$frame->BrowseEntry(%{$D{BEntry_defaults}},
        -variable     => \$midi_outdev,
        -choices      => [''],
        -font         => $conf{midicfgfnt},
        -width        => 28,
        -listheight   => 9,
        -browsecmd    => sub{ MidiConSetup('out'); },
        -listcmd      => sub{ @midi_outdevs=MidiPortList('out');
                              $midiout->delete( 0, "end" );
                              $midiout->insert("end", $_) for (@midi_outdevs); }
    )->grid(-row=>0, -column=>1, -sticky=>'w', -padx=>8, -pady=>6);
    $outtest=$frame->Button(%{$D{Btn_defaults}},
        -text         => 'Test'
    )->grid(-row=>0, -column=>2, -sticky=>'w', -pady=>6);
    $frame->Label(%{$D{Label_defaults}}, -text=>""
    )->grid(-row=>0, -column=>3, -padx=>1, -pady=>6);
    $panicbtn=$frame->Button(%{$D{Btn_defaults}},
        -text         => 'Panic',
        -command      => sub{for my $ch ($AN{MIDIch},$SN1{MIDIch},$SN2{MIDIch},$DR{MIDIch}) {MIDIpanic($ch)}}
    )->grid(-row=>0, -column=>4, -sticky=>'e', -pady=>6);

    if (!$LINUX && !$WINDOWS) { $midiout->configure(-state=>'disabled'); }

    $midiout->Subwidget('choices')->configure(%{$D{choices_defaults}});
    $midiout->Subwidget('arrow'  )->configure(%{$D{arrow_defaults}});

    $outtest->bind('<Button-1>'        => sub { PlayMidiNote($mchan,60,127,1); });
    $outtest->bind('<ButtonRelease-1>' => sub { PlayMidiNote($mchan,60,127,0); });

    if ($midi_outdev ne '') {
         $outtest->configure(-state=>'normal');
        $panicbtn->configure(-state=>'normal');
    } else {
         $outtest->configure(-state=>'disabled');
        $panicbtn->configure(-state=>'disabled');
    }

    # MIDI IN device selection
    $frame->Label(%{$D{Label_defaults}},
        -text         => " Input MIDI Device:",
        -font         => $conf{midicfgfnt},
        -justify      => 'right'
    )->grid(-row=>1, -column=>0, -sticky=>'e', -pady=>4);
    $midiin=$frame->BrowseEntry(%{$D{BEntry_defaults}},
        -variable     => \$midi_indev,
        -choices      => [''],
        -font         => $conf{midicfgfnt},
        -width        => 28,
        -listheight   => 9,
        -browsecmd    => sub{ MidiConSetup('in'); },
        -listcmd      => sub{ @midi_indevs=MidiPortList('in');
                              $midiin->delete( 0, "end" );
                              $midiin->insert("end", $_) for (@midi_indevs); }
    )->grid(-row=>1, -column=>1, -sticky=>'w', -padx=>8, -pady=>4);
    my $ChFr=$frame->Frame(-bg=>$conf{bgcolor}
    )->grid(-row=>1, -column=>2, -columnspan=>3, -sticky=>'ew', -pady=>4);

    if (!$LINUX && !$WINDOWS) { $midiin->configure(-state=>'disabled'); }

    $midiin->Subwidget('choices')->configure(%{$D{choices_defaults}});
    $midiin->Subwidget('arrow'  )->configure(%{$D{arrow_defaults}});

    $ChFr->Label(%{$D{Label_defaults}},
        -text         => "Rx/Tx Ch: ",
        -font         => $conf{midicfgfnt},
        -justify      => 'right'
    )->grid(
    NrSpinBox(\$ChFr, \$dev_nr, 1, 16, 1, 3)
    );
}

# Play a Note via MIDI (send 'note on' or 'note off' event)
sub PlayMidiNote { 
    my $ch=$_[0]; # midi channel 0-15
    my $nt=$_[1]; # midi note 0-127
    my $vl=$_[2]; # note velocity 0-127
    my $oo=$_[3]; # note on (1) or note off (0)

    if ($DEBUG) {print STDOUT "ch:[$ch] note:[$nt] vol:[$vl] on/off:[$oo]\n"}

    if ($LINUX) {
        if ($oo) {
            MIDI::ALSA::output(MIDI::ALSA::noteonevent($ch,$nt,$vl));
        } else {
            MIDI::ALSA::output(MIDI::ALSA::noteoffevent($ch,$nt,$vl));
        }
    }
}

# Send CC
sub SendCC { 
    my $ch=$_[0]; # midi channel 0-15
    my $cc=$_[1]; # continuous controller 0-127
    my $vl=$_[2]; # value 0-127
    if ($DEBUG) {print STDOUT "MIDI Ch:[$ch] CC Nr:[$cc] Val:[$vl]\n"}
    if ($LINUX) {
        MIDI::ALSA::output(MIDI::ALSA::controllerevent( $ch, $cc, $vl));
    }
}

# Send MIDI Panic
sub MIDIpanic {
    my ($ch)=@_;
    for my $v (120, 121, 123) { SendCC($ch, $v, 0) }
}

# send Patch Parameter Change Message (real time sysex) to JD-Xi
sub SendPaChMsg {
    my ($addr, $value, $nr)=@_;

    if ($midi_outdev ne '') {
        until ($midilock == 0) { usleep(1); };      # wait until preceding par changes are done
        $midilock=1;                                # lock out other par change attempts
        if ($DEBUG) {print STDOUT "par:[$addr] val:[$value] len:[$nr]\n"}

        # prepare sysex string to send
        my $data='';
        if ($nr > 1) {
            $data=sprintf("%0${nr}X", $value);
            $data=~s/\G([0-9A-F])/chr(hex($1))/gei;
        } else {
            $data=chr($value);
        }
        $addr=~s/\G([0-9A-F][0-9A-F])/chr(hex($1))/gei;
        my $chksum=chksumCalc(\($addr.$data));
        my $sysex=$ROL_ID.chr($dev_nr).$JDXI_ID.$DT1.$addr.$data.chr($chksum);

        # Enforce 2 ms gap since last par change msg sent
        my $midinow=time;
        my $gap=($midinow - $midilast);
        if ($gap < 0.002) {
            usleep ((0.002 - $gap) * 1000000 );
        }

        # Send the MIDI data to the synth
        if ($LINUX) {
            MIDI::ALSA::output( MIDI::ALSA::sysex($dev_nr-1, $sysex, 0));
        }
        $midilast=time;    # store timestamp
        $midilock=0;       # allow other par changes to proceed
    }
}

# send sysex dump of current patch in editor to JD-Xi edit buffer via MIDI
sub SysexPatSend { 
    my ($rf_hash)=@_;

    if ($midi_outdev ne '') {
        $mw->Busy(-recurse=>1);
        for (my $n=0; $n<@{$$rf_hash{data}}; $n++) {
            # enforce 75 ms gap between sysex strings (=225 MIDI bytes)
            usleep(75000);
            SysexStrSend($rf_hash, $n);
        }
        $mw->Unbusy;
    }
}

# send specific single sysex string of patch
sub SysexStrSend {
    my ($rf_hash, $n)=@_;

    if ($midi_outdev ne '') {
            # prepare sysex string to send
            if ($$rf_hash{name}[$n] ne "\x00") { Name2PData(\$$rf_hash{name}[$n], $$rf_hash{data}[$n]) }
            my $sysex=$$rf_hash{addr}[$n].WritePatData($rf_hash, $n);
            my $chksum=chksumCalc(\$sysex);
            $sysex=$ROL_ID.chr($dev_nr).$JDXI_ID.$DT1.$sysex.chr($chksum);

            # Send the MIDI data to the synth
            if ($LINUX) {
                MIDI::ALSA::output( MIDI::ALSA::sysex($dev_nr-1, $sysex, 0));
                MIDI::ALSA::syncoutput();
            }
    }
}

# request and receive a sysex dump from edit buffer of the JD-Xi via MIDI
sub SysexPatRcve {
    my ($rf_hash)=@_;

    my @tmp_dump;
    $mw->Busy(-recurse=>1);
    for (my $n=0; $n<@{$$rf_hash{data}}; $n++) {
        my $sysex=$$rf_hash{addr}[$n].$$rf_hash{rqlen}[$n];
        my $exp_len=(($$rf_hash{datalen}[$n])+14);
        $tmp_dump[$n]=SyxReceive(($ROL_ID.chr($dev_nr).$JDXI_ID.$DR1.$sysex.chr(chksumCalc(\$sysex))), $exp_len, $$rf_hash{window});

        if ($tmp_dump[$n] eq '') {
            $mw->Unbusy;
            Error($$rf_hash{window}, "No Sysex data received from JD-Xi\nCheck your MIDI connections and settings");
            return;
        }
        if ($DEBUG) {print STDOUT "tmp dump[$n] length ".(length $tmp_dump[$n])."\n"}
        my $check=ValidatePatData(\$tmp_dump[$n], \$$rf_hash{pattern}[$n], $exp_len);
        if ($check ne 'ok') {
            if ($DEBUG) {print STDOUT "$check\n"}
            $mw->Unbusy;
            Error($$rf_hash{window}, "Error while receiving data from JD-Xi\n\n$check");
            return;
        }
    }
    # All data received and checked successfully
    for (my $n=0; $n<@{$$rf_hash{data}}; $n++) {
        ReadPatData(\substr($tmp_dump[$n],12,($$rf_hash{datalen}[$n])), $rf_hash, $n);
        if ($$rf_hash{name}[$n] ne "\x00") { $$rf_hash{name}[$n]=PData2Name($$rf_hash{data}[$n]) }
    }
    $$rf_hash{modified}=0;
    $$rf_hash{filename}='';
    $$rf_hash{window}->title($$rf_hash{titlestr});
    if ($$rf_hash{type} eq 'FX') { ShowFXCtrls(0); ShowFXCtrls(1); }
    $mw->Unbusy;
}

# request and receive a sysex dump
sub SyxReceive {
    my($req_sysex, $exp_len, $rf_win)=@_;

    my $tmp_dump='';

    if ($LINUX and ($midi_outdev ne '') and ($midi_indev ne '')) {
        MIDI::ALSA::output(MIDI::ALSA::sysex($dev_nr-1, $req_sysex, 0));
        my $midinow=time;
        while (time < ($midinow+2)) {
            if (MIDI::ALSA::inputpending()) {                                            # if MIDI input data pending
                my @alsaevent=MIDI::ALSA::input();                                       # read next ALSA input event
                if ( $alsaevent[0] == SND_SEQ_EVENT_PORT_UNSUBSCRIBED() ) {              # if the input connection has disappeared then exit
                    Error($rf_win,"Error: MIDI connection \'$midi_indev\' dropped.");
                    return '';
                }
                elsif ( $alsaevent[0] == SND_SEQ_EVENT_SYSEX() ) {                       # if sysex data received then do this
                    my @data=@{$alsaevent[7]};                                           # save event data array
                    $tmp_dump=$tmp_dump.$data[0];                                        # append sysex data chunk to $tmp_dump
                    if ( substr($data[0],-1) eq chr(247) ) {                             # if last byte is F7 then sysex dump is complete
                        if ((length $tmp_dump) == $exp_len) {  last; } else { $tmp_dump=''; }  # if length doesn't match then discard sysex data
                    }
                }
            }
        }
    } 
    return $tmp_dump;
}

#------------------------------------------------------------------------------------------------
# Standard GUI Elements

# Set equal weight to all grid elements
sub GridW1 {
    my($frame)=@_;

    my ($cols, $rows)=$$frame->gridSize();
    for (my $i=0; $i < $cols; $i++) {
        $$frame->gridColumnconfigure($i, -weight=>1);
    }
    for (my $i=0; $i < $rows; $i++) {
        $$frame->gridRowconfigure($i, -weight=>1);
    }
}

# Set equal weight to all grid elements vertically
sub GridYW1 {
    my($frame)=@_;

    my ($cols, $rows)=$$frame->gridSize();
    for (my $i=0; $i < $rows; $i++) {
        $$frame->gridRowconfigure($i, -weight=>1);
    }
}

# Set equal weight to all grid elements horizontally
sub GridXW1 {
    my($frame)=@_;

    my ($cols, $rows)=$$frame->gridSize();
    for (my $i=0; $i < $cols; $i++) {
        $$frame->gridColumnconfigure($i, -weight=>1);
    }
}

# Subframe with header, returns Subframe created
sub StdFrame {
    my ($frame, $title, $tbgc, $tfgc)=@_;

    if (!$tbgc) {$tbgc=$conf{Titlebg}}
    if (!$tfgc) {$tfgc=$conf{Titlefg}}

    if ($title) { Header($frame, $title, $tbgc, $tfgc)->pack(-fill=>'x'); }

    my $sf=SubFrame($frame
    )->pack(-fill=>'both', -expand=>1, -anchor=>'n', -padx=>4, -pady=>8);

    return $sf;
}

# Header
sub Header {
    my ($frame, $title, $tbgc, $tfgc, $pos)=@_;

    if (!$pos) {$pos='center'}

    my $sf=$$frame->Label(
        -font       => $conf{Titlefnt},
        -text       => $title,
        -background => $tbgc,
        -foreground => $tfgc,
        -anchor     => $pos
    );
    return $sf;
}

# Subframe
sub SubFrame {
    my ($frame)=@_;
    my $subframe=$$frame->Frame(-bg=>$conf{bgcolor});
    return $subframe;
}

# Horizontal Slider with Label and Value Box
sub StdSlider { 
    my ($frame, $md, $var, $len, $from, $to, $intv, $incr, $parm, $label, $transf)=@_;
    if (! $transf) {$transf=''}

    my $sf=$$frame->Frame(-bg=>$conf{bgcolor});

    my $scale=$sf->Scale(%{$D{Scale_defaults}},
        -variable     =>  $var,
        -from         =>  $from,
        -to           =>  $to,
        -resolution   =>  $incr,
        -tickinterval =>  $intv,
        -label        =>  '',
        -command      => sub { if ($$md{ct}{$parm}) {$$md{modified}=1; SendPaChMsg($parm,(eval "$$var$transf"),$len)} else {$$md{ct}{$parm}=1} }
    )->grid(%{$D{Scale_geo}}, -row=>1, -column=>0);
    BindMWheel(\$scale, \$sf,   \$scale, $var, $incr);
    BindMWheel(\$sf,    $frame, \$scale, $var, $incr);

    if ($label ne '') {
        my $sclab1=$sf->Label(%{$D{SCLab1_defaults}},
            -text     => $label
        )->grid(%{$D{SCLab1_geo}}, -row=>0, -column=>0);
        BindMWheel(\$sclab1, \$sf,   \$scale, $var, $incr);
    }

    my $sclab2=$sf->Label(%{$D{SCLab2_defaults}},
        -justify      => 'center',
        -textvariable =>  $var
    )->grid(%{$D{SCLab2_geo}}, -row=>0, -column=>1, -rowspan=>2);
    BindMWheel(\$sclab2, \$sf,   \$scale, $var, $incr);

    if ($label=~/.*Detune.*/) {
        my $balloon=$sf->Balloon();
        $balloon->attach($scale, -initwait=>4000, -state=>'balloon', -balloonmsg=>'..than what?');
    }

    return $sf;
}

# Vertical Slider with Value Box and Label
sub VertSlider { 
    my ($frame, $md, $var, $len, $from, $to, $intv, $incr, $parm, $label, $transf)=@_;
    if (! $transf) {$transf=''}

    my $sf=$$frame->Frame(-bg=>$conf{bgcolor});
    $sf->gridColumnconfigure(0, -minsize=>41);

    my $sclab1=$sf->Label(%{$D{SCLab1_defaults}},
        -justify      => 'center',
        -anchor       => 's',
        -wraplength   => 40,
        -text         => $label
    )->grid(-row=>0, -column=>0, -pady=>4);

    my $scale=$sf->Scale(%{$D{Scale_defaults}},
        -orient       => 'vertical',
        -length       =>  $conf{Vsldrlen},
        -variable     =>  $var,
        -from         =>  $to,
        -to           =>  $from,
        -resolution   =>  $incr,
        -tickinterval =>  $intv,
        -label        =>  '',
        -command      => sub { if ($$md{ct}{$parm}) {$$md{modified}=1; SendPaChMsg($parm, (eval "$$var$transf"), $len)} else {$$md{ct}{$parm}=1} }
    )->grid(-row=>1, -column=>0);
    BindMWheel(\$scale,  \$sf,   \$scale, $var, $incr);
    BindMWheel(\$sf,     $frame, \$scale, $var, $incr);

    my $sclab2=$sf->Label(%{$D{SCLab2_defaults}},
        -justify      => 'center',
        -pady         =>  4,
        -textvariable =>  $var
    )->grid(-row=>2, -column=>0, -pady=>4);
    BindMWheel(\$sclab2, \$sf,   \$scale, $var, $incr);

    return $sf;
}

# Radiobuttons with Labels and Title
sub OptSelect { 
    my ($frame, $md, $var, $len, $options, $parm, $pbtnwdth, $tbtnwdth, $desc, $onerow, $transf)=@_;
    if (! $transf) {$transf=''}

    my $optnr=(@{$options});
    my $sf=$$frame->Frame(-bg=>$conf{bgcolor});
    my $row=1;
    my $col=0;
    my $span=$optnr;

    if ($desc) {
        if ($onerow) {$row=0; $col=1; $span=1}
        $sf->Label(%{$D{Label_defaults}},
            -text     => $desc
        )->grid(-row=>0, -columnspan=>$span, -sticky=>'nsew');
    }

    for (my $n=0; $n<$optnr; $n++) {

        my %label=();
        my $btnwidth;

        if (substr($$options[$n],0,9) eq 'Tk::Photo') {
            %label=(-image=>$$options[$n], -height=>'0.180i');
            $btnwidth=$pbtnwdth;
        } else {
            %label=(-text=>$$options[$n]);
            if (ref($tbtnwdth) eq '') {$btnwidth=$tbtnwdth} else {$btnwidth=$$tbtnwdth[$n]}
        }

        my $rdbtn=$sf->Radiobutton(%{$D{RadioB_defaults}}, %label,
            -width    => $btnwidth,
            -value    => $n,
            -variable => $var,
            -command  => sub{$$md{modified}=1; SendPaChMsg($parm, (eval "$$var$transf"), $len); }
        )->grid(-row=>$row, -column=>$n+$col, -sticky=>'nsew');

        # remove binding for Enter and Leave to avoid activecolor
        my $class = ref $rdbtn;
        $rdbtn->bind($class,'<Enter>'=> sub {});
        $rdbtn->bind($class,'<Leave>'=> sub {});
    }

    return $sf;
}

# Pulldown Menu with Label
sub PullDwnMenu {
    my ($frame, $md, $var, $len, $options, $parm, $menuwidth, $desc, $onerow, $transf)=@_;
    if (! $transf) {$transf='+0'}

    my $sf=$$frame->Frame(-bg=>$conf{bgcolor});
    my $row=1;
    my $col=0;
    my $sty1='nsew';
    my $sty2='nsew';

    if ($desc) {
        if ($onerow) {$row=0; $col=1; $sty1='e'; $sty2='w'}
        $sf->Label(%{$D{Label_defaults}},
            -text         => $desc
        )->grid(-row=>0, -column=>0, -sticky =>$sty1);
    }

    my $prmcount=@$options;
    my $lbhgt=$conf{lstheight};
    if ($prmcount<$conf{lstheight}) { $lbhgt=($prmcount+1) }
    #if ($DEBUG) {print "nr. of listbox options: $prmcount lbhgt: $lbhgt\n"}

    my $entry=$sf->BrowseEntry(%{$D{BEntry_defaults}},
        -variable     => \$PDM_val{$parm},
        -choices      => ["$PDM_val{$parm}"],
        -width        => $menuwidth,
        -listheight   => $lbhgt,
        -listcmd      => sub{ $_[0]->delete(0, 'end');
                              $_[0]->insert('end', $_) for (@$options);
                              $_[0]->Subwidget('slistbox')->see($$var);
                            },
        -browse2cmd   => sub{ $$md{modified}=1; 
                              if    ($PDM_val{$parm}=~/^(\d\d):.*/) {($$var)=$PDM_val{$parm}=~/^(\d\d):.*/}
                              else  {$$var=$_[1]}
                              if    ($parm eq '18000200') {ReadPatData(\$FX_send[$$var], \%FX, 0); SysexStrSend(\%FX, 0); ShowFXCtrls(0)}
                              elsif ($parm eq '18000400') {ReadPatData(\$FX_send[$$var], \%FX, 1); SysexStrSend(\%FX, 1); ShowFXCtrls(1)}
                              else  { SendPaChMsg($parm, (eval '$$var'.$transf), $len) }
                            }
    )->grid(-row=>$row, -column=>$col, -sticky =>$sty2);
    $entry->Subwidget('choices' )->configure(%{$D{choices_defaults}});
    $entry->Subwidget('arrow'   )->configure(%{$D{arrow_defaults}});
    $entry->Subwidget('slistbox')->configure(-activestyle=>'none');

    # configure mousewheel browsing and selecting of waveforms (SN + DR) and of arp style
    if ($parm=~/^19(0|2)12(0|1|2)35$/ ||                             # SN waveforms
        $parm=~/^1970[2-7][0-9,A-F](27|2B|44|48|61|65|7E|02)$/ ||    # DR waveforms
        $parm=~/^18004005$/                                          # arp style
       ) {
        my @subparms=($options, $parm, $md, $var, $len, $transf, \$entry);
        if ($LINUX) {
            $entry->bind('<Button-4>'=>sub{ ChgVal('next', @subparms) });
            $entry->bind('<Button-5>'=>sub{ ChgVal('prev', @subparms) });
            $entry->Subwidget('arrow')->bind('<Button-4>'=>sub{ ChgVal('next', @subparms) });
            $entry->Subwidget('arrow')->bind('<Button-5>'=>sub{ ChgVal('prev', @subparms) });
        } 
    }
    return $sf;
}

# select next/previous waveform
sub ChgVal {
    my ($chg, $rf_opt, $parm, $md, $var, $len, $transf, $rf_entry)=@_;
    if ($PDM_val{$parm} eq '') {
        $PDM_val{$parm}=$$rf_opt[0];
    }
    my ($prnr)=$PDM_val{$parm}=~/^(\d\d\d):.*/;
    if ($parm==18004005) {$prnr-=1}
    if    ($chg eq 'prev' && ($prnr > 0))            { $$var=$prnr-1; }
    elsif ($chg eq 'next' && ($prnr < (@$rf_opt-1))) { $$var=$prnr+1; }
    else  { return }
    $$md{modified}=1;
    $PDM_val{$parm}=$$rf_opt[$$var];
    SendPaChMsg($parm, (eval '$$var'.$transf), $len);
    $$rf_entry->Subwidget('slistbox')->see($$var);
}

# ON/OFF Switch
sub OnOffSwitch {
    my ($frame, $md, $var, $len, $parm, $desc, $btxt, $onval, $transf)=@_;
    if (! $transf) {$transf=''}

    if (! $onval) {$onval=1}
    my %Label;
    if ($btxt) { %Label=(-text=>"$btxt") }

    my $sf=$$frame->Frame(-bg=>$conf{bgcolor});

    $sf->Label(%{$D{Label_defaults}},
        -text         => $desc
    )->grid(-row=>0, -column=>0, -sticky =>'e');

    my $ckbtn=$sf->Checkbutton(%{$D{Chkbtn_defaults}}, %Label,
        -variable     => $var,
        -onvalue      => $onval,
        -command      => sub{$$md{modified}=1; SendPaChMsg($parm, (eval "$$var$transf"), $len); }
    )->grid(-row=>0, -column=>1, -sticky =>'w');

    # remove binding for Enter and Leave to avoid activecolor
    my $class = ref $ckbtn;
    $ckbtn->bind($class,'<Enter>'=> sub {});
    $ckbtn->bind($class,'<Leave>'=> sub {});

    return $sf;
}

# Spinbox
sub NrSpinBox {
    my ($frame, $var, $from, $to, $incr, $width)=@_;

    my $spbox=$$frame->Spinbox(%{$D{Spinbox_defaults}},
        -width        => $width,
        -textvariable => $var,
        -to           => $to,
        -from         => $from,
        -increment    => $incr,
        -state        => 'readonly'
    );

    return $spbox;
}

# Patch Name
sub PNameEdit {
    my ($frame, $md, $name, $labeltxt)=@_;

    my $sf=$$frame->Frame(-bg=>$conf{bgcolor});

    my $vcn_width=14;

    $sf->Label(%{$D{Label_defaults}},
        -text=> $labeltxt
    )->grid(-row=>0, -column=>0, -sticky =>'e');

    my $namentry=$sf->Entry(%{$D{Entry_defaults}},
        -width           => $vcn_width,
        -font            => $conf{patnamefnt},
        -validate        => 'key',
        -justify         => 'center',
        -validatecommand => sub {$_[0]=~/^[\x20-\x7E]{0,12}$/},
        -invalidcommand  => sub {},
        -textvariable    => $name
    )->grid(-row=>0, -column=>1, -sticky =>'w');
    $namentry->bind('<Return>'=>  sub {
                                       #Name2PData(\%AN);
                                       #for (my $n=0x19420000; $n<0x1942000B; $n++) {
                                         #  SendPaChMsg($parm, (eval"$$var"), 1);
                                       #}
                                       $$md{modified}=1;
                                       $$frame->focus});
    $namentry->bind('<FocusIn>' =>  sub { $mute=1 });
    $namentry->bind('<FocusOut>'=>  sub { $mute=0 });

    return $sf;
}

# Spacer
sub Spacer {
    my ($frame, $height, $bgcol)=@_;

    if (!$bgcol) {$bgcol=$conf{bgcolor}}

    my $sf=$$frame->Label(
        -image       => $spacer_xpm,
        -height      => $height,
        -background  => $bgcol,
        -borderwidth => 0
    );
    return $sf;
}

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Analog Synth Editor Frames

sub AN_OSC_Frame {
    my($frame)=@_;
    my $md=\%AN;
    my $sfr=StdFrame($frame, 'OSC', $conf{OSCbgc}, $conf{OSCfgc});
    my @OSCWav_label=($upsaw_icon, $triang_icon, $square_icon);
    OptSelect  ( \$sfr, $md, \$ANdata[0x16], 1, \@OSCWav_label,   '19420016', '0.4i',5,'Oscillator Waveform:')->grid(%{$D{GridCfg}});
    Spacer     ( \$sfr, '1'                                                                                  )->grid(%{$D{GridCfg}});
    StdSlider  ( \$sfr, $md, \$ANdata[0x19], 1,   0, 127, $sp, 1, '19420019', 'Pulse Width'                  )->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$ANdata[0x1A], 1,   0, 127, $sp, 1, '1942001A', 'PW Mod Depth'                 )->grid(%{$D{SCFr_geo}});
    my @SubOSC_label=('OFF', 'Oct-1', 'Oct-2');
    OptSelect  ( \$sfr, $md, \$ANdata[0x1F], 1, \@SubOSC_label,   '1942001F', 39, 7, 'Sub Oscillator:'       )->grid(%{$D{GridCfg}});
    Spacer     ( \$sfr, '1'                                                                                  )->grid(%{$D{GridCfg}});
    StdSlider  ( \$sfr, $md, \$ANdata[0x17], 1, -24,  24, $sn, 1, '19420017', 'Pitch (semitones)',     '+64' )->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$ANdata[0x18], 1, -50,  50, $sn, 1, '19420018', 'Detune (cents)',        '+64' )->grid(%{$D{SCFr_geo}});
    Header     ( \$sfr, "\nPitch Envelope", $conf{bgcolor}, $conf{fontcolor}, 's'                            )->grid(%{$D{GridCfg}});
    my $vfr=SubFrame(\$sfr                                                                                   )->grid(%{$D{GridCfg}});
    VertSlider ( \$vfr, $md, \$ANdata[0x1C], 1,   0, 127, $sp, 1, '1942001C', 'Att'                          )->pack(%{$D{VSliConf}});
    VertSlider ( \$vfr, $md, \$ANdata[0x1D], 1,   0, 127, $sp, 1, '1942001D', 'Dec'                          )->pack(%{$D{VSliConf}});
    StdSlider  ( \$sfr, $md, \$ANdata[0x1E], 1, -63,  63, $sn, 1, '1942001E', 'Env Depth',             '+64' )->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$ANdata[0x1B], 1, -63,  63, $sn, 1, '1942001B', 'Env Vel Sensitivity',   '+64' )->grid(%{$D{SCFr_geo}});
    GridYW1(\$sfr);
}

sub AN_VCF_Frame {
    my($frame)=@_;
    my $md=\%AN;
    my $sfr=StdFrame($frame, 'FILTER', $conf{VCFbgc}, $conf{VCFfgc});
    Spacer     ( \$sfr, '1'                                                                                  )->grid(%{$D{GridCfg}});
    OnOffSwitch( \$sfr, $md, \$ANdata[0x20], 1,                   '19420020', 'Analog LPF: '                 )->grid(%{$D{GridCfg}});
    Spacer     ( \$sfr, '1'                                                                                  )->grid(%{$D{GridCfg}});
    StdSlider  ( \$sfr, $md, \$ANdata[0x21], 1,   0, 127, $sp, 1, '19420021', 'Cutoff'                       )->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$ANdata[0x23], 1,   0, 127, $sp, 1, '19420023', 'Resonance'                    )->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$ANdata[0x22], 1,-100, 100, $sn,10, '19420022', 'Cutoff Keyfollow',   '/10+64' )->grid(%{$D{SCFr_geo}});
    Header     ( \$sfr, "\nFilter Envelope", $conf{bgcolor}, $conf{fontcolor}, 's'                           )->grid(%{$D{GridCfg}});
    my $vfr=SubFrame(\$sfr                                                                                   )->grid(%{$D{GridCfg}});
    VertSlider ( \$vfr, $md, \$ANdata[0x25], 1,   0, 127, $sp, 1, '19420025', 'Att'                          )->pack(%{$D{VSliConf}});
    VertSlider ( \$vfr, $md, \$ANdata[0x26], 1,   0, 127, $sp, 1, '19420026', 'Dec'                          )->pack(%{$D{VSliConf}});
    VertSlider ( \$vfr, $md, \$ANdata[0x27], 1,   0, 127, $sp, 1, '19420027', 'Sus'                          )->pack(%{$D{VSliConf}});
    VertSlider ( \$vfr, $md, \$ANdata[0x28], 1,   0, 127, $sp, 1, '19420028', 'Rel'                          )->pack(%{$D{VSliConf}});
    Spacer     ( \$sfr, '1'                                                                                  )->grid(%{$D{GridCfg}});
    StdSlider  ( \$sfr, $md, \$ANdata[0x29], 1, -63,  63, $sn, 1, '19420029', 'Env Depth',             '+64' )->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$ANdata[0x24], 1, -63,  63, $sn, 1, '19420024', 'Env Vel Sensitivity',   '+64' )->grid(%{$D{SCFr_geo}});
    Spacer     ( \$sfr, '1'                                                                                  )->grid(%{$D{GridCfg}});
    GridYW1(\$sfr);
}

sub AN_AMP_Frame {
    my($frame)=@_;
    my $md=\%AN;
    my $sfr=StdFrame($frame, 'AMP/ENV', $conf{AMPbgc}, $conf{AMPfgc});
    StdSlider  ( \$sfr, $md, \$ANdata[0x2A], 1,   0, 127, $sp, 1, '1942002A', 'Level'                        )->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$ANdata[0x2B], 1,-100, 100, $sn,10, '1942002B', 'Level Keyfollow',    '/10+64' )->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$ANdata[0x2C], 1, -63,  63, $sn, 1, '1942002C', 'Level Vel Sensitivity', '+64' )->grid(%{$D{SCFr_geo}});
    Spacer     ( \$sfr, '1'                                                                                  )->grid(%{$D{GridCfg}});
    my $vfr=SubFrame(\$sfr                                                                                   )->grid(%{$D{GridCfg}});
    VertSlider ( \$vfr, $md, \$ANdata[0x2D], 1,   0, 127, $sp, 1, '1942002D', 'Att'                          )->pack(%{$D{VSliConf}});
    VertSlider ( \$vfr, $md, \$ANdata[0x2E], 1,   0, 127, $sp, 1, '1942002E', 'Dec'                          )->pack(%{$D{VSliConf}});
    VertSlider ( \$vfr, $md, \$ANdata[0x2F], 1,   0, 127, $sp, 1, '1942002F', 'Sus'                          )->pack(%{$D{VSliConf}});
    VertSlider ( \$vfr, $md, \$ANdata[0x30], 1,   0, 127, $sp, 1, '19420030', 'Rel'                          )->pack(%{$D{VSliConf}});
    GridYW1(\$sfr);
}

sub AN_LFO_Frame {
    my($frame)=@_;
    my $md=\%AN;
    my $sfr=StdFrame($frame, 'LFO', $conf{LFObgc}, $conf{LFOfgc});
    my @LFOWav_label=($triang_icon, $sine_icon, $upsaw_icon, $square_icon, 'S&H', 'RND');
    OptSelect  ( \$sfr, $md, \$ANdata[0x0D], 1, \@LFOWav_label,   '1942000D', '0.3i', 5, 'Shape:'            )->grid(-columnspan => 2, %{$D{GridCfg}});
    Spacer     ( \$sfr, '1'                                                                                  )->grid(-columnspan => 2, %{$D{GridCfg}});
    StdSlider  ( \$sfr, $md, \$ANdata[0x0E], 1,   0, 127, $sp, 1, '1942000E', 'Rate'                         )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$ANdata[0x0F], 1,   0, 127, $sp, 1, '1942000F', 'Fade Time'                    )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    Spacer     ( \$sfr, '1'                                                                                  )->grid(%{$D{GridCfg}});
    OnOffSwitch( \$sfr, $md, \$ANdata[0x10], 1,                   '19420010', 'Tempo Sync: '                 )->grid(
    PullDwnMenu( \$sfr, $md, \$ANdata[0x11], 1, \@sync_notes,     '19420011', 5, 'Note: '                 ,1 ), %{$D{GridCfg}});
    Spacer     ( \$sfr, '1'                                                                                  )->grid(%{$D{GridCfg}});
    StdSlider  ( \$sfr, $md, \$ANdata[0x12], 1, -63,  63, $sn, 1, '19420012', 'Pitch Depth',           '+64' )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$ANdata[0x13], 1, -63,  63, $sn, 1, '19420013', 'Filter Depth',          '+64' )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$ANdata[0x14], 1, -63,  63, $sn, 1, '19420014', 'Amp Depth',             '+64' )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    Spacer     ( \$sfr, '1'                                                                                  )->grid(%{$D{GridCfg}});
    OnOffSwitch( \$sfr, $md, \$ANdata[0x15], 1,                   '19420015', 'Key Trigger: '                )->grid(-columnspan => 2, %{$D{GridCfg}});
    Spacer     ( \$sfr, '1'                                                                                  )->grid(%{$D{GridCfg}});
    StdSlider  ( \$sfr, $md, \$ANdata[0x38], 1, -63,  63, $sn, 1, '19420038', 'Pitch Mod Ctrl',        '+64' )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$ANdata[0x39], 1, -63,  63, $sn, 1, '19420039', 'Filter Mod Ctrl',       '+64' )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$ANdata[0x3A], 1, -63,  63, $sn, 1, '1942003A', 'Amp Mod Ctrl',          '+64' )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$ANdata[0x3B], 1, -63,  63, $sn, 1, '1942003B', 'Rate Mod Ctrl',         '+64' )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    Spacer     ( \$sfr, '1'                                                                                  )->grid(%{$D{GridCfg}});
    GridYW1(\$sfr);
}

sub AN_COM_Frame {
    my($frame)=@_;
    my $md=\%AN;
    my $sfr=StdFrame($frame, 'COMMON', $conf{COMbgc}, $conf{COMfgc});
    PNameEdit  ( \$sfr, $md, \$AN{name}[0],                                   'Tone Name: '                  )->grid(-columnspan => 2, %{$D{GridCfg}});
    OnOffSwitch( \$sfr, $md, \$ANdata[0x31], 1,                   '19420031', 'Portamento: '                 )->grid(
    OnOffSwitch( \$sfr, $md, \$ANdata[0x33], 1,                   '19420033', 'Legato: '                     ), %{$D{GridCfg}});
    StdSlider  ( \$sfr, $md, \$ANdata[0x32], 1,   0, 127, $sp, 1, '19420032', 'Portamento Time'              )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$ANdata[0x34], 1,  -3,   3, $sn, 1, '19420034', 'Octave Shift',          '+64' )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$ANdata[0x35], 1,   0,  24, $sp, 1, '19420035', 'Pitch Bend Range Up'          )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$ANdata[0x36], 1,   0,  24, $sp, 1, '19420036', 'Pitch Bend Range Down'        )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    GridYW1(\$sfr);
}

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# SuperNatural Synth Editor Frames

sub SN_COM_Frame {
    my($D,$frame)=@_;
    my $md=$SN[$D];
    my $sfr=StdFrame($frame, 'COMMON', $conf{COMbgc}, $conf{COMfgc});
    PNameEdit  ( \$sfr, $md, \$SN[$D]{name}[0],                                                'Tone Name: '            )->grid(-columnspan => 2, %{$D{GridCfg}});
    PullDwnMenu( \$sfr, $md, \$SN_COM[$D][0x36], 1, \@tone_cats,      $SN[$D]{msb}.'0036', 15, 'Category: '          ,1 )->grid(-columnspan => 2, %{$D{GridCfg}});
    my @PolyMono_label=('Poly', 'Mono');
    OptSelect  ( \$sfr, $md, \$SN_COM[$D][0x14], 1, \@PolyMono_label, $SN[$D]{msb}.'0014', 0, 6                         )->grid(
    OnOffSwitch( \$sfr, $md, \$SN_COM[$D][0x1F], 1,                   $SN[$D]{msb}.'001F', 'Ring: '          ,' on ' ,2 ), %{$D{GridCfg}});
    my $vfr=SubFrame(\$sfr                                                                                              )->grid(-columnspan => 2, %{$D{GridCfg}});
    my @UniSize_label=('2', '4', '6', '8');
    OnOffSwitch( \$vfr, $md, \$SN_COM[$D][0x2E], 1,                   $SN[$D]{msb}.'002E', 'Unison:'                    )->grid(
    OptSelect  ( \$vfr, $md, \$SN_COM[$D][0x3C], 1, \@UniSize_label,  $SN[$D]{msb}.'003C', 0, 3, ' Size:'            ,1 ), %{$D{GridCfg}});
    StdSlider  ( \$sfr, $md, \$SN_COM[$D][0x0C], 1,   0, 127, $sp, 1, $SN[$D]{msb}.'000C', 'Tone Level'                 )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$SN_COM[$D][0x34], 1,   0, 127, $sp, 1, $SN[$D]{msb}.'0034', 'Analog Feel'                )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$SN_COM[$D][0x35], 1,   0, 127, $sp, 1, $SN[$D]{msb}.'0035', 'Wave Shape'                 )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    OnOffSwitch( \$sfr, $md, \$SN_COM[$D][0x12], 1,                   $SN[$D]{msb}.'0012', 'Portamento:'                )->grid(
    OnOffSwitch( \$sfr, $md, \$SN_COM[$D][0x32], 1,                   $SN[$D]{msb}.'0032', 'Legato:'                    ), %{$D{GridCfg}});
    my @PortMode_label=('Normal', 'Legato');
    OptSelect  ( \$sfr, $md, \$SN_COM[$D][0x31], 1, \@PortMode_label, $SN[$D]{msb}.'0031', 0, 7, 'Portam. Mode: '    ,1 )->grid(-columnspan => 2, %{$D{GridCfg}});
    StdSlider  ( \$sfr, $md, \$SN_COM[$D][0x13], 1,   0, 127, $sp, 1, $SN[$D]{msb}.'0013', 'Portamento Time'            )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$SN_COM[$D][0x15], 1,  -3,   3, $sn, 1, $SN[$D]{msb}.'0015', 'Octave Shift',        '+64' )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$SN_COM[$D][0x16], 1,   0,  24, $sp, 1, $SN[$D]{msb}.'0016', 'Pitch Bend Range Up'        )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$SN_COM[$D][0x17], 1,   0,  24, $sp, 1, $SN[$D]{msb}.'0017', 'Pitch Bend Range Down'      )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    GridYW1(\$sfr);
}

sub SN_MOD_Frame {
    my($D,$frame)=@_;
    my $md=$SN[$D];
    my $sfr=StdFrame($frame, 'MISC', $conf{COMbgc}, $conf{COMfgc});
    StdSlider  ( \$sfr, $md, \$SN_MOD[$D][0x01], 1,   0, 127, $sp, 1, $SN[$D]{msb}.'5001', 'AT Interval Sens'           )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$SN_MOD[$D][0x02], 1,   0, 127, $sp, 1, $SN[$D]{msb}.'5002', 'RT Interval Sens'           )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$SN_MOD[$D][0x03], 1,   0, 127, $sp, 1, $SN[$D]{msb}.'5003', 'Portamento Time Intvl Sens' )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    my @LoopMode_label=('Off', 'Free Run', 'Tempo Sync');
    OptSelect  ( \$sfr, $md, \$SN_MOD[$D][0x04], 1, \@LoopMode_label, $SN[$D]{msb}.'5004', 0, [5,10,12], 'Envelope Loop Mode:')->grid(-columnspan => 2, %{$D{GridCfg}});
    PullDwnMenu( \$sfr, $md, \$SN_MOD[$D][0x05], 1, \@sync_notes,     $SN[$D]{msb}.'5005', 5, 'Sync Note: '          ,1       )->grid(-columnspan => 2, %{$D{GridCfg}});
    OnOffSwitch( \$sfr, $md, \$SN_MOD[$D][0x06], 1,                   $SN[$D]{msb}.'5006', 'Chromatic Portamento: '           )->grid(-columnspan => 2, %{$D{GridCfg}});
    GridYW1(\$sfr);
}

sub SN_PRT_Frame {
    my($D,$frame)=@_;
    my $md=$SN[$D];
    my $vfr=$$frame->Frame(-bg=>$conf{bgcolor});
    OnOffSwitch( \$vfr, $md, \$SN_COM[$D][0x1A], 1,                   $SN[$D]{msb}.'001A', 'Edit Select: '        ,' P1 '  )->grid(
    OnOffSwitch( \$vfr, $md, \$SN_COM[$D][0x1C], 1,                   $SN[$D]{msb}.'001C', ''                     ,' P2 '  ),
    OnOffSwitch( \$vfr, $md, \$SN_COM[$D][0x1E], 1,                   $SN[$D]{msb}.'001E', ''                     ,' P3 '  ),
    OnOffSwitch( \$vfr, $md, \$SN_COM[$D][0x19], 1,                   $SN[$D]{msb}.'0019', '   Partials on/off: ' ,' P1 '  ),
    OnOffSwitch( \$vfr, $md, \$SN_COM[$D][0x1B], 1,                   $SN[$D]{msb}.'001B', ''                     ,' P2 '  ),
    OnOffSwitch( \$vfr, $md, \$SN_COM[$D][0x1D], 1,                   $SN[$D]{msb}.'001D', ''                     ,' P3 '  ), -pady=>2);
   return $vfr;
}

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# SN Partials Tabs

sub SN_OSC_Frame {
    my($D,$pl,$frame)=@_;
    my $md=$SN[$D];
    if ($DEBUG) {print STDOUT "SN_OSC_Frame D$D P$pl\n"}
    my $sfr=StdFrame($frame, 'OSC', $conf{OSCbgc}, $conf{OSCfgc});
    my @OSCWav_label=($upsaw_icon, $square_icon, $pwsqu_icon, $triang_icon, $sine_icon, $noise_icon, $spsaw_icon, 'PCM');
    OptSelect  ( \$sfr, $md, \$SN_PL[$D][$pl][0x00], 1,  \@OSCWav_label,  $SN[$D]{msb}.'2'.$pl.'00', '0.38i', 6,'Oscillator Waveform:')->grid(-columnspan => 2, %{$D{GridCfg}});
    my @OSC_var=('A', 'B', 'C');
    my @OSC_gain=('-6', '0', '+6', '+12');
    my $vfr=SubFrame(\$sfr                                                                                                        )->grid(-columnspan => 2, %{$D{GridCfg}});
    OptSelect  ( \$vfr, $md, \$SN_PL[$D][$pl][0x01], 1,  \@OSC_var,       $SN[$D]{msb}.'2'.$pl.'01',  0, 5, 'Wave Variation:'     )->grid(
    PullDwnMenu( \$vfr, $md, \$SN_PL[$D][$pl][0x35], 4,  \@PCMwaves,      $SN[$D]{msb}.'2'.$pl.'35', 18, 'PCM Wave: '             ),
    OptSelect  ( \$vfr, $md, \$SN_PL[$D][$pl][0x34], 1,  \@OSC_gain,      $SN[$D]{msb}.'2'.$pl.'34',  0, 5, 'PCM Gain [dB]:'      ), %{$D{GridCfg}}, -padx=>4);
    GridW1(\$vfr);
    StdSlider  ( \$sfr, $md, \$SN_PL[$D][$pl][0x06], 1,   0, 127, $sp, 1, $SN[$D]{msb}.'2'.$pl.'06', 'Pulse Width'                )->grid(
    StdSlider  ( \$sfr, $md, \$SN_PL[$D][$pl][0x2A], 1,   0, 127, $sp, 1, $SN[$D]{msb}.'2'.$pl.'2A', 'PW Shift'                   ), %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$SN_PL[$D][$pl][0x05], 1,   0, 127, $sp, 1, $SN[$D]{msb}.'2'.$pl.'05', 'PW Mod Depth'               )->grid(
    StdSlider  ( \$sfr, $md, \$SN_PL[$D][$pl][0x3A], 1,   0, 127, $sp, 1, $SN[$D]{msb}.'2'.$pl.'3A', 'SuperSaw Detune'            ), %{$D{SCFr_geo}});
    GridW1(\$sfr);
}

sub SN_PITCH_Frame {
    my($D,$pl,$frame)=@_;
    my $md=$SN[$D];
    my $sfr=StdFrame($frame, 'PITCH', $conf{OSCbgc}, $conf{OSCfgc});
    StdSlider  ( \$sfr, $md, \$SN_PL[$D][$pl][0x03], 1, -24,  24, $sn, 1, $SN[$D]{msb}.'2'.$pl.'03', 'Pitch (semitones)', '+64')->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$SN_PL[$D][$pl][0x04], 1, -50,  50, $sn, 1, $SN[$D]{msb}.'2'.$pl.'04', 'Detune (cents)',    '+64')->grid(%{$D{SCFr_geo}});
    Header     ( \$sfr, "\nPitch Envelope", $conf{bgcolor}, $conf{fontcolor}, 's'                                              )->grid(%{$D{GridCfg}});
    my $vfr=SubFrame(\$sfr                                                                                                     )->grid(%{$D{GridCfg}});
    VertSlider ( \$vfr, $md, \$SN_PL[$D][$pl][0x07], 1,   0, 127, $sp, 1, $SN[$D]{msb}.'2'.$pl.'07', 'Att'                     )->pack(%{$D{VSliConf}});
    VertSlider ( \$vfr, $md, \$SN_PL[$D][$pl][0x08], 1,   0, 127, $sp, 1, $SN[$D]{msb}.'2'.$pl.'08', 'Dec'                     )->pack(%{$D{VSliConf}});
    StdSlider  ( \$sfr, $md, \$SN_PL[$D][$pl][0x09], 1, -63,  63, $sn, 1, $SN[$D]{msb}.'2'.$pl.'09', 'Env Depth',         '+64')->grid(%{$D{SCFr_geo}});
    GridYW1(\$sfr);
}

sub SN_VCF_Frame {
    my($D,$pl,$frame)=@_;
    my $md=$SN[$D];
    my $sfr=StdFrame($frame, 'FILTER', $conf{VCFbgc}, $conf{VCFfgc});
    my @filter_type=('OFF', 'LPF1', 'HPF', 'BPF', 'PKG', 'LPF2', 'LPF3', 'LPF4');
    OptSelect  ( \$sfr, $md, \$SN_PL[$D][$pl][0x0A], 1,  \@filter_type,   $SN[$D]{msb}.'2'.$pl.'0A',  0, 6, 'Filter Type:'          )->grid(-columnspan => 2, %{$D{GridCfg}});
    Spacer     ( \$sfr, '1'                                                                                                         )->grid(-columnspan => 2, %{$D{GridCfg}});
    my @filter_slope=('-12', '-24');
    OptSelect  ( \$sfr, $md, \$SN_PL[$D][$pl][0x0B], 1, \@filter_slope,   $SN[$D]{msb}.'2'.$pl.'0B',  0, 6, 'Filter Slope [dB]: ' ,1)->grid(
    StdSlider  ( \$sfr, $md, \$SN_PL[$D][$pl][0x0D], 1,-100, 100, $sn,10, $SN[$D]{msb}.'2'.$pl.'0D', 'Cutoff Keyfollow',    '/10+64'), %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$SN_PL[$D][$pl][0x0C], 1,   0, 127, $sp, 1, $SN[$D]{msb}.'2'.$pl.'0C', 'Cutoff'                       )->grid(
    StdSlider  ( \$sfr, $md, \$SN_PL[$D][$pl][0x30], 1, -63,  63, $sn, 1, $SN[$D]{msb}.'2'.$pl.'30', 'Cutoff AFT Sensitivity', '+64'), %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$SN_PL[$D][$pl][0x0F], 1,   0, 127, $sp, 1, $SN[$D]{msb}.'2'.$pl.'0F', 'Resonance'                    )->grid(
    StdSlider  ( \$sfr, $md, \$SN_PL[$D][$pl][0x39], 1,   0, 127, $sp, 1, $SN[$D]{msb}.'2'.$pl.'39', 'HPF Cutoff'                   ), %{$D{SCFr_geo}});
    GridW1(\$sfr);
}

sub SN_VCFENV_Frame {
    my($D,$pl,$frame)=@_;
    my $md=$SN[$D];
    my $sfr=StdFrame($frame, 'FILTER ENVELOPE', $conf{VCFbgc}, $conf{VCFfgc});
    my $vfr=SubFrame(\$sfr                                                                                                      )->grid(%{$D{GridCfg}});
    VertSlider ( \$vfr, $md, \$SN_PL[$D][$pl][0x10], 1,   0, 127, $sp, 1, $SN[$D]{msb}.'2'.$pl.'10', 'Att'                      )->pack(%{$D{VSliConf}});
    VertSlider ( \$vfr, $md, \$SN_PL[$D][$pl][0x11], 1,   0, 127, $sp, 1, $SN[$D]{msb}.'2'.$pl.'11', 'Dec'                      )->pack(%{$D{VSliConf}});
    VertSlider ( \$vfr, $md, \$SN_PL[$D][$pl][0x12], 1,   0, 127, $sp, 1, $SN[$D]{msb}.'2'.$pl.'12', 'Sus'                      )->pack(%{$D{VSliConf}});
    VertSlider ( \$vfr, $md, \$SN_PL[$D][$pl][0x13], 1,   0, 127, $sp, 1, $SN[$D]{msb}.'2'.$pl.'13', 'Rel'                      )->pack(%{$D{VSliConf}});
    StdSlider  ( \$sfr, $md, \$SN_PL[$D][$pl][0x14], 1, -63,  63, $sn, 1, $SN[$D]{msb}.'2'.$pl.'14', 'Env Depth',          '+64')->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$SN_PL[$D][$pl][0x0E], 1, -63,  63, $sn, 1, $SN[$D]{msb}.'2'.$pl.'0E', 'Env Vel Sensitivity','+64')->grid(%{$D{SCFr_geo}});
    GridYW1(\$sfr);
}

sub SN_AMP_Frame {
    my($D,$pl,$frame)=@_;
    my $md=$SN[$D];
    my $sfr=StdFrame($frame, 'AMP / ENV', $conf{AMPbgc}, $conf{AMPfgc});
    StdSlider  ( \$sfr, $md, \$SN_PL[$D][$pl][0x15], 1,   0, 127, $sp, 1, $SN[$D]{msb}.'2'.$pl.'15','Level'                      )->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$SN_PL[$D][$pl][0x3C], 1,-100, 100, $sn,10, $SN[$D]{msb}.'2'.$pl.'3C','Level Keyfollow',   '/10+64')->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$SN_PL[$D][$pl][0x16], 1, -63,  63, $sn, 1, $SN[$D]{msb}.'2'.$pl.'16','Level Vel Sensitivity','+64')->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$SN_PL[$D][$pl][0x31], 1, -63,  63, $sn, 1, $SN[$D]{msb}.'2'.$pl.'31','Level AFT Sensitivity','+64')->grid(%{$D{SCFr_geo}});
    my $gp=' 'x$conf{pgap};
    StdSlider  ( \$sfr, $md, \$SN_PL[$D][$pl][0x1B], 1, -64,  63, $sn, 1, $SN[$D]{msb}.'2'.$pl.'1B','Pan'.$gp.'L<---0--->R','+64')->grid(%{$D{SCFr_geo}});
    my $vfr=SubFrame(\$sfr                                                                                                       )->grid(%{$D{SCFr_geo}},
                                                                                                                           -row=>0, -column=>1, -rowspan=>5);
    GridW1(\$sfr);
    $sfr->gridColumnconfigure(1, -minsize=>212);
    VertSlider ( \$vfr, $md, \$SN_PL[$D][$pl][0x17], 1,   0, 127, $sp, 1, $SN[$D]{msb}.'2'.$pl.'17', 'Att'                 )->pack(%{$D{VSliConf}});
    VertSlider ( \$vfr, $md, \$SN_PL[$D][$pl][0x18], 1,   0, 127, $sp, 1, $SN[$D]{msb}.'2'.$pl.'18', 'Dec'                 )->pack(%{$D{VSliConf}});
    VertSlider ( \$vfr, $md, \$SN_PL[$D][$pl][0x19], 1,   0, 127, $sp, 1, $SN[$D]{msb}.'2'.$pl.'19', 'Sus'                 )->pack(%{$D{VSliConf}});
    VertSlider ( \$vfr, $md, \$SN_PL[$D][$pl][0x1A], 1,   0, 127, $sp, 1, $SN[$D]{msb}.'2'.$pl.'1A', 'Rel'                 )->pack(%{$D{VSliConf}});
}

sub SN_LFO_Frame {
    my($D,$pl,$frame)=@_;
    my $md=$SN[$D];
    my $sfr=StdFrame($frame, 'LFO', $conf{LFObgc}, $conf{LFOfgc});
    my @LFOWav_label=($triang_icon, $sine_icon, $upsaw_icon, $square_icon, 'S&H', 'RND');
    OptSelect  ( \$sfr, $md, \$SN_PL[$D][$pl][0x1C], 1, \@LFOWav_label,   $SN[$D]{msb}.'2'.$pl.'1C', '0.3i', 5, ''    ,1 )->grid(-columnspan => 2, %{$D{GridCfg}});
    StdSlider  ( \$sfr, $md, \$SN_PL[$D][$pl][0x1D], 1,   0, 127, $sp, 1, $SN[$D]{msb}.'2'.$pl.'1D', 'Rate'              )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$SN_PL[$D][$pl][0x20], 1,   0, 127, $sp, 1, $SN[$D]{msb}.'2'.$pl.'20', 'Fade Time'         )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    OnOffSwitch( \$sfr, $md, \$SN_PL[$D][$pl][0x1E], 1,                   $SN[$D]{msb}.'2'.$pl.'1E', 'Tempo Sync:'       )->grid(
    PullDwnMenu( \$sfr, $md, \$SN_PL[$D][$pl][0x1F], 1, \@sync_notes,     $SN[$D]{msb}.'2'.$pl.'1F', 5, ' Note:'      ,1 ), %{$D{GridCfg}});
    StdSlider  ( \$sfr, $md, \$SN_PL[$D][$pl][0x22], 1, -63,  63, $sn, 1, $SN[$D]{msb}.'2'.$pl.'22', 'Pitch Depth', '+64')->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$SN_PL[$D][$pl][0x23], 1, -63,  63, $sn, 1, $SN[$D]{msb}.'2'.$pl.'23', 'Filter Depth','+64')->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$SN_PL[$D][$pl][0x24], 1, -63,  63, $sn, 1, $SN[$D]{msb}.'2'.$pl.'24', 'Amp Depth',   '+64')->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$SN_PL[$D][$pl][0x25], 1, -63,  63, $sn, 1, $SN[$D]{msb}.'2'.$pl.'25', 'Pan Depth',   '+64')->grid(-columnspan => 2, %{$D{SCFr_geo}});
    OnOffSwitch( \$sfr, $md, \$SN_PL[$D][$pl][0x21], 1,                   $SN[$D]{msb}.'2'.$pl.'21', 'Key Trigger: '     )->grid(-columnspan => 2, %{$D{GridCfg}});
    GridYW1(\$sfr);
}

sub SN_MLFO_Frame {
    my($D,$pl,$frame)=@_;
    my $md=$SN[$D];
    my $sfr=StdFrame($frame, 'MOD LFO', $conf{LFObgc}, $conf{LFOfgc});
    my @LFOWav_label=($triang_icon, $sine_icon, $upsaw_icon, $square_icon, 'S&H', 'RND');
    OptSelect  ( \$sfr, $md, \$SN_PL[$D][$pl][0x26], 1, \@LFOWav_label,   $SN[$D]{msb}.'2'.$pl.'26', '0.3i', 5, ''    ,1 )->grid(-columnspan => 2, %{$D{GridCfg}});
    StdSlider  ( \$sfr, $md, \$SN_PL[$D][$pl][0x27], 1,   0, 127, $sp, 1, $SN[$D]{msb}.'2'.$pl.'27', 'Rate'              )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$SN_PL[$D][$pl][0x3B], 1, -63,  63, $sn, 1, $SN[$D]{msb}.'2'.$pl.'3B', 'Rate Control','+64')->grid(-columnspan => 2, %{$D{SCFr_geo}});
    OnOffSwitch( \$sfr, $md, \$SN_PL[$D][$pl][0x28], 1,                   $SN[$D]{msb}.'2'.$pl.'28', 'Tempo Sync:'       )->grid(
    PullDwnMenu( \$sfr, $md, \$SN_PL[$D][$pl][0x29], 1, \@sync_notes,     $SN[$D]{msb}.'2'.$pl.'29', 5, ' Note:'      ,1 ), %{$D{GridCfg}});
    StdSlider  ( \$sfr, $md, \$SN_PL[$D][$pl][0x2C], 1, -63,  63, $sn, 1, $SN[$D]{msb}.'2'.$pl.'2C', 'Pitch Depth', '+64')->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$SN_PL[$D][$pl][0x2D], 1, -63,  63, $sn, 1, $SN[$D]{msb}.'2'.$pl.'2D', 'Filter Depth','+64')->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$SN_PL[$D][$pl][0x2E], 1, -63,  63, $sn, 1, $SN[$D]{msb}.'2'.$pl.'2E', 'Amp Depth',   '+64')->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$SN_PL[$D][$pl][0x2F], 1, -63,  63, $sn, 1, $SN[$D]{msb}.'2'.$pl.'2F', 'Pan Depth',   '+64')->grid(-columnspan => 2, %{$D{SCFr_geo}});
    GridYW1(\$sfr);
}

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Drums Synth Editor Frames

sub DR_COM_Frame {
    my($frame)=@_;
    my $md=\%DR;
    my $sfr=StdFrame($frame, '', $conf{COMbgc}, $conf{COMfgc});
    StdSlider  ( \$sfr, $md, \$DRdata[0][0x00C],  1,   0, 127, $sp, 1, '1970000C', 'Kit Level'                  )->grid(
    PNameEdit  ( \$sfr, $md, \$DR{name}[0],                                        'Kit Name:  '                ), %{$D{SCFr_geo}});
}

sub DR_MAIN_Frame {
    my($D, $LO, $HI, $frame)=@_;
    my $md=\%DR;
    my $sfr=StdFrame($frame, 'COMMON', $conf{COMbgc}, $conf{COMfgc});
    PNameEdit  ( \$sfr, $md, \$DR{name}[$D],                                      'Part Name: '                        )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    Spacer     ( \$sfr, '1'                                                                                            )->grid(-columnspan => 2, %{$D{GridCfg}});
    OptSelect  ( \$sfr, $md, \$DRdata[$D][0x0C], 1,['MULTI','SINGLE'],'1970'.$LO.'0C', 31, 10, 'Assign Type: '      ,1 )->grid(-columnspan => 2, %{$D{GridCfg}});
    PullDwnMenu( \$sfr, $md, \$DRdata[$D][0x0D], 1, \@mute_grp,       '1970'.$LO.'0D',  5, 'Mute Group: '           ,1 )->grid(-columnspan => 2, %{$D{GridCfg}});
    StdSlider  ( \$sfr, $md, \$DRdata[$D][0x1C], 1,   0,  48, $sp, 1, '1970'.$LO.'1C', 'Pitch Bend Range'              )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    OnOffSwitch( \$sfr, $md, \$DRdata[$D][0x1D], 1,                   '1970'.$LO.'1D', 'Rcv Expr:'                     )->grid(
    OnOffSwitch( \$sfr, $md, \$DRdata[$D][0x1E], 1,                   '1970'.$LO.'1E', '    Rcv Hold-1:   '            ), %{$D{GridCfg}});
    OnOffSwitch( \$sfr, $md, \$DRdata[$D][0x15], 1,                   '1970'.$LO.'15', 'Sustain:   '                   )->grid(
    OnOffSwitch( \$sfr, $md, \$DRdata[$D][0xC1], 1,                   '1970'.$HI.'41', 'One Shot Mode:'                ), %{$D{GridCfg}});
    OptSelect  ( \$sfr, $md, \$DRdata[$D][0x20], 1,['OFF','ON','RND'],'1970'.$LO.'20', 31, 6, 'WMT Vel Ctrl:  '     ,1 )->grid(-columnspan => 2, %{$D{GridCfg}});
    GridYW1(\$sfr);
}

sub DR_PRT_Frame {
    my($D, $LO, $frame)=@_;
    my $md=\%DR;
    my $vfr=$$frame->Frame(-bg=>$conf{divcol});
    OnOffSwitch( \$vfr, $md, \$DRdata[$D][0x21], 1,                   '1970'.$LO.'21', 'Wave on/off: '        ,' W1 '  )->grid(
    OnOffSwitch( \$vfr, $md, \$DRdata[$D][0x3E], 1,                   '1970'.$LO.'3E', ''                     ,' W2 '  ),
    OnOffSwitch( \$vfr, $md, \$DRdata[$D][0x5B], 1,                   '1970'.$LO.'5B', ''                     ,' W3 '  ),
    OnOffSwitch( \$vfr, $md, \$DRdata[$D][0x78], 1,                   '1970'.$LO.'78', ''                     ,' W4 '  ), -pady=>2);
   return $vfr;
}

sub DR_OUT_Frame {
    my($D, $LO, $HI, $frame)=@_;
    my $md=\%DR;
    my $sfr=StdFrame($frame, 'OUTPUT', $conf{COMbgc}, $conf{COMfgc});
    my @OA_label=('EFX1', 'EFX2', 'DLY', 'REV', 'DIR');
    OptSelect  ( \$sfr, $md, \$DRdata[$D][0x1B], 1, \@OA_label,       '1970'.$LO.'1B', 31,[6,6,5,5,5], 'Output Assign:')->grid(-columnspan => 2, %{$D{GridCfg}});
    StdSlider  ( \$sfr, $md, \$DRdata[$D][0x16], 1,   0, 127, $sp, 1, '1970'.$LO.'16', 'Output Level'                  )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$DRdata[$D][0x19], 1,   0, 127, $sp, 1, '1970'.$LO.'19', 'Delay Send'                    )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$DRdata[$D][0x1A], 1,   0, 127, $sp, 1, '1970'.$LO.'1A', 'Reverb Send'                   )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    GridYW1(\$sfr);
}

sub Addr {
    my($a,$LO,$HI)=@_;
    if ($a < 0x80) { return '1970'.$LO.(sprintf("%02X", $a)); }
    else           { return '1970'.$HI.(sprintf("%02X", ($a-0x80))); }
}

sub DR_WMT_Frame {
    my($D, $WMT, $LO, $HI, $frame)=@_;
    my $md=\%DR;
    my $a=(29*$WMT);
    my $sfr=StdFrame($frame, '', $conf{OSCbgc}, $conf{OSCfgc});
    PullDwnMenu( \$sfr, $md, \$DRdata[$D][0x27+$a], 4,  \@DRMwaves,      Addr(0x27+$a,$LO,$HI), 18, 'Wave (L/Mono): '  ,0)->grid(
    PullDwnMenu( \$sfr, $md, \$DRdata[$D][0x2B+$a], 4,  \@DRMwaves,      Addr(0x2B+$a,$LO,$HI), 18, 'Wave (R): '       ,0), %{$D{GridCfg}});
    my $xfr=SubFrame(\$sfr                                                                                               )->grid(-columnspan => 2, %{$D{GridCfg}});
    my @OSC_gain=('-6', '0', '+6', '+12');
    OptSelect  ( \$xfr, $md, \$DRdata[$D][0x2F+$a], 1, \@OSC_gain,       Addr(0x2F+$a,$LO,$HI), 0, 4, 'Gain [dB]: '    ,1)->grid(
    OnOffSwitch( \$xfr, $md, \$DRdata[$D][0x37+$a], 1,                   Addr(0x37+$a,$LO,$HI), '  Rnd Pan: '            ),
    OptSelect  ( \$xfr, $md, \$DRdata[$D][0x38+$a], 1,['OFF','ON','REV'],Addr(0x38+$a,$LO,$HI), 0, 4, '  Alt Pan: '    ,1), %{$D{GridCfg}});
    GridW1(\$xfr);
    my $vfr=SubFrame(\$sfr                                                                                               )->grid(
    StdSlider  ( \$sfr, $md, \$DRdata[$D][0x32+$a], 1,   0,  16, $sp, 1, Addr(0x32+$a,$LO,$HI), 'FXM Depth'              ), %{$D{SCFr_geo}});
    OnOffSwitch( \$vfr, $md, \$DRdata[$D][0x30+$a], 1,                   Addr(0x30+$a,$LO,$HI), 'FXM: '                  )->grid(
    OptSelect  ( \$vfr, $md, \$DRdata[$D][0x31+$a], 1, [1..4],           Addr(0x31+$a,$LO,$HI), 0, 3, 'Colour: '       ,1), %{$D{GridCfg}});
    GridW1(\$vfr);
    my $gp=' 'x$conf{pgap};
    StdSlider  ( \$sfr, $md, \$DRdata[$D][0x39+$a], 1,   0, 127, $sp, 1, Addr(0x39+$a,$LO,$HI), 'Level'                     )->grid(
    StdSlider  ( \$sfr, $md, \$DRdata[$D][0x36+$a], 1, -64,  63, $sn, 1, Addr(0x36+$a,$LO,$HI),'Pan'.$gp.'L<---0--->R','+64'), %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$DRdata[$D][0x34+$a], 1, -48,  48, $sn, 1, Addr(0x34+$a,$LO,$HI),'Coarse Tune'          ,'+64')->grid(
    StdSlider  ( \$sfr, $md, \$DRdata[$D][0x35+$a], 1, -50,  50, $sn, 1, Addr(0x35+$a,$LO,$HI),'Fine Tune'            ,'+64'), %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$DRdata[$D][0x3B+$a], 1,   1, 127, $sp, 1, Addr(0x3B+$a,$LO,$HI), 'Vel Range Upper'           )->grid(
    StdSlider  ( \$sfr, $md, \$DRdata[$D][0x3D+$a], 1,   0, 127, $sp, 1, Addr(0x3D+$a,$LO,$HI), 'Vel Fade Upper'            ), %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$DRdata[$D][0x3A+$a], 1,   1, 127, $sp, 1, Addr(0x3A+$a,$LO,$HI), 'Vel Range Lower'           )->grid(
    StdSlider  ( \$sfr, $md, \$DRdata[$D][0x3C+$a], 1,   0, 127, $sp, 1, Addr(0x3C+$a,$LO,$HI), 'Vel Fade Lower'            ), %{$D{SCFr_geo}});
    GridW1(\$sfr);
}

sub DR_PITCH_Frame {
    my($D, $LO, $HI, $frame)=@_;
    my $md=\%DR;
    my $sfr=StdFrame($frame, 'PITCH', $conf{OSCbgc}, $conf{OSCfgc});
    Spacer     ( \$sfr, '2'                                                                                             )->grid(-columnspan => 2, %{$D{GridCfg}});
    PullDwnMenu( \$sfr, $md, \$DRdata[$D][0x0F], 1, \@coarse_tune,    '1970'.$LO.'0F',  6, 'Coarse Tune: '           ,1 )->grid(-columnspan => 2, %{$D{GridCfg}});
    StdSlider  ( \$sfr, $md, \$DRdata[$D][0x10], 1, -50,  50, $sn, 1, '1970'.$LO.'10', 'Fine Tune'                ,'+64')->grid(-columnspan => 2, %{$D{SCFr_geo}});
    PullDwnMenu( \$sfr, $md, \$DRdata[$D][0x11], 1, \@rnd_pdepth,     '1970'.$LO.'11',  6, 'Random Pitch Depth: '    ,1 )->grid(-columnspan => 2, %{$D{GridCfg}});
    Spacer     ( \$sfr, '2'                                                                                             )->grid(-columnspan => 2, %{$D{GridCfg}});
    GridYW1(\$sfr);
}

sub DR_PITCHENV_Frame {
    my($D, $LO, $HI, $frame)=@_;
    my $md=\%DR;
    my $sfr=StdFrame($frame, '', $conf{OSCbgc}, $conf{OSCfgc});
    my $afr=SubFrame(\$sfr)->grid(%{$D{SCFr_geo}}, -row=>0, -column=>0);
    StdSlider  ( \$afr, $md, \$DRdata[$D][0x95], 1, -12,  12, $sn, 1, '1970'.$HI.'15', 'Env Depth'                ,'+64')->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$afr, $md, \$DRdata[$D][0x96], 1, -63,  63, $sn, 1, '1970'.$HI.'16', 'Env Vel Sensitivity'      ,'+64')->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$afr, $md, \$DRdata[$D][0x97], 1, -63,  63, $sn, 1, '1970'.$HI.'17', 'Env T1 Vel Sensitivity'   ,'+64')->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$afr, $md, \$DRdata[$D][0x98], 1, -63,  63, $sn, 1, '1970'.$HI.'18', 'Env T4 Vel Sensitivity'   ,'+64')->grid(%{$D{SCFr_geo}});
    GridYW1(\$afr);
    my $bfr=SubFrame(\$sfr)->grid(%{$D{SCFr_geo}},-row=>0, -column=>1);
    VertSlider ( \$bfr, $md, \$DRdata[$D][0x9D], 1, -63,  63, $sn, 1, '1970'.$HI.'1D', 'Lvl 0'                    ,'+64')->pack(%{$D{VSliConf}});
    VertSlider ( \$bfr, $md, \$DRdata[$D][0x9E], 1, -63,  63, $sn, 1, '1970'.$HI.'1E', 'Lvl 1'                    ,'+64')->pack(%{$D{VSliConf}});
    VertSlider ( \$bfr, $md, \$DRdata[$D][0x9F], 1, -63,  63, $sn, 1, '1970'.$HI.'1F', 'Lvl 2'                    ,'+64')->pack(%{$D{VSliConf}});
    VertSlider ( \$bfr, $md, \$DRdata[$D][0xA0], 1, -63,  63, $sn, 1, '1970'.$HI.'20', 'Lvl 3'                    ,'+64')->pack(%{$D{VSliConf}});
    VertSlider ( \$bfr, $md, \$DRdata[$D][0xA1], 1, -63,  63, $sn, 1, '1970'.$HI.'21', 'Lvl 4'                    ,'+64')->pack(%{$D{VSliConf}});
    my $cfr=SubFrame(\$sfr)->grid(%{$D{SCFr_geo}},-row=>0, -column=>2);
    StdSlider  ( \$cfr, $md, \$DRdata[$D][0x99], 1,   0, 127, $sp, 1, '1970'.$HI.'19', 'Env Time 1'                     )->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$cfr, $md, \$DRdata[$D][0x9A], 1,   0, 127, $sp, 1, '1970'.$HI.'1A', 'Env Time 2'                     )->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$cfr, $md, \$DRdata[$D][0x9B], 1,   0, 127, $sp, 1, '1970'.$HI.'1B', 'Env Time 3'                     )->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$cfr, $md, \$DRdata[$D][0x9C], 1,   0, 127, $sp, 1, '1970'.$HI.'1C', 'Env Time 4'                     )->grid(%{$D{SCFr_geo}});
    GridYW1(\$cfr);
    $sfr->gridColumnconfigure(1, -minsize=>250);
    GridW1(\$sfr);
}

sub DR_TVF_Frame {
    my($D, $LO, $HI, $frame)=@_;
    my $md=\%DR;
    my $sfr=StdFrame($frame, 'TVF', $conf{VCFbgc}, $conf{VCFfgc});
    my @filter_type=('OFF', 'LPF', 'BPF', 'HPF', 'PKG', 'LPF2', 'LPF3');
    OptSelect  ( \$sfr, $md, \$DRdata[$D][0xA2], 1,  \@filter_type,   '1970'.$HI.'22',  0, 5, 'Filter Type:'            )->grid(-columnspan => 2, %{$D{GridCfg}});
    StdSlider  ( \$sfr, $md, \$DRdata[$D][0xA3], 1,   0, 127, $sp, 1, '1970'.$HI.'23', 'Cutoff'                         )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$DRdata[$D][0xA6], 1,   0, 127, $sp, 1, '1970'.$HI.'26', 'Resonance'                      )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    OptSelect  ( \$sfr, $md, \$DRdata[$D][0xA4], 1, ['FIX', 1..7],    '1970'.$HI.'24',  0,[4,(3)x7], 'Cutoff Vel Curve:')->grid(-columnspan => 2, %{$D{GridCfg}});
    StdSlider  ( \$sfr, $md, \$DRdata[$D][0xA5], 1, -63,  63, $sn, 1, '1970'.$HI.'25', 'Cutoff Vel Sensitivity'   ,'+64')->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$DRdata[$D][0xA7], 1, -63,  63, $sn, 1, '1970'.$HI.'27', 'Resonance Vel Sensitivity','+64')->grid(-columnspan => 2, %{$D{SCFr_geo}});
    GridYW1(\$sfr);
}

sub DR_TVFENV_Frame {
    my($D, $LO, $HI, $frame)=@_;
    my $md=\%DR;
    my $sfr=StdFrame($frame, '', $conf{VCFbgc}, $conf{VCFfgc});
    my $afr=SubFrame(\$sfr)->grid(%{$D{SCFr_geo}}, -row=>0, -column=>0);
    StdSlider  ( \$afr, $md, \$DRdata[$D][0xA8], 1, -63,  63, $sn, 1, '1970'.$HI.'28', 'Env Depth'                ,'+64')->grid(%{$D{SCFr_geo}});
    OptSelect  ( \$afr, $md, \$DRdata[$D][0xA9], 1, ['FIX', 1..7],    '1970'.$HI.'29',  0,[4,(3)x7], 'Env Vel Curve:'   )->grid(%{$D{GridCfg}});
    StdSlider  ( \$afr, $md, \$DRdata[$D][0xAA], 1, -63,  63, $sn, 1, '1970'.$HI.'2A', 'Env Vel Sensitivity'      ,'+64')->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$afr, $md, \$DRdata[$D][0xAB], 1, -63,  63, $sn, 1, '1970'.$HI.'2B', 'Env T1 Vel Sensitivity'   ,'+64')->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$afr, $md, \$DRdata[$D][0xAC], 1, -63,  63, $sn, 1, '1970'.$HI.'2C', 'Env T4 Vel Sensitivity'   ,'+64')->grid(%{$D{SCFr_geo}});
    GridYW1(\$afr);
    my $bfr=SubFrame(\$sfr)->grid(%{$D{SCFr_geo}},-row=>0, -column=>1);
    VertSlider ( \$bfr, $md, \$DRdata[$D][0xB1], 1,   0, 127, $sp, 1, '1970'.$HI.'31', 'Lvl 0'                          )->pack(%{$D{VSliConf}});
    VertSlider ( \$bfr, $md, \$DRdata[$D][0xB2], 1,   0, 127, $sp, 1, '1970'.$HI.'32', 'Lvl 1'                          )->pack(%{$D{VSliConf}});
    VertSlider ( \$bfr, $md, \$DRdata[$D][0xB3], 1,   0, 127, $sp, 1, '1970'.$HI.'33', 'Lvl 2'                          )->pack(%{$D{VSliConf}});
    VertSlider ( \$bfr, $md, \$DRdata[$D][0xB4], 1,   0, 127, $sp, 1, '1970'.$HI.'34', 'Lvl 3'                          )->pack(%{$D{VSliConf}});
    VertSlider ( \$bfr, $md, \$DRdata[$D][0xB5], 1,   0, 127, $sp, 1, '1970'.$HI.'35', 'Lvl 4'                          )->pack(%{$D{VSliConf}});
    my $cfr=SubFrame(\$sfr)->grid(%{$D{SCFr_geo}},-row=>0, -column=>2);
    StdSlider  ( \$cfr, $md, \$DRdata[$D][0xAD], 1,   0, 127, $sp, 1, '1970'.$HI.'2D', 'Env Time 1'                     )->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$cfr, $md, \$DRdata[$D][0xAE], 1,   0, 127, $sp, 1, '1970'.$HI.'2E', 'Env Time 2'                     )->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$cfr, $md, \$DRdata[$D][0xAF], 1,   0, 127, $sp, 1, '1970'.$HI.'2F', 'Env Time 3'                     )->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$cfr, $md, \$DRdata[$D][0xB0], 1,   0, 127, $sp, 1, '1970'.$HI.'30', 'Env Time 4'                     )->grid(%{$D{SCFr_geo}});
    GridYW1(\$cfr);
    $sfr->gridColumnconfigure(1, -minsize=>250);
    GridW1(\$sfr);
}

sub DR_TVA_Frame {
    my($D, $LO, $HI, $frame)=@_;
    my $md=\%DR;
    my $sfr=StdFrame($frame, 'TVA', $conf{AMPbgc}, $conf{AMPfgc});
    StdSlider  ( \$sfr, $md, \$DRdata[$D][0x0E], 1,   0, 127, $sp, 1, '1970'.$LO.'0E', 'Level'                          )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$DRdata[$D][0xB7], 1, -63,  63, $sn, 1, '1970'.$HI.'37', 'Level Vel Sensitivity'    ,'+64')->grid(-columnspan => 2, %{$D{SCFr_geo}});
    OptSelect  ( \$sfr, $md, \$DRdata[$D][0xB6], 1, ['FIX', 1..7],    '1970'.$HI.'36',  0,[4,(3)x7], 'Level Vel Curve:' )->grid(-columnspan => 2, %{$D{GridCfg}});
    StdSlider  ( \$sfr, $md, \$DRdata[$D][0xC2], 1, -64,  63, $sn, 1, '1970'.$HI.'42', 'Relative Level'           ,'+64')->grid(-columnspan => 2, %{$D{SCFr_geo}});
    my $gp=' 'x$conf{pgap};
    StdSlider  ( \$sfr, $md, \$DRdata[$D][0x12], 1, -64,  63, $sn, 1, '1970'.$LO.'12','Pan'.$gp.'L<---0--->R'     ,'+64')->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$DRdata[$D][0x13], 1,   0,  63, $sp, 1, '1970'.$LO.'13', 'Random Pan Depth'               )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$DRdata[$D][0x14], 1, -63,  63, $sn, 1, '1970'.$LO.'14','Alt Pan Depth L<>R'        ,'+64')->grid(-columnspan => 2, %{$D{SCFr_geo}});
    GridYW1(\$sfr);
}

sub DR_TVAENV_Frame {
    my($D, $LO, $HI, $frame)=@_;
    my $md=\%DR;
    my $sfr=StdFrame($frame, '', $conf{AMPbgc}, $conf{AMPfgc});
    my $afr=SubFrame(\$sfr)->grid(%{$D{SCFr_geo}}, -row=>0, -column=>0);
    StdSlider  ( \$afr, $md, \$DRdata[$D][0xB8], 1, -63,  63, $sn, 1, '1970'.$HI.'38', 'Env T1 Vel Sensitivity'   ,'+64')->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$afr, $md, \$DRdata[$D][0xB9], 1, -63,  63, $sn, 1, '1970'.$HI.'39', 'Env T4 Vel Sensitivity'   ,'+64')->grid(%{$D{SCFr_geo}});
    GridYW1(\$afr);
    my $bfr=SubFrame(\$sfr)->grid(%{$D{SCFr_geo}},-row=>0, -column=>1);
    VertSlider ( \$bfr, $md, \$DRdata[$D][0xBE], 1,   0, 127, $sp, 1, '1970'.$HI.'3E', 'Lvl 1'                          )->pack(%{$D{VSliConf}});
    VertSlider ( \$bfr, $md, \$DRdata[$D][0xBF], 1,   0, 127, $sp, 1, '1970'.$HI.'3F', 'Lvl 2'                          )->pack(%{$D{VSliConf}});
    VertSlider ( \$bfr, $md, \$DRdata[$D][0xC0], 1,   0, 127, $sp, 1, '1970'.$HI.'40', 'Lvl 3'                          )->pack(%{$D{VSliConf}});
    my $cfr=SubFrame(\$sfr)->grid(%{$D{SCFr_geo}},-row=>0, -column=>2);
    StdSlider  ( \$cfr, $md, \$DRdata[$D][0xBA], 1,   0, 127, $sp, 1, '1970'.$HI.'3A', 'Env Time 1'                     )->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$cfr, $md, \$DRdata[$D][0xBB], 1,   0, 127, $sp, 1, '1970'.$HI.'3B', 'Env Time 2'                     )->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$cfr, $md, \$DRdata[$D][0xBC], 1,   0, 127, $sp, 1, '1970'.$HI.'3C', 'Env Time 3'                     )->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$cfr, $md, \$DRdata[$D][0xBD], 1,   0, 127, $sp, 1, '1970'.$HI.'3D', 'Env Time 4'                     )->grid(%{$D{SCFr_geo}});
    GridYW1(\$cfr);
    $sfr->gridColumnconfigure(1, -minsize=>250);
    GridW1(\$sfr);
}

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Effects Editor Frames

sub FX_FX1_Frame {
    my($frame)=@_;
    my $md=\%FX;
    my $sfr=StdFrame($frame, 'Effect 1', $conf{OSCbgc}, $conf{OSCfgc});
    PullDwnMenu( \$sfr, $md, \$FXdata[0][0x00], 1, \@fx1_type,       '18000200',  16, 'Effect Type: '            ,1)->grid(%{$D{GridCfg}});
    StdSlider  ( \$sfr, $md, \$FXdata[0][0x01], 1,   0, 127, $sp, 1, '18000201', 'Effect 1 Level'                  )->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$FXdata[0][0x02], 1,   0, 127, $sp, 1, '18000202', 'Delay send level'                )->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$FXdata[0][0x03], 1,   0, 127, $sp, 1, '18000203', 'Reverb send level'               )->grid(%{$D{SCFr_geo}});
    OptSelect  ( \$sfr, $md, \$FXdata[0][0x04], 1,   ['DIR','EFX2'], '18000204',  0, 6, 'Output Assign: '        ,1)->grid(%{$D{GridCfg}});
    GridYW1(\$sfr);
}

sub FX_FX2_Frame {
    my($frame)=@_;
    my $md=\%FX;
    my $sfr=StdFrame($frame, 'Effect 2', $conf{LFObgc}, $conf{LFOfgc});
    PullDwnMenu( \$sfr, $md, \$FXdata[1][0x00], 1, \@fx2_type,       '18000400',  16, 'Effect Type: '            ,1)->grid(%{$D{GridCfg}});
    StdSlider  ( \$sfr, $md, \$FXdata[1][0x01], 1,   0, 127, $sp, 1, '18000401', 'Effect 2 Level'                  )->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$FXdata[1][0x02], 1,   0, 127, $sp, 1, '18000402', 'Delay send level'                )->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$FXdata[1][0x03], 1,   0, 127, $sp, 1, '18000403', 'Reverb send level'               )->grid(%{$D{SCFr_geo}});
    Spacer     ( \$sfr, '16'                                                                                       )->grid(%{$D{GridCfg}});
    GridYW1(\$sfr);
}

sub FX_DEL_Frame {
    my($frame)=@_;
    my $md=\%FX;
    my $sfr=StdFrame($frame, 'Delay', $conf{VCFbgc}, $conf{VCFfgc});
    OnOffSwitch( \$sfr, $md, \$FXdata[2][0x00], 1,                   '18000600', '', '  on  '                      )->grid(
    OptSelect  ( \$sfr, $md, \$FXdata[2][0x04], 4, ['SINGLE','PAN'], '18000604',  0, [8,5], '  Type: ' ,1 ,'+32768'), %{$D{GridCfg}});
    my $cfr=SubFrame(\$sfr)->grid(%{$D{GridCfg}}, -columnspan => 2);
    OptSelect  ( \$cfr, $md, \$FXdata[2][0x08], 4, ['Time','Note'],  '18000608',  0, 6,''              ,1 ,'+32768')->grid(
    PullDwnMenu( \$cfr, $md, \$FXdata[2][0x10], 4, \@dly_notes,      '18000610',  5, '  Note: '        ,1 ,'+32768'), %{$D{GridCfg}});
    GridXW1(\$cfr);
    StdSlider  ( \$sfr, $md, \$FXdata[2][0x0C], 4,   0,2600, $sn, 1, '1800060C', 'Time [ms]'              ,'+32768')->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$FXdata[2][0x14], 4,   0, 100, $sp, 1, '18000614', 'Tap Time [%]'           ,'+32768')->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$FXdata[2][0x18], 4,   0,  98, $sp, 1, '18000618', 'Feedback [%]'           ,'+32768')->grid(-columnspan => 2, %{$D{SCFr_geo}});
    PullDwnMenu( \$sfr, $md, \$FXdata[2][0x1C], 4, \@hf_damp,        '1800061C',  8, 'HF Damp: '       ,1 ,'+32768')->grid(-columnspan => 2, %{$D{GridCfg}});
    StdSlider  ( \$sfr, $md, \$FXdata[2][0x03], 1,   0, 127, $sp, 1, '18000603', 'Reverb send level'               )->grid(-columnspan => 2, %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$FXdata[2][0x20], 4,   0, 127, $sp, 1, '18000620', 'Level'                  ,'+32768')->grid(-columnspan => 2, %{$D{SCFr_geo}});
    GridYW1(\$sfr);
}

sub FX_REV_Frame {
    my($frame)=@_;
    my $md=\%FX;
    my $sfr=StdFrame($frame, 'Reverb', $conf{AMPbgc}, $conf{AMPfgc});
    OnOffSwitch( \$sfr, $md, \$FXdata[3][0x00], 1,                   '18000800', '', '  on  '                      )->grid(
    PullDwnMenu( \$sfr, $md, \$FXdata[3][0x03], 4, \@rev_type,       '18000803',  8, 'Type: '          ,1 ,'+32768'), %{$D{GridCfg}});
    StdSlider  ( \$sfr, $md, \$FXdata[3][0x07], 4,   0, 127, $sp, 1, '18000807', 'Time'                   ,'+32768')->grid(-columnspan => 2, %{$D{SCFr_geo}});
    PullDwnMenu( \$sfr, $md, \$FXdata[3][0x0B], 4, \@hf_damp,        '1800080B',  8, 'HF Damp: '       ,1 ,'+32768')->grid(-columnspan => 2, %{$D{GridCfg}});
    StdSlider  ( \$sfr, $md, \$FXdata[3][0x0F], 4,   0, 127, $sp, 1, '1800080F', 'Level'                  ,'+32768')->grid(-columnspan => 2, %{$D{SCFr_geo}});
    GridYW1(\$sfr);
}

#----FX1----
sub FX12_Through {
    my($frame)=@_;
}

sub FX1_DistFuzz_Frame {
    my($frame)=@_;
    my $md=\%FX;
    my $sfr=StdFrame($frame, substr($fx1_type[$FXdata[0][0x00]],4), $conf{COMbgc}, $conf{COMfgc});
    OptSelect  ( \$sfr, $md, \$FXdata[0][0x19], 4,           [0..5], '18000219',  0, 4, 'Type: '       ,1 ,'+32768')->grid(%{$D{GridCfg}});
    StdSlider  ( \$sfr, $md, \$FXdata[0][0x15], 4,   0, 127, $sp, 1, '18000215', 'Drive'                  ,'+32768')->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$FXdata[0][0x1D], 4,   0, 127, $sp, 1, '1800021D', 'Presence'               ,'+32768')->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$FXdata[0][0x11], 4,   0, 127, $sp, 1, '18000211', 'Level'                  ,'+32768')->grid(%{$D{SCFr_geo}});
    GridYW1(\$sfr);
}

sub FX1_Compressor_Frame {
    my($frame)=@_;
    my $md=\%FX;
    my $sfr=StdFrame($frame, 'Compressor', $conf{COMbgc}, $conf{COMfgc});
    PullDwnMenu( \$sfr, $md, \$FXdata[0][0x15], 4,   \@ratio,        '18000215', 6, 'Ratio: '          ,1 ,'+32768')->grid(%{$D{GridCfg}});
    StdSlider  ( \$sfr, $md, \$FXdata[0][0x11], 4,   0, 127, $sp, 1, '18000211', 'Threshold'              ,'+32768')->grid(%{$D{SCFr_geo}});
    my $dfr=SubFrame(\$sfr)->grid(%{$D{GridCfg}});
    PullDwnMenu( \$dfr, $md, \$FXdata[0][0x19], 4,   \@comp_att,     '18000219', 4, 'Att + Rel [ms]: ' ,1 ,'+32768')->grid(
    PullDwnMenu( \$dfr, $md, \$FXdata[0][0x1D], 4,   \@comp_rel,     '1800021D', 5, ' '                ,1 ,'+32768'),%{$D{GridCfg}});
    GridXW1(\$dfr);
    StdSlider  ( \$sfr, $md, \$FXdata[0][0x21], 4,   0, 127, $sp, 1, '18000221', 'Level'                  ,'+32768')->grid(%{$D{SCFr_geo}});
    my $cfr=SubFrame(\$sfr)->grid(%{$D{GridCfg}});
    OnOffSwitch( \$cfr, $md, \$FXdata[0][0x25], 4,                   '18000225', 'Side Chain', '  on  ',1 ,'+32768')->grid(
    OnOffSwitch( \$cfr, $md, \$FXdata[0][0x39], 4,                   '18000239', ' Side Sync', '  on  ',1 ,'+32768'),%{$D{GridCfg}});
    GridXW1(\$cfr);
    StdSlider  ( \$sfr, $md, \$FXdata[0][0x29], 4,   0, 127, $sp, 1, '18000229', 'Side Level'             ,'+32768')->grid(%{$D{SCFr_geo}});
    PullDwnMenu( \$sfr, $md, \$FXdata[0][0x2D], 4,   \@coarse_tune,  '1800022D', 5, 'Side Note: '      ,1 ,'+32768')->grid(%{$D{GridCfg}});
    StdSlider  ( \$sfr, $md, \$FXdata[0][0x31], 4,  60,1000, $sp, 1, '18000231', 'Side Time [ms]'         ,'+32768')->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$FXdata[0][0x35], 4,   0, 127, $sp, 1, '18000235', 'Side Release'           ,'+32768')->grid(%{$D{SCFr_geo}});
    GridYW1(\$sfr);
}

sub FX1_BitCrusher_Frame {
    my($frame)=@_;
    my $md=\%FX;
    my $sfr=StdFrame($frame, 'Bit Crusher', $conf{COMbgc}, $conf{COMfgc});
    StdSlider  ( \$sfr, $md, \$FXdata[0][0x15], 4,   0, 127, $sp, 1, '18000215', 'Rate'                   ,'+32768')->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$FXdata[0][0x19], 4,   0, 127, $sp, 1, '18000219', 'Bit'                    ,'+32768')->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$FXdata[0][0x1D], 4,   0, 127, $sp, 1, '1800021D', 'Filter'                 ,'+32768')->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$FXdata[0][0x11], 4,   0, 127, $sp, 1, '18000211', 'Level'                  ,'+32768')->grid(%{$D{SCFr_geo}});
    GridYW1(\$sfr);
}

#----FX2----
sub FX2_Flanger_Frame {
    my($frame)=@_;
    my $md=\%FX;
    my $sfr=StdFrame($frame, 'Flanger', $conf{COMbgc}, $conf{COMfgc});
    my $cfr=SubFrame(\$sfr)->grid(%{$D{GridCfg}}, -columnspan => 2);
    OptSelect  ( \$cfr, $md, \$FXdata[1][0x11], 4, ['Rate','Note'],  '18000411',  0, 6,''              ,1 ,'+32768')->grid(
    PullDwnMenu( \$cfr, $md, \$FXdata[1][0x19], 4, \@dly_notes,      '18000419',  5, '  Note: '        ,1 ,'+32768'), %{$D{GridCfg}});
    GridXW1(\$cfr);
    StdSlider  ( \$sfr, $md, \$FXdata[1][0x15], 4,   0, 127, $sp, 1, '18000415', 'Rate'                   ,'+32768')->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$FXdata[1][0x1D], 4,   0, 127, $sp, 1, '1800041D', 'Depth'                  ,'+32768')->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$FXdata[1][0x21], 4,   0, 127, $sp, 1, '18000421', 'Feedback (0=Chorus)'    ,'+32768')->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$FXdata[1][0x25], 4,   0, 127, $sp, 1, '18000425', 'Manual'                 ,'+32768')->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$FXdata[1][0x29], 4,   0, 100, $sp, 1, '18000429', 'Balance [dry->wet]'     ,'+32768')->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$FXdata[1][0x2D], 4,   0, 127, $sp, 1, '1800042D', 'Level'                  ,'+32768')->grid(%{$D{SCFr_geo}});
    GridYW1(\$sfr);
}

sub FX2_Phaser_Frame {
    my($frame)=@_;
    my $md=\%FX;
    my $sfr=StdFrame($frame, 'Phaser', $conf{COMbgc}, $conf{COMfgc});
    my $cfr=SubFrame(\$sfr)->grid(%{$D{GridCfg}}, -columnspan => 2);
    OptSelect  ( \$cfr, $md, \$FXdata[1][0x11], 4, ['Rate','Note'],  '18000411',  0, 6,''              ,1 ,'+32768')->grid(
    PullDwnMenu( \$cfr, $md, \$FXdata[1][0x19], 4, \@dly_notes,      '18000419',  5, '  Note: '        ,1 ,'+32768'), %{$D{GridCfg}});
    GridXW1(\$cfr);
    StdSlider  ( \$sfr, $md, \$FXdata[1][0x15], 4,   0, 127, $sp, 1, '18000415', 'Rate'                   ,'+32768')->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$FXdata[1][0x1D], 4,   0, 127, $sp, 1, '1800041D', 'Depth'                  ,'+32768')->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$FXdata[1][0x21], 4,   0, 127, $sp, 1, '18000421', 'Resonance'              ,'+32768')->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$FXdata[1][0x25], 4,   0, 127, $sp, 1, '18000425', 'Manual'                 ,'+32768')->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$FXdata[1][0x29], 4,   0, 127, $sp, 1, '18000429', 'Level'                  ,'+32768')->grid(%{$D{SCFr_geo}});
    GridYW1(\$sfr);
}

sub FX2_RingMod_Frame {
    my($frame)=@_;
    my $md=\%FX;
    my $sfr=StdFrame($frame, 'Ring Mod', $conf{COMbgc}, $conf{COMfgc});
    StdSlider  ( \$sfr, $md, \$FXdata[1][0x11], 4,   0, 127, $sp, 1, '18000411', 'Frequency'              ,'+32768')->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$FXdata[1][0x15], 4,   0, 127, $sp, 1, '18000415', 'Sens'                   ,'+32768')->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$FXdata[1][0x19], 4,   0, 100, $sp, 1, '18000419', 'Balance [dry->wet]'     ,'+32768')->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$FXdata[1][0x1D], 4,   0, 127, $sp, 1, '1800041D', 'Level'                  ,'+32768')->grid(%{$D{SCFr_geo}});
    GridYW1(\$sfr);
}

sub FX2_Slicer_Frame {
    my($frame)=@_;
    my $md=\%FX;
    my $sfr=StdFrame($frame, 'Slicer', $conf{COMbgc}, $conf{COMfgc});
    StdSlider  ( \$sfr, $md, \$FXdata[1][0x11], 4,   0,  15, $sp, 1, '18000411', 'Timing Pattern'         ,'+32768')->grid(%{$D{SCFr_geo}});
    PullDwnMenu( \$sfr, $md, \$FXdata[1][0x15], 4, \@dly_notes,      '18000415',  5, 'Rate [Note]: '   ,1 ,'+32768')->grid(%{$D{GridCfg}});
    StdSlider  ( \$sfr, $md, \$FXdata[1][0x19], 4,   0, 127, $sp, 1, '18000419', 'Attack'                 ,'+32768')->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$FXdata[1][0x1D], 4,   0, 127, $sp, 1, '1800041D', 'Trigger Level'          ,'+32768')->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$FXdata[1][0x21], 4,   0, 127, $sp, 1, '18000421', 'Level'                  ,'+32768')->grid(%{$D{SCFr_geo}});
    GridYW1(\$sfr);
}

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Arpeggio Editor Frame

sub ARP_Frame {
    my($frame)=@_;
    my $md=\%ARP;
    my $sfr=StdFrame($frame, 'Arpeggio', $conf{LFObgc}, $conf{LFOfgc});
    my $cfr=SubFrame(\$sfr)->grid(%{$D{GridCfg}}, -columnspan => 2);
    OnOffSwitch( \$cfr, $md, \$ARPdata[0x03], 1,                   '18004003', '', '  on  '                             )->grid(
    PullDwnMenu( \$cfr, $md, \$ARPdata[0x05], 1, \@arp_type,       '18004005',  19, 'Arpeggio Style: '               ,1 ), %{$D{GridCfg}});
    GridXW1(\$cfr);
    OptSelect  ( \$sfr, $md, \$ARPdata[0x01], 1, \@arp_grid,       '18004001',  0, [5,5,6,6,5,5,7,7,6],'Grid:'       ,0 )->grid(-columnspan => 2, %{$D{GridCfg}});
    OptSelect  ( \$sfr, $md, \$ARPdata[0x02], 1, \@arp_duration,   '18004002',  0, [5,5,5,5,5,5,5,6,6,6],'Duration:' ,0 )->grid(-columnspan => 2, %{$D{GridCfg}});
    Spacer     ( \$sfr, '5'                                                                                             )->grid(-columnspan => 2, %{$D{GridCfg}});
    PullDwnMenu( \$sfr, $md, \$ARPdata[0x06], 1, \@arp_motif,      '18004006',  15, 'Motif: '                        ,1 )->grid(
    StdSlider  ( \$sfr, $md, \$ARPdata[0x0A], 1,   0, 127, $sp, 1, '1800400A', 'Velocity (0=Real)'                      ), %{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$ARPdata[0x07], 1,  -3,   3, $sp, 1, '18004007', 'Oct Range'                       ,'+64' )->grid(
    StdSlider  ( \$sfr, $md, \$ARPdata[0x09], 1,   0, 100, $sp, 1, '18004009', 'Accent'                                 ), %{$D{SCFr_geo}});
    Spacer     ( \$sfr, '1'                                                                                             )->grid(-columnspan => 2, %{$D{GridCfg}});
    GridW1(\$sfr);
}

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Vocal Effects Editor Frame
sub VFX_Frame {
    my($frame)=@_;
    my $md=\%VFX;
    my $sfr=StdFrame($frame, 'Common', $conf{OSCbgc}, $conf{OSCfgc});
    my @OA_label=('EFX1', 'EFX2', 'DLY', 'REV', 'DIR');
    OptSelect  ( \$sfr, $md, \$VFXdata[0x04], 1, \@OA_label,       '18000104', 31,[6,6,5,5,5], 'Output Assign:')->grid(%{$D{GridCfg}});
    StdSlider  ( \$sfr, $md, \$VFXdata[0x00], 1,   0, 127, $sp, 1, '18000100', 'Level'                         )->grid(%{$D{SCFr_geo}});
    my $gp=' 'x$conf{pgap};
    StdSlider  ( \$sfr, $md, \$VFXdata[0x01], 1, -64,  63, $sn, 1, '18000101', 'Pan'.$gp.'L<---0--->R','+64'   )->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$VFXdata[0x02], 1,   0, 127, $sp, 1, '18000102', 'Delay send level'              )->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$VFXdata[0x03], 1,   0, 127, $sp, 1, '18000103', 'Reverb send level'             )->grid(%{$D{SCFr_geo}});

    GridW1(\$sfr);
}

sub VC_Frame {
    my($frame)=@_;
    my $md=\%VFX;
    my $sfr=StdFrame($frame, 'Vocoder', $conf{LFObgc}, $conf{LFOfgc});
    OnOffSwitch( \$sfr, $md, \$VFXdata[0x0D], 1,                   '1800010D', '', '  on  '                             )->grid(%{$D{GridCfg}});
    my @VCenv_label=('Sharp', 'Soft', 'Long');
    OptSelect  ( \$sfr, $md, \$VFXdata[0x0E], 1, \@VCenv_label,    '1800010E', 31,[6,6,6],                'Envelope: ',1)->grid(%{$D{GridCfg}});
    StdSlider  ( \$sfr, $md, \$VFXdata[0x10], 1,   0, 127, $sp, 1, '18000110', 'Mic Sens'                               )->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$VFXdata[0x11], 1,   0, 127, $sp, 1, '18000111', 'Synth Level'                            )->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$VFXdata[0x12], 1,   0, 127, $sp, 1, '18000112', 'Mic Mix Level'                          )->grid(%{$D{SCFr_geo}});
    PullDwnMenu( \$sfr, $md, \$VFXdata[0x13], 1, \@vc_hpf,         '18000113', 10, 'Mic HPF: '                        ,1)->grid(%{$D{GridCfg}});
    GridW1(\$sfr);
}

sub AP_Frame {
    my($frame)=@_;
    my $md=\%VFX;
    my $sfr=StdFrame($frame, 'Auto Pitch', $conf{VCFbgc}, $conf{VCFfgc});
    OnOffSwitch( \$sfr, $md, \$VFXdata[0x05], 1,                   '18000105', '', '  on  '                             )->grid(%{$D{GridCfg}});
    my @TYPE_label=('Soft', 'Hard', 'Electric1', 'Electric2');
    OptSelect  ( \$sfr, $md, \$VFXdata[0x06], 1, \@TYPE_label,     '18000106', 31,[6,6,9,9],                     'Type:')->grid(%{$D{GridCfg}});
    my @SCALE_label=('Chromatic', 'Maj(Min)');
    OptSelect  ( \$sfr, $md, \$VFXdata[0x07], 1, \@SCALE_label,    '18000107', 31,[11,10],                   'Scale: ',1)->grid(%{$D{GridCfg}});
    PullDwnMenu( \$sfr, $md, \$VFXdata[0x08], 1, \@ap_key,         '18000108',  5, 'Key: '                            ,1)->grid(%{$D{GridCfg}});
    StdSlider  ( \$sfr, $md, \$VFXdata[0x0A], 1, -10,  10, $sn, 1, '1800010A', 'Gender (m <-> f)'                 ,'+10')->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$VFXdata[0x0B], 1,  -1,   1, $sn, 1, '1800010B', 'Octave'                           ,'+1' )->grid(%{$D{SCFr_geo}});
    StdSlider  ( \$sfr, $md, \$VFXdata[0x0C], 1,   0, 100, $sp, 1, '1800010C', 'Balance (dry <-> wet)'                  )->grid(%{$D{SCFr_geo}});
    GridW1(\$sfr);
}

