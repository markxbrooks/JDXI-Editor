
use Test;
use Test::More;
BEGIN { plan tests => 1 };

use Mac::CoreMIDI qw(FindObject);
diag("FindObject(0): " . (FindObject(0) // 'undef'));
#diag("Skipping test for FindObject(0) due to unexpected behavior");
ok(!defined FindObject(0));

