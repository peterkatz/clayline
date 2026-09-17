from __future__ import annotations

import json
import plistlib
import re
from pathlib import Path

from scripts.verify_macos_app import (
    BUNDLED_GALLERY_RELATIVE,
    BUNDLED_STATIC_RELATIVE,
    GALLERY_MANIFEST,
    Audit,
    _audit_gallery_parity,
    _audit_plist,
    _audit_static_asset_parity,
    _audit_tree_for_leaks,
)

ROOT = Path(__file__).resolve().parents[1]


def _write_assets(root: Path, assets: dict[str, bytes]) -> None:
    for relative, payload in assets.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)


def test_static_asset_audit_requires_exact_inventory_and_bytes(tmp_path: Path) -> None:
    source = tmp_path / "source-static"
    app = tmp_path / "Clayline.app"
    bundled = app / BUNDLED_STATIC_RELATIVE
    assets = {
        "app.js": b"const pageMode = 'stack';\n",
        "app.css": b".stack { display: grid; }\n",
        "nested/license.txt": b"license\n",
    }
    _write_assets(source, assets)
    _write_assets(bundled, assets)

    exact = Audit()
    _audit_static_asset_parity(app, exact, source_static=source)
    assert not exact.failures

    (bundled / "app.js").write_bytes(b"const pageMode = 'bed';\n")
    stale = Audit()
    _audit_static_asset_parity(app, stale, source_static=source)
    assert any(
        "bundled static asset is stale: app.js" in failure
        and "repository sha256=" in failure
        and "bundle sha256=" in failure
        for failure in stale.failures
    )

    (bundled / "unexpected.js").write_bytes(b"unexpected\n")
    inventory = Audit()
    _audit_static_asset_parity(app, inventory, source_static=source)
    assert any(
        "inventory differs" in failure and "unexpected.js" in failure
        for failure in inventory.failures
    )


def _synthetic_gallery(tmp_path: Path) -> tuple[Path, Path, Path]:
    """A small repository with a manifest, and an app bundle that carries it faithfully."""

    source_root = tmp_path / "repo"
    drawings = {
        "examples/first/knot.svg": b"<svg><path d='M0 0L9 9'/></svg>\n",
        "examples/first/cross.svg": b"<svg><path d='M1 1L8 8'/></svg>\n",
        "examples/second/owl.svg": b"<svg><path d='M2 2L7 7'/></svg>\n",
    }
    _write_assets(source_root, drawings)
    manifest_path = source_root / "examples" / "gallery-manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "schema": "clayline.gallery.v1",
                "sources": ["examples/first", "examples/second"],
                "categories": [
                    {
                        "folder": "Celtic",
                        "files": ["examples/first/knot.svg", "examples/first/cross.svg"],
                    },
                    {"folder": "Animals & Birds", "files": ["examples/second/owl.svg"]},
                ],
            }
        ),
        encoding="utf-8",
    )
    app = tmp_path / "Clayline.app"
    _write_assets(
        app / BUNDLED_GALLERY_RELATIVE,
        {
            "Celtic/knot.svg": drawings["examples/first/knot.svg"],
            "Celtic/cross.svg": drawings["examples/first/cross.svg"],
            "Animals & Birds/owl.svg": drawings["examples/second/owl.svg"],
        },
    )
    return app, manifest_path, source_root


def _gallery_failures(app: Path, manifest_path: Path, source_root: Path) -> list[str]:
    audit = Audit()
    _audit_gallery_parity(app, audit, manifest_path=manifest_path, source_root=source_root)
    return audit.failures


def test_gallery_audit_accepts_a_faithful_bundle(tmp_path: Path) -> None:
    app, manifest_path, source_root = _synthetic_gallery(tmp_path)

    audit = Audit()
    _audit_gallery_parity(app, audit, manifest_path=manifest_path, source_root=source_root)

    assert not audit.failures
    assert audit.checks >= 3


