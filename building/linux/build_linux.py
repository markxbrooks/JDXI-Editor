#!/usr/bin/env python3
"""
Linux Build System for JD-Xi Editor

Builds distributable packages for Linux:
- AppImage (universal Linux binary)
- .deb (Debian/Ubuntu)
- .rpm (Fedora/RHEL/CentOS)
- .snap (Snap Store)

Usage:
    python build_linux.py [--deb] [--rpm] [--snap] [--appimage] [--all]
    
Requirements:
    - PyInstaller: pip install pyinstaller
    - For .deb: dpkg-deb (apt install dpkg)
    - For .rpm: rpmbuild (dnf install rpm-build)
    - For .snap: snapcraft (snap install snapcraft --classic)
    - For AppImage: appimagetool (download from github.com/AppImage)
"""

import os
import sys
import shutil
import subprocess
import argparse
import tempfile
from pathlib import Path
from distutils.dir_util import copy_tree

# Directories - determine project root (this script is in building/linux/)
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent  # Go up two levels to project root
BUILD_DIR = PROJECT_ROOT / "build" / "linux"
DIST_DIR = PROJECT_ROOT / "dist" / "linux"

# Import project metadata
sys.path.insert(0, str(PROJECT_ROOT))
from jdxi_editor.project import __version__, __package_name__, __program__, __author__

# Build configuration
APP_NAME = "jdxi-editor"
APP_DISPLAY_NAME = __program__
VERSION = __version__
DESCRIPTION = "A MIDI editor and toolkit for the Roland JD-Xi synthesizer"
MAINTAINER = "Mark Brooks <mark.x.brooks@gmail.com>"
HOMEPAGE = "https://github.com/markxbrooks/JDXI-Editor"
LICENSE = "MIT"
CATEGORIES = "AudioVideo;Audio;Midi;Music;"


def run_command(cmd, cwd=None, check=True):
    """Run a shell command and return the result."""
    print(f"  → Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(
        cmd,
        cwd=cwd,
        shell=isinstance(cmd, str),
        capture_output=True,
        text=True
    )
    if check and result.returncode != 0:
        print(f"  ✗ Command failed: {result.stderr}")
        return None
    return result


def check_dependencies():
    """Check if required build tools are installed."""
    tools = {
        "pyinstaller": "pip install pyinstaller",
        "dpkg-deb": "apt install dpkg (for .deb)",
        "rpmbuild": "dnf install rpm-build (for .rpm)",
        "snapcraft": "snap install snapcraft --classic (for .snap)",
    }
    
    missing = []
    for tool, install_hint in tools.items():
        if shutil.which(tool) is None:
            missing.append((tool, install_hint))
    
    if missing:
        print("⚠ Some optional build tools are missing:")
        for tool, hint in missing:
            print(f"  • {tool}: {hint}")
        print()
    
    # PyInstaller is required
    if shutil.which("pyinstaller") is None:
        print("✗ PyInstaller is required. Install with: pip install pyinstaller")
        sys.exit(1)


def clean_build_dirs():
    """Remove previous build artifacts."""
    print("\n🧹 Cleaning previous builds...")
    for path in [BUILD_DIR, DIST_DIR]:
        if path.exists():
            print(f"  Removing: {path}")
            shutil.rmtree(path)
    
    # Also clean PyInstaller artifacts
    for path in [PROJECT_ROOT / "build" / __package_name__, 
                 PROJECT_ROOT / "dist" / __package_name__]:
        if path.exists():
            shutil.rmtree(path)


