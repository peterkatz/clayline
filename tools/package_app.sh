#!/bin/bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SWIFT_PACKAGE="$ROOT/app/ClaylineMac"
INFO_PLIST="$SWIFT_PACKAGE/Info.plist"
ENTITLEMENTS="$SWIFT_PACKAGE/Clayline.entitlements"
ICON_SOURCE="$SWIFT_PACKAGE/Assets/ClaylineIcon.svg"
ENGINE_SPEC="$ROOT/tools/ClaylineEngine.spec"

APP_VARIANT="${CLAYLINE_APP_VARIANT:-standard}"
case "$APP_VARIANT" in
  standard)
    APP_BASENAME="Clayline"
    APP_BUNDLE_NAME="Clayline"
    APP_DISPLAY_NAME="Clayline"
    APP_BUNDLE_IDENTIFIER="com.clayline.app"
    ;;
  recovery)
    APP_BASENAME="Clayline Recovery"
    APP_BUNDLE_NAME="ClaylineRecovery"
    APP_DISPLAY_NAME="Clayline Recovery"
    APP_BUNDLE_IDENTIFIER="com.clayline.recovery"
    ;;
  *)
    echo "package_app.sh: CLAYLINE_APP_VARIANT must be 'standard' or 'recovery'" >&2
    exit 1
    ;;
esac

BUILD_ROOT="$ROOT/build"
WORK_ROOT="$BUILD_ROOT/.mac-app-work"
ENGINE_ENV="$WORK_ROOT/python-env"
ENGINE_DIST="$WORK_ROOT/engine-dist"
ENGINE_WORK="$WORK_ROOT/engine-build"
STAGE_ROOT="$WORK_ROOT/stage"
STAGED_APP="$STAGE_ROOT/$APP_BASENAME.app"
FINAL_APP="$BUILD_ROOT/$APP_BASENAME.app"

SWIFT_BINARY="$SWIFT_PACKAGE/.build/arm64-apple-macosx/release/Clayline"
APP_EXECUTABLE="$STAGED_APP/Contents/MacOS/Clayline"
SIGNED_APP_EXECUTABLE="$WORK_ROOT/Clayline-signed"
HELPER_ROOT="$STAGED_APP/Contents/Resources/Engine"
HELPER_EXECUTABLE="$HELPER_ROOT/ClaylineEngine"
SOURCE_STATIC="$ROOT/src/clayline/webui/static"

PYTHON_VERSION="${CLAYLINE_PYTHON_VERSION:-3.12.11}"
SIGNING_IDENTITY="${CLAYLINE_CODESIGN_IDENTITY:--}"

export LC_ALL=C
export LANG=C
export PYTHONHASHSEED=0
export SOURCE_DATE_EPOCH=315532800
export TZ=UTC

fail() {
  echo "package_app.sh: $*" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "required command not found: $1"
}

require_file() {
  [[ -f "$1" ]] || fail "required file not found: $1"
}

sign_resource() {
  local path="$1"
  local arguments=(--force --sign "$SIGNING_IDENTITY")
  if [[ "$SIGNING_IDENTITY" != "-" ]]; then
    arguments+=(--timestamp)
  fi
  /usr/bin/codesign "${arguments[@]}" "$path"
}

sign_executable() {
  local path="$1"
  local arguments=(--force --sign "$SIGNING_IDENTITY")
  if [[ "$SIGNING_IDENTITY" != "-" ]]; then
    arguments+=(--options runtime --timestamp)
  fi
  /usr/bin/codesign "${arguments[@]}" "$path"
}

sign_application() {
  local path="$1"
  local arguments=(
    --force
    --sign "$SIGNING_IDENTITY"
    --entitlements "$ENTITLEMENTS"
    --generate-entitlement-der
  )
  if [[ "$SIGNING_IDENTITY" != "-" ]]; then
    arguments+=(--options runtime --timestamp)
  fi
  /usr/bin/codesign "${arguments[@]}" "$path"
}

assert_arm64_macho() {
  local path="$1"
  local description
  description="$(/usr/bin/file -b "$path")"
  [[ "$description" == Mach-O* ]] || fail "expected Mach-O file: $path ($description)"
  [[ "$description" == *arm64* ]] || fail "expected arm64 Mach-O file: $path ($description)"
  [[ "$description" != *x86_64* ]] || fail "unexpected x86_64 slice: $path ($description)"
}

