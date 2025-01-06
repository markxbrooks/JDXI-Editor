package LTNicons;

use warnings;
use strict;

use GD;
use GD::Polyline;
use MIME::Base64 qw(encode_base64);

use Exporter;
our @ISA=qw(Exporter);
our @EXPORT=qw(
  knob_png
  darrow_bits
  triangle_png
  sine_png
  upsaw_png
  spsaw_png
  square_png
  pwsqu_png
  noise_png
  spacer_xpm
);

# JD-Xi knob icon
sub knob_png {
    my($icon128, $rz)=@_;
    my $x=int(128*($rz/4)); my $y=int(128*($rz/4));
    my $x1=$x; my $y1=$y;
    # if ($rz*2 != int($rz*2)) {$x=$x+8; $y=$y+8}
    my $im=new GD::Image($x,$y,1);
    my $im1=GD::Image->newFromPng($icon128, 1);
    $im->copyResampled($im1,0,0,0,0,$x1,$y1,128,128);
    return encode_base64($im->png);
}

# down arrow bitmap for pulldown menu
sub darrow_bits {
    my($dpi)=@_;
    my $bits;
    if ($dpi < 140) {
        $bits=pack("b11"x10,
        "...........", ".111111111.", "...........", "...........", ".111111111.",
        "..1111111..", "...11111...", "....111....", ".....1.....", "...........");
        return (11,10,$bits);
    } else {
        $bits=pack("b17"x15,
        ".................", ".111111111111111.", ".111111111111111.", ".................", ".................",
        ".................", ".111111111111111.", "..1111111111111..", "...11111111111...", "....111111111....",
        ".....1111111.....", "......11111......", ".......111.......", "........1........", ".................");
        return (17,15,$bits);
    }
}

# triangle wave pixmap
sub triangle_png {
  my($btnfcol, $rz)=@_;
  my @rgb=  unpack 'C*', pack 'H*', substr($btnfcol,1);
  my $x=int(17*$rz); my $y=int(9*$rz); my $th=int($rz+.49);
  my $im=new GD::Image($x,$y);
  my $white = $im->colorAllocate(255,255,255);
  my $black = $im->colorAllocate(@rgb[0..2]);
  $im->transparent($white);
  $im->setThickness($th);
  $im->line(      0, $y*.5-int($rz*.5), $x*.25,     0, $black);
  $im->line( $x*.25,                 0, $x*.75,  $y-1, $black);
  $im->line( $x*.75,              $y-1,     $x, $y*.5, $black);
  return encode_base64($im->png);
}

# sine wave pixmap
sub sine_png {
  my($btnfcol, $rz)=@_;
  my @rgb=  unpack 'C*', pack 'H*', substr($btnfcol,1);
  my $x=int(17*$rz); my $y=int(9*$rz); my $th=int($rz+.49);
  my $im=new GD::Image($x,$y);
  my $white = $im->colorAllocate(255,255,255);
  my $black = $im->colorAllocate(@rgb[0..2]);
  $im->transparent($white);
  $im->setThickness($th);
  if ($rz == 1.75) {
    $im->arc($x*.25, $y*.5, $x*.5+.5, $y-.5, 180, 360, $black);
    $im->arc($x*.75, $y*.5, $x*.5+.5, $y+.5,   0, 180, $black);
  } elsif ($rz >= 2.75) {
    $im->arc($x*.25, $y*.5, $x*.5+.5, $y-.5, 180, 360, $black);
    $im->arc($x*.75, $y*.5, $x*.5+.5, $y-1.5,  0, 180, $black);
  } else {
    $im->arc($x*.25, $y*.5, $x*.5+.5, $y+.5, 180, 360, $black);
    $im->arc($x*.75, $y*.5, $x*.5+.5, $y+.5,   0, 180, $black);
  }
  return encode_base64($im->png);
}

# upsaw wave pixmap
sub upsaw_png {
  my($btnfcol, $rz)=@_;
  my @rgb=  unpack 'C*', pack 'H*', substr($btnfcol,1);
  my $x=int(17*$rz); my $y=int(9*$rz); my $th=int($rz+.49);
  if ($x % 2 == 0) {$x=$x+1}
  my $im=new GD::Image($x,$y);
  my $white = $im->colorAllocate(255,255,255);
  my $black = $im->colorAllocate(@rgb[0..2]);
  $im->transparent($white);
  $im->setThickness($th);
  $im->line(         0,      $y-1,     $x*.5,         0, $black);
  $im->line(     $x*.5,         0,     $x*.5,      $y-1, $black);
  $im->line(     $x*.5,      $y-1,      $x-1,         0, $black);
  $im->line( $x-$th*.5,         0, $x-$th*.5,      $y-1, $black);
  return encode_base64($im->png);
}

# supersaw wave pixmap
sub spsaw_png {
  my($btnfcol, $rz)=@_;
  my @rgb=  unpack 'C*', pack 'H*', substr($btnfcol,1);
  my $x=int(17*$rz); my $y=int(9*$rz); my $th=int($rz+.49);
  my $im=new GD::Image($x,$y);
  my $white = $im->colorAllocate(255,255,255);
  my $black = $im->colorAllocate(@rgb[0..2]);
  $im->transparent($white);
  $im->setThickness($th);
  $im->line(                 0, $y*.5,             $y*.5,     0, $black);
  $im->line(             $y*.5,     0,             $y*.5,  $y-1, $black);
  $im->line(             $y*.5,  $y-1, $y*.5+$y-int($rz),     0, $black);
  $im->line( $y*.5+$y-int($rz),     0, $y*.5+$y-int($rz),  $y-1, $black);
  $im->line( $y*.5+$y-int($rz),  $y-1,              $x-1, $y*.5, $black);
  $im->line(                 0,  $y-1,              $y-1,     0, $black);
  $im->line(              $y-1,     0,              $y-1,  $y-1, $black);
  $im->line(              $y-1,  $y-1,              $x-1,     0, $black);
  $im->line(         $x-$th*.5,     0,         $x-$th*.5,  $y-1, $black);
  return encode_base64($im->png);
}

