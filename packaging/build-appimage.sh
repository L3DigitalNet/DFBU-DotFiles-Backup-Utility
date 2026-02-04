#!/usr/bin/env bash
#
# Build DFBU AppImage
#
# Requirements:
#   - uv (Python package manager)
#   - PyInstaller (installed as dev dependency)
#   - appimagetool (downloaded automatically if not found)
#
# Usage: ./packaging/build-appimage.sh
# Output: dist/DFBU-x86_64.AppImage
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILD_DIR="$PROJECT_ROOT/build/appimage"
APPDIR="$BUILD_DIR/DFBU.AppDir"
DIST_DIR="$PROJECT_ROOT/dist"
ARCH="$(uname -m)"

echo "=== DFBU AppImage Builder ==="
echo "Project root: $PROJECT_ROOT"
echo "Architecture: $ARCH"
echo ""

# --- Step 1: Clean previous builds ---
echo "[1/6] Cleaning previous builds..."
rm -rf "$BUILD_DIR" "$DIST_DIR/dfbu" "$DIST_DIR/DFBU-$ARCH.AppImage"
mkdir -p "$BUILD_DIR" "$DIST_DIR"

# --- Step 2: Run PyInstaller ---
echo "[2/6] Running PyInstaller..."
cd "$PROJECT_ROOT"
uv run pyinstaller packaging/dfbu.spec --noconfirm --distpath "$DIST_DIR" --workpath "$BUILD_DIR/pyinstaller-work"
echo "  PyInstaller output: $DIST_DIR/dfbu/"

# --- Step 3: Assemble AppDir ---
echo "[3/6] Assembling AppDir..."
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/applications"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$APPDIR/usr/share/icons/hicolor/scalable/apps"
mkdir -p "$APPDIR/usr/share/metainfo"

# Copy frozen application into AppDir
cp -r "$DIST_DIR/dfbu/"* "$APPDIR/usr/bin/"

# Copy desktop integration files
cp "$SCRIPT_DIR/com.l3digital.dfbu.desktop" "$APPDIR/usr/share/applications/"
cp "$SCRIPT_DIR/com.l3digital.dfbu.desktop" "$APPDIR/com.l3digital.dfbu.desktop"
cp "$SCRIPT_DIR/com.l3digital.dfbu.appdata.xml" "$APPDIR/usr/share/metainfo/"

# Copy icons
cp "$PROJECT_ROOT/DFBU/resources/icons/dfbu.svg" "$APPDIR/usr/share/icons/hicolor/scalable/apps/com.l3digital.dfbu.svg"
cp "$PROJECT_ROOT/DFBU/resources/icons/dfbu-256.png" "$APPDIR/usr/share/icons/hicolor/256x256/apps/com.l3digital.dfbu.png"

# AppImage requires icon at root of AppDir
cp "$PROJECT_ROOT/DFBU/resources/icons/dfbu-256.png" "$APPDIR/com.l3digital.dfbu.png"

# --- Step 4: Create AppRun script ---
echo "[4/6] Creating AppRun script..."
cat > "$APPDIR/AppRun" << 'APPRUN_EOF'
#!/usr/bin/env bash
# AppRun - Entry point for DFBU AppImage
SELF_DIR="$(dirname "$(readlink -f "$0")")"
exec "$SELF_DIR/usr/bin/dfbu" "$@"
APPRUN_EOF
chmod +x "$APPDIR/AppRun"

# --- Step 5: Download appimagetool if needed ---
echo "[5/6] Checking for appimagetool..."
APPIMAGETOOL="$BUILD_DIR/appimagetool-$ARCH.AppImage"
if [ ! -f "$APPIMAGETOOL" ]; then
    echo "  Downloading appimagetool..."
    wget -q -O "$APPIMAGETOOL" \
        "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-$ARCH.AppImage"
    chmod +x "$APPIMAGETOOL"
fi

# --- Step 6: Build AppImage ---
echo "[6/6] Building AppImage..."
ARCH="$ARCH" "$APPIMAGETOOL" "$APPDIR" "$DIST_DIR/DFBU-$ARCH.AppImage"

echo ""
echo "=== Build Complete ==="
echo "AppImage: $DIST_DIR/DFBU-$ARCH.AppImage"
echo "Size: $(du -h "$DIST_DIR/DFBU-$ARCH.AppImage" | cut -f1)"
echo ""
echo "Test it with:"
echo "  chmod +x $DIST_DIR/DFBU-$ARCH.AppImage"
echo "  $DIST_DIR/DFBU-$ARCH.AppImage"
