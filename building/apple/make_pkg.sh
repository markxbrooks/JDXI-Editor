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

# === EXTRACT VERSION FROM PROJECT.PY ===
PROJECT_PY="${PROJECT_ROOT}/jdxi_editor/project.py"
if [[ ! -f "${PROJECT_PY}" ]]; then
    echo "❌ ERROR: project.py not found at ${PROJECT_PY}"
    exit 1
fi

# Extract __version__ from project.py using Python (more reliable than regex)
VERSION=$(cd "${PROJECT_ROOT}" && python3 -c "import sys; sys.path.insert(0, '.'); from jdxi_editor.project import __version__; print(__version__)")

if [[ -z "${VERSION}" ]]; then
    echo "❌ ERROR: Could not extract __version__ from ${PROJECT_PY}"
    exit 1
fi

echo "📦 Version extracted: ${VERSION}"

# === CONFIGURATION ===
APP_NAME="JD-Xi Editor.app"
PKG_NAME="JD-Xi_Editor_${VERSION}_MacOS_Universal.pkg"
INSTALL_LOCATION="/Applications"
# This project's virtualenv is .venv; older checkouts used venv. Take
# whichever exists so the script does not stop before it starts.
if [[ -d "${PROJECT_ROOT}/.venv" ]]; then
    VENV_PATH="${PROJECT_ROOT}/.venv"
else
    VENV_PATH="${PROJECT_ROOT}/venv"
fi
APP_PATH="${PROJECT_ROOT}/dist/${APP_NAME}"
BUILD_DIR="${PROJECT_ROOT}/pkg_build"
PKG_IDENTIFIER="com.jdxi.editor"

echo ""
echo "=== CONFIGURATION ==="
echo "APP_NAME: ${APP_NAME}"
echo "PKG_NAME: ${PKG_NAME}"
echo "VERSION: ${VERSION}"
echo "INSTALL_LOCATION: ${INSTALL_LOCATION}"
echo "VENV_PATH: ${VENV_PATH}"
echo "APP_PATH: ${APP_PATH}"
echo "BUILD_DIR: ${BUILD_DIR}"
echo "PKG_IDENTIFIER: ${PKG_IDENTIFIER}"
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
if [[ ! -d "${APP_PATH}" ]]; then
    echo "❌ ERROR: App bundle not found at ${APP_PATH}"
    echo "   py2app build may have failed."
    exit 1
fi
echo "✅ App bundle created: ${APP_PATH}"

# === PREPARE PKG ===
echo ""
echo "📦 Preparing PKG..."

# Clean previous builds
if [[ -d "${BUILD_DIR}" ]]; then
    echo "🗑️  Removing existing ${BUILD_DIR} directory..."
    rm -rf "${BUILD_DIR}"
fi

if [[ -f "${PROJECT_ROOT}/${PKG_NAME}" ]]; then
    echo "🗑️  Removing existing ${PKG_NAME}..."
    rm -f "${PROJECT_ROOT}/${PKG_NAME}"
fi

# Create package root directory
echo "📁 Creating staging directory..."
mkdir -p "${BUILD_DIR}/${INSTALL_LOCATION}"

# Copy the app bundle to the staging directory
echo "📋 Copying app bundle to staging directory..."
cp -R "${APP_PATH}" "${BUILD_DIR}/${INSTALL_LOCATION}/"
echo "✅ App bundle copied"

# === BUILD PKG INSTALLER ===
echo ""
echo "🔨 Building PKG installer..."
cd "${PROJECT_ROOT}"

pkgbuild \
    --root "${BUILD_DIR}" \
    --identifier "${PKG_IDENTIFIER}" \
    --version "${VERSION}" \
    --install-location "/" \
    "${PKG_NAME}"

if [[ ! -f "${PROJECT_ROOT}/${PKG_NAME}" ]]; then
    echo "❌ ERROR: PKG was not created!"
    exit 1
fi

# Get PKG size for summary
PKG_SIZE=$(du -h "${PROJECT_ROOT}/${PKG_NAME}" | cut -f1)

# Clean up staging directory
echo "🧹 Cleaning up staging directory..."
rm -rf "${BUILD_DIR}"

echo ""
echo "✅ ${PKG_NAME} created successfully!"
echo ""
echo "📋 Summary:"
echo "   PKG file: ${PROJECT_ROOT}/${PKG_NAME}"
echo "   PKG size: ${PKG_SIZE}"
echo "   Version: ${VERSION}"
echo "   App bundle: ${APP_PATH}"
echo ""
echo "🚀 PKG is ready for distribution!"
echo "   Users can install by double-clicking the PKG file."
