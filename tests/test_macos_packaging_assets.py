from __future__ import annotations

from pathlib import Path

from scripts.verify_macos_app import (
    BUNDLED_STATIC_RELATIVE,
    Audit,
    _audit_static_asset_parity,
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
