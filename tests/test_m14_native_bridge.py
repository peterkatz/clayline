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


def test_bundle_owns_the_project_file_it_writes() -> None:
    with (MAC / "Info.plist").open("rb") as handle:
        info = plistlib.load(handle)

    project_document = next(
        item
        for item in info["CFBundleDocumentTypes"]
        if "com.clayline.project" in item["LSItemContentTypes"]
    )
    assert project_document["CFBundleTypeName"] == "Clayline project"
    assert project_document["CFBundleTypeRole"] == "Editor"
    assert project_document["LSHandlerRank"] == "Owner"

    exported = {
        declaration["UTTypeIdentifier"]: declaration
        for declaration in info["UTExportedTypeDeclarations"]
    }
    project_type = exported["com.clayline.project"]
    assert project_type["UTTypeConformsTo"] == ["public.data"]
    tags = project_type["UTTypeTagSpecification"]
    assert tags["public.filename-extension"] == ["clayline"]
    assert tags["public.mime-type"] == "application/vnd.clayline.project+zip"

    verifier = (ROOT / "scripts" / "verify_macos_app.py").read_text(encoding="utf-8")
    assert '"com.clayline.project" in declared_types' in verifier


def test_native_project_menu_carries_petes_july_shortcuts() -> None:
    commands = _source("ClaylineCommands.swift")
    actions = _source("WebActions.swift")

    assert 'Button("Open…")' in commands
    assert 'Button("Open Project…")' in commands
    assert 'Button("Save Project…")' in commands
    assert 'Button("Export G-code…")' in commands
    for button, shortcut in (
        ("Open…", '.keyboardShortcut("o", modifiers: .command)'),
        ("Open Project…", '.keyboardShortcut("o", modifiers: [.command, .shift])'),
        ("Save Project…", '.keyboardShortcut("s", modifiers: .command)'),
        ("Export G-code…", '.keyboardShortcut("e", modifiers: [.command, .shift])'),
    ):
        rest = commands[commands.index(f'Button("{button}")') + 1 :]
        following = rest.find('Button("')
        assert shortcut in (rest if following < 0 else rest[:following])

    assert "window.claylineDesktop && window.claylineDesktop.openProject()" in actions
    assert "window.claylineDesktop && window.claylineDesktop.saveProject()" in actions


def test_native_project_handoff_is_bounded_binary_like_a_mesh() -> None:
    actions = _source("WebActions.swift")
    project_method = actions[
        actions.index("private func importProject") : actions.index(
            "nonisolated static func readBoundedBinaryFile"
        )
    ]

    assert "maximumProjectBytes = 96 * 1_024 * 1_024" in actions
    assert "readBoundedBinaryFile" in project_method
    assert "base64EncodedString()" in project_method
    assert "callAsyncJavaScript" in project_method
    assert "window.claylineDesktop.importProject(payload)" in project_method
    assert "String(data:" not in project_method
    assert 'messageText = "Project could not be opened"' in actions


