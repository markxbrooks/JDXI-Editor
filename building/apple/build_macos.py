#!/usr/bin/env python3
"""
macOS Build System for JD-Xi Editor

Builds distributable packages for macOS:
- App Bundle (.app)
- DMG (disk image for distribution)
- PKG (installer package)

Usage:
    python build_macos.py [--app] [--dmg] [--pkg] [--all]
    
Requirements:
    - py2app: pip install py2app
    - For DMG: hdiutil (built-in macOS tool)
    - For PKG: pkgbuild (built-in macOS tool)
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path

# Import project metadata
# Navigate up from building/apple/ to project root
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from jdxi_editor.project import (
        __version__,
        __package_name__,
        __program__,
        __author__,
    )
except ImportError:
    # Fallback if running from different location
    sys.path.insert(0, str(SCRIPT_DIR.parent.parent))
    from jdxi_editor.project import (
        __version__,
        __package_name__,
        __program__,
        __author__,
    )

# Build configuration
APP_NAME = "JD-Xi Editor.app"
APP_DISPLAY_NAME = __program__
VERSION = __version__
PKG_IDENTIFIER = "com.jdxi.editor"
INSTALL_LOCATION = "/Applications"

# Directories
BUILD_DIR = PROJECT_ROOT / "build" / "macos"
DIST_DIR = PROJECT_ROOT / "dist"
VENV_PATH = PROJECT_ROOT / "venv"
PYTHON_PATH = VENV_PATH / "bin" / "python"

# Paths to editable packages (installed from git repositories)
DECOLOGR_PATH = PROJECT_ROOT.parent / "decologr"
PICOMIDI_PATH = PROJECT_ROOT.parent / "PicoMidi"

# Fallback to absolute paths if not found in sibling directories
if not DECOLOGR_PATH.exists():
    DECOLOGR_PATH = Path("/Users/brooks/projects/decologr")
if not PICOMIDI_PATH.exists():
    PICOMIDI_PATH = Path("/Users/brooks/projects/PicoMidi")


def run_command(cmd, cwd=None, check=True, shell=False, capture_output=True):
    """Run a shell command and return the result."""
    if isinstance(cmd, list):
        cmd_str = " ".join(str(c) for c in cmd)
    else:
        cmd_str = str(cmd)
    print(f"  → Running: {cmd_str}")
    
    result = subprocess.run(
        cmd,
        cwd=cwd,
        shell=shell or isinstance(cmd, str),
        capture_output=capture_output,
        text=True,
    )
    
    if check and result.returncode != 0:
        print(f"  ✗ Command failed with exit code {result.returncode}")
        if capture_output:
            if result.stderr:
                print(f"  Error: {result.stderr}")
            if result.stdout:
                print(f"  Output: {result.stdout}")
        return None
    return result


def check_dependencies():
    """Check if required build tools are installed."""
    print("\n🔍 Checking dependencies...")
    
    # Check Python virtual environment
    if not VENV_PATH.exists():
        print(f"  ✗ Virtual environment not found at {VENV_PATH}")
        print("     Please create a virtual environment first.")
        sys.exit(1)
    print(f"  ✓ Virtual environment found: {VENV_PATH}")
    
    # Check Python
    if not PYTHON_PATH.exists():
        print(f"  ✗ Python not found at {PYTHON_PATH}")
        sys.exit(1)
    
    python_version = run_command(
        [str(PYTHON_PATH), "--version"],
        check=False,
        shell=False
    )
    if python_version:
        print(f"  ✓ Python: {python_version.stdout.strip()}")
    
    # Check setup.py
    setup_py = PROJECT_ROOT / "setup.py"
    if not setup_py.exists():
        print(f"  ✗ setup.py not found at {setup_py}")
        sys.exit(1)
    print(f"  ✓ setup.py found")
    
    # Check py2app (optional, will be checked when needed)
    print("  ✓ Dependencies validated")


def clean_build_dirs():
    """Remove previous build artifacts."""
    print("\n🧹 Cleaning previous builds...")
    
    dirs_to_clean = [
        BUILD_DIR,
        PROJECT_ROOT / "pkg_build",
        PROJECT_ROOT / "jdxi_dmg",
    ]
    
    files_to_clean = [
        PROJECT_ROOT / f"JD-Xi_Editor_{VERSION}_MacOS_Universal.pkg",
        PROJECT_ROOT / f"JD-Xi_Editor_{VERSION}_MacOS_Universal.dmg",
    ]
    
    for path in dirs_to_clean:
        if path.exists():
            print(f"  Removing: {path}")
            shutil.rmtree(path)
    
    for path in files_to_clean:
        if path.exists():
            print(f"  Removing: {path}")
            path.unlink()
    
    # Also clean py2app artifacts
    py2app_build = PROJECT_ROOT / "build"
    py2app_dist = PROJECT_ROOT / "dist" / APP_NAME
    if py2app_build.exists():
        for item in py2app_build.iterdir():
            if item.is_dir() and item.name != "macos":
                print(f"  Removing: {item}")
                shutil.rmtree(item)
    
    print("  ✓ Clean complete")


def build_with_py2app():
    """Build the application using py2app."""
    print("\n🔨 Building app with py2app...")
    
    setup_py = PROJECT_ROOT / "setup.py"
    if not setup_py.exists():
        print(f"  ✗ setup.py not found: {setup_py}")
        return None
    
    # Prepare environment with PYTHONPATH to include editable packages
    env = os.environ.copy()
    
    # Add editable package paths to PYTHONPATH so py2app can find them
    pythonpath_parts = [str(PROJECT_ROOT)]
    if DECOLOGR_PATH.exists():
        pythonpath_parts.append(str(DECOLOGR_PATH.resolve()))
        print(f"  ✓ Adding decologr to PYTHONPATH: {DECOLOGR_PATH.resolve()}")
    else:
        print(f"  ⚠ decologr not found at {DECOLOGR_PATH}")
    
    if PICOMIDI_PATH.exists():
        pythonpath_parts.append(str(PICOMIDI_PATH.resolve()))
        print(f"  ✓ Adding picomidi to PYTHONPATH: {PICOMIDI_PATH.resolve()}")
    else:
        print(f"  ⚠ picomidi not found at {PICOMIDI_PATH}")
    
    # Update PYTHONPATH
    existing_pythonpath = env.get("PYTHONPATH", "")
    if existing_pythonpath:
        env["PYTHONPATH"] = ":".join(pythonpath_parts + [existing_pythonpath])
    else:
        env["PYTHONPATH"] = ":".join(pythonpath_parts)
    
    # Activate venv and run py2app
    # On macOS, we need to use the venv's Python directly
    cmd = [str(PYTHON_PATH), "setup.py", "py2app"]
    
    print("  This may take a few minutes...")
    print("  (Showing output in real-time...)")
    
    # Run py2app with real-time output for better visibility
    process = subprocess.Popen(
        cmd,
        cwd=PROJECT_ROOT,
        env=env,  # Pass the modified environment
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # Combine stderr with stdout
        text=True,
        bufsize=1,  # Line buffered
    )
    
    # Print output in real-time
    output_lines = []
    for line in process.stdout:
        line = line.rstrip()
        if line:
            print(f"    {line}")
            output_lines.append(line)
    
    # Wait for process to complete
    returncode = process.wait()
    
    if returncode != 0:
        print(f"\n  ✗ py2app build failed with exit code {returncode}")
        if output_lines:
            # Show last 30 lines for context
            print("\n  Last 30 lines of output:")
            for line in output_lines[-30:]:
                print(f"    {line}")
        return None
    
    # Verify app bundle was created
    app_bundle = DIST_DIR / APP_NAME
    if not app_bundle.exists():
        print(f"  ✗ App bundle not found at {app_bundle}")
        return None
    
    print(f"  ✓ App bundle created: {app_bundle}")
    return app_bundle


def create_app_bundle():
    """Create a simple app bundle (alternative to py2app)."""
    print("\n📦 Creating app bundle...")
    
    app_dir = Path(APP_NAME.replace(".app", ".app"))
    contents_dir = app_dir / "Contents"
    macos_dir = contents_dir / "MacOS"
    resources_dir = contents_dir / "Resources"
    
    # Clean up existing app
    if app_dir.exists():
        print(f"  Removing existing {app_dir}...")
        shutil.rmtree(app_dir)
    
    # Create directory structure
    macos_dir.mkdir(parents=True, exist_ok=True)
    resources_dir.mkdir(parents=True, exist_ok=True)
    
    # Create executable stub
    executable = macos_dir / "jdxi_editor"
    icon_path = PROJECT_ROOT / "jdxi_icon.icns"
    
    # Resolve paths to absolute
    decologr_abs = DECOLOGR_PATH.resolve() if DECOLOGR_PATH.exists() else DECOLOGR_PATH
    picomidi_abs = PICOMIDI_PATH.resolve() if PICOMIDI_PATH.exists() else PICOMIDI_PATH
    project_root_abs = PROJECT_ROOT.resolve()
    python_path_abs = PYTHON_PATH.resolve()
    
    executable_content = f"""#!/bin/bash
