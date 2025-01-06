package LTNstyle;

use warnings;
use strict;

use Exporter;
our @ISA=qw(Exporter);
our @EXPORT=qw(
  SetDefaults
  SetStyle
  SetElemDefaults
);

sub SetDefaults {
    my %defaults;
    # general background colour
    $defaults{bgcolor}   = '#3C3C3C';
    # dividing bars colour and width
    $defaults{divcol}    = '#232323';
    $defaults{divwidth}  = 1;
    # vertical distance between individual controllers
    $defaults{pady}      = 5;
    # general font color
    $defaults{fontcolor} = '#FFFFFF';
    # general fonts standard, small, midicfg, patchname
    $defaults{stdfont}   = 'Sans 10';
    $defaults{smlfont}   = 'Sans 8';
    $defaults{smlbldft}  = 'Sans 8 bold';
    $defaults{midicfgfnt}= 'Sans 9';
    $defaults{patnamefnt}= 'Fixed 10';
    # button colours and fonts
    $defaults{btncol}    = '#303030';
    $defaults{btnfcol}   = $defaults{fontcolor};
    $defaults{btnselfg}  = '#2897B7';
    $defaults{btnenafg}  = '#2897B7';
    $defaults{btndisfg}  = '#545454';
    $defaults{btnfont}   = 'Sans 9 bold';
    $defaults{btnpadx}   = '0.050i';
    $defaults{btnpady}   = '0.020i';
    $defaults{RadioBfnt} = $defaults{smlfont};
    # Parts Buttons in control Panel
    $defaults{DPtbtncol} = 'red';
    $defaults{APtbtncol} = '#2897B7';
    $defaults{Ptbtnpadx} = '0.120i';
    $defaults{Ptbtnpady} = '0.070i';
    # title strips default background and font colour and font
    $defaults{Titlebg}   = '#888888';
    $defaults{Titlefg}   = $defaults{fontcolor};
    $defaults{Titlefnt}  = 'Sans 9 bold';
    # other title strips background and font colours
    $defaults{OSCbgc}    = '#FFA200';
    $defaults{OSCfgc}    = $defaults{fontcolor};
    $defaults{VCFbgc}    = '#E83939';
    $defaults{VCFfgc}    = $defaults{fontcolor};
    $defaults{AMPbgc}    = '#AF7200';
    $defaults{AMPfgc}    = $defaults{fontcolor};
    $defaults{COMbgc}    = '#3A464E';
    $defaults{COMfgc}    = $defaults{fontcolor};
    $defaults{CFGbgc}    = '#3C3C3C';
    $defaults{CFGfgc}    = '#EFEFEF';
    $defaults{LFObgc}    = '#E86333';
    $defaults{LFOfgc}    = $defaults{fontcolor};
    # slider handle colour, through colour, label and label2 font
    $defaults{sliderbg}  = '#2897B7';
    $defaults{trucol}    = '#545454';
    $defaults{sllab2bg}  = $defaults{btncol};
    $defaults{sllab2fg}  = $defaults{btnfcol};
    $defaults{sllabfnt}  = 'Sans 7'; if ($::WINDOWS) { $defaults{sllabfnt}='Tahoma 7'; }
    $defaults{sllab2fnt} = 'Sans 9 bold';
    # BEntry colours
    $defaults{entryfg}   = $defaults{btnfcol};
    $defaults{entrybg}   = $defaults{btncol};
    # Slider length
    $defaults{Hsldrlen}  = '1.60i';
    $defaults{Vsldrlen}  = '1.15i';
    $defaults{sldrwidth} = '0.10i';
    # Listbox height
    $defaults{lstheight} = 25;
    # Pan gap
    $defaults{pgap} = 9; if ($::WINDOWS) { $defaults{pgap} = 12; }
    # 'flat' or '3D' style
    $defaults{style}     = 'flat';
    # defaults for 'flat' style
    $defaults{btnstyle}  = 'flat';
    $defaults{snkstyle}  = 'flat';
    $defaults{frmstyle}  = 'flat';
    $defaults{frmbdwidth}= 0;
    $defaults{BEbdwidth} = 2;
    $defaults{bdwidth}   = 0;

    return %defaults;
}

