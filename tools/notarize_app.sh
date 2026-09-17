#!/bin/bash
# Notarize, staple, and package a Developer ID-signed build/Clayline.app.
#
# Prerequisites (one-time, interactive, must be done by the account holder):
#   xcrun notarytool store-credentials "$CLAYLINE_NOTARY_PROFILE" \
#     --apple-id <apple-id-email> --team-id 3CW95F5842 --password <app-specific-password>
#
# Build first with the Developer ID identity and hardened runtime:
#   CLAYLINE_CODESIGN_IDENTITY="Developer ID Application: Pete Katz (3CW95F5842)" make mac-app
#
# Then:
#   bash tools/notarize_app.sh
#
# Produces build/Clayline-<version>.zip (stapled app, ready to upload) and prints
# the Gatekeeper assessment.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="${1:-$ROOT/build/Clayline.app}"
PROFILE="${CLAYLINE_NOTARY_PROFILE:-clayline-notary}"
WORK="$ROOT/build/.notarize"

fail() {
  echo "notarize_app.sh: $*" >&2
  exit 1
}

[[ -d "$APP" ]] || fail "app bundle not found: $APP (run make mac-app first)"

# Read the signature once; piping codesign into grep -q under pipefail makes
# grep close the pipe on the first match and codesign fail with SIGPIPE.
SIGNATURE="$(/usr/bin/codesign -d --verbose=2 "$APP" 2>&1 || true)"
if ! grep -q "Authority=Developer ID Application" <<<"$SIGNATURE"; then
  fail "$APP is not Developer ID signed; rebuild with CLAYLINE_CODESIGN_IDENTITY set"
fi
if ! grep -q "flags=.*runtime" <<<"$SIGNATURE"; then
  fail "$APP was not signed with the hardened runtime"
fi

# Ask notarytool itself; the keychain item it stores is not a plain generic password.
if ! xcrun notarytool history --keychain-profile "$PROFILE" >/dev/null 2>&1; then
  cat >&2 <<MSG
notarize_app.sh: no notarytool keychain profile named "$PROFILE".
Store one once (interactive, requires an app-specific password for the Apple ID):
  xcrun notarytool store-credentials "$PROFILE" --apple-id <apple-id> --team-id 3CW95F5842 --password <app-specific-password>
MSG
  exit 2
fi

VERSION="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' "$APP/Contents/Info.plist")"
NAME="$(basename "$APP" .app)"
SUBMISSION="$WORK/$NAME-submission.zip"
RELEASE="$ROOT/build/$NAME-$VERSION.zip"

/bin/rm -rf "$WORK"
/bin/mkdir -p "$WORK"

echo "[1/4] Zipping $APP for submission"
/usr/bin/ditto -c -k --keepParent --norsrc --noextattr --noqtn --noacl "$APP" "$SUBMISSION"

echo "[2/4] Submitting to Apple's notary service (this waits for the verdict)"
xcrun notarytool submit "$SUBMISSION" --keychain-profile "$PROFILE" --wait --output-format plist \
  > "$WORK/submit.plist"
STATUS="$(/usr/libexec/PlistBuddy -c 'Print :status' "$WORK/submit.plist")"
SUBMISSION_ID="$(/usr/libexec/PlistBuddy -c 'Print :id' "$WORK/submit.plist")"
if [[ "$STATUS" != "Accepted" ]]; then
  xcrun notarytool log "$SUBMISSION_ID" --keychain-profile "$PROFILE" "$WORK/notary-log.json" || true
  fail "notarization status: $STATUS (see $WORK/notary-log.json)"
fi

echo "[3/4] Stapling the ticket"
xcrun stapler staple "$APP"
xcrun stapler validate "$APP"

echo "[4/4] Gatekeeper assessment and release archive"
/usr/sbin/spctl --assess --type execute --verbose=4 "$APP"
/bin/rm -f "$RELEASE"
# No extended attributes in the archive. ditto otherwise stores each file's
# attributes (macOS stamps com.apple.provenance on everything) as AppleDouble
# "._" entries; Archive Utility cannot apply those to the engine's symlinked
# libraries, leaves them behind as real files, and the added files break the
# bundle's seal, so a double-clicked download opens as "damaged".
/usr/bin/ditto -c -k --keepParent --norsrc --noextattr --noqtn --noacl "$APP" "$RELEASE"
# Read the listing once: piping unzip into grep -q under pipefail lets grep
# close the pipe on the first match, unzip dies with SIGPIPE, and the guard
# would pass a bad zip.
ZIP_LISTING="$(/usr/bin/unzip -l "$RELEASE")"
if /usr/bin/grep -q '/\._' <<<"$ZIP_LISTING"; then
  fail "$RELEASE still carries AppleDouble entries; a double-click unzip would break the seal"
fi
# Unpack it the way a person does and check what they would get.
CHECK="$WORK/unzip-check"
/bin/rm -rf "$CHECK" && /bin/mkdir -p "$CHECK"
/bin/cp "$RELEASE" "$CHECK/"
/usr/bin/open -W -g -a "Archive Utility" "$CHECK/$(/usr/bin/basename "$RELEASE")"
for _ in 1 2 3 4 5 6 7 8 9 10; do [[ -d "$CHECK/$NAME.app" ]] && break; /bin/sleep 2; done
/bin/sleep 3
/usr/bin/codesign --verify --deep --strict "$CHECK/$NAME.app" || \
  fail "the app unpacked by Archive Utility fails signature verification"
/usr/sbin/spctl --assess --type execute "$CHECK/$NAME.app" || \
  fail "Gatekeeper rejects the app unpacked by Archive Utility"
/bin/rm -rf "$CHECK"
/usr/bin/shasum -a 256 "$RELEASE"
echo "Notarized and stapled: $RELEASE"
