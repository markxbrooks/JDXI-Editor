#!/bin/bash

# Build script for JDXI Manager 0.3.0 Mac version
# This script creates a Mac .app bundle from the Perl/Tk application

set -e  # Exit on error

APP_NAME="JDXI Manager.app"
VERSION="0.3.0"
BUILD_DIR="jdxi_manager_build"
APP_DIR="$BUILD_DIR/$APP_NAME"
RESOURCES_DIR="$APP_DIR/Contents/Resources"
MACOS_DIR="$APP_DIR/Contents/MacOS"
PERL_DIR="doc/perl"

echo "🔨 Building JDXI Manager $VERSION for macOS..."

# Clean previous builds
rm -rf "$BUILD_DIR" "$APP_NAME"

# Create app bundle structure
mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

# Copy Perl script and modules
echo "📦 Copying Perl files..."
cp "$PERL_DIR/jdxi_manager.pl" "$RESOURCES_DIR/"
cp "$PERL_DIR/JDXidata.pm" "$RESOURCES_DIR/"
cp "$PERL_DIR/LTNicons.pm" "$RESOURCES_DIR/"
cp "$PERL_DIR/LTNstyle.pm" "$RESOURCES_DIR/"

# Create launcher script
echo "📝 Creating launcher script..."
cat > "$MACOS_DIR/JDXI Manager" << 'LAUNCHER_EOF'
#!/bin/bash

# Get the directory where the app bundle is located
APP_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
RESOURCES_DIR="$APP_DIR/Contents/Resources"

# Change to resources directory so Perl can find modules
cd "$RESOURCES_DIR"

# Find Perl (try system Perl first, then Homebrew)
PERL=""
if [ -f "/usr/bin/perl" ]; then
    PERL="/usr/bin/perl"
elif [ -f "/opt/homebrew/bin/perl" ]; then
    PERL="/opt/homebrew/bin/perl"
elif [ -f "/usr/local/bin/perl" ]; then
    PERL="/usr/local/bin/perl"
else
    PERL=$(which perl)
fi

if [ -z "$PERL" ]; then
    osascript -e 'display dialog "Perl is not installed. Please install Perl to run JDXI Manager." buttons {"OK"} default button "OK" with icon stop'
    exit 1
fi

# Check if required Perl modules are installed
MISSING_MODULES=()
if ! "$PERL" -MTk -e "1" 2>/dev/null; then
    MISSING_MODULES+=("Tk")
fi
if ! "$PERL" -MConfig::Simple -e "1" 2>/dev/null; then
    MISSING_MODULES+=("Config::Simple")
fi
if ! "$PERL" -MTime::HiRes -e "1" 2>/dev/null; then
    MISSING_MODULES+=("Time::HiRes")
fi
if ! "$PERL" -MLWP::UserAgent -e "1" 2>/dev/null; then
    MISSING_MODULES+=("LWP::UserAgent")
fi

if [ ${#MISSING_MODULES[@]} -gt 0 ]; then
    MODULES_LIST=$(IFS=', '; echo "${MISSING_MODULES[*]}")
    osascript -e "display dialog \"Missing required Perl modules: $MODULES_LIST\n\nPlease install them using:\ncpan install $MODULES_LIST\" buttons {\"OK\"} default button \"OK\" with icon stop"
    exit 1
fi

# Run the Perl application
exec "$PERL" -I"$RESOURCES_DIR" "$RESOURCES_DIR/jdxi_manager.pl"
LAUNCHER_EOF

# Make launcher executable
chmod +x "$MACOS_DIR/JDXI Manager"

# Create Info.plist
echo "📝 Creating Info.plist..."
cat > "$APP_DIR/Contents/Info.plist" << PLIST_EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleExecutable</key>
    <string>JDXI Manager</string>
    <key>CFBundleIdentifier</key>
    <string>com.linuxtech.jdxi-manager</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>JDXI Manager</string>
    <key>CFBundleDisplayName</key>
    <string>JDXI Manager</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>$VERSION</string>
    <key>CFBundleVersion</key>
    <string>$VERSION</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSRequiresAquaSystemAppearance</key>
    <false/>
</dict>
</plist>
PLIST_EOF

# Create PkgInfo
echo "APPLjdxi" > "$APP_DIR/Contents/PkgInfo"

# Move app to current directory
mv "$APP_DIR" "./$APP_NAME"

echo "✅ JDXI Manager $VERSION Mac app bundle created: $APP_NAME"
echo ""
echo "📋 Next steps:"
echo "   1. Test the app: open '$APP_NAME'"
echo "   2. Install required Perl modules if needed:"
echo "      cpan install Tk Config::Simple Time::HiRes LWP::UserAgent"
echo "   3. To create a DMG, run: ./make_jdxi_manager_dmg.sh"
