#!/bin/bash

# Install Perl Tk module on macOS with Homebrew tcl-tk

set -e

echo "🔧 Installing Perl Tk module for macOS..."
echo ""

# Get Homebrew Tcl-Tk path
TCL_TK_PREFIX=$(brew --prefix tcl-tk)

if [ -z "$TCL_TK_PREFIX" ] || [ ! -d "$TCL_TK_PREFIX" ]; then
    echo "❌ Error: tcl-tk not found via Homebrew"
    echo "   Install it with: brew install tcl-tk"
    exit 1
fi

echo "✅ Found tcl-tk at: $TCL_TK_PREFIX"
echo ""

# Find Tcl and Tk library files
TCL_LIB=$(find "$TCL_TK_PREFIX/lib" -name "libtcl*.dylib" -o -name "libtcl*.a" | head -1 | xargs dirname)
TK_LIB=$(find "$TCL_TK_PREFIX/lib" -name "libtk*.dylib" -o -name "libtk*.a" | head -1 | xargs dirname)

if [ -z "$TCL_LIB" ] || [ -z "$TK_LIB" ]; then
    echo "⚠️  Warning: Could not find Tcl/Tk libraries, but will try anyway"
    TCL_LIB="$TCL_TK_PREFIX/lib"
    TK_LIB="$TCL_TK_PREFIX/lib"
fi

echo "   Tcl library: $TCL_LIB"
echo "   Tk library: $TK_LIB"
echo ""

# Set environment variables for Tk build
export TCL_PREFIX="$TCL_TK_PREFIX"
export TK_PREFIX="$TCL_TK_PREFIX"
export TCL_LIBRARY="$TCL_TK_PREFIX/lib"
export TK_LIBRARY="$TCL_TK_PREFIX/lib"

# For MakeMaker - specify include and library paths
export PERL_MM_OPT="TCL_PREFIX=$TCL_TK_PREFIX TK_PREFIX=$TCL_TK_PREFIX INC=-I$TCL_TK_PREFIX/include LIBS=-L$TCL_TK_PREFIX/lib"

echo "📦 Installing Tk module..."
echo "   This may take several minutes (10-15 minutes is normal)..."
echo "   Environment configured:"
echo "     TCL_PREFIX=$TCL_TK_PREFIX"
echo "     TK_PREFIX=$TCL_TK_PREFIX"
echo ""

# Try installing with cpan
echo "Running: cpan -i Tk"
echo ""
cpan -i Tk

echo ""
echo "✅ Tk installation complete!"
echo ""
echo "Test it with: perl -MTk -e 'print \"Tk installed successfully\\n\"'"
