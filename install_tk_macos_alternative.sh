#!/bin/bash

# Alternative method to install Perl Tk on macOS
# This uses CPAN's interactive mode to configure Tk properly

set -e

TCL_TK_PREFIX=$(brew --prefix tcl-tk)

if [ -z "$TCL_TK_PREFIX" ] || [ ! -d "$TCL_TK_PREFIX" ]; then
    echo "❌ Error: tcl-tk not found via Homebrew"
    echo "   Install it with: brew install tcl-tk"
    exit 1
fi

echo "🔧 Installing Perl Tk module (Alternative Method)"
echo "=================================================="
echo ""
echo "This will use CPAN's interactive mode."
echo "When prompted, you'll need to configure Tk paths."
echo ""
echo "Tcl-Tk prefix: $TCL_TK_PREFIX"
echo ""

# Method 1: Try with environment variables set
echo "Method 1: Installing with environment variables..."
echo ""

export TCL_PREFIX="$TCL_TK_PREFIX"
export TK_PREFIX="$TCL_TK_PREFIX"

# Create a CPAN config override
mkdir -p ~/.cpan/CPAN
cat > ~/.cpan/CPAN/MyConfig.pm.override << EOF
\$CPAN::Config->{makepl_arg} = "TCL_PREFIX=$TCL_TK_PREFIX TK_PREFIX=$TCL_TK_PREFIX";
EOF

# Try the installation
echo "Running: cpan -i Tk"
echo "If this fails, try Method 2 (manual configuration)"
echo ""

cpan -i Tk || {
    echo ""
    echo "⚠️  Method 1 failed. Trying Method 2..."
    echo ""
    echo "Method 2: Manual CPAN configuration"
    echo "===================================="
    echo ""
    echo "Run these commands manually:"
    echo ""
    echo "1. Start CPAN shell:"
    echo "   cpan"
    echo ""
    echo "2. In CPAN shell, run:"
    echo "   o conf makepl_arg \"TCL_PREFIX=$TCL_TK_PREFIX TK_PREFIX=$TCL_TK_PREFIX\""
    echo "   o conf commit"
    echo "   install Tk"
    echo ""
    echo "3. If prompted for Tcl/Tk paths, use:"
    echo "   Tcl directory: $TCL_TK_PREFIX"
    echo "   Tk directory: $TCL_TK_PREFIX"
    echo ""
    echo "Or try installing via Homebrew's Perl (if different):"
    echo "   brew install perl-tk"
    echo ""
}
