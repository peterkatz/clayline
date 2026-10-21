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
    assert "actions.projectWasOpened(at: url)" in web_view
    opened = web_view[web_view.index("private func handleProjectOpened") :][:700]
    assert opened.index("projectAwaitingThePage = nil") < opened.index('payload?["ok"]')
    assert 'guard payload?["ok"] as? Bool ?? true else { return }' in opened
    # A project waits for the page whichever panel it was chosen in, the
    # Open Project panel or Weave's Model box, before anything else is kept.
    chose = web_view[web_view.index("func rememberPanelChoice(") :]
    chose = chose[: chose.index("private func rememberProject")]
    assert "if request.awaitsThePage(url) {" in chose
    assert chose.index("projectAwaitingThePage = url\n                return") < chose.index(
        "settingsStore.rememberMeshURL(url)"
    )
    assert "rememberProject(url)" not in chose
    assert "isProject || ClaylineFileTypes.kind(for: url) == .project" in _source(
        "ClaylineFileTypes.swift"
    )


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
    # Load pattern opens a panel of saved patterns: without its own marker it
    # opened the Model box's panel, where a pattern file was greyed out.
    assert 'document.body.dataset.claylineFileRequest = "pattern"' in weave
    assert weave.index('claylineFileRequest = "pattern"') < weave.index('$("#weavePatternFile").click()')
    assert 'isPattern = requestToken == "pattern"' in file_types
    assert "static let patternTypes: [UTType] = [.json]" in file_types
    assert "request.isPattern" in web_view
    assert "ClaylineFileTypes.patternTypes" in web_view
    assert 'panel.title = "Open a Clayline Print File"' in web_view
    assert "ClaylineFileTypes.printFileTypes" in web_view

    assert "DESKTOP_MAX_MESH_BYTES = 1024 * 1024 * 1024" in weave
    assert "new Uint8Array(byteCount)" in weave
    assert 'new File([bytes], name, { type: "application/octet-stream" })' in weave
    assert 'open: () => $("#weaveFileInput").click()' in weave
    assert "exportGcode: downloadGcode" in weave
    assert "importMesh: desktopImportMesh" in weave


def test_file_menu_carries_open_recent_right_under_open() -> None:
    commands = _source("ClaylineCommands.swift")
    app = _source("ClaylineApp.swift")

    open_at = commands.index('Button("Open…")')
    recent_at = commands.index('Menu("Open Recent")')
    assert open_at < recent_at < commands.index('Button("Open Project…")')
    assert recent_at < commands.index('Button("Open from Gallery…")')
    # Nothing but Open…'s own shortcut and greying sits between the two.
    between = commands[open_at:recent_at]
    assert between.count("Button(") == 1
    assert '.keyboardShortcut("o", modifiers: .command)' in between

    menu = commands[recent_at : commands.index("// Only a copy", recent_at)]
    assert "ForEach(recentFiles.entries)" in menu
    assert "Button(entry.title)" in menu
    assert "actions.openRecent(entry.url)" in menu
    assert "if !recentFiles.urls.isEmpty {\n                    Divider()" in menu
    assert 'Button("Clear Menu")' in menu
    assert "recentFiles.clear()" in menu
    # With nothing on it the submenu shows only a greyed Clear Menu, and the
    # whole submenu waits for the studio like every other File item.
    assert (
        ".disabled(recentFiles.urls.isEmpty)\n"
        "            }\n"
        "            .disabled(!actions.isReady)"
    ) in menu
    # The menu watches the list itself, so a file opened or saved appears at once.
    assert "@ObservedObject var recentFiles: RecentFilesStore" in commands
    assert "recentFiles: appDelegate.coordinator.webActions.recentFiles" in app


