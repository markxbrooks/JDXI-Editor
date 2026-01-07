#!/bin/bash
source venv/bin/activate
python setup.py py2app
APP_NAME="JD-Xi Editor.app"
DMG_NAME="JD-Xi_Editor_0.9.1_MacOS_Universal.dmg"
VOLUME_NAME="JDXI Editor"
SRC_DIR="dist/$APP_NAME"
BUILD_DIR="jdxi_dmg/JDXI-Editor"

# Clean previous builds
rm -rf jdxi_dmg "$DMG_NAME"

# Prepare .dmg content folder
mkdir -p "$BUILD_DIR"
cp -R "$SRC_DIR" "$BUILD_DIR/"
ln -s /Applications "$BUILD_DIR/Applications"

# Create .dmg
hdiutil create -volname "$VOLUME_NAME" \
  -srcfolder "$BUILD_DIR" \
  -ov -format UDZO "$DMG_NAME"

echo "✅ $DMG_NAME created successfully."