# Style settings
sub SetStyle {
    my($win, $conf)=@_;

    # default font
    $win->optionAdd('*font', $$conf{stdfont});
    # for better looking menus
    $win->optionAdd('*Menu.activeBorderWidth', 1, 99);
    $win->optionAdd('*Menu.borderWidth', 1, 99);
    $win->optionAdd('*Menubutton.borderWidth', 1, 99);
    $win->optionAdd('*Optionmenu.borderWidth', 1, 99);
    # set default listbox properties
    $win->optionAdd('*Listbox.borderWidth', 3, 99);
    $win->optionAdd('*Listbox.selectBorderWidth', 0, 99);
    $win->optionAdd('*Listbox.highlightThickness', 0, 99);
    $win->optionAdd('*Listbox.Relief', 'flat', 99);
    $win->optionAdd('*Listbox.Width', 0, 99);
    # set default entry properties
    $win->optionAdd('*Entry.borderWidth', 1, 99);
    $win->optionAdd('*Entry.highlightThickness', 0, 99);
    $win->optionAdd('*Entry.disabledForeground', $$conf{entryfg},99);
    $win->optionAdd('*Entry.disabledBackground', $$conf{entrybg},99);
    # set default scrollbar properties
    $win->optionAdd('*Scrollbar.borderWidth', 1, 99);
    $win->optionAdd('*Scrollbar.highlightThickness', 0, 99);
    if ($::LINUX) {$win->optionAdd('*Scrollbar.Width', 10, 99);}
    # set default button properties
    $win->optionAdd('*Button.borderWidth', 1, 99);
    $win->optionAdd('*Button.highlightThickness', 0, 99);
    $win->optionAdd('*Checkbutton.borderWidth', 1, 99);
    # set default canvas properties
    $win->optionAdd('*Canvas.highlightThickness', 0, 99);
    $win->optionAdd('*Balloon.Background', '#FFFF94', 99);
}