def build_with_pyinstaller():
    """Build the application using PyInstaller."""
    print("\n📦 Building with PyInstaller...")
    
    entry_point = PROJECT_ROOT / __package_name__ / "main.py"
    icon_file = PROJECT_ROOT / "resources" / "jdxi_icon.png"
    
    if not entry_point.exists():
        print(f"  ✗ Entry point not found: {entry_point}")
        return None
    
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--clean",
        "--onedir",
        "--windowed",
        f"--name={APP_NAME}",
        # Collect all PySide6 components
        "--collect-all=PySide6",
        "--collect-all=shiboken6",
        # Hidden imports for Qt
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=PySide6.QtGui", 
        "--hidden-import=PySide6.QtWidgets",
        "--hidden-import=PySide6.QtNetwork",
        "--hidden-import=PySide6.QtSvg",
        "--hidden-import=PySide6.QtPrintSupport",
        # Other dependencies
        "--hidden-import=numpy",
        "--hidden-import=numpy.core._methods",
        "--hidden-import=numpy.lib.format",
        "--hidden-import=mido",
        "--hidden-import=mido.backends",
        "--hidden-import=mido.backends.rtmidi",
        "--hidden-import=rtmidi",
        "--hidden-import=rtmidi._rtmidi",
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        "--hidden-import=matplotlib",
        "--hidden-import=pubsub",
        "--hidden-import=pubsub.core",
        # Decologr logging library
        "--hidden-import=decologr",
        "--collect-all=decologr",
        "--hidden-import=picomidi",
        "--collect-all=decologr",
        # Collect other packages
        "--collect-submodules=jdxi_editor",
        "--collect-data=jdxi_editor",
        # Add data files
        f"--add-data={PROJECT_ROOT / 'resources'}:resources",
    ]
    
    if icon_file.exists():
        cmd.append(f"--icon={icon_file}")
    
    cmd.append(str(entry_point))
    
    print("  This may take a few minutes...")
    result = run_command(cmd, cwd=PROJECT_ROOT)
    if result is None:
        return None
    
    pyinstaller_dist = PROJECT_ROOT / "dist" / APP_NAME
    if pyinstaller_dist.exists():
        print(f"  ✓ PyInstaller build complete: {pyinstaller_dist}")
        return pyinstaller_dist
    
    print("  ✗ PyInstaller build failed")
    return None


def create_desktop_file(dest_dir):
    """Create a .desktop file for Linux desktop integration."""
    desktop_content = f"""[Desktop Entry]
Name={APP_DISPLAY_NAME}
Comment={DESCRIPTION}
Exec={APP_NAME}
Icon={APP_NAME}
Terminal=false
Type=Application
Categories={CATEGORIES}
Keywords=MIDI;Synthesizer;Roland;JD-Xi;Editor;Music;
StartupWMClass={APP_NAME}
"""
    desktop_file = dest_dir / f"{APP_NAME}.desktop"
    desktop_file.write_text(desktop_content)
    return desktop_file


def create_icon_files(dest_dir):
    """Copy icon files to the destination directory."""
    icon_src = PROJECT_ROOT / "resources" / "jdxi_icon_512.png"
    if not icon_src.exists():
        icon_src = PROJECT_ROOT / "resources" / "jdxi_icon.png"
    
    if icon_src.exists():
        # Copy main icon
        shutil.copy(icon_src, dest_dir / f"{APP_NAME}.png")
        return True
    return False


def build_deb_package(pyinstaller_dist):
    """Build a .deb package for Debian/Ubuntu."""
    print("\n📦 Building .deb package...")
    
    if shutil.which("dpkg-deb") is None:
        print("  ⚠ dpkg-deb not found, skipping .deb build")
        return None
    
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    deb_root = BUILD_DIR / "deb"
    deb_root.mkdir(parents=True, exist_ok=True)
    
    # Create directory structure
    install_dir = deb_root / "opt" / APP_NAME
    bin_dir = deb_root / "usr" / "bin"
    desktop_dir = deb_root / "usr" / "share" / "applications"
    debian_dir = deb_root / "DEBIAN"
    pixmaps_dir = deb_root / "usr" / "share" / "pixmaps"
    
    # Create icon directories for multiple sizes
    icon_sizes = ["512x512", "256x256", "128x128", "64x64", "48x48"]
    icon_dirs = {}
    for size in icon_sizes:
        icon_dirs[size] = deb_root / "usr" / "share" / "icons" / "hicolor" / size / "apps"
    
    for d in [install_dir, bin_dir, desktop_dir, debian_dir, pixmaps_dir] + list(icon_dirs.values()):
        d.mkdir(parents=True, exist_ok=True)
    
    # Copy application files
    print("  Copying application files...")
    shutil.copytree(pyinstaller_dist, install_dir, dirs_exist_ok=True)
    
    # Create symlink script
    launcher_script = f"""#!/bin/bash
exec /opt/{APP_NAME}/{APP_NAME} "$@"
"""
    launcher_path = bin_dir / APP_NAME
    launcher_path.write_text(launcher_script)
    launcher_path.chmod(0o755)
    
    # Create desktop file
    create_desktop_file(desktop_dir)
    
    # Copy icons in multiple sizes
    icon_src = PROJECT_ROOT / "resources" / "jdxi_icon_512.png"
    if not icon_src.exists():
        icon_src = PROJECT_ROOT / "resources" / "jdxi_icon.png"
    
    if icon_src.exists():
        from PIL import Image
        img = Image.open(icon_src)
        
        # Create icons for each size
        for size_str, icon_dir in icon_dirs.items():
            size = int(size_str.split("x")[0])
            resized = img.resize((size, size), Image.LANCZOS)
            resized.save(icon_dir / f"{APP_NAME}.png", "PNG")
        
        # Also copy to pixmaps (fallback location)
        shutil.copy(icon_src, pixmaps_dir / f"{APP_NAME}.png")
        print(f"  Icons created for sizes: {', '.join(icon_sizes)}")
    
    # Calculate installed size
    installed_size = sum(f.stat().st_size for f in deb_root.rglob("*") if f.is_file()) // 1024
    
    # Create control file
    control_content = f"""Package: {APP_NAME}
Version: {VERSION}
Section: sound
Priority: optional
Architecture: amd64
Installed-Size: {installed_size}
Maintainer: {MAINTAINER}
Homepage: {HOMEPAGE}
Description: {DESCRIPTION}
 JD-Xi Editor is a comprehensive MIDI editor and toolkit
 for the Roland JD-Xi synthesizer. It provides an intuitive
 interface for editing patches, managing presets, and
 controlling the synthesizer in real-time.
"""
    (debian_dir / "control").write_text(control_content)
    
    # Create postinst script
    postinst = f"""#!/bin/bash
chmod +x /opt/{APP_NAME}/{APP_NAME}
update-desktop-database /usr/share/applications 2>/dev/null || true
gtk-update-icon-cache /usr/share/icons/hicolor 2>/dev/null || true
"""
    postinst_path = debian_dir / "postinst"
    postinst_path.write_text(postinst)
    postinst_path.chmod(0o755)
    
    # Build the package
    deb_file = DIST_DIR / f"{APP_NAME}_{VERSION}_amd64.deb"
    result = run_command(["dpkg-deb", "--build", "--root-owner-group", str(deb_root), str(deb_file)])
    
    if result and deb_file.exists():
        print(f"  ✓ Created: {deb_file}")
        return deb_file
    
    print("  ✗ Failed to create .deb package")
    return None


