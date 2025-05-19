#!/bin/bash

# Input source image (should ideally be 1024x1024)
SOURCE_IMAGE="jdxi_icon.png"
ICONSET_DIR="AppIcon.iconset"

# Create iconset directory
mkdir -p $ICONSET_DIR

# Generate icon sizes
sips -z 16 16     $SOURCE_IMAGE --out $ICONSET_DIR/icon_16x16.png
sips -z 32 32     $SOURCE_IMAGE --out $ICONSET_DIR/icon_16x16@2x.png
sips -z 32 32     $SOURCE_IMAGE --out $ICONSET_DIR/icon_32x32.png
sips -z 64 64     $SOURCE_IMAGE --out $ICONSET_DIR/icon_32x32@2x.png
sips -z 128 128   $SOURCE_IMAGE --out $ICONSET_DIR/icon_128x128.png
sips -z 256 256   $SOURCE_IMAGE --out $ICONSET_DIR/icon_128x128@2x.png
sips -z 256 256   $SOURCE_IMAGE --out $ICONSET_DIR/icon_256x256.png
sips -z 512 512   $SOURCE_IMAGE --out $ICONSET_DIR/icon_256x256@2x.png
sips -z 512 512   $SOURCE_IMAGE --out $ICONSET_DIR/icon_512x512.png
cp $SOURCE_IMAGE                   $ICONSET_DIR/icon_512x512@2x.png  # Full size copy

# Convert to .icns
iconutil -c icns $ICONSET_DIR -o jdxi_icon.icns

echo "✅ jdxi_icon.icns has been created."