def test_the_recent_list_is_its_own_ten_paths_mirrored_to_the_dock() -> None:
    recents = _source("RecentFiles.swift")
    actions = _source("WebActions.swift")

    assert 'static let defaultsKey = "clayline.recent-files.v1"' in recents
    assert "static let maximumCount = 10" in recents
    assert "@Published private(set) var urls: [URL]" in recents
    assert "ObservableObject" in recents
    # One entry per standardized path, newest first, ten at most.
    assert "url.standardizedFileURL" in recents
    assert "next.insert(file, at: 0)" in recents
    assert "next.prefix(Self.maximumCount)" in recents
    # The Dock's list follows, and Clear Menu clears both.
    assert "NSDocumentController.shared.noteNewRecentDocumentURL($0)" in recents
    assert "NSDocumentController.shared.clearRecentDocuments(nil)" in recents
    clear = recents[recents.index("func clear()") :][:120]
    assert "store([])" in clear and "system.clear()" in clear
    # Only what Clayline opens as a document, and never a file inside an app.
    assert "ClaylineFileTypes.kind(for: url) != nil" in recents
    assert "ClaylineGallery.isInsideAnApp(" in recents
    # The app is not sandboxed: plain paths, no bookmarks.
    assert "bookmarkData" not in recents

    assert "let recentFiles: RecentFilesStore" in actions
    # A file that is gone is said so and leaves the list.
    missing = 'alert.messageText = "\u201c\\(url.lastPathComponent)\u201d can\u2019t be found."'
    assert missing in actions
    assert 'alert.informativeText = "It may have been moved or deleted."' in actions
    reopen = actions[actions.index("func openRecent(") :][:300]
    assert "recentFiles.fileToReopen(url)" in reopen
    assert "presentMissingRecentFile(url)" in reopen
    assert "importDocuments([file])" in reopen


def test_files_go_on_open_recent_where_they_open_and_where_a_project_is_saved() -> None:
    web_view = _source("ClaylineWebView.swift")
    actions = _source("WebActions.swift")
    file_types = _source("ClaylineFileTypes.swift")

    # The open panels: everything but a reference photo and the print file
    # Restore pattern reads for its pattern; the Open Project panel's file
    # waits for the page.
    remember = web_view[web_view.index("let remember:") :]
    remember = remember[: remember.index("if let window = webView.window")]
    assert "self?.rememberPanelChoice(urls, for: request)" in remember
    chose = web_view[web_view.index("func rememberPanelChoice(") :]
    chose = chose[: chose.index("private func rememberProject")]
    assert "for chosen in urls where request.notesOnPick(chosen) {" in chose
    assert "actions.noteRecentFile(chosen)" in chose
    assert "!isProject && !isReferencePhoto && !isPrintFile" in file_types
    # Only what the menu could open again: the panels and the menu's route
    # share one table of bounds.
    assert (
        "addsToOpenRecent && !awaitsThePage(url) && WebActions.reopenRouteCanCarry(url)"
        in file_types
    )
    assert "size <= maximumBytes(for: kind)" in actions
    for kind in ("svg", "mesh", "project", "printFile"):
        assert f"let maximumBytes = Self.maximumBytes(for: .{kind})" in actions
    # A project once the page has opened it, from any route.
    opened = actions[actions.index("func projectWasOpened(at url: URL)") :][:120]
    assert "recentFiles.note(url)" in opened
    # Finder, the Dock and Open Recent: once the page has the file.
    assert "read.forEach { recentFiles.note($0) }" in actions
    mesh = actions[
        actions.index("private func importMesh") : actions.index("private func importProject")
    ]
    assert "if accepted == true {\n                    self.recentFiles.note(url)" in mesh
    # A saved project, and nothing else a save panel writes.
    finished = web_view[web_view.index("func downloadDidFinish") :]
    finished = finished[: finished.index("func download(_ download: WKDownload, didFailWithError")]
    assert finished.count("noteRecentFile") == 1
    assert finished.index("guard staged.isProject else") < finished.index(
        "actions.noteRecentFile(staged.destination)"
    )
    # Nothing on the list is opened at launch.
    launch = web_view[web_view.index("func webView(_ webView: WKWebView, didFinish navigation") :][
        :900
    ]
    assert "recent" not in launch.lower()
    assert "openRecent" not in web_view


