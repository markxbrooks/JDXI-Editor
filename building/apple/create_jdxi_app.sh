#!/bin/bash
set -e  # Exit on error

# === AUTOMATIC PROJECT ROOT DETECTION ===
# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "🔍 Script directory: ${SCRIPT_DIR}"

# Navigate up from building/apple/ to project root
if [[ -f "${SCRIPT_DIR}/../../pyproject.toml" ]] || [[ -f "${SCRIPT_DIR}/../../requirements.txt" ]]; then
    PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
elif [[ -f "${SCRIPT_DIR}/../pyproject.toml" ]] || [[ -f "${SCRIPT_DIR}/../requirements.txt" ]]; then
    PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
else
    # Fallback: try to find project root by looking for jdxi_editor directory
    CURRENT_DIR="$(pwd)"
    if [[ -d "${CURRENT_DIR}/jdxi_editor" ]]; then
        PROJECT_ROOT="${CURRENT_DIR}"
    else
        echo "❌ ERROR: Could not detect PROJECT_ROOT automatically."
        echo "   Please set PROJECT_ROOT manually in the script."
        exit 1
    fi
fi

echo "📁 PROJECT_ROOT detected: ${PROJECT_ROOT}"
echo "   Verifying project structure..."

# Verify project structure
if [[ ! -d "${PROJECT_ROOT}/jdxi_editor" ]]; then
    echo "❌ ERROR: jdxi_editor directory not found in ${PROJECT_ROOT}"
    exit 1
fi
if [[ ! -f "${PROJECT_ROOT}/requirements.txt" ]]; then
    echo "⚠️  WARNING: requirements.txt not found in ${PROJECT_ROOT}"
fi

# === CONFIGURATION ===
APP_NAME="JD-Xi-Editor"
SCRIPT_PATH="${PROJECT_ROOT}/jdxi_editor/main.py"
ICON_PATH="${PROJECT_ROOT}/jdxi_icon.icns"
VENV_PATH="${PROJECT_ROOT}/venv"
PYTHON_PATH="${VENV_PATH}/bin/python"

# Paths to editable packages (installed from git repositories)
# Try to detect automatically, fallback to common locations
DECOLOGR_PATH="${PROJECT_ROOT}/../decologr"
PICOMIDI_PATH="${PROJECT_ROOT}/../PicoMidi"

# If not found in sibling directories, try absolute paths
if [[ ! -d "${DECOLOGR_PATH}" ]]; then
    DECOLOGR_PATH="/Users/brooks/projects/decologr"
fi
if [[ ! -d "${PICOMIDI_PATH}" ]]; then
    PICOMIDI_PATH="/Users/brooks/projects/PicoMidi"
fi

# Resolve paths to absolute for use in executable
DECOLOGR_PATH="$(cd "${DECOLOGR_PATH}" 2>/dev/null && pwd || echo "${DECOLOGR_PATH}")"
PICOMIDI_PATH="$(cd "${PICOMIDI_PATH}" 2>/dev/null && pwd || echo "${PICOMIDI_PATH}")"

echo ""
echo "=== CONFIGURATION ==="
echo "APP_NAME: ${APP_NAME}"
echo "SCRIPT_PATH: ${SCRIPT_PATH}"
echo "ICON_PATH: ${ICON_PATH}"
echo "VENV_PATH: ${VENV_PATH}"
echo "PYTHON_PATH: ${PYTHON_PATH}"
echo "PROJECT_ROOT: ${PROJECT_ROOT}"
echo "DECOLOGR_PATH: ${DECOLOGR_PATH}"
echo "PICOMIDI_PATH: ${PICOMIDI_PATH}"
echo ""

# === VALIDATE PREREQUISITES ===
echo "🔍 Validating prerequisites..."

if [[ ! -f "${PYTHON_PATH}" ]]; then
    echo "❌ ERROR: Python not found at ${PYTHON_PATH}"
    echo "   Please ensure the virtual environment is set up."
    exit 1
fi
echo "✅ Python found: ${PYTHON_PATH}"
echo "   Python version: $("${PYTHON_PATH}" --version 2>&1)"

if [[ ! -f "${SCRIPT_PATH}" ]]; then
    echo "❌ ERROR: Main script not found: ${SCRIPT_PATH}"
    exit 1
fi
echo "✅ Main script found: ${SCRIPT_PATH}"

if [[ ! -d "${DECOLOGR_PATH}" ]]; then
    echo "⚠️  WARNING: decologr directory not found: ${DECOLOGR_PATH}"
    echo "            The app may not be able to import decologr."
else
    echo "✅ decologr found: ${DECOLOGR_PATH}"
