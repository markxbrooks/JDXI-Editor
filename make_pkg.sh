#!/bin/bash

# Build the app using py2app
source venv/bin/activate
python setup.py py2app

# Configuration
APP_NAME="JD-Xi Editor.app"
PKG_NAME="JD-Xi_Editor_0.9.1_MacOS_Universal.pkg"
INSTALL_LOCATION="/Applications"
APP_PATH="dist/$APP_NAME"
BUILD_DIR="pkg_build"
PKG_IDENTIFIER="com.jdxi.editor"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf "$BUILD_DIR" "$PKG_NAME"

# Create package root directory
echo "📁 Creating staging directory..."
mkdir -p "$BUILD_DIR/$INSTALL_LOCATION"

# Copy the app bundle to the staging directory
echo "📦 Copying app bundle..."
if [ ! -d "$APP_PATH" ]; then
    echo "❌ Error: App bundle not found at $APP_PATH"
    echo "   Make sure py2app build completed successfully."
    exit 1
fi

cp -R "$APP_PATH" "$BUILD_DIR/$INSTALL_LOCATION/"

# Build the PKG installer
echo "🔨 Building PKG installer..."
pkgbuild \
    --root "$BUILD_DIR" \
    --identifier "$PKG_IDENTIFIER" \
    --version "0.9.1" \
    --install-location "/" \
    "$PKG_NAME"

# Clean up staging directory
echo "🧹 Cleaning up staging directory..."
rm -rf "$BUILD_DIR"

echo "✅ $PKG_NAME created successfully."
echo "   Users can install by double-clicking the PKG file."