sub SetElemDefaults {
    my($conf)=@_;

    my %ElDef;

    # Button defaults
    $ElDef{Btn_defaults}={
        -background         => $$conf{btncol},
        -activebackground   => $$conf{btncol},
        -foreground         => $$conf{btnenafg},
        -activeforeground   => $$conf{btnenafg},
        -disabledforeground => $$conf{btndisfg},
        -highlightthickness => 0,
        -borderwidth        => $$conf{bdwidth},
        -anchor             => 'center',
        -justify            => 'center',
        -relief             => $$conf{btnstyle},
        -font               => $$conf{btnfont},
        -padx               => $$conf{btnpadx},
        -pady               => $$conf{btnpady}
    };
    # Part Button defaults
    $ElDef{PtBtn_defaults}={
        -background         => $$conf{btncol},
        -activebackground   => $$conf{btncol},
        -foreground         => $$conf{DPtbtncol},
        -activeforeground   => $$conf{DPtbtncol},
        -disabledforeground => $$conf{btndisfg},
        -highlightthickness => 0,
        -borderwidth        => $$conf{bdwidth},
        -anchor             => 'center',
        -justify            => 'center',
        -relief             => $$conf{btnstyle},
        -font               => $$conf{btnfont},
        -padx               => $$conf{Ptbtnpadx},
        -pady               => $$conf{Ptbtnpady}
    };
    # Slider defaults
    $ElDef{Scale_defaults}={
        -width              => $$conf{sldrwidth},
        -length             => $$conf{Hsldrlen},
        -sliderlength       => '0.20i',
        -borderwidth        => $$conf{bdwidth},
        -sliderrelief       => $$conf{btnstyle},
        -background         => $$conf{sliderbg},
        -activebackground   => $$conf{sliderbg},
        -foreground         => $$conf{trucol},
        -troughcolor        => $$conf{trucol},
        -highlightthickness => 0, #'0.01i',
#        -highlightbackground=> 'black',
#        -highlightcolor     => 'black',
        -showvalue          => 0,
        -cursor             => 'hand2',
        -orient             => 'horizontal'
    };
    # Text label above Slider
    $ElDef{SCLab1_geo}={
        -padx               => 2,
        -sticky             => 'nsew'
    };
    $ElDef{SCLab1_defaults}={
        -justify            => 'left',
        -anchor             => 'w',
        -borderwidth        => 0,
        -font               => $$conf{sllabfnt},
        -background         => $$conf{bgcolor},
        -foreground         => $$conf{fontcolor}
    };
    # Label right of Slider with numeric value
    $ElDef{SCLab2_geo}={
        -padx               => 2,
        -pady               => 0,
        -sticky             => 'ns'
    };
    $ElDef{SCLab2_defaults}={
        -width              => 4,
        -font               => $$conf{sllab2fnt},
        -highlightthickness => 0,
        -borderwidth        => $$conf{bdwidth},
        -background         => $$conf{sllab2bg},
        -foreground         => $$conf{sllab2fg},
        -relief             => $$conf{snkstyle}
    };
    # Slider scale geometry
    $ElDef{Scale_geo}={
        -padx               => 2
    };
    # common Grid element config
    $ElDef{GridCfg}={
        -sticky             => 'nsew',
        -pady               => $$conf{pady}
    };
    # Slider outer frame Grid config
    $ElDef{SCFr_geo}={
        %{$ElDef{GridCfg}},
        -ipadx              => 4
    };
    # Vertical Slider Pack config
    $ElDef{VSliConf}={
        -side               => 'left',
        -expand             =>  1,
        -fill               => 'x'
    };
    # Label defaults
    $ElDef{Label_defaults}={
        -font               => $$conf{smlfont},
        -background         => $$conf{bgcolor},
        -foreground         => $$conf{fontcolor}
    };
    # Checkbutton (On/Off Button) defaults
    $ElDef{Chkbtn_defaults}={
        -borderwidth        => $$conf{bdwidth},
        -relief             => $$conf{snkstyle},
        -offrelief          => $$conf{btnstyle},
        -background         => $$conf{btncol},
        -activebackground   => $$conf{btncol},
        -foreground         => $$conf{btnfcol},
        -activeforeground   => $$conf{btnfcol},
        -highlightthickness => 0,
        -indicatoron        => 0,
        -selectcolor        => $$conf{btnselfg},
        -font               => $$conf{smlfont},
        -text               => ' on ',
        -padx               => '0.040i',
        -pady               => '0.020i'
    };
    # BrowseEntry defaults
    $ElDef{BEntry_defaults}={
        -state              => 'readonly',
        -font               => $$conf{smlfont},
        -style              => 'MSWin32',
        -relief             => $$conf{snkstyle},
        -highlightthickness => 0,
        -borderwidth        => $$conf{BEbdwidth},
        -background         => $$conf{btncol},
        -listheight         => $$conf{lstheight}
    };
    # BrowseEntry pulldown choices defaults
    $ElDef{choices_defaults}={
        -borderwidth        => $$conf{bdwidth},
        -relief             => 'raised',
        -padx               => 1,
        -pady               => 1
    };
    # BrowseEntry arrow button defaults
    $ElDef{arrow_defaults}={
        -borderwidth        => $$conf{bdwidth},
        -relief             => $$conf{btnstyle},
        -highlightthickness => 0,
        -background         => $$conf{btncol},
        -activebackground   => $$conf{btncol},
        -foreground         => $$conf{btnenafg},
        -activeforeground   => $$conf{btnenafg},
        -disabledforeground => $$conf{btndisfg},
        -width              => '0.13i',
        -height             => '0.19i',
        -bitmap             => 'bm:darrow'
    };
    # Text Entry defaults (also for Spinbox)
    $ElDef{Entry_defaults}={
        -borderwidth        => $$conf{bdwidth},
        -relief             => $$conf{snkstyle},
        -foreground         => $$conf{entryfg},
        -background         => $$conf{entrybg},
        -highlightthickness => 0,
        -insertbackground   => $$conf{entryfg},
        -insertofftime      => 500,
        -insertontime       => 500,
        -insertwidth        => 1,
        -selectborderwidth  => 0
    };
    # Spinbox defaults
    $ElDef{Spinbox_defaults}={
        %{$ElDef{Entry_defaults}},
        -buttonbackground   => $$conf{btncol},
        -readonlybackground => $$conf{entrybg},
        -disabledbackground => $$conf{entrybg},
        -disabledforeground => $$conf{btndisfg},
        -buttonuprelief     => $$conf{btnstyle},
        -buttondownrelief   => $$conf{btnstyle},
        -font               => $$conf{midicfgfnt},
        -justify            => 'center'
    };
    # Radiobutton defaults (also for Drums Notebook Tabs)
    $ElDef{RadioB_defaults}={
        -font               => $$conf{RadioBfnt},
        -indicatoron        => 0,
        -borderwidth        => $$conf{bdwidth},
        -highlightthickness => 0,
        -padx               => '0.010i',
        -pady               => '0.020i',
        -selectcolor        => $$conf{btnselfg},
        -foreground         => $$conf{btnfcol},
        -background         => $$conf{btncol}
    };
    # Control Panel Top Menu Bar defaults
    $ElDef{MBar_defaults}={
        -borderwidth        => 1,
        -relief             => 'raised'
    };
    # Digital Synth Partials Tabs defaults
    $ElDef{NB_defaults}={
        -borderwidth        => $$conf{bdwidth},
        -ipadx              => 0,
        -ipady              => 0,
        -tabpadx            => '0.020i',
        -tabpady            => '0.070i',
        -foreground         => $$conf{btnfcol},
        -inactivebackground => $$conf{btncol},
        -background         => $$conf{btnselfg},
        -focuscolor         => $$conf{btnselfg},
        -font               => $$conf{Titlefnt},
        -backpagecolor      => $$conf{bgcolor}
    };
    # Drum Wave/WMT and Envelopes Tabs defaults
    $ElDef{NB2_defaults}={
        -borderwidth        => $$conf{bdwidth},
        -ipadx              => 0,
        -ipady              => 0,
        -tabpadx            => '0.020i',
        -foreground         => $$conf{btnfcol},
        -inactivebackground => $$conf{btncol},
        -background         => $$conf{bgcolor},
        -focuscolor         => $$conf{btnselfg},
        -font               => $$conf{Titlefnt},
        -backpagecolor      => $$conf{divcol}
    };
    # Frame Defaults
    $ElDef{Frame_defaults}={
        -background         => $$conf{bgcolor},
        -borderwidth        => $$conf{frmbdwidth},
        -highlightthickness => 0,
        -relief             => $$conf{frmstyle}
    };
    # pack parameters for horizontally maximised frame 
    $ElDef{X_elastic}={
        -anchor             => 'n',
        -fill               => 'x',
        -expand             =>  0,
        -padx               => $$conf{divwidth},
        -pady               => $$conf{divwidth}
    };
    # pack parameters for vertically maximised frame
    $ElDef{Y_elastic}={
        -anchor             => 'n',
        -fill               => 'y',
        -expand             =>  0,
        -padx               => $$conf{divwidth},
        -pady               => $$conf{divwidth}
    };
    # pack parameters for both vertically and horizontally maximised frame
    $ElDef{B_elastic}={
        -anchor             => 'n',
        -fill               => 'both',
        -expand             =>  1,
        -padx               => $$conf{divwidth},
        -pady               => $$conf{divwidth}
    };
    return \%ElDef;
}

1;
