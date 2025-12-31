#!/bin/bash

# Test script for JDXI Manager MIDI functionality
# This tests MIDI without building the full app

set -e

PERL_DIR="doc/perl"
cd "$(dirname "$0")"

echo "🧪 Testing JDXI Manager MIDI Functionality"
echo "=========================================="
echo ""

# Check Perl version
echo "📋 Perl version:"
perl -v | head -2
echo ""

# Check if we're on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "✅ Running on macOS"
    MACOS=1
else
    echo "⚠️  Not macOS - MIDI::ALSA would be used on Linux"
    MACOS=0
fi
echo ""

# Check for required Perl modules
echo "📦 Checking Perl modules..."
echo ""

MISSING_MODULES=()

# Check Tk (GUI)
if perl -MTk -e "1" 2>/dev/null; then
    echo "✅ Tk (GUI) - installed"
else
    echo "❌ Tk (GUI) - NOT installed"
    MISSING_MODULES+=("Tk")
fi

# Check Config::Simple
if perl -MConfig::Simple -e "1" 2>/dev/null; then
    echo "✅ Config::Simple - installed"
else
    echo "❌ Config::Simple - NOT installed"
    MISSING_MODULES+=("Config::Simple")
fi

# Check Time::HiRes
if perl -MTime::HiRes -e "1" 2>/dev/null; then
    echo "✅ Time::HiRes - installed"
else
    echo "❌ Time::HiRes - NOT installed"
    MISSING_MODULES+=("Time::HiRes")
fi

# Check LWP::UserAgent
if perl -MLWP::UserAgent -e "1" 2>/dev/null; then
    echo "✅ LWP::UserAgent - installed"
else
    echo "❌ LWP::UserAgent - NOT installed"
    MISSING_MODULES+=("LWP::UserAgent")
fi

# Check Mac::CoreMIDI (macOS only)
if [ "$MACOS" -eq 1 ]; then
    if perl -MMac::CoreMIDI -e "1" 2>/dev/null; then
        echo "✅ Mac::CoreMIDI (MIDI) - installed"
    else
        echo "❌ Mac::CoreMIDI (MIDI) - NOT installed"
        MISSING_MODULES+=("Mac::CoreMIDI")
    fi
fi

echo ""

# Test MIDI functionality
echo "🎹 Testing MIDI functionality..."
echo ""

if [ "$MACOS" -eq 1 ]; then
    if perl -MMac::CoreMIDI -e "1" 2>/dev/null; then
        echo "Creating MIDI test script..."
        cat > /tmp/test_midi.pl << 'MIDI_TEST_EOF'
#!/usr/bin/perl
use strict;
use warnings;
use Mac::CoreMIDI;

print "🔍 Scanning for MIDI devices...\n\n";

# Get number of sources and destinations
my $num_sources = Mac::CoreMIDI::GetNumberOfSources();
my $num_destinations = Mac::CoreMIDI::GetNumberOfDestinations();

print "MIDI Sources (inputs): $num_sources\n";
print "MIDI Destinations (outputs): $num_destinations\n\n";

if ($num_sources > 0) {
    print "📥 Available MIDI Input Devices:\n";
    for (my $i = 0; $i < $num_sources; $i++) {
        my $endpoint = Mac::CoreMIDI::GetSource($i);
        my $name = $endpoint->GetName();
        print "  [$i] $name\n";
    }
    print "\n";
}

if ($num_destinations > 0) {
    print "📤 Available MIDI Output Devices:\n";
    for (my $i = 0; $i < $num_destinations; $i++) {
        my $endpoint = Mac::CoreMIDI::GetDestination($i);
        my $name = $endpoint->GetName();
        print "  [$i] $name\n";
    }
    print "\n";
}

# Look for JD-Xi specifically
print "🔎 Searching for JD-Xi devices...\n";
my $found_jdxi = 0;
for (my $i = 0; $i < $num_sources; $i++) {
    my $endpoint = Mac::CoreMIDI::GetSource($i);
    my $name = $endpoint->GetName();
    if ($name =~ /JD-Xi|JDXi|jdxi/i) {
        print "  ✅ Found JD-Xi input: $name\n";
        $found_jdxi = 1;
    }
}
for (my $i = 0; $i < $num_destinations; $i++) {
    my $endpoint = Mac::CoreMIDI::GetDestination($i);
    my $name = $endpoint->GetName();
    if ($name =~ /JD-Xi|JDXi|jdxi/i) {
        print "  ✅ Found JD-Xi output: $name\n";
        $found_jdxi = 1;
    }
}

if (!$found_jdxi) {
    print "  ⚠️  No JD-Xi device found. Make sure it's connected and powered on.\n";
}

print "\n✅ MIDI system is accessible!\n";
MIDI_TEST_EOF

        perl /tmp/test_midi.pl
        rm /tmp/test_midi.pl
    else
        echo "❌ Cannot test MIDI - Mac::CoreMIDI is not installed"
        echo "   Install with: cpan install Mac::CoreMIDI"
    fi
else
    echo "⚠️  MIDI testing for Linux would require MIDI::ALSA"
fi

echo ""
echo "=========================================="
echo ""

# Summary
if [ ${#MISSING_MODULES[@]} -eq 0 ]; then
    echo "✅ All required modules are installed!"
    echo ""
    echo "You can test the full application with:"
    echo "  cd $PERL_DIR && perl jdxi_manager.pl"
else
    echo "⚠️  Missing modules: ${MISSING_MODULES[*]}"
    echo ""
    echo "Install missing modules with:"
    echo "  cpan install ${MISSING_MODULES[*]}"
    echo ""
    echo "Or install all at once:"
    echo "  cpan install Tk Config::Simple Time::HiRes LWP::UserAgent Mac::CoreMIDI"
fi