# Set PYTHONPATH to include project root and editable packages (decologr and picomidi)
# PROJECT_ROOT must be first so jdxi_editor module can be found
export PYTHONPATH="{project_root_abs}:{decologr_abs}:{picomidi_abs}:${{PYTHONPATH}}"
# Change to project root directory for relative imports/resources
cd "{project_root_abs}"
exec "{python_path_abs}" -m jdxi_editor.main
"""
    
    executable.write_text(executable_content)
    executable.chmod(0o755)
    print(f"  ✓ Executable created: {executable}")
    
    # Create Info.plist
    plist = contents_dir / "Info.plist"
    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>jdxi_editor</string>
    <key>CFBundleIconFile</key>
    <string>jdxi_editor.icns</string>
    <key>CFBundleIdentifier</key>
    <string>{PKG_IDENTIFIER}</string>
    <key>CFBundleName</key>
    <string>{APP_DISPLAY_NAME}</string>
    <key>CFBundleVersion</key>
    <string>{VERSION}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
</dict>
</plist>
"""
    plist.write_text(plist_content)
    print(f"  ✓ Info.plist created: {plist}")
    
    # Copy icon
    if icon_path.exists():
        icon_dest = resources_dir / "jdxi_editor.icns"
        shutil.copy2(icon_path, icon_dest)
        print(f"  ✓ Icon copied: {icon_dest}")
    else:
        print(f"  ⚠ Icon not found: {icon_path}")
    
    # Validate package paths
    if not DECOLOGR_PATH.exists():
        print(f"  ⚠ WARNING: decologr directory not found: {DECOLOGR_PATH}")
    else:
        print(f"  ✓ decologr found: {DECOLOGR_PATH}")
    
    if not PICOMIDI_PATH.exists():
        print(f"  ⚠ WARNING: picomidi directory not found: {PICOMIDI_PATH}")
    else:
        print(f"  ✓ picomidi found: {PICOMIDI_PATH}")
    
    print(f"  ✓ App bundle created: {app_dir.absolute()}")
    return app_dir.absolute()