def test_native_project_panels_and_staged_downloads_protect_the_saved_file() -> None:
    web_view = _source("ClaylineWebView.swift")
    store = _source("StudioSettingsStore.swift")

    assert 'panel.title = "Open a Clayline Project"' in web_view
    assert "panel.allowedContentTypes = ClaylineFileTypes.projectTypes" in web_view
    assert '"Save Clayline Project"' in web_view
    assert "panel.directoryURL = directory" in web_view
    assert "settingsStore.projectDirectoryURL()" in web_view
    assert 'projectPathDefaultsKey = "clayline.native-project-path.v1"' in store
    assert "rememberProjectURL" in store

    # Every download writes to a working file first; the chosen name is only
    # touched once the whole file has arrived.
    assert "func stage(" in web_view
    assert "StagedDownload(destination: destination, isProject: isProject)" in web_view
    assert "return staged.staging" in web_view
    assert "func downloadDidFinish" in web_view
    assert (
        "StagedDownload.commit(staging: staged.staging, destination: staged.destination)"
        in web_view
    )
    assert "StagedDownload.discard(staging: staged.staging)" in web_view
    assert "FileManager.default.removeItem(at: url)" not in web_view

    # The page is told the outcome; a cancelled panel carries no reason.
    assert (
        "actions.reportProjectSaveResult(ok: true, name: staged.destination.lastPathComponent)"
        in web_view
    )
    assert "actions.reportProjectSaveResult(ok: false, name: nil)" in web_view
    assert "window.representedURL = url" in web_view

    # The Open panel hands the page a file it has not read yet, so the window
    # and the remembered folder wait for the page to say it opened -- and the
    # shell lets the file go the moment the page answers either way, so a
    # project it turned down cannot hand its folder to the next one.
    assert 'projectOpenedHandlerName = "claylineProjectOpened"' in web_view
    assert "private var projectAwaitingThePage: URL?" in web_view
    assert "self?.projectAwaitingThePage = url" in web_view
    assert "actions.projectWasOpened(at: url)" in web_view
    opened = web_view[web_view.index("private func handleProjectOpened") :][:700]
    assert opened.index("projectAwaitingThePage = nil") < opened.index('payload?["ok"]')
    assert 'guard payload?["ok"] as? Bool ?? true else { return }' in opened
    assert "self?.rememberProject(url)" not in web_view[web_view.index("let remember:") :][:600]


def test_native_open_and_finder_routes_are_mode_aware() -> None:
    file_types = _source("ClaylineFileTypes.swift")
    web_view = _source("ClaylineWebView.swift")
    actions = _source("WebActions.swift")
    delegate = _source("AppDelegate.swift")
    commands = _source("ClaylineCommands.swift")

    for file_extension in ("obj", "stl", "3mf", "ply"):
        assert f'"{file_extension}"' in file_types
    assert "mode == .weave ? meshTypes + projectTypes + printFileTypes : [svg]" in file_types
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
        actions.index("private func importMesh") : actions.index("private func importProject")
    ]

    assert "maximumMeshBytes = 64 * 1_024 * 1_024" in actions
    assert "readBoundedBinaryFile" in mesh_method
    assert "base64EncodedString()" in mesh_method
    assert "callAsyncJavaScript" in mesh_method
    assert "String(data:" not in mesh_method
    # The bounded reader both hand-offs share.
    assert "read(upToCount:" in actions


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
    assert "saveProject" in desktop
    assert "openProject: () => openProjectChooser()" in desktop
    assert "importProject: (payload) => desktopImportProject(payload)" in desktop
    # One way in for the shell, whether the file came from Finder or a panel.
    assert "self.projectWasOpened(at: url)" in _source("WebActions.swift")
    assert "projectSaveResult" in desktop
    assert 'document.body.dataset.claylineFileRequest = "project"' in app
    assert "body.dataset.claylineFileRequest" in _source("ClaylineWebView.swift")
    # Restore pattern from G-code… opens a panel of print files, not meshes:
    # the packaged app filters by this one-shot marker, never by the accept list.
    assert 'document.body.dataset.claylineFileRequest = "gcode"' in weave
    file_types = _source("ClaylineFileTypes.swift")
    assert 'isPrintFile = requestToken == "gcode"' in file_types
    assert "static let printFileTypes = [gcode]" in file_types
    assert "meshTypes + projectTypes + printFileTypes" in file_types
    web_view = _source("ClaylineWebView.swift")
    assert "request.isPrintFile" in web_view
    assert 'panel.title = "Open a Clayline Print File"' in web_view
    assert "ClaylineFileTypes.printFileTypes" in web_view

    assert "DESKTOP_MAX_MESH_BYTES = 1024 * 1024 * 1024" in weave
    assert "new Uint8Array(byteCount)" in weave
    assert 'new File([bytes], name, { type: "application/octet-stream" })' in weave
    assert 'open: () => $("#weaveFileInput").click()' in weave
    assert "exportGcode: downloadGcode" in weave
    assert "importMesh: desktopImportMesh" in weave