def test_gallery_audit_rejects_a_missing_drawing(tmp_path: Path) -> None:
    app, manifest_path, source_root = _synthetic_gallery(tmp_path)
    (app / BUNDLED_GALLERY_RELATIVE / "Celtic" / "knot.svg").unlink()

    failures = _gallery_failures(app, manifest_path, source_root)

    assert any(
        "inventory differs" in failure and "missing=['Celtic/knot.svg']" in failure
        for failure in failures
    )


def test_gallery_audit_rejects_anything_extra(tmp_path: Path) -> None:
    app, manifest_path, source_root = _synthetic_gallery(tmp_path)
    bundled = app / BUNDLED_GALLERY_RELATIVE

    (bundled / "Celtic" / "stray.svg").write_bytes(b"<svg/>\n")
    failures = _gallery_failures(app, manifest_path, source_root)
    assert any(
        "inventory differs" in failure and "extra=['Celtic/stray.svg']" in failure
        for failure in failures
    )
    (bundled / "Celtic" / "stray.svg").unlink()

    # Nothing is ignored: a Finder leftover or an empty folder shows in the Open panel too.
    (bundled / ".DS_Store").write_bytes(b"\x00")
    failures = _gallery_failures(app, manifest_path, source_root)
    assert any("extra=['.DS_Store']" in failure for failure in failures)
    (bundled / ".DS_Store").unlink()

    (bundled / "Unsorted").mkdir()
    failures = _gallery_failures(app, manifest_path, source_root)
    assert any(
        "folders differ" in failure and "extra=['Unsorted']" in failure for failure in failures
    )
    (bundled / "Unsorted").rmdir()

    (bundled / "Celtic" / "alias.svg").symlink_to(bundled / "Celtic" / "knot.svg")
    failures = _gallery_failures(app, manifest_path, source_root)
    assert any("not a plain file: Celtic/alias.svg" in failure for failure in failures)
    (bundled / "Celtic" / "alias.svg").unlink()

    assert not _gallery_failures(app, manifest_path, source_root)


def test_gallery_audit_rejects_a_changed_byte(tmp_path: Path) -> None:
    app, manifest_path, source_root = _synthetic_gallery(tmp_path)
    drawing = app / BUNDLED_GALLERY_RELATIVE / "Animals & Birds" / "owl.svg"
    payload = bytearray(drawing.read_bytes())
    payload[-2] ^= 0x01
    drawing.write_bytes(bytes(payload))

    failures = _gallery_failures(app, manifest_path, source_root)

    assert any(
        "bundled gallery drawing differs from its source: Animals & Birds/owl.svg" in failure
        and "repository sha256=" in failure
        and "bundle sha256=" in failure
        for failure in failures
    )


def test_gallery_audit_rejects_a_bundle_without_a_gallery(tmp_path: Path) -> None:
    app, manifest_path, source_root = _synthetic_gallery(tmp_path)
    for path in sorted((app / BUNDLED_GALLERY_RELATIVE).rglob("*"), reverse=True):
        path.rmdir() if path.is_dir() else path.unlink()
    (app / BUNDLED_GALLERY_RELATIVE).rmdir()

    failures = _gallery_failures(app, manifest_path, source_root)

    assert any("bundle gallery directory is missing" in failure for failure in failures)

    verifier = (ROOT / "scripts" / "verify_macos_app.py").read_text(encoding="utf-8")
    assert "    _audit_gallery_parity(app, audit)\n" in verifier.split("def audit_app(")[1]


def test_the_real_gallery_passes_the_parity_and_leak_audits(tmp_path: Path) -> None:
    """The real folder names and drawings must not trip the bundle's own leak audit."""

    manifest = json.loads(GALLERY_MANIFEST.read_text(encoding="utf-8"))
    app = tmp_path / "Clayline.app"
    for category in manifest["categories"]:
        for listed in category["files"]:
            _write_assets(
                app / BUNDLED_GALLERY_RELATIVE / category["folder"],
                {Path(listed).name: (ROOT / listed).read_bytes()},
            )

    parity = Audit()
    _audit_gallery_parity(app, parity)
    assert not parity.failures

    leaks = Audit()
    _audit_tree_for_leaks(app, leaks)
    assert not leaks.failures