# square wave pixmap
sub square_png {
  my($btnfcol, $rz)=@_;
  my @rgb=  unpack 'C*', pack 'H*', substr($btnfcol,1);
  my $x=int(17*$rz); my $y=int(9*$rz); my $th=int($rz+.49);
  my $im=new GD::Image($x,$y);
  my $white = $im->colorAllocate(255,255,255);
  my $black = $im->colorAllocate(@rgb[0..2]);
  $im->transparent($white);
  $im->setThickness($th);
  $im->line(    $th*.5,      $y-1,    $th*.5,         0, $black);
  $im->line(         0,    $th*.5,     $x*.5,    $th*.5, $black);
  $im->line(     $x*.5,         0,     $x*.5,      $y-1, $black);
  $im->line(     $x*.5, $y-$th*.5,      $x-1, $y-$th*.5, $black);
  $im->line( $x-$th*.5,      $y-1, $x-$th*.5,         0, $black);
  return encode_base64($im->png);
}

# pw-square wave pixmap
sub pwsqu_png {
  my($btnfcol, $rz)=@_;
  my @rgb=  unpack 'C*', pack 'H*', substr($btnfcol,1);
  my $x=int(17*$rz); my $y=int(9*$rz); my $th=int($rz+.49);
  my $im=new GD::Image($x,$y);
  my $white = $im->colorAllocate(255,255,255);
  my $black = $im->colorAllocate(@rgb[0..2]);
  $im->transparent($white);
  $im->setThickness($th);
  $im->line(    $th*.5,      $y-1,    $th*.5,         0, $black);
  $im->line(         0,    $th*.5,$x*0.68-$th*.5,$th*.5, $black);
  $im->line(   $x*0.68,         0,   $x*0.68,      $y-1, $black);
  $im->line(   $x*0.68, $y-$th*.5,      $x-1, $y-$th*.5, $black);
  $im->line( $x-$th*.5,      $y-1, $x-$th*.5,         0, $black);
  $im->line(  $x*0.325+int($th*.5),  $y*0.223,  $x*0.325+int($th*.5),  $y*0.443, $black);
  $im->line(  $x*0.325+int($th*.5),  $y*0.556,  $x*0.325+int($th*.5),  $y*0.776, $black);
  $im->line(  $x*0.324, $y-$th*.5,  $x*0.400, $y-$th*.5, $black);
  $im->line(  $x*0.500, $y-$th*.5,  $x*0.580, $y-$th*.5, $black);
  return encode_base64($im->png);
}

# noise wave pixmap
sub noise_png {
  my($btnfcol, $rz)=@_;
  my @rgb=  unpack 'C*', pack 'H*', substr($btnfcol,1);
  my $x=int(17*$rz); my $y=int(9*$rz); my $th=int($rz+.49);
  my $im=new GD::Image($x,$y);
  my $white = $im->colorAllocate(255,255,255);
  my $black = $im->colorAllocate(@rgb[0..2]);
  $im->transparent($white);
  $im->setThickness($th);
  my $polyline = new GD::Polyline;
  $polyline->addPt(           $th*.5 ,      $y-1);
  $polyline->addPt(           $th*.5 ,         0);
  $polyline->addPt($th*.5+$x*.0588   ,    $y*.61);
  $polyline->addPt($th*.5+$x*.0588*2 ,    $y*.12);
  $polyline->addPt($th*.5+$x*.0588*3 ,    $y*.87);
  $polyline->addPt($th*.5+$x*.0588*4 ,    $y*.50);
  $polyline->addPt($th*.5+$x*.0588*5 ,    $y*.99);
  $polyline->addPt($th*.5+$x*.0588*6 ,    $y*.01);
  $polyline->addPt($th*.5+$x*.0588*7 ,    $y*.93);
  $polyline->addPt($th*.5+$x*.0588*8 ,    $y*.15);
  $polyline->addPt($th*.5+$x*.0588*9 ,    $y*.85);
  $polyline->addPt($th*.5+$x*.0588*10,    $y*.01);
  $polyline->addPt($th*.5+$x*.0588*11,    $y*.92);
  $polyline->addPt($th*.5+$x*.0588*12,    $y*.23);
  $polyline->addPt($th*.5+$x*.0588*13,    $y*.72);
  $polyline->addPt($th*.5+$x*.0588*14,    $y*.06);
  $polyline->addPt($th*.5+$x*.0588*15,    $y*.45);
  $polyline->addPt(        $x-$th*.5,      $y-1);
  $polyline->addPt(        $x-$th*.5,         0);
  $im->polyline($polyline,$black);
  return encode_base64($im->png);
}

# 10x4px empty transparent pixmap as spacer
sub spacer_xpm {
my($btnfcol)=@_;
my $bits=<< "end-of-xpm-data";
/* XPM */
static char * spacer_xpm[] = {
"10 4 2 1",".      c None","1      c $btnfcol",
"..........", "..........", "..........", ".........."};
end-of-xpm-data
return $bits;
}

1;