assert_static_asset_parity() {
  local bundled_static="$1"
  local source_inventory="$WORK_ROOT/source-static-files.txt"
  local bundled_inventory="$WORK_ROOT/bundled-static-files.txt"

  [[ -d "$SOURCE_STATIC" ]] || fail "source static directory is missing: $SOURCE_STATIC"
  [[ -d "$bundled_static" ]] || fail "bundled static directory is missing: $bundled_static"
  (
    cd "$SOURCE_STATIC"
    /usr/bin/find . -type f -print | LC_ALL=C /usr/bin/sort
  ) > "$source_inventory"
  (
    cd "$bundled_static"
    /usr/bin/find . -type f -print | LC_ALL=C /usr/bin/sort
  ) > "$bundled_inventory"
  /usr/bin/cmp -s "$source_inventory" "$bundled_inventory" || \
    fail "bundled static asset inventory differs from the current repository"

  while IFS= read -r relative; do
    relative="${relative#./}"
    /usr/bin/cmp -s "$SOURCE_STATIC/$relative" "$bundled_static/$relative" || \
      fail "bundled static asset is stale: $relative"
  done < "$source_inventory"
}

make_icon() {
  local master_png="$WORK_ROOT/AppIcon-1024.png"
  local iconset="$WORK_ROOT/AppIcon.iconset"

  /bin/rm -rf "$iconset"
  /bin/mkdir -p "$iconset"
  /usr/bin/sips -s format png -z 1024 1024 "$ICON_SOURCE" --out "$master_png" >/dev/null

  local points
  local pixels
  for points in 16 32 128 256 512; do
    pixels=$((points * 2))
    /usr/bin/sips -z "$points" "$points" "$master_png" \
      --out "$iconset/icon_${points}x${points}.png" >/dev/null
    /usr/bin/sips -z "$pixels" "$pixels" "$master_png" \
      --out "$iconset/icon_${points}x${points}@2x.png" >/dev/null
  done

  /usr/bin/iconutil -c icns "$iconset" \
    -o "$STAGED_APP/Contents/Resources/AppIcon.icns"
}

[[ "$(/usr/bin/uname -s)" == "Darwin" ]] || fail "macOS is required"
[[ "$(/usr/bin/uname -m)" == "arm64" ]] || fail "an arm64 Mac is required"

for command in uv swift sips iconutil plutil file codesign strip xattr cmp find sort; do
  require_command "$command"
done

for source in \
  "$INFO_PLIST" \
  "$ENTITLEMENTS" \
  "$ICON_SOURCE" \
  "$ENGINE_SPEC" \
  "$ROOT/tools/clayline_engine.py" \
  "$ROOT/LICENSE"; do
  require_file "$source"
done

echo "[1/7] Synchronizing the locked Python packaging environment"
/bin/mkdir -p "$WORK_ROOT" "$BUILD_ROOT"
UV_PROJECT_ENVIRONMENT="$ENGINE_ENV" uv sync \
  --locked \
  --python "$PYTHON_VERSION" \
  --no-dev \
  --extra ui \
  --group mac-app \
  --no-editable \
  --reinstall-package clayline

echo "[2/7] Freezing the managed Clayline engine"
/bin/rm -rf "$ENGINE_DIST" "$ENGINE_WORK"
/bin/mkdir -p "$ENGINE_DIST" "$ENGINE_WORK"
"$ENGINE_ENV/bin/pyinstaller" \
  --noconfirm \
  --clean \
  --distpath "$ENGINE_DIST" \
  --workpath "$ENGINE_WORK" \
  "$ENGINE_SPEC"

ENGINE_OUTPUT="$ENGINE_DIST/ClaylineEngine"
require_file "$ENGINE_OUTPUT/ClaylineEngine"

echo "[3/7] Building the native Swift shell"
swift build \
  --package-path "$SWIFT_PACKAGE" \
  --configuration release \
  --arch arm64 \
  -Xswiftc -debug-prefix-map \
  -Xswiftc "$ROOT=." \
  -Xswiftc -file-prefix-map \
  -Xswiftc "$ROOT=."
require_file "$SWIFT_BINARY"