fi

if [[ ! -d "${PICOMIDI_PATH}" ]]; then
    echo "⚠️  WARNING: picomidi directory not found: ${PICOMIDI_PATH}"
    echo "            The app may not be able to import picomidi."
else
    echo "✅ picomidi found: ${PICOMIDI_PATH}"
fi

# === DIRECTORY STRUCTURE ===
APP_DIR="${APP_NAME}.app"
CONTENTS_DIR="${APP_DIR}/Contents"
MACOS_DIR="${CONTENTS_DIR}/MacOS"
RESOURCES_DIR="${CONTENTS_DIR}/Resources"

echo ""
echo "📦 Creating bundle structure..."
echo "   APP_DIR: ${APP_DIR}"
echo "   CONTENTS_DIR: ${CONTENTS_DIR}"
echo "   MACOS_DIR: ${MACOS_DIR}"
echo "   RESOURCES_DIR: ${RESOURCES_DIR}"

# Clean up existing app if it exists
if [[ -d "${APP_DIR}" ]]; then
    echo "🗑️  Removing existing ${APP_DIR}..."
    rm -rf "${APP_DIR}"
fi

mkdir -p "${MACOS_DIR}"
mkdir -p "${RESOURCES_DIR}"
echo "✅ Directory structure created"

# === CREATE STUB EXECUTABLE ===
EXECUTABLE="${MACOS_DIR}/jdxi_editor"
echo ""
echo "📝 Creating executable stub..."
echo "   Executable: ${EXECUTABLE}"

cat << EOF > "${EXECUTABLE}"
#!/bin/bash
# Set PYTHONPATH to include project root and editable packages (decologr and picomidi)
# PROJECT_ROOT must be first so jdxi_editor module can be found
export PYTHONPATH="${PROJECT_ROOT}:${DECOLOGR_PATH}:${PICOMIDI_PATH}:\${PYTHONPATH}"
# Change to project root directory for relative imports/resources
cd "${PROJECT_ROOT}"
exec "${PYTHON_PATH}" -m jdxi_editor.main
EOF

chmod +x "${EXECUTABLE}"
echo "✅ Executable created and made executable"
echo "   Contents:"
echo "   ---"
cat "${EXECUTABLE}" | sed 's/^/   /'
echo "   ---"

# === CREATE Info.plist ===
PLIST="${CONTENTS_DIR}/Info.plist"
echo ""
echo "📝 Creating Info.plist..."
echo "   Plist: ${PLIST}"

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
echo "✅ Info.plist created"

# === COPY ICON ===
echo ""
echo "🖼️  Copying icon..."
if [[ -f "${ICON_PATH}" ]]; then
    cp "${ICON_PATH}" "${RESOURCES_DIR}/jdxi_editor.icns"
    echo "✅ Icon copied: ${ICON_PATH} -> ${RESOURCES_DIR}/jdxi_editor.icns"
else
    echo "⚠️  WARNING: Icon file not found: ${ICON_PATH}"
    echo "            App will run without custom icon."
fi

# === VERIFY APP BUNDLE ===
echo ""
echo "🔍 Verifying app bundle structure..."
if [[ ! -d "${APP_DIR}" ]]; then
    echo "❌ ERROR: App bundle was not created!"
    exit 1
fi

if [[ ! -f "${EXECUTABLE}" ]]; then
    echo "❌ ERROR: Executable was not created!"
    exit 1
fi

if [[ ! -f "${PLIST}" ]]; then
    echo "❌ ERROR: Info.plist was not created!"
    exit 1
fi

echo "✅ App bundle structure verified"
echo ""
echo "📊 App bundle contents:"
find "${APP_DIR}" -type f | sed 's/^/   /'

echo ""
echo "✅ ${APP_NAME}.app created successfully!"
echo ""
echo "📋 Summary:"
echo "   App bundle: $(pwd)/${APP_DIR}"
echo "   Executable: ${EXECUTABLE}"
echo "   Python: ${PYTHON_PATH}"
echo "   PYTHONPATH will include (in order):"
echo "     1. ${PROJECT_ROOT} (for jdxi_editor module)"
if [[ -d "${DECOLOGR_PATH}" ]]; then
    echo "     2. ${DECOLOGR_PATH}"
fi
if [[ -d "${PICOMIDI_PATH}" ]]; then
    echo "     3. ${PICOMIDI_PATH}"
fi
echo "   Working directory will be: ${PROJECT_ROOT}"
echo ""
echo "🚀 To run the app:"
echo "   open '${APP_DIR}'"
echo "   or"
echo "   ./${APP_DIR}/Contents/MacOS/jdxi_editor"
