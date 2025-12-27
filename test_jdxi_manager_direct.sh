#!/bin/bash

# Test JDXI Manager directly without building
# This runs the Perl script with proper environment setup

set -e

PERL_DIR="doc/perl"
cd "$(dirname "$0")"

echo "🧪 Testing JDXI Manager Directly"
echo "================================"
echo ""

# Check if Perl script exists
if [ ! -f "$PERL_DIR/jdxi_manager.pl" ]; then
    echo "❌ Error: $PERL_DIR/jdxi_manager.pl not found"
    exit 1
fi

# Set MACOS variable for the script (it seems to check this but never sets it)
export MACOS=1

# Change to perl directory so modules can be found
cd "$PERL_DIR"

echo "📋 Testing with: perl jdxi_manager.pl"
echo ""
echo "⚠️  Note: This will attempt to launch the GUI"
echo "   Press Ctrl+C to stop if needed"
echo ""
echo "Checking dependencies first..."
echo ""

# Quick dependency check
MISSING=0

if ! perl -MTk -e "1" 2>/dev/null; then
    echo "❌ Tk (GUI) is missing"
    MISSING=1
fi

if ! perl -MMac::CoreMIDI -e "1" 2>/dev/null; then
    echo "❌ Mac::CoreMIDI (MIDI) is missing"
    MISSING=1
fi

if [ $MISSING -eq 1 ]; then
    echo ""
    echo "⚠️  Missing dependencies detected!"
    echo ""
    echo "Install with:"
    echo "  cpan install Tk Mac::CoreMIDI Config::Simple Time::HiRes LWP::UserAgent"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "🚀 Launching JDXI Manager..."
echo ""

# Run the script
MACOS=1 perl jdxi_manager.pl