def make_dmg(app_bundle_path):
    """Create a DMG file from the app bundle."""
    print("\n💿 Creating DMG...")
    
    if not app_bundle_path or not Path(app_bundle_path).exists():
        print("  ✗ App bundle not found, cannot create DMG")
        return None
    
    dmg_name = f"JD-Xi_Editor_{VERSION}_MacOS_Universal.dmg"
    volume_name = "JDXI Editor"
    build_dir = PROJECT_ROOT / "jdxi_dmg" / "JDXI-Editor"
    dmg_path = PROJECT_ROOT / dmg_name
    
    # Clean previous builds
    if build_dir.exists():
        print(f"  Removing existing {build_dir}...")
        shutil.rmtree(build_dir)
    
    if dmg_path.exists():
        print(f"  Removing existing {dmg_path}...")
        dmg_path.unlink()
    
    # Prepare DMG content folder
    print(f"  Creating DMG staging directory: {build_dir}")
    build_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy app bundle
    print(f"  Copying app bundle to staging directory...")
    shutil.copytree(app_bundle_path, build_dir / APP_NAME)
    print("  ✓ App bundle copied")
    
    # Create Applications symlink
    apps_link = build_dir / "Applications"
    if apps_link.exists() or apps_link.is_symlink():
        apps_link.unlink()
    apps_link.symlink_to("/Applications")
    print("  ✓ Applications symlink created")
    
    # Create DMG
    print(f"  Creating DMG: {dmg_name}...")
    cmd = [
        "hdiutil", "create",
        "-volname", volume_name,
        "-srcfolder", str(build_dir),
        "-ov",
        "-format", "UDZO",
        str(dmg_path),
    ]
    
    result = run_command(cmd, check=False)
    if result is None or result.returncode != 0:
        print("  ✗ DMG creation failed")
        return None
    
    if not dmg_path.exists():
        print("  ✗ DMG was not created")
        return None
    
    # Get DMG size
    dmg_size = shutil.disk_usage(dmg_path).used / (1024 * 1024)  # MB
    print(f"  ✓ DMG created: {dmg_path}")
    print(f"  ✓ DMG size: {dmg_size:.1f} MB")
    
    return dmg_path


