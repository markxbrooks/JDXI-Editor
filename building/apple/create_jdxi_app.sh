#!/bin/bash
PROJECT_ROOT="/Users/brooks/projects/JDXI-Editor"
# === CONFIGURATION ===
APP_NAME="JD-Xi-Editor"
SCRIPT_PATH="$PROJECT_ROOT/jdxi_editor/main.py"  # Adjust this if your script is in a different folder
ICON_PATH="$PROJECT_ROOT/jdxi_icon.icns"  # Path to your icon file
PYTHON_PATH="/Users/brooks/projects/JDXI-Editor/venv/bin/python"  # Or your virtualenv Python path

# === DIRECTORY STRUCTURE ===
APP_DIR="${APP_NAME}.app"
CONTENTS_DIR="${APP_DIR}/Contents"
MACOS_DIR="${CONTENTS_DIR}/MacOS"
RESOURCES_DIR="${CONTENTS_DIR}/Resources"

echo "Creating bundle structure..."
mkdir -p "${MACOS_DIR}"
mkdir -p "${RESOURCES_DIR}"

# === CREATE STUB EXECUTABLE ===
EXECUTABLE="${MACOS_DIR}/jdxi_editor"
echo "Creating executable stub..."
cat << EOF > "${EXECUTABLE}"
#!/bin/bash
exec "${PYTHON_PATH}" -m jdxi_editor.main
EOF
chmod +x "${EXECUTABLE}"

# === CREATE Info.plist ===
PLIST="${CONTENTS_DIR}/Info.plist"
echo "Creating Info.plist..."
cat << EOF > "${PLIST}"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>jdxi_editor</string>
    <key>CFBundleIconFile</key>
    <string>jdxi_editor.icns</string>
    <key>CFBundleIdentifier</key>
    <string>com.jdxi.editor</string>
    <key>CFBundleName</key>
    <string>JD-Xi Editor</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
</dict>
</plist>
EOF

# === COPY ICON ===
if [[ -f "${ICON_PATH}" ]]; then
    echo "Copying icon..."
    cp "${ICON_PATH}" "${RESOURCES_DIR}/jdxi_editor.icns"
else
    echo "WARNING: Icon file not found: ${ICON_PATH}"
fi

echo "✅ ${APP_NAME}.app created."
echo "Run it with: open '${APP_NAME}.app'"
