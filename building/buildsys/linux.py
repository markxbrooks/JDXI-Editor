"""
Linux Builder Module

Builds distributable packages for Linux:
- .deb (Debian/Ubuntu)
- AppImage (universal Linux binary)
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

from decologr import Decologr as log, setup_logging

# Import project metadata
try:
    from jdxi_editor.project import (
        __version__,
        __package_name__,
        __program__,
        __author__,
    )
except ImportError:
    # Will be set from context
    __version__ = "0.0.0"
    __package_name__ = "jdxi_editor"
    __program__ = "JD-Xi Editor"
    __author__ = "Mark Brooks"

# Build configuration
APP_NAME = "jdxi-editor"
DESCRIPTION = "A MIDI editor and toolkit for the Roland JD-Xi synthesizer"
MAINTAINER = "Mark Brooks <mark.x.brooks@gmail.com>"
HOMEPAGE = "https://github.com/markxbrooks/JDXI-Editor"
LICENSE = "MIT"
CATEGORIES = "AudioVideo;Audio;Midi;Music;"


def build(ctx):
    """Main build entry point called by buildsys."""
    setup_logging(project_name="linux builder", use_rich=True)
    
    project_root = ctx.project_root
    build_dir = project_root / "build" / "linux"
    dist_dir = project_root / "dist" / "linux"
    
    log.message(f"🎹 {__program__} v{__version__} - Linux Build System")
    log.message("=" * 50)
    
    # Clean previous builds
    clean_build_dirs(build_dir, dist_dir, project_root)
    
    # Build with PyInstaller
    pyinstaller_dist = build_with_pyinstaller(project_root)
    if pyinstaller_dist is None:
        raise RuntimeError("PyInstaller build failed")
    
    # Build .deb package
    deb_file = build_deb_package(project_root, pyinstaller_dist, build_dir, dist_dir)
    
    # Build AppImage
    appimage_file = build_appimage(project_root, pyinstaller_dist, build_dir, dist_dir)
    
    # Summary
    log.message("\n" + "=" * 50)
    log.message("📋 Build Summary:")
    if deb_file:
        log.message(f"  ✓ DEB: {deb_file}")
    if appimage_file:
        log.message(f"  ✓ AppImage: {appimage_file}")
    log.message(f"\n📁 Output directory: {dist_dir}")


def clean_build_dirs(build_dir, dist_dir, project_root):
    """Remove previous build artifacts."""
    log.message("\n🧹 Cleaning previous builds...")
    
    for path in [build_dir, dist_dir]:
        if path.exists():
            log.message(f"  Removing: {path}")
            shutil.rmtree(path)
    
    # Also clean PyInstaller artifacts
    for path in [project_root / "build" / __package_name__, 
                 project_root / "dist" / __package_name__,
                 project_root / "dist" / APP_NAME]:
        if path.exists():
            shutil.rmtree(path)


def build_with_pyinstaller(project_root):
    """Build the application using PyInstaller."""
    log.message("\n📦 Building with PyInstaller...")
    
    entry_point = project_root / __package_name__ / "main.py"
    icon_file = project_root / "resources" / "jdxi_icon.png"
    
    if not entry_point.exists():
        log.error(f"Entry point not found: {entry_point}")
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
        "--collect-all=decologr",
        # Hidden imports
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=PySide6.QtGui", 
        "--hidden-import=PySide6.QtWidgets",
        "--hidden-import=PySide6.QtNetwork",
        "--hidden-import=PySide6.QtSvg",
        "--hidden-import=PySide6.QtPrintSupport",
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
        "--hidden-import=decologr",
        # Collect submodules
        "--collect-submodules=jdxi_editor",
        "--collect-data=jdxi_editor",
        f"--add-data={project_root / 'resources'}:resources",
    ]
    
    if icon_file.exists():
        cmd.append(f"--icon={icon_file}")
    
    cmd.append(str(entry_point))
    
    log.message("  This may take a few minutes...")
    result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)
    
    if result.returncode != 0:
        log.error(f"PyInstaller failed: {result.stderr}")
        return None
    
    pyinstaller_dist = project_root / "dist" / APP_NAME
    if pyinstaller_dist.exists():
        log.message(f"  ✓ PyInstaller build complete: {pyinstaller_dist}")
        return pyinstaller_dist
    
    log.error("PyInstaller build failed - output not found")
    return None


def create_desktop_file(dest_dir):
    """Create a .desktop file for Linux desktop integration."""
    desktop_content = f"""[Desktop Entry]