def build_rpm_package(pyinstaller_dist):
    """Build an .rpm package for Fedora/RHEL."""
    print("\n📦 Building .rpm package...")
    
    if shutil.which("rpmbuild") is None:
        print("  ⚠ rpmbuild not found, skipping .rpm build")
        return None
    
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    rpm_root = BUILD_DIR / "rpm"
    
    # Create RPM build structure
    for d in ["BUILD", "RPMS", "SOURCES", "SPECS", "SRPMS"]:
        (rpm_root / d).mkdir(parents=True, exist_ok=True)
    
    # Create tarball of the application
    tarball_name = f"{APP_NAME}-{VERSION}"
    tarball_dir = rpm_root / "SOURCES" / tarball_name
    tarball_dir.mkdir(parents=True, exist_ok=True)
    
    shutil.copytree(pyinstaller_dist, tarball_dir / "app", dirs_exist_ok=True)
    create_desktop_file(tarball_dir)
    create_icon_files(tarball_dir)
    
    # Create tarball
    tarball_path = rpm_root / "SOURCES" / f"{tarball_name}.tar.gz"
    run_command(f"tar -czf {tarball_path} -C {rpm_root / 'SOURCES'} {tarball_name}")
    
    # Create spec file
    spec_content = f"""Name:           {APP_NAME}
Version:        {VERSION}
Release:        1%{{?dist}}
Summary:        {DESCRIPTION}

License:        {LICENSE}
URL:            {HOMEPAGE}
Source0:        %{{name}}-%{{version}}.tar.gz

BuildArch:      x86_64
AutoReqProv:    no

%description
JD-Xi Editor is a comprehensive MIDI editor and toolkit
for the Roland JD-Xi synthesizer. It provides an intuitive
interface for editing patches, managing presets, and
controlling the synthesizer in real-time.

%prep
%setup -q

%install
mkdir -p %{{buildroot}}/opt/%{{name}}
mkdir -p %{{buildroot}}/usr/bin
mkdir -p %{{buildroot}}/usr/share/applications
mkdir -p %{{buildroot}}/usr/share/icons/hicolor/512x512/apps

cp -r app/* %{{buildroot}}/opt/%{{name}}/
cp %{{name}}.desktop %{{buildroot}}/usr/share/applications/
cp %{{name}}.png %{{buildroot}}/usr/share/icons/hicolor/512x512/apps/ 2>/dev/null || true

cat > %{{buildroot}}/usr/bin/%{{name}} << 'EOF'
#!/bin/bash
exec /opt/%{{name}}/%{{name}} "$@"
EOF
chmod 755 %{{buildroot}}/usr/bin/%{{name}}

%files
/opt/%{{name}}
/usr/bin/%{{name}}
/usr/share/applications/%{{name}}.desktop
/usr/share/icons/hicolor/512x512/apps/%{{name}}.png

%post
update-desktop-database /usr/share/applications 2>/dev/null || true
gtk-update-icon-cache /usr/share/icons/hicolor 2>/dev/null || true

%changelog
* {subprocess.getoutput("date '+%a %b %d %Y'")} {MAINTAINER} - {VERSION}-1
- Initial package
"""
    spec_file = rpm_root / "SPECS" / f"{APP_NAME}.spec"
    spec_file.write_text(spec_content)
    
    # Build RPM
    result = run_command([
        "rpmbuild",
        "-bb",
        f"--define=_topdir {rpm_root}",
        str(spec_file)
    ])
    
    # Find and move the RPM
    rpm_files = list((rpm_root / "RPMS").rglob("*.rpm"))
    if rpm_files:
        rpm_file = DIST_DIR / rpm_files[0].name
        shutil.copy(rpm_files[0], rpm_file)
        print(f"  ✓ Created: {rpm_file}")
        return rpm_file
    
    print("  ✗ Failed to create .rpm package")
    return None


