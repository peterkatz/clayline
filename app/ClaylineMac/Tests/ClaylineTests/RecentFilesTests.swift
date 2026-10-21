import Foundation
import WebKit
import XCTest

@testable import Clayline

/// File → Open Recent: the store behind the menu, the kinds that go on it,
/// and the real handoff of a chosen file through a `WKWebView` page.
@MainActor
final class RecentFilesTests: XCTestCase {
    /// What the store copied into macOS's own list, so no test writes into
    /// the list of the process running it.
    private final class SystemRecorder {
        var noted: [URL] = []
        var clears = 0

        /// Holds the recorder for as long as the store holds the mirror.
        var mirror: SystemRecentDocuments {
            SystemRecentDocuments(
                note: { self.noted.append($0) },
                clear: { self.clears += 1 }
            )
        }
    }

    private var suites: [String] = []
    private var folders: [URL] = []

    override func tearDown() {
        for suite in suites {
            UserDefaults().removePersistentDomain(forName: suite)
        }
        for folder in folders {
            try? FileManager.default.removeItem(at: folder)
        }
        suites = []
        folders = []
        super.tearDown()
    }

    private func isolatedDefaults() throws -> UserDefaults {
        let suite = "RecentFilesTests.\(UUID().uuidString)"
        suites.append(suite)
        return try XCTUnwrap(UserDefaults(suiteName: suite))
    }

    private func store(
        _ defaults: UserDefaults,
        _ recorder: SystemRecorder = SystemRecorder()
    ) -> RecentFilesStore {
        RecentFilesStore(defaults: defaults, system: recorder.mirror)
    }

