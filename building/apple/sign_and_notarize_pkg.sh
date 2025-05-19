#!/bin/bash

# ==== CONFIGURATION ====

APP_NAME="jdxi_manager.app"
PKG_NAME="jdxi_editor.pkg"
INSTALL_LOCATION="/Applications"
APP_PATH="dist/$APP_NAME"
BUILD_DIR="pkg_build"
IDENTITY_APP="Developer ID Application: Your Name (TEAMID)"
IDENTITY_INSTALLER="Developer ID Installer: Your Name (TEAMID)"
NOTARY_PROFILE="notarize-profile"  # Set via `xcrun notarytool store-credentials`

# ==== STEP 1: Sign the .app ====
echo "🔏 Signing the app bundle..."
codesign --deep --force --verify \
  --options runtime \
  --sign "$IDENTITY_APP" \
  "$APP_PATH"

# ==== STEP 2: Create package root ====
echo "📁 Creating staging directory..."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/$INSTALL_LOCATION"
cp -R "$APP_PATH" "$BUILD_DIR/$INSTALL_LOCATION"

# ==== STEP 3: Build unsigned .pkg ====
echo "📦 Building unsigned .pkg..."
pkgbuild \
  --root "$BUILD_DIR" \
  --identifier "com.example.jdximanager" \
  --version "1.0.0" \
  --install-location "/" \
  "$PKG_NAME"

# ==== STEP 4: Sign the .pkg ====
echo "🔐 Signing the package..."
productsign \
  --sign "$IDENTITY_INSTALLER" \
  "$PKG_NAME" "signed_$PKG_NAME"

# ==== STEP 5: Submit to notarization ====
echo "☁️ Submitting to Apple for notarization..."
xcrun notarytool submit "signed_$PKG_NAME" \
  --keychain-profile "$NOTARY_PROFILE" \
  --wait

# ==== STEP 6: Staple the ticket ====
echo "📎 Stapling notarization ticket..."
xcrun stapler staple "signed_$PKG_NAME"

echo "✅ Done! Notarized and stapled package: signed_$PKG_NAME"
