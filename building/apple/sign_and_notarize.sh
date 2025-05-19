#!/bin/bash

# ==== CONFIGURATION ====


# xcrun notarytool store-credentials notarize-profile \
  #  --apple-id "your_apple_id@example.com" \
  #  --team-id "YOUR_TEAM_ID" \
  #  --password "your-app-specific-password"

APP_NAME="jdxi_manager.app"
DMG_NAME="jdxi_editor.dmg"
VOLUME_NAME="JDXI Editor"
APP_PATH="dist/$APP_NAME"
DMG_TEMP_DIR="jdxi_dmg/JDXI-Editor"

DEVELOPER_ID_APP="Developer ID Application: Your Name (TEAMID)"
DEVELOPER_ID_INSTALLER="Developer ID Installer: Your Name (TEAMID)"
NOTARY_PROFILE="notarize-profile"  # Must be set with `xcrun notarytool store-credentials`

# ==== STEP 1: Sign the .app ====
echo "🔏 Signing the app bundle..."
codesign --deep --force --verify \
  --options runtime \
  --sign "$DEVELOPER_ID_APP" \
  "$APP_PATH"

# ==== STEP 2: Verify .app Signature ====
codesign --verify --deep --strict --verbose=2 "$APP_PATH"

# ==== STEP 3: Create .dmg ====
echo "📦 Creating DMG..."
mkdir -p "$DMG_TEMP_DIR"
cp -R "$APP_PATH" "$DMG_TEMP_DIR"

hdiutil create -volname "$VOLUME_NAME" \
  -srcfolder "$DMG_TEMP_DIR" \
  -ov -format UDZO "$DMG_NAME"

# ==== STEP 4: Sign the .dmg ====
echo "🔐 Signing the DMG..."
codesign --force --sign "$DEVELOPER_ID_INSTALLER" "$DMG_NAME"

# ==== STEP 5: Submit to Apple for Notarization ====
echo "☁️ Submitting to Apple for notarization..."
xcrun notarytool submit "$DMG_NAME" \
  --keychain-profile "$NOTARY_PROFILE" \
  --wait

# ==== STEP 6: Staple the ticket ====
echo "📎 Stapling notarization ticket..."
xcrun stapler staple "$DMG_NAME"

echo "✅ Done! Notarized DMG: $DMG_NAME"