echo "[4/7] Assembling $APP_BASENAME.app"
/bin/rm -rf "$STAGE_ROOT"
/bin/mkdir -p \
  "$STAGED_APP/Contents/MacOS" \
  "$STAGED_APP/Contents/Resources/Legal"
/usr/bin/install -m 644 "$INFO_PLIST" "$STAGED_APP/Contents/Info.plist"
if [[ "$APP_VARIANT" == "recovery" ]]; then
  /usr/bin/plutil -replace CFBundleIdentifier -string "$APP_BUNDLE_IDENTIFIER" \
    "$STAGED_APP/Contents/Info.plist"
  /usr/bin/plutil -replace CFBundleName -string "$APP_BUNDLE_NAME" \
    "$STAGED_APP/Contents/Info.plist"
  /usr/bin/plutil -replace CFBundleDisplayName -string "$APP_DISPLAY_NAME" \
    "$STAGED_APP/Contents/Info.plist"
fi
/usr/bin/install -m 755 "$SWIFT_BINARY" "$APP_EXECUTABLE"
/usr/bin/ditto "$ENGINE_OUTPUT" "$HELPER_ROOT"
/usr/bin/install -m 644 "$ROOT/LICENSE" \
  "$STAGED_APP/Contents/Resources/Legal/Clayline-GPL-3.0.txt"
make_icon
assert_static_asset_parity "$HELPER_ROOT/_internal/clayline/webui/static"

/usr/bin/plutil -lint "$STAGED_APP/Contents/Info.plist" >/dev/null
PLIST_HELPER="$(/usr/libexec/PlistBuddy -c 'Print :ClaylineEngineExecutable' \
  "$STAGED_APP/Contents/Info.plist")"
[[ "$PLIST_HELPER" == "Resources/Engine/ClaylineEngine" ]] || \
  fail "unexpected ClaylineEngineExecutable value: $PLIST_HELPER"
require_file "$STAGED_APP/Contents/$PLIST_HELPER"

assert_arm64_macho "$APP_EXECUTABLE"
assert_arm64_macho "$HELPER_EXECUTABLE"
while IFS= read -r -d '' candidate; do
  if [[ "$(/usr/bin/file -b "$candidate")" == Mach-O* ]]; then
    assert_arm64_macho "$candidate"
  fi
done < <(/usr/bin/find "$HELPER_ROOT/_internal" -type f -print0)

echo "[5/7] Signing nested code inside-out with identity: $SIGNING_IDENTITY"
/usr/bin/xattr -cr "$STAGED_APP"
while IFS= read -r -d '' candidate; do
  if [[ "$(/usr/bin/file -b "$candidate")" == Mach-O* ]]; then
    sign_resource "$candidate"
  fi
done < <(/usr/bin/find "$HELPER_ROOT/_internal" -type f -print0)
sign_executable "$HELPER_EXECUTABLE"
/usr/bin/install -m 755 "$APP_EXECUTABLE" "$SIGNED_APP_EXECUTABLE"
/usr/bin/strip -S "$SIGNED_APP_EXECUTABLE"
sign_executable "$SIGNED_APP_EXECUTABLE"
/usr/bin/install -m 755 "$SIGNED_APP_EXECUTABLE" "$APP_EXECUTABLE"
sign_application "$STAGED_APP"

echo "[6/7] Verifying signatures and the managed-helper handshake"
while IFS= read -r -d '' candidate; do
  if [[ "$(/usr/bin/file -b "$candidate")" == Mach-O* ]]; then
    /usr/bin/codesign --verify --strict "$candidate"
  fi
done < <(/usr/bin/find "$HELPER_ROOT/_internal" -type f -print0)
/usr/bin/codesign --verify --strict "$HELPER_EXECUTABLE"
/usr/bin/codesign --verify --strict "$APP_EXECUTABLE"
/usr/bin/codesign --verify --strict --verbose=2 "$STAGED_APP"

READY_LINE="$(/usr/bin/printf '%064d\n' 0 | "$HELPER_EXECUTABLE")"
[[ "$READY_LINE" == *'"schema":"clayline.desktop.ready.v1"'* ]] || \
  fail "managed helper did not emit the readiness schema"

echo "[7/7] Publishing build/$APP_BASENAME.app"
/bin/rm -rf "$FINAL_APP"
/bin/mv "$STAGED_APP" "$FINAL_APP"

echo "Built $FINAL_APP"