def build_snap_package():
    """Build a .snap package."""
    print("\n📦 Building .snap package...")
    
    if shutil.which("snapcraft") is None:
        print("  ⚠ snapcraft not found, skipping .snap build")
        print("  Install with: snap install snapcraft --classic")
        return None
    
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check if snapcraft.yaml exists
    snap_dir = PROJECT_ROOT / "snap"
    snapcraft_yaml = snap_dir / "snapcraft.yaml"
    
    if not snapcraft_yaml.exists():
        print(f"  ⚠ {snapcraft_yaml} not found, please create it first")
        return None
    
    # Run snapcraft
    result = run_command(["snapcraft", "--destructive-mode"], cwd=PROJECT_ROOT)
    
    # Find the created snap
    snap_files = list(PROJECT_ROOT.glob("*.snap"))
    if snap_files:
        snap_file = DIST_DIR / snap_files[0].name
        shutil.move(snap_files[0], snap_file)
        print(f"  ✓ Created: {snap_file}")
        return snap_file
    
    print("  ✗ Failed to create .snap package")
    return None


def build_appimage(pyinstaller_dist):
    """Build an AppImage."""
    print("\n📦 Building AppImage...")
    
    # Check for appimagetool (multiple possible locations)
    appimagetool = shutil.which("appimagetool") or shutil.which("appimagetool-x86_64.AppImage")
    
    # Check for extracted appimagetool in project directory
    extracted_tool = PROJECT_ROOT / "appimagetool-extracted" / "AppRun"
    if appimagetool is None and extracted_tool.exists():
        appimagetool = str(extracted_tool)
        print(f"  Using extracted appimagetool: {appimagetool}")
    
    if appimagetool is None:
        print("  ⚠ appimagetool not found, skipping AppImage build")
        print("  Download from: https://github.com/AppImage/AppImageKit/releases")
        return None
    
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    appdir = BUILD_DIR / "AppDir"
    
    if appdir.exists():
        shutil.rmtree(appdir)
    
    # Create AppDir structure
    usr_bin = appdir / "usr" / "bin"
    usr_lib = appdir / "usr" / "lib"
    usr_share_apps = appdir / "usr" / "share" / "applications"
    usr_share_icons = appdir / "usr" / "share" / "icons" / "hicolor" / "512x512" / "apps"
    
    for d in [usr_bin, usr_lib, usr_share_apps, usr_share_icons]:
        d.mkdir(parents=True, exist_ok=True)
    
    # Copy application
    shutil.copytree(pyinstaller_dist, usr_lib / APP_NAME, dirs_exist_ok=True)
    
    # Create wrapper script in usr/bin
    # HERE will be /path/to/AppDir/usr/bin, so we go up two levels to AppDir root
    wrapper = f"""#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${{SELF%/*}}
APPDIR=${{HERE%/usr/bin}}
export LD_LIBRARY_PATH="${{APPDIR}}/usr/lib/{APP_NAME}:${{LD_LIBRARY_PATH}}"
exec "${{APPDIR}}/usr/lib/{APP_NAME}/{APP_NAME}" "$@"
"""
    wrapper_path = usr_bin / APP_NAME
    wrapper_path.write_text(wrapper)
    wrapper_path.chmod(0o755)
    
    # Create AppRun at AppDir root
    apprun = f"""#!/bin/bash
SELF=$(readlink -f "$0")
APPDIR=${{SELF%/*}}
export LD_LIBRARY_PATH="${{APPDIR}}/usr/lib/{APP_NAME}:${{LD_LIBRARY_PATH}}"
exec "${{APPDIR}}/usr/lib/{APP_NAME}/{APP_NAME}" "$@"
"""
    apprun_path = appdir / "AppRun"
    apprun_path.write_text(apprun)
    apprun_path.chmod(0o755)
    
    # Create desktop file
    create_desktop_file(appdir)
    shutil.copy(appdir / f"{APP_NAME}.desktop", usr_share_apps)
    
    # Copy icon
    create_icon_files(appdir)
    icon_src = appdir / f"{APP_NAME}.png"
    if icon_src.exists():
        shutil.copy(icon_src, usr_share_icons)
    
    # Build AppImage
    appimage_file = DIST_DIR / f"{APP_NAME}-{VERSION}-x86_64.AppImage"
    
    env = os.environ.copy()
    env["ARCH"] = "x86_64"
    
    result = subprocess.run(
        [appimagetool, str(appdir), str(appimage_file)],
        env=env,
        capture_output=True,
        text=True
    )
    
    if appimage_file.exists():
        appimage_file.chmod(0o755)
        print(f"  ✓ Created: {appimage_file}")
        return appimage_file
    
    print("  ✗ Failed to create AppImage")
    if result.stderr:
        print(f"  Error: {result.stderr}")
    return None


