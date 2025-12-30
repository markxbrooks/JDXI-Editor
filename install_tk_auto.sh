#!/bin/bash

# Fully automated Tk installation script

set -e

echo "🔧 Installing Perl Tk Module (Automated)"
echo "========================================"
echo ""

TCL_TK_PREFIX=$(brew --prefix tcl-tk)

if [ -z "$TCL_TK_PREFIX" ]; then
    echo "❌ tcl-tk not found. Install with: brew install tcl-tk"
    exit 1
fi

echo "Using Tcl-Tk from: $TCL_TK_PREFIX"
echo ""

# Configure CPAN non-interactively
echo "📝 Configuring CPAN..."
export TCL_PREFIX="$TCL_TK_PREFIX"
export TK_PREFIX="$TCL_TK_PREFIX"

# Use expect or here-doc to configure CPAN
perl -MCPAN -e "
    \$CPAN::Config->{makepl_arg} = 'TCL_PREFIX=$TCL_TK_PREFIX TK_PREFIX=$TCL_TK_PREFIX';
    CPAN::Shell->commit();
    print 'CPAN configured\n';
" 2>&1 || {
    # Alternative: direct CPAN config
    echo "Configuring CPAN via config file..."
    mkdir -p ~/.cpan/CPAN
    # Update or create MyConfig.pm with makepl_arg
    if [ -f ~/.cpan/CPAN/MyConfig.pm ]; then
        perl -i -pe "s/'makepl_arg'\s*=>\s*'[^']*'/'makepl_arg' => 'TCL_PREFIX=$TCL_TK_PREFIX TK_PREFIX=$TCL_TK_PREFIX'/ if /makepl_arg/" ~/.cpan/CPAN/MyConfig.pm 2>/dev/null || true
    fi
}

echo ""
echo "📦 Installing Tk module..."
echo "   This will take 10-15 minutes. Please wait..."
echo ""

# Install Tk with automatic yes to prompts
export PERL_MM_USE_DEFAULT=1
export PERL_AUTOINSTALL=1

cpan -i Tk << CPAN_INPUT
yes
CPAN_INPUT

echo ""
echo "✅ Installation attempt complete!"
echo ""
echo "Testing installation..."
if perl -MTk -e 'print "Tk installed successfully!\n"' 2>/dev/null; then
    echo "✅ Tk is now installed and working!"
else
    echo "⚠️  Tk installation may have failed. Check the output above for errors."
    echo ""
    echo "You may need to install manually. See install_tk_manual.txt for instructions."
fi