    private func scratchFolder() throws -> URL {
        let folder = FileManager.default.temporaryDirectory
            .appendingPathComponent("ClaylineRecent.\(UUID().uuidString)", isDirectory: true)
        try FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)
        folders.append(folder)
        return folder
    }

    private func file(_ path: String) -> URL { URL(fileURLWithPath: path) }

    // MARK: - The store

    func testNewestFirstAndOneEntryPerFileByItsStandardizedPath() throws {
        let recorder = SystemRecorder()
        let recents = store(try isolatedDefaults(), recorder)

        XCTAssertTrue(recents.note(file("/Users/potter/Forms/lantern.stl")))
        XCTAssertTrue(recents.note(file("/Users/potter/Jobs/lantern.clayline")))
        // The same model again, reached by a roundabout path: it moves to the
        // top rather than going on twice.
        XCTAssertTrue(recents.note(file("/Users/potter/Jobs/../Forms/./lantern.stl")))

        XCTAssertEqual(
            recents.urls.map(\.path),
            ["/Users/potter/Forms/lantern.stl", "/Users/potter/Jobs/lantern.clayline"]
        )
        // Every one is copied to macOS's own list for the Dock.
        XCTAssertEqual(
            recorder.noted.map(\.path),
            [
                "/Users/potter/Forms/lantern.stl",
                "/Users/potter/Jobs/lantern.clayline",
                "/Users/potter/Forms/lantern.stl",
            ]
        )
    }

    func testTheListKeepsTheTenNewest() throws {
        let recents = store(try isolatedDefaults())
        for index in 1 ... 12 {
            recents.note(file("/Users/potter/Forms/form-\(index).obj"))
        }

        XCTAssertEqual(RecentFilesStore.maximumCount, 10)
        XCTAssertEqual(recents.urls.count, 10)
        XCTAssertEqual(recents.urls.first?.lastPathComponent, "form-12.obj")
        XCTAssertEqual(recents.urls.last?.lastPathComponent, "form-3.obj")
    }

    func testClearMenuEmptiesClaylinesListAndTheDocks() throws {
        let defaults = try isolatedDefaults()
        let recorder = SystemRecorder()
        let recents = store(defaults, recorder)
        recents.note(file("/Users/potter/Drawings/knot.svg"))

        recents.clear()

        XCTAssertEqual(recents.urls, [])
        XCTAssertEqual(recorder.clears, 1)
        XCTAssertEqual(defaults.stringArray(forKey: RecentFilesStore.defaultsKey), [])
        XCTAssertEqual(store(defaults).urls, [])
    }

    func testTheListComesBackAfterARelaunchAndNothingElseDoes() throws {
        let defaults = try isolatedDefaults()
        let first = store(defaults)
        first.note(file("/Users/potter/Prints/bowl.gcode"))
        first.note(file("/Users/potter/Jobs/bowl.clayline"))

        XCTAssertEqual(RecentFilesStore.defaultsKey, "clayline.recent-files.v1")
        XCTAssertEqual(
            defaults.stringArray(forKey: RecentFilesStore.defaultsKey),
            ["/Users/potter/Jobs/bowl.clayline", "/Users/potter/Prints/bowl.gcode"]
        )
        XCTAssertEqual(store(defaults).urls, first.urls)

        // A list written by hand, or by a later Clayline, is read with care:
        // no relative paths, nothing the menu would refuse, no repeats, ten
        // at most.
        let tidy = (1 ... 11).map { "/Users/potter/Forms/form-\($0).ply" }
        defaults.set(
            [
                "Forms/relative.stl",
                "/Users/potter/Patterns/rib.json",
                "/Applications/Clayline.app/Contents/Resources/Gallery/Celtic/knot.svg",
                tidy[0],
                "/Users/potter/Forms/../Forms/form-1.ply",
            ] + tidy.dropFirst(),
            forKey: RecentFilesStore.defaultsKey
        )
        XCTAssertEqual(store(defaults).urls.map(\.path), Array(tidy.prefix(10)))
    }

    func testOnlyProjectsModelsDrawingsAndPrintFilesOutsideAnAppGoOn() throws {
        for name in [
            "job.clayline", "form.stl", "form.OBJ", "form.ply", "form.3mf",
            "knot.svg", "bowl.gcode",
        ] {
            XCTAssertTrue(RecentFilesStore.isRecordable(file("/Users/potter/\(name)")), name)
        }
        for name in ["rib.json", "photo.png", "photo.heic", "notes.txt", "bowl.gcode.txt"] {
            XCTAssertFalse(RecentFilesStore.isRecordable(file("/Users/potter/\(name)")), name)
        }
        // The gallery's drawings sit inside the app, which can move.
        XCTAssertFalse(
            RecentFilesStore.isRecordable(
                file("/Applications/Clayline.app/Contents/Resources/Gallery/Celtic/knot.svg")
            )
        )
        XCTAssertFalse(RecentFilesStore.isRecordable(URL(string: "https://example.com/form.stl")!))

        let recorder = SystemRecorder()
        let recents = store(try isolatedDefaults(), recorder)
        XCTAssertFalse(recents.note(file("/Users/potter/Patterns/rib.json")))
        XCTAssertFalse(
            recents.note(file("/Applications/Clayline.app/Contents/Resources/Gallery/Celtic/knot.svg"))
        )
        XCTAssertEqual(recents.urls, [])
        XCTAssertEqual(recorder.noted, [])
    }

    func testTheMenuNamesEachFileAndTellsSharedNamesApartByFolder() {
        let entries = RecentFilesStore.entries(for: [
            file("/Users/potter/Jobs/lantern.clayline"),
            file("/Users/potter/Forms/vase.stl"),
            file("/Users/potter/Old jobs/Lantern.clayline"),
            file("/Users/potter/Drawings/knot.svg"),
        ])

        XCTAssertEqual(
            entries.map(\.title),
            [
                "lantern.clayline — Jobs",
                "vase.stl",
                "Lantern.clayline — Old jobs",
                "knot.svg",
            ]
        )
        XCTAssertEqual(entries.map(\.id), entries.map(\.url.path))
    }

    func testSameNamesInSameNamedFoldersAreToldApartByTheFoldersAbove() {
        let entries = RecentFilesStore.entries(for: [
            file("/Users/potter/2025/Jobs/vase.stl"),
            file("/Users/potter/2026/Jobs/vase.stl"),
            file("/Users/potter/Forms/vase.stl"),
            file("/Users/potter/Drawings/knot.svg"),
        ])

        XCTAssertEqual(
            entries.map(\.title),
            [
                "vase.stl — 2025/Jobs",
                "vase.stl — 2026/Jobs",
                "vase.stl — Forms",
                "knot.svg",
            ]
        )

        // Folders that differ only by case read the same in a menu, and a
        // path that runs out of folders is shown whole.
        XCTAssertEqual(
            RecentFilesStore.entries(for: [
                file("/Jobs/bowl.gcode"),
                file("/Users/potter/Jobs/bowl.gcode"),
                file("/Volumes/Stick/jobs/bowl.gcode"),
            ]).map(\.title),
            [
                "bowl.gcode — /Jobs",
                "bowl.gcode — potter/Jobs",
                "bowl.gcode — Stick/jobs",
            ]
        )
    }

    func testChoosingAFileThatIsGoneTakesItOffTheList() throws {
        let recents = store(try isolatedDefaults())
        recents.note(file("/Users/potter/Forms/kept.stl"))
        recents.note(file("/Users/potter/Forms/gone.stl"))

        XCTAssertNil(recents.fileToReopen(file("/Users/potter/Forms/gone.stl"), fileExists: { _ in false }))
        XCTAssertEqual(recents.urls.map(\.lastPathComponent), ["kept.stl"])

        XCTAssertEqual(
            recents.fileToReopen(file("/Users/potter/Forms/./kept.stl"), fileExists: { _ in true }),
            file("/Users/potter/Forms/kept.stl")
        )
        XCTAssertEqual(recents.urls.map(\.lastPathComponent), ["kept.stl"])
    }

    func testOpenRecentOnAMissingFileSaysSoAndOpensNothing() throws {
        let folder = try scratchFolder()
        let gone = folder.appendingPathComponent("moved-away.gcode")
        try Data("G28\n".utf8).write(to: gone)
        let recents = store(try isolatedDefaults())
        recents.note(gone)
        try FileManager.default.removeItem(at: gone)

        let actions = WebActions(recentFiles: recents)
        var reported: [URL] = []
        actions.reportMissingRecentFile = { reported.append($0) }
        actions.openRecent(gone)

        XCTAssertEqual(reported, [gone])
        XCTAssertEqual(recents.urls, [])
        XCTAssertFalse(actions.hasPendingImports)
    }

    // MARK: - Which files reach Weave, and which panels add to the list

    func testAPrintFileRoutesToWeaveOneAtATime() throws {
        for name in ["bowl.gcode", "BOWL.GCODE"] {
            XCTAssertEqual(ClaylineFileTypes.kind(for: file("/tmp/\(name)")), .printFile, name)
        }
        XCTAssertEqual(ClaylineDocumentKind.printFile.mode, .weave)
        XCTAssertNil(ClaylineFileTypes.kind(for: file("/tmp/bowl.gcode.txt")))
        XCTAssertNil(ClaylineFileTypes.kind(for: file("/tmp/bowl.gco")))

        let urls = ["bowl.gcode", "other.gcode", "tile.svg"].map { file("/tmp/\($0)") }
        let selection = try XCTUnwrap(ClaylineFileTypes.importSelection(from: urls))
        XCTAssertEqual(selection.kind, .printFile)
        XCTAssertEqual(selection.mode, .weave)
        XCTAssertEqual(selection.urls, [urls[0]])
        XCTAssertEqual(selection.ignoredCount, 2)
        XCTAssertEqual(WebActions.maximumPrintFileBytes, 128 * 1_024 * 1_024)
    }

    func testOpenPanelsThatAddToOpenRecent() {
        for raw in ["tiles:", "weave:", "tiles:gallery", nil] {
            XCTAssertTrue(ClaylineOpenRequest(raw: raw).addsToOpenRecent, raw ?? "nil")
        }
        // A photo is traced over, and Restore pattern takes only the pattern
        // out of a print file; the Open Project panel's file waits for the
        // page to say it opened.
        for raw in ["tiles:reference-photo", "weave:gcode", "tiles:project", "weave:project"] {
            XCTAssertFalse(ClaylineOpenRequest(raw: raw).addsToOpenRecent, raw)
        }
    }

    /// A file of `bytes` bytes that takes no room on disk.
    private func sizedFile(_ name: String, bytes: Int, in folder: URL) throws -> URL {
        let url = folder.appendingPathComponent(name)
        XCTAssertTrue(FileManager.default.createFile(atPath: url.path, contents: nil))
        let handle = try FileHandle(forWritingTo: url)
        try handle.truncate(atOffset: UInt64(bytes))
        try handle.close()
        return url
    }

    func testAPanelPutsOnTheListOnlyWhatTheMenuCanOpenAgain() throws {
        // One table of bounds, shared by the menu's route and the panels.
        XCTAssertEqual(WebActions.maximumBytes(for: .svg), WebActions.maximumSVGBytes)
        XCTAssertEqual(WebActions.maximumBytes(for: .mesh), WebActions.maximumMeshBytes)
        XCTAssertEqual(WebActions.maximumBytes(for: .project), WebActions.maximumProjectBytes)
        XCTAssertEqual(WebActions.maximumBytes(for: .printFile), WebActions.maximumPrintFileBytes)

        let folder = try scratchFolder()
        let drawings = ClaylineOpenRequest(raw: "tiles:")
        let modelBox = ClaylineOpenRequest(raw: "weave:")
        let cases: [(ClaylineOpenRequest, String, Int)] = [
            (drawings, "knot.svg", WebActions.maximumSVGBytes),
            (modelBox, "form.stl", WebActions.maximumMeshBytes),
            (modelBox, "ladder.gcode", WebActions.maximumPrintFileBytes),
        ]
        for (request, name, bound) in cases {
            let fits = try sizedFile("fits-\(name)", bytes: bound, in: folder)
            let over = try sizedFile("over-\(name)", bytes: bound + 1, in: folder)
            XCTAssertTrue(WebActions.reopenRouteCanCarry(fits), name)
            XCTAssertTrue(request.notesOnPick(fits), name)
            XCTAssertFalse(WebActions.reopenRouteCanCarry(over), name)
            XCTAssertFalse(request.notesOnPick(over), name)
        }
        // A file that is not there cannot be measured, and is left off.
        XCTAssertFalse(drawings.notesOnPick(folder.appendingPathComponent("gone.svg")))
        // A pattern's .json is no kind the menu opens.
        let pattern = try sizedFile("rib.clayline-weave.json", bytes: 10, in: folder)
        XCTAssertFalse(modelBox.notesOnPick(pattern))
    }

    func testAProjectFromAnyPanelWaitsForThePage() throws {
        let folder = try scratchFolder()
        let project = try sizedFile("lantern.clayline", bytes: 10, in: folder)
        for raw in ["weave:", "tiles:project", "weave:project"] {
            let request = ClaylineOpenRequest(raw: raw)
            XCTAssertTrue(request.awaitsThePage(project), raw)
            XCTAssertFalse(request.notesOnPick(project), raw)
        }
        let model = try sizedFile("form.stl", bytes: 10, in: folder)
        XCTAssertFalse(ClaylineOpenRequest(raw: "weave:").awaitsThePage(model))
    }

    func testADrawingIsReadAsThePagesPickerReadsIt() {
        // One Latin-1 byte (é) is replaced, not refused, and a byte-order mark
        // is dropped, exactly as Blob.text() does.
        let latin1 = Data([0x3C, 0x73, 0x76, 0x67, 0x3E, 0xE9, 0x3C, 0x2F, 0x73, 0x76, 0x67, 0x3E])
        XCTAssertEqual(WebActions.svgText(from: latin1), "<svg>\u{FFFD}</svg>")
        XCTAssertEqual(WebActions.svgText(from: Data([0xEF, 0xBB, 0xBF]) + Data("<svg/>".utf8)), "<svg/>")
        XCTAssertEqual(WebActions.svgText(from: Data("<svg>é</svg>".utf8)), "<svg>é</svg>")
    }

    // MARK: - The handoff through a real page

    private let page = """
    <!doctype html><meta charset="utf-8"><body><script>
    window.printFiles = [];
    window.projects = [];
    window.drawings = [];
    window.claylineDesktop = {
      importFiles: (files) => { window.drawings.push(...files); return true; },
      importPrintFile: (payload) => { window.printFiles.push(payload); return true; },
      importProject: (payload) => { window.projects.push(payload.name); return true; },
    };
    </script></body>
    """

    private func makeWebView(_ actions: WebActions) -> WKWebView {
        let webView = WKWebView(frame: .zero, configuration: WKWebViewConfiguration())
        let loaded = expectation(description: "page loaded")
        let probe = RecentPageProbe { loaded.fulfill() }
        webView.navigationDelegate = probe
        webView.loadHTMLString(page, baseURL: URL(string: "http://127.0.0.1:49152/")!)
        wait(for: [loaded], timeout: 10)
        webView.navigationDelegate = nil
        withExtendedLifetime(probe) {}
        actions.attach(webView)
        actions.markReady()
        return webView
    }

    private func evaluate(_ script: String, in webView: WKWebView) throws -> Any? {
        let ran = expectation(description: "script ran")
        var value: Any?
        var failure: Error?
        webView.evaluateJavaScript(script) { result, error in
            value = result
            failure = error
            ran.fulfill()
        }
        wait(for: [ran], timeout: 10)
        if let failure { throw failure }
        return value
    }

    private func settle(until condition: () -> Bool) {
        var ticks = 0
        while !condition(), ticks < 60 {
            ticks += 1
            let tick = expectation(description: "tick")
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) { tick.fulfill() }
            wait(for: [tick], timeout: 5)
        }
    }

    func testAPrintFileFromFinderReachesWeaveAsBytesAndGoesOnTheList() throws {
        let folder = try scratchFolder()
        let printFile = folder.appendingPathComponent("bowl.gcode")
        let bytes = Data("; CLAYLINE_HEADER_BEGIN\n; CLAYLINE_HEADER_END\nG1 X1 Y2 E0.5\n\u{00ff}".utf8)
        try bytes.write(to: printFile)
        let recents = store(try isolatedDefaults())
        let actions = WebActions(recentFiles: recents)
        let webView = makeWebView(actions)
        defer { actions.detach(webView) }

        actions.importDocuments([printFile])
        settle { !recents.urls.isEmpty }

        XCTAssertEqual(try evaluate("window.printFiles.length", in: webView) as? Int, 1)
        XCTAssertEqual(try evaluate("window.printFiles[0].name", in: webView) as? String, "bowl.gcode")
        let base64 = try XCTUnwrap(try evaluate("window.printFiles[0].base64", in: webView) as? String)
        XCTAssertEqual(Data(base64Encoded: base64), bytes)
        XCTAssertEqual(recents.urls, [printFile.standardizedFileURL])
    }

    func testAProjectFromFinderGoesOnTheListOnceThePageHasOpenedIt() throws {
        let folder = try scratchFolder()
        let project = folder.appendingPathComponent("lantern.clayline")
        try Data("PK".utf8).write(to: project)
        let recents = store(try isolatedDefaults())
        let actions = WebActions(recentFiles: recents)
        let webView = makeWebView(actions)
        defer { actions.detach(webView) }
        var opened: [URL] = []
        actions.onProjectOpened = { opened.append($0) }

        actions.importDocuments([project])
        settle { !recents.urls.isEmpty }

        XCTAssertEqual(try evaluate("window.projects", in: webView) as? [String], ["lantern.clayline"])
        XCTAssertEqual(recents.urls, [project.standardizedFileURL])
        // The window title and the save folder hear of it the same way.
        XCTAssertEqual(opened, [project])
    }

    func testOpenRecentOpensTheFileAgainAndPutsItBackOnTop() throws {
        let folder = try scratchFolder()
        let printFile = folder.appendingPathComponent("ladder.gcode")
        try Data("G28\nG1 X10 E1\n".utf8).write(to: printFile)
        let recents = store(try isolatedDefaults())
        recents.note(printFile)
        recents.note(file("/Users/potter/Forms/newer.stl"))
        let actions = WebActions(recentFiles: recents)
        let webView = makeWebView(actions)
        defer { actions.detach(webView) }

        actions.openRecent(printFile)
        settle { recents.urls.first == printFile.standardizedFileURL }

        XCTAssertEqual(try evaluate("window.printFiles.length", in: webView) as? Int, 1)
        XCTAssertEqual(try evaluate("window.printFiles[0].name", in: webView) as? String, "ladder.gcode")
        XCTAssertEqual(
            recents.urls.map(\.lastPathComponent),
            ["ladder.gcode", "newer.stl"]
        )
    }

    func testADrawingThePickerOpensOpensFromTheMenuToo() throws {
        let folder = try scratchFolder()
        let drawing = folder.appendingPathComponent("rosette.svg")
        // Saved by another program as Latin-1: the page's own picker opens it.
        try Data([0x3C, 0x73, 0x76, 0x67, 0x3E, 0xE9, 0x3C, 0x2F, 0x73, 0x76, 0x67, 0x3E])
            .write(to: drawing)
        let recents = store(try isolatedDefaults())
        recents.note(drawing)
        recents.note(file("/Users/potter/Forms/newer.stl"))
        let actions = WebActions(recentFiles: recents)
        var failures: [ClaylineDocumentKind] = []
        actions.reportImportFailure = { failures.append($0) }
        let webView = makeWebView(actions)
        defer { actions.detach(webView) }

        actions.openRecent(drawing)
        settle { recents.urls.first == drawing.standardizedFileURL }

        XCTAssertEqual(try evaluate("window.drawings.length", in: webView) as? Int, 1)
        XCTAssertEqual(try evaluate("window.drawings[0].svg", in: webView) as? String, "<svg>\u{FFFD}</svg>")
        XCTAssertEqual(recents.urls.map(\.lastPathComponent), ["rosette.svg", "newer.stl"])
        XCTAssertEqual(failures, [])
    }

    func testADrawingTooLargeToHandOverSaysSoRatherThanDoingNothing() throws {
        let folder = try scratchFolder()
        let drawing = try sizedFile("mural.svg", bytes: WebActions.maximumSVGBytes + 1, in: folder)
        let recents = store(try isolatedDefaults())
        let actions = WebActions(recentFiles: recents)
        var failures: [ClaylineDocumentKind] = []
        actions.reportImportFailure = { failures.append($0) }
        let webView = makeWebView(actions)
        defer { actions.detach(webView) }

        actions.importDocuments([drawing])

        XCTAssertEqual(failures, [.svg])
        XCTAssertEqual(try evaluate("window.drawings.length", in: webView) as? Int, 0)
        XCTAssertEqual(recents.urls, [])
    }

    func testAProjectFromTheModelBoxGoesOnOnlyOnceThePageHasOpenedIt() throws {
        let folder = try scratchFolder()
        let project = folder.appendingPathComponent("lantern.clayline")
        try Data("PK".utf8).write(to: project)
        let recents = store(try isolatedDefaults())
        let actions = WebActions(recentFiles: recents)
        var opened: [URL] = []
        actions.onProjectOpened = { opened.append($0) }
        let coordinator = ClaylineWebView.Coordinator(
            launch: EngineLaunch(
                readiness: EngineReadyMessage(
                    schema: EngineReadyMessage.expectedSchema,
                    host: EngineReadyMessage.expectedHost,
                    port: 49_152,
                    pid: 4_321
                ),
                token: String(repeating: "a", count: 32)
            ),
            actions: actions,
            onReady: {},
            onFailure: { _ in }
        )
        let configuration = WKWebViewConfiguration()
        coordinator.installSettingsBridge(in: configuration.userContentController)
        let webView = WKWebView(frame: .zero, configuration: configuration)
        defer { coordinator.invalidate(webView: webView) }
        let loaded = expectation(description: "page loaded")
        let probe = RecentPageProbe { loaded.fulfill() }
        webView.navigationDelegate = probe
        webView.loadHTMLString(page, baseURL: URL(string: "http://127.0.0.1:49152/")!)
        wait(for: [loaded], timeout: 10)
        webView.navigationDelegate = nil
        withExtendedLifetime(probe) {}
        let answer = { (ok: Bool) in
            "window.webkit.messageHandlers.claylineProjectOpened"
                + ".postMessage({ name: 'lantern.clayline', ok: \(ok) }); true"
        }
        func waitForThePage() {
            let tick = expectation(description: "the page answered")
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.4) { tick.fulfill() }
            wait(for: [tick], timeout: 5)
        }

        // Chosen in Weave's Model box: nothing goes on until the page answers,
        // and a file the page turns down never does.
        let modelBox = ClaylineOpenRequest(raw: "weave:")
        coordinator.rememberPanelChoice([project], for: modelBox)
        XCTAssertEqual(recents.urls, [])
        _ = try evaluate(answer(false), in: webView)
        waitForThePage()
        XCTAssertEqual(recents.urls, [])
        XCTAssertEqual(opened, [])

        // The same file chosen again and opened: on the list, and the window
        // and the save folder hear of it the same way.
        coordinator.rememberPanelChoice([project], for: modelBox)
        _ = try evaluate(answer(true), in: webView)
        settle { !recents.urls.isEmpty }
        XCTAssertEqual(recents.urls, [project.standardizedFileURL])
        XCTAssertEqual(opened, [project])
    }
}

private final class RecentPageProbe: NSObject, WKNavigationDelegate {
    private let finished: @MainActor () -> Void

    init(finished: @escaping @MainActor () -> Void) {
        self.finished = finished
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        MainActor.assumeIsolated { finished() }
    }
}