def main():
    parser = argparse.ArgumentParser(
        description=f"Build Linux packages for {APP_DISPLAY_NAME}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build_linux.py --deb          Build only .deb package
  python build_linux.py --rpm          Build only .rpm package  
  python build_linux.py --snap         Build only .snap package
  python build_linux.py --appimage     Build only AppImage
  python build_linux.py --all          Build all package types
  python build_linux.py                Build .deb and AppImage (default)
"""
    )
    parser.add_argument("--deb", action="store_true", help="Build .deb package")
    parser.add_argument("--rpm", action="store_true", help="Build .rpm package")
    parser.add_argument("--snap", action="store_true", help="Build .snap package")
    parser.add_argument("--appimage", action="store_true", help="Build AppImage")
    parser.add_argument("--all", action="store_true", help="Build all package types")
    parser.add_argument("--clean", action="store_true", help="Clean build directories only")
    parser.add_argument("--no-clean", action="store_true", help="Don't clean before building")
    
    args = parser.parse_args()
    
    print(f"🎹 {APP_DISPLAY_NAME} v{VERSION} - Linux Build System")
    print("=" * 50)
    
    if args.clean:
        clean_build_dirs()
        print("\n✓ Clean complete")
        return
    
    # Default: build deb and appimage
    if not any([args.deb, args.rpm, args.snap, args.appimage, args.all]):
        args.deb = True
        args.appimage = True
    
    if args.all:
        args.deb = args.rpm = args.snap = args.appimage = True
    
    check_dependencies()
    
    if not args.no_clean:
        clean_build_dirs()
    
    # Build with PyInstaller first (needed for deb, rpm, appimage)
    pyinstaller_dist = None
    if args.deb or args.rpm or args.appimage:
        pyinstaller_dist = build_with_pyinstaller()
        if pyinstaller_dist is None:
            print("\n✗ PyInstaller build failed, cannot continue")
            sys.exit(1)
    
    results = []
    
    if args.deb and pyinstaller_dist:
        result = build_deb_package(pyinstaller_dist)
        results.append(("DEB", result))
    
    if args.rpm and pyinstaller_dist:
        result = build_rpm_package(pyinstaller_dist)
        results.append(("RPM", result))
    
    if args.snap:
        result = build_snap_package()
        results.append(("Snap", result))
    
    if args.appimage and pyinstaller_dist:
        result = build_appimage(pyinstaller_dist)
        results.append(("AppImage", result))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Build Summary:")
    success_count = 0
    for name, path in results:
        if path:
            print(f"  ✓ {name}: {path}")
            success_count += 1
        else:
            print(f"  ✗ {name}: Failed")
    
    print(f"\n✓ {success_count}/{len(results)} packages built successfully")
    
    if success_count > 0:
        print(f"\n📁 Output directory: {DIST_DIR}")


if __name__ == "__main__":
    main()