def test_packager_builds_the_gallery_before_anything_is_signed() -> None:
    script = (ROOT / "tools" / "package_app.sh").read_text(encoding="utf-8")
    lines = script.splitlines()

    assert 'GALLERY_BUILDER="$ROOT/tools/build_gallery.py"' in script
    function_body = script.split("build_gallery() {", 1)[1].split("\n}\n", 1)[0]
    assert '"$PACKAGING_PYTHON" "$GALLERY_BUILDER" --out "$gallery"' in function_body
    assert "fail " in function_body
    assert "-name '*.svg'" in function_body

    def first_line(pattern: str) -> int:
        return next(index for index, line in enumerate(lines) if re.match(pattern, line))

    license_install = first_line(r"/usr/bin/install -m 644 \"\$ROOT/LICENSE\"")
    gallery_call = first_line(r"build_gallery \"\$STAGED_APP/Contents/Resources/Gallery\"$")
    attribute_sweep = first_line(r"/usr/bin/xattr -cr \"\$STAGED_APP\"")
    first_signing = first_line(r"\s*(sign_resource|sign_executable|sign_application) ")
    assert license_install < gallery_call < attribute_sweep < first_signing
    # Both variants take the same path through the script, so Recovery gets it too.
    assert not any("APP_VARIANT" in line for line in lines[license_install : gallery_call + 1])


def test_packager_reinstalls_local_project_and_checks_staged_bundle() -> None:
    script = (ROOT / "tools" / "package_app.sh").read_text(encoding="utf-8")

    assert "--reinstall-package clayline" in script
    assert 'assert_static_asset_parity "$HELPER_ROOT/_internal/clayline/webui/static"' in script


def test_packager_supports_a_separate_recovery_bundle() -> None:
    """Recovery validation must never overwrite the user's installed app."""

    script = (ROOT / "tools" / "package_app.sh").read_text(encoding="utf-8")

    assert 'APP_VARIANT="${CLAYLINE_APP_VARIANT:-standard}"' in script
    assert 'APP_BASENAME="Clayline Recovery"' in script
    assert 'APP_BUNDLE_IDENTIFIER="com.clayline.recovery"' in script
    assert 'FINAL_APP="$BUILD_ROOT/$APP_BASENAME.app"' in script


def test_bundle_audit_requires_the_project_file_type(tmp_path: Path) -> None:
    """A double-clicked project must reach Clayline, so the bundle owns the type."""

    with (ROOT / "app" / "ClaylineMac" / "Info.plist").open("rb") as handle:
        shipped = plistlib.load(handle)
    resources = tmp_path / "Resources"
    resources.mkdir()

    def failures_for(info: dict) -> list[str]:
        audit = Audit()
        _audit_plist(info, resources, audit)
        return audit.failures

    assert not [failure for failure in failures_for(shipped) if "com.clayline.project" in failure]

    without_document_type = plistlib.loads(plistlib.dumps(shipped))
    without_document_type["CFBundleDocumentTypes"] = [
        item
        for item in without_document_type["CFBundleDocumentTypes"]
        if "com.clayline.project" not in item["LSItemContentTypes"]
    ]
    assert any(
        "CFBundleDocumentTypes must declare the Clayline project type" in failure
        for failure in failures_for(without_document_type)
    )

    wrong_extension = plistlib.loads(plistlib.dumps(shipped))
    for declaration in wrong_extension["UTExportedTypeDeclarations"]:
        if declaration["UTTypeIdentifier"] == "com.clayline.project":
            declaration["UTTypeTagSpecification"]["public.filename-extension"] = ["claylinez"]
    assert any(
        "UTExportedTypeDeclarations must map com.clayline.project to .clayline" in failure
        for failure in failures_for(wrong_extension)
    )