Name={__program__}
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


def build_deb_package(project_root, pyinstaller_dist, build_dir, dist_dir):
    """Build a .deb package for Debian/Ubuntu."""
    log.message("\n📦 Building .deb package...")
    
    if shutil.which("dpkg-deb") is None:
        log.warning("dpkg-deb not found, skipping .deb build")
        return None
    
    dist_dir.mkdir(parents=True, exist_ok=True)
    deb_root = build_dir / "deb"
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
    log.message("  Copying application files...")
    shutil.copytree(pyinstaller_dist, install_dir, dirs_exist_ok=True)
    
    # Create launcher script
    launcher_script = f"""#!/bin/bash
exec /opt/{APP_NAME}/{APP_NAME} "$@"
"""
    launcher_path = bin_dir / APP_NAME
    launcher_path.write_text(launcher_script)
    launcher_path.chmod(0o755)
    
    # Create desktop file
    create_desktop_file(desktop_dir)
    
    # Copy icons in multiple sizes
    icon_src = project_root / "resources" / "jdxi_icon_512.png"
    if not icon_src.exists():
        icon_src = project_root / "resources" / "jdxi_icon.png"
    
    if icon_src.exists():
        try:
            from PIL import Image
            img = Image.open(icon_src)
            
            for size_str, icon_dir in icon_dirs.items():
                size = int(size_str.split("x")[0])
                resized = img.resize((size, size), Image.LANCZOS)
                resized.save(icon_dir / f"{APP_NAME}.png", "PNG")
            
            shutil.copy(icon_src, pixmaps_dir / f"{APP_NAME}.png")
            log.message(f"  Icons created for sizes: {', '.join(icon_sizes)}")
        except ImportError:
            shutil.copy(icon_src, pixmaps_dir / f"{APP_NAME}.png")
    
    # Calculate installed size
    installed_size = sum(f.stat().st_size for f in deb_root.rglob("*") if f.is_file()) // 1024
    
    # Create control file
    control_content = f"""Package: {APP_NAME}
Version: {__version__}
Section: sound
Priority: optional
Architecture: amd64
Installed-Size: {installed_size}
Maintainer: {MAINTAINER}
Homepage: {HOMEPAGE}
Description: {DESCRIPTION}
 JD-Xi Editor is a comprehensive MIDI editor and toolkit
 for the Roland JD-Xi synthesizer.
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
    deb_file = dist_dir / f"{APP_NAME}_{__version__}_amd64.deb"
    result = subprocess.run(
        ["dpkg-deb", "--build", "--root-owner-group", str(deb_root), str(deb_file)],
        capture_output=True, text=True
    )
    
    if result.returncode == 0 and deb_file.exists():
        log.message(f"  ✓ Created: {deb_file}")
        return deb_file
    
    log.error("Failed to create .deb package")
    return None


def build_appimage(project_root, pyinstaller_dist, build_dir, dist_dir):
    """Build an AppImage."""
    log.message("\n📦 Building AppImage...")
    
    # Check for appimagetool
    appimagetool = shutil.which("appimagetool") or shutil.which("appimagetool-x86_64.AppImage")
    
    # Check for extracted appimagetool in project directory
    extracted_tool = project_root / "appimagetool-extracted" / "AppRun"
    if appimagetool is None and extracted_tool.exists():
        appimagetool = str(extracted_tool)
        log.message(f"  Using extracted appimagetool: {appimagetool}")
    
    if appimagetool is None:
        log.warning("appimagetool not found, skipping AppImage build")
        return None
    
    dist_dir.mkdir(parents=True, exist_ok=True)
    appdir = build_dir / "AppDir"
    
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
    
    # Create wrapper script
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
    
    # Create AppRun
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
    icon_src = project_root / "resources" / "jdxi_icon_512.png"
    if not icon_src.exists():
        icon_src = project_root / "resources" / "jdxi_icon.png"
    if icon_src.exists():
        shutil.copy(icon_src, appdir / f"{APP_NAME}.png")
        shutil.copy(icon_src, usr_share_icons / f"{APP_NAME}.png")
    
    # Build AppImage
    appimage_file = dist_dir / f"{APP_NAME}-{__version__}-x86_64.AppImage"
    
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
        log.message(f"  ✓ Created: {appimage_file}")
        return appimage_file
    
    log.error("Failed to create AppImage")
    return None


if __name__ == "__main__":
    from .context import BuildContext
    build(BuildContext())
