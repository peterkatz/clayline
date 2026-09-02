from __future__ import annotations

import plistlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAC = ROOT / "app" / "ClaylineMac"
SOURCES = MAC / "Sources" / "Clayline"
STATIC = ROOT / "src" / "clayline" / "webui" / "static"


def _source(name: str) -> str:
    return (SOURCES / name).read_text(encoding="utf-8")


def test_bundle_registers_svg_and_all_weave_mesh_types() -> None:
    with (MAC / "Info.plist").open("rb") as handle:
        info = plistlib.load(handle)

    document_types = info["CFBundleDocumentTypes"]
    registered = {
        uti for document_type in document_types for uti in document_type["LSItemContentTypes"]
    }
    expected_mesh_types = {
        "public.geometry-definition-format",
        "public.standard-tesselated-geometry-format",
        "com.clayline.mesh.3mf",
        "public.polygon-file-format",
    }
    assert "public.svg-image" in registered
    assert expected_mesh_types <= registered

    imported = {
        declaration["UTTypeIdentifier"]: set(
            declaration["UTTypeTagSpecification"]["public.filename-extension"]
        )
        for declaration in info["UTImportedTypeDeclarations"]
    }
    assert imported == {"com.clayline.mesh.3mf": {"3mf"}}

    verifier = (ROOT / "scripts" / "verify_macos_app.py").read_text(encoding="utf-8")
    assert "weave_mesh_types <= declared_types" in verifier
    assert "UTImportedTypeDeclarations must map com.clayline.mesh.3mf to .3mf" in verifier


def test_native_open_and_finder_routes_are_mode_aware() -> None:
    file_types = _source("ClaylineFileTypes.swift")
    web_view = _source("ClaylineWebView.swift")
    actions = _source("WebActions.swift")
    delegate = _source("AppDelegate.swift")
    commands = _source("ClaylineCommands.swift")

    for file_extension in ("obj", "stl", "3mf", "ply"):
        assert f'"{file_extension}"' in file_types
    assert "mode == .weave ? meshTypes : [svg]" in file_types
    assert "first.1" in file_types and "selected = [first.0]" in file_types
    assert "ignoredCount" in file_types

    assert "const body = document.body" in web_view
    assert 'body.dataset.claylineMode || "tiles"' in web_view
    assert "ClaylineFileTypes.allowedContentTypes(for: mode)" in web_view
    assert "mode == .tiles && parameters.allowsMultipleSelection" in web_view
    assert "importDocuments(urls)" in delegate
    assert "actions.openDocuments()" in commands
    assert "window.claylineDesktop && window.claylineDesktop.open()" in actions


def test_native_mesh_handoff_is_bounded_binary_and_not_interpreted_as_text() -> None:
    actions = _source("WebActions.swift")
    mesh_method = actions[
        actions.index("private func importMesh") : actions.index(
            "private func presentIgnoredFilesNotice"
        )
    ]

    assert "maximumMeshBytes = 64 * 1_024 * 1_024" in actions
    assert "readBoundedBinaryFile" in mesh_method
    assert "base64EncodedString()" in mesh_method
    assert "callAsyncJavaScript" in mesh_method
    assert "String(data:" not in mesh_method
    assert "read(upToCount:" in mesh_method


def test_native_settings_bridge_keeps_web_session_ephemeral_and_survives_random_origin() -> None:
    web_view = _source("ClaylineWebView.swift")
    store = _source("StudioSettingsStore.swift")

    assert "configuration.websiteDataStore = .nonPersistent()" in web_view
    assert "installSettingsBridge(in: configuration.userContentController)" in web_view
    assert "WKScriptMessageHandler" in web_view
    assert "injectionTime: .atDocumentStart" in store
    assert 'static let webStorageKey = "clayline-ui-state.v1"' in store
    assert "UserDefaults" in store
    assert "claylineSettingsStorage" in store


def test_native_weave_relaunch_is_a_clean_slate_for_the_last_mesh() -> None:
    web_view = _source("ClaylineWebView.swift")
    store = _source("StudioSettingsStore.swift")
    actions = _source("WebActions.swift")

    assert 'meshPathDefaultsKey = "clayline.native-weave-mesh-path.v1"' in store
    assert "rememberMeshURL" in store
    assert "restorableMeshURL" in store
    assert "FileManager.default.isReadableFile" in store
    assert "settingsStore.rememberMeshURL(url)" in web_view
    assert "settingsStore.restorableMeshURL()" not in web_view
    assert "let shouldRestoreMesh = !actions.hasPendingImports" not in web_view
    assert "actions.restoreMesh(meshURL)" not in web_view
    assert "settingsStore.forgetMeshURL()" in web_view
    assert "importMesh(url, showFailure: false)" in actions


def test_browser_bridge_routes_open_export_and_finder_import_by_active_mode() -> None:
    app = (STATIC / "app.js").read_text(encoding="utf-8")
    weave = (STATIC / "weave.js").read_text(encoding="utf-8")

    desktop = app[app.index("window.claylineDesktop = Object.freeze") :]
    assert "document.body.dataset.claylineMode" in desktop
    assert "window.claylineWeaveMode?.open()" in desktop
    assert "window.claylineWeaveMode?.exportGcode()" in desktop
    assert "window.claylineWeaveMode?.activateTiles()" in desktop
    assert "window.claylineWeaveMode?.importMesh(payload)" in desktop

    assert "DESKTOP_MAX_MESH_BYTES = 1024 * 1024 * 1024" in weave
    assert "new Uint8Array(byteCount)" in weave
    assert 'new File([bytes], name, { type: "application/octet-stream" })' in weave
    assert 'open: () => $("#weaveFileInput").click()' in weave
    assert "exportGcode: downloadGcode" in weave
    assert "importMesh: desktopImportMesh" in weave
