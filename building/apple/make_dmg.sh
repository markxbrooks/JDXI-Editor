#!/bin/bash
set -e  # Exit on error

# === AUTOMATIC PROJECT ROOT DETECTION ===
# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "🔍 Script directory: ${SCRIPT_DIR}"

# Navigate up from building/apple/ to project root
if [[ -f "${SCRIPT_DIR}/../../setup.py" ]] || [[ -f "${SCRIPT_DIR}/../../pyproject.toml" ]]; then
    PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
elif [[ -f "${SCRIPT_DIR}/../setup.py" ]] || [[ -f "${SCRIPT_DIR}/../pyproject.toml" ]]; then
    PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
else
    # Fallback: try to find project root by looking for jdxi_editor directory
    CURRENT_DIR="$(pwd)"
    if [[ -d "${CURRENT_DIR}/jdxi_editor" ]] && [[ -f "${CURRENT_DIR}/setup.py" ]]; then
        PROJECT_ROOT="${CURRENT_DIR}"
    else
        echo "❌ ERROR: Could not detect PROJECT_ROOT automatically."
        echo "   Please run this script from the project root or set PROJECT_ROOT manually."
        exit 1
    fi
fi

echo "📁 PROJECT_ROOT detected: ${PROJECT_ROOT}"

# Verify project structure
if [[ ! -f "${PROJECT_ROOT}/setup.py" ]]; then
    echo "❌ ERROR: setup.py not found in ${PROJECT_ROOT}"
    exit 1
fi

# === CONFIGURATION ===
APP_NAME="JD-Xi Editor.app"
DMG_NAME="JD-Xi_Editor_0.9.3_MacOS_Universal.dmg"
VOLUME_NAME="JDXI Editor"
VENV_PATH="${PROJECT_ROOT}/venv"
SRC_DIR="${PROJECT_ROOT}/dist/${APP_NAME}"
BUILD_DIR="${PROJECT_ROOT}/jdxi_dmg/JDXI-Editor"

echo ""
echo "=== CONFIGURATION ==="
echo "APP_NAME: ${APP_NAME}"
echo "DMG_NAME: ${DMG_NAME}"
echo "VOLUME_NAME: ${VOLUME_NAME}"
echo "VENV_PATH: ${VENV_PATH}"
echo "SRC_DIR: ${SRC_DIR}"
echo "BUILD_DIR: ${BUILD_DIR}"
echo ""

# === VALIDATE PREREQUISITES ===
echo "🔍 Validating prerequisites..."

if [[ ! -d "${VENV_PATH}" ]]; then
    echo "❌ ERROR: Virtual environment not found at ${VENV_PATH}"
    echo "   Please create a virtual environment first."
    exit 1
fi
echo "✅ Virtual environment found: ${VENV_PATH}"

if [[ ! -f "${PROJECT_ROOT}/setup.py" ]]; then
    echo "❌ ERROR: setup.py not found: ${PROJECT_ROOT}/setup.py"
    exit 1
fi
echo "✅ setup.py found: ${PROJECT_ROOT}/setup.py"

# === BUILD APP WITH PY2APP ===
echo ""
echo "🔨 Building app with py2app..."
cd "${PROJECT_ROOT}"

# Activate virtual environment and build
source "${VENV_PATH}/bin/activate"
echo "✅ Virtual environment activated"

echo "📦 Running: python setup.py py2app"
if ! python setup.py py2app; then
    echo "❌ ERROR: py2app build failed!"
    exit 1
fi

# Verify app bundle was created
if [[ ! -d "${SRC_DIR}" ]]; then
    echo "❌ ERROR: App bundle not found at ${SRC_DIR}"
    echo "   py2app build may have failed."
    exit 1
fi
echo "✅ App bundle created: ${SRC_DIR}"

# === PREPARE DMG ===
echo ""
echo "📦 Preparing DMG..."

# Clean previous builds
if [[ -d "${PROJECT_ROOT}/jdxi_dmg" ]]; then
    echo "🗑️  Removing existing jdxi_dmg directory..."
    rm -rf "${PROJECT_ROOT}/jdxi_dmg"
fi

if [[ -f "${PROJECT_ROOT}/${DMG_NAME}" ]]; then
    echo "🗑️  Removing existing ${DMG_NAME}..."
    rm -f "${PROJECT_ROOT}/${DMG_NAME}"
fi

# Prepare .dmg content folder
echo "📁 Creating DMG staging directory: ${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"

echo "📋 Copying app bundle to staging directory..."
cp -R "${SRC_DIR}" "${BUILD_DIR}/"
echo "✅ App bundle copied"

echo "🔗 Creating Applications symlink..."
ln -s /Applications "${BUILD_DIR}/Applications"
echo "✅ Applications symlink created"

# === CREATE DMG ===
echo ""
echo "💿 Creating DMG: ${DMG_NAME}..."
cd "${PROJECT_ROOT}"

hdiutil create -volname "${VOLUME_NAME}" \
  -srcfolder "${BUILD_DIR}" \
  -ov -format UDZO \
  "${DMG_NAME}"

if [[ ! -f "${PROJECT_ROOT}/${DMG_NAME}" ]]; then
    echo "❌ ERROR: DMG was not created!"
    exit 1
fi

# Get DMG size for summary
DMG_SIZE=$(du -h "${PROJECT_ROOT}/${DMG_NAME}" | cut -f1)

echo ""
echo "✅ ${DMG_NAME} created successfully!"
echo ""
echo "📋 Summary:"
echo "   DMG file: ${PROJECT_ROOT}/${DMG_NAME}"
echo "   DMG size: ${DMG_SIZE}"
echo "   Volume name: ${VOLUME_NAME}"
echo "   App bundle: ${SRC_DIR}"
echo ""
echo "🚀 DMG is ready for distribution!"
