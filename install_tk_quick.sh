#!/bin/bash

# Quick Tk installation script - tries the easiest method first

set -e

echo "🔧 Installing Perl Tk Module"
echo "============================"
echo ""

# Method 1: Check if system Perl has Tk
echo "Method 1: Checking system Perl..."
if /usr/bin/perl -MTk -e '1' 2>/dev/null; then
    echo "✅ System Perl already has Tk!"
    echo ""
    echo "You can use system Perl instead:"
    echo "  /usr/bin/perl doc/perl/jdxi_manager.pl"
    echo ""
    echo "Or update your build script to use system Perl."
    exit 0
fi

# Method 2: Try CPAN with proper paths
echo "Method 2: Installing via CPAN with Homebrew tcl-tk..."
echo ""

TCL_TK_PREFIX=$(brew --prefix tcl-tk)

if [ -z "$TCL_TK_PREFIX" ]; then
    echo "❌ tcl-tk not found. Install with: brew install tcl-tk"
    exit 1
fi

export TCL_PREFIX="$TCL_TK_PREFIX"
export TK_PREFIX="$TCL_TK_PREFIX"

echo "Using Tcl-Tk from: $TCL_TK_PREFIX"
echo ""
echo "⚠️  This will start CPAN interactive mode."
echo "   When prompted, answer 'yes' to configure Tk paths."
echo "   Use these paths when asked:"
echo "     Tcl directory: $TCL_TK_PREFIX"
echo "     Tk directory: $TCL_TK_PREFIX"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

# Configure CPAN first
echo ""
echo "Configuring CPAN..."
cpan << CPAN_CONFIG
o conf makepl_arg "TCL_PREFIX=$TCL_TK_PREFIX TK_PREFIX=$TCL_TK_PREFIX"
o conf commit
exit
CPAN_CONFIG

# Now install
echo ""
echo "Installing Tk (this will take 10-15 minutes)..."
cpan -i Tk

echo ""
echo "✅ Installation complete!"
echo ""
echo "Test with: perl -MTk -e 'print \"Tk installed\\n\"'"