def test_a_print_file_reaches_weave_as_bounded_bytes() -> None:
    actions = _source("WebActions.swift")
    file_types = _source("ClaylineFileTypes.swift")
    delegate = _source("AppDelegate.swift")

    assert "case printFile" in file_types
    assert 'static let printFileExtension = "gcode"' in file_types
    assert "if fileExtension == printFileExtension {\n            return .printFile" in file_types
    assert "case .mesh, .project, .printFile:\n            selected = [first.0]" in file_types
    assert "case .mesh, .printFile: .weave" in file_types
    assert "importDocuments(urls)" in delegate

    assert "maximumPrintFileBytes = 128 * 1_024 * 1_024" in actions
    method = actions[actions.index("private func importPrintFile") :]
    method = method[: method.index("private func presentIgnoredFilesNotice")]
    assert "ClaylineFileTypes.kind(for: url) == .printFile" in method
    assert "readBoundedBinaryFile(url, maximumBytes: maximumBytes)" in method
    assert "base64EncodedString()" in method
    assert "callAsyncJavaScript" in method
    assert "window.claylineDesktop.importPrintFile(payload)" in method
    assert "String(data:" not in method
    assert (
        "case .printFile:\n"
        "            if let url = selection.urls.first {\n"
        "                importPrintFile(url)"
    ) in actions
    assert 'messageText = "Print file could not be opened"' in actions
    assert '"Choose one readable G-code file no larger than 128 MiB."' in actions


def test_the_page_takes_a_print_file_the_way_the_model_box_does() -> None:
    app = (STATIC / "app.js").read_text(encoding="utf-8")
    weave = (STATIC / "weave.js").read_text(encoding="utf-8")

    start = app.index("window.claylineDesktop = Object.freeze({")
    desktop = app[start : app.index("\n});", start)]
    entry = desktop[desktop.index("importPrintFile: (payload) => {") :][:200]
    assert "window.claylineWeaveMode?.activate();" in entry
    assert "return window.claylineWeaveMode?.importPrintFile?.(payload) || false;" in entry

    exposed = weave[weave.index("window.claylineWeaveMode = Object.freeze({") :][:900]
    assert "importPrintFile: desktopImportPrintFile," in exposed
    assert "importMesh: desktopImportMesh," in exposed
    method = weave[weave.index("function desktopImportPrintFile(payload)") :]
    method = method[: method.index("\n  }\n")]
    assert "DESKTOP_MAX_PRINT_FILE_BYTES" in method
    assert "decodedBase64Size(payload?.base64)" in method
    assert "new Uint8Array(byteCount)" in method
    # The very function the Model box's picker and drop zone call.
    assert (
        'setDroppedFile(new File([bytes], name, { type: "application/octet-stream" }));' in method
    )
    assert "DESKTOP_MAX_PRINT_FILE_BYTES = 128 * 1024 * 1024" in weave
    assert "if (!/\\.gcode$/i.test(leaf)) return null;" in weave


def test_the_guide_and_changelog_say_only_a_project_goes_on_when_saved() -> None:
    changelog = " ".join((ROOT / "CHANGELOG.md").read_text(encoding="utf-8").split())
    assert (
        "**File → Open Recent.** The last ten projects you opened or saved, and models, "
        "drawings and print files you opened, newest first"
    ) in changelog
    sentence = (
        "**File → Open Recent** lists the last ten projects you opened or saved, and models, "
        "drawings and print files you opened, newest first; choose one to open it again."
    )
    for page, sliced in (
        ("tiles.md", "If the job was sliced when you saved it"),
        ("weave.md", "If the form was sliced when you saved it"),
    ):
        text = (ROOT / "guide" / page).read_text(encoding="utf-8")
        assert "print files you opened or saved" not in text
        assert text.count(sentence) == 1
        # The project paragraph stays whole: brought back, then sliced again,
        # then the menu.
        assert text.index("brings it all back") < text.index(sliced) < text.index(sentence)
