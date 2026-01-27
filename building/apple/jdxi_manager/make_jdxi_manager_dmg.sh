#!/bin/bash

# Create a DMG for JDXI Manager 0.3.0 Mac version

set -e  # Exit on error

APP_NAME="JDXI Manager.app"
DMG_NAME="JDXI_Manager_0.3.0_MacOS.dmg"
VOLUME_NAME="JDXI Manager"
SRC_DIR="$APP_NAME"
BUILD_DIR="jdxi_manager_dmg/JDXI Manager"

# Check if app exists
if [ ! -d "$APP_NAME" ]; then
    echo "❌ Error: $APP_NAME not found. Please run build_jdxi_manager_mac.sh first."
    exit 1
fi

echo "📦 Creating DMG for JDXI Manager 0.3.0..."

# Clean previous builds
rm -rf jdxi_manager_dmg "$DMG_NAME"

# Prepare .dmg content folder
mkdir -p "$BUILD_DIR"
cp -R "$SRC_DIR" "$BUILD_DIR/"
ln -s /Applications "$BUILD_DIR/Applications"

# Create .dmg
hdiutil create -volname "$VOLUME_NAME" \
  -srcfolder jdxi_manager_dmg \
  -ov -format UDZO "$DMG_NAME"

echo "✅ $DMG_NAME created successfully."