def make_pkg(app_bundle_path):
    """Create a PKG installer from the app bundle."""
    print("\n📦 Creating PKG installer...")
    
    if not app_bundle_path or not Path(app_bundle_path).exists():
        print("  ✗ App bundle not found, cannot create PKG")
        return None
    
    pkg_name = f"JD-Xi_Editor_{VERSION}_MacOS_Universal.pkg"
    build_dir = PROJECT_ROOT / "pkg_build"
    install_dir = build_dir / INSTALL_LOCATION.lstrip("/")
    pkg_path = PROJECT_ROOT / pkg_name
    
    # Clean previous builds
    if build_dir.exists():
        print(f"  Removing existing {build_dir}...")
        shutil.rmtree(build_dir)
    
    if pkg_path.exists():
        print(f"  Removing existing {pkg_path}...")
        pkg_path.unlink()
    
    # Create staging directory
    print(f"  Creating staging directory: {install_dir}")
    install_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy app bundle
    print(f"  Copying app bundle to staging directory...")
    shutil.copytree(app_bundle_path, install_dir / APP_NAME)
    print("  ✓ App bundle copied")
    
    # Build PKG
    print(f"  Building PKG installer: {pkg_name}...")
    cmd = [
        "pkgbuild",
        "--root", str(build_dir),
        "--identifier", PKG_IDENTIFIER,
        "--version", VERSION,
        "--install-location", "/",
        str(pkg_path),
    ]
    
    result = run_command(cmd, check=False)
    if result is None or result.returncode != 0:
        print("  ✗ PKG creation failed")
        return None
    
    if not pkg_path.exists():
        print("  ✗ PKG was not created")
        return None
    
    # Get PKG size
    pkg_size = shutil.disk_usage(pkg_path).used / (1024 * 1024)  # MB
    print(f"  ✓ PKG created: {pkg_path}")
    print(f"  ✓ PKG size: {pkg_size:.1f} MB")
    
    # Clean up staging directory
    print("  Cleaning up staging directory...")
    shutil.rmtree(build_dir)
    
    return pkg_path


def main():
    parser = argparse.ArgumentParser(
        description=f"Build macOS packages for {APP_DISPLAY_NAME}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build_macos.py --app          Create app bundle only
  python build_macos.py --dmg          Build app and create DMG
  python build_macos.py --pkg          Build app and create PKG
  python build_macos.py --all          Build app, DMG, and PKG
  python build_macos.py                Build app with py2app (default)
"""
    )
    parser.add_argument(
        "--app",
        action="store_true",
        help="Create simple app bundle (alternative to py2app)"
    )
    parser.add_argument(
        "--dmg",
        action="store_true",
        help="Create DMG disk image"
    )
    parser.add_argument(
        "--pkg",
        action="store_true",
        help="Create PKG installer"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Build app with py2app, create DMG and PKG"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean build directories only"
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Don't clean before building"
    )
    parser.add_argument(
        "--no-py2app",
        action="store_true",
        help="Skip py2app build (use with --app for simple bundle)"
    )
    
    args = parser.parse_args()
    
    print(f"🎹 {APP_DISPLAY_NAME} v{VERSION} - macOS Build System")
    print("=" * 50)
    
    if args.clean:
        clean_build_dirs()
        print("\n✓ Clean complete")
        return
    
    # Determine what to build
    build_py2app = not args.no_py2app and not args.app
    build_simple_app = args.app
    build_dmg = args.dmg or args.all
    build_pkg = args.pkg or args.all
    
    check_dependencies()
    
    if not args.no_clean:
        clean_build_dirs()
    
    app_bundle = None
    
    # Build app bundle
    if build_py2app:
        app_bundle = build_with_py2app()
        if app_bundle is None:
            print("\n✗ py2app build failed")
            if not build_simple_app:
                sys.exit(1)
    
    if build_simple_app:
        app_bundle = create_app_bundle()
        if app_bundle is None:
            print("\n✗ App bundle creation failed")
            sys.exit(1)
    
    # Build DMG and PKG if requested
    results = []
    
    if build_dmg:
        if app_bundle:
            dmg_path = make_dmg(app_bundle)
            results.append(("DMG", dmg_path))
        else:
            print("\n⚠ Cannot create DMG: no app bundle available")
            results.append(("DMG", None))
    
    if build_pkg:
        if app_bundle:
            pkg_path = make_pkg(app_bundle)
            results.append(("PKG", pkg_path))
        else:
            print("\n⚠ Cannot create PKG: no app bundle available")
            results.append(("PKG", None))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Build Summary:")
    
    if app_bundle:
        print(f"  ✓ App Bundle: {app_bundle}")
    
    success_count = 0
    for name, path in results:
        if path:
            print(f"  ✓ {name}: {path}")
            success_count += 1
        else:
            print(f"  ✗ {name}: Failed")
    
    if results:
        print(f"\n✓ {success_count}/{len(results)} packages built successfully")
    
    if app_bundle or success_count > 0:
        print(f"\n📁 Output directory: {DIST_DIR if build_py2app else PROJECT_ROOT}")


if __name__ == "__main__":
    main()
