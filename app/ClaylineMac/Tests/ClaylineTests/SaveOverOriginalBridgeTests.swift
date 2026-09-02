import WebKit
import XCTest

@testable import Clayline

/// The whole save path, driven the way the studio drives it: real page
/// JavaScript posting through a real `WKWebView` message handler into the real
/// shell, ending at a real file on disk.
///
/// The unit tests around `SVGSourceIndex` prove the bookkeeping. They cannot
/// prove the wiring — a handler registered under the wrong name, or an import
/// that forgets to record where a file came from, passes every one of them and
/// still leaves the artist's Save doing nothing.
@MainActor
final class SaveOverOriginalBridgeTests: XCTestCase {
    private func makeCoordinator(_ actions: WebActions) -> ClaylineWebView.Coordinator {
        let launch = EngineLaunch(
            readiness: EngineReadyMessage(
                schema: EngineReadyMessage.expectedSchema,
                host: EngineReadyMessage.expectedHost,
                port: 49_152,
                pid: 4_321
            ),
            token: String(repeating: "a", count: 32)
        )
        return ClaylineWebView.Coordinator(
            launch: launch,
            actions: actions,
            onReady: {},
            onFailure: { _ in }
        )
    }

    /// A page with just enough of the studio's shape: it records what the shell
    /// hands it, and can post a save back.
    private let page = """
    <!doctype html><meta charset="utf-8"><body><script>
    window.imported = [];
    window.saveResults = [];
    window.claylineDesktop = {
      importFiles: (files) => { window.imported = files; },
      svgSaveResult: (payload) => { window.saveResults.push(payload); },
    };
    window.saveFirst = (svg) => {
      window.webkit.messageHandlers.claylineSaveSVG.postMessage({
        name: window.imported[0].name, svg,
      });
    };
    </script></body>
    """

    private func load(_ webView: WKWebView) {
        let expectation = expectation(description: "page loaded")
        let probe = LoadProbe { expectation.fulfill() }
        webView.navigationDelegate = probe
        webView.loadHTMLString(page, baseURL: URL(string: "http://127.0.0.1:49152/")!)
        wait(for: [expectation], timeout: 10)
        webView.navigationDelegate = nil
        withExtendedLifetime(probe) {}
    }

    private func evaluate(_ script: String, in webView: WKWebView) throws -> Any? {
        let expectation = expectation(description: "script ran")
        var value: Any?
        var failure: Error?
        webView.evaluateJavaScript(script) { result, error in
            value = result
            failure = error
            expectation.fulfill()
        }
        wait(for: [expectation], timeout: 10)
        if let failure { throw failure }
        return value
    }

    private func settle() {
        let expectation = expectation(description: "shell replied")
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.4) { expectation.fulfill() }
        wait(for: [expectation], timeout: 5)
    }

    func testAnEditedDesignLandsBackOnTheArtistsOwnFile() throws {
        let directory = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: directory) }
        let original = directory.appendingPathComponent("rosette-study.svg")
        try Data("<svg>as it was on disk</svg>".utf8).write(to: original)

        let actions = WebActions()
        let coordinator = makeCoordinator(actions)
        let configuration = WKWebViewConfiguration()
        coordinator.installSettingsBridge(in: configuration.userContentController)
        let webView = WKWebView(frame: .zero, configuration: configuration)
        defer { coordinator.invalidate(webView: webView) }

        actions.attach(webView)
        load(webView)
        actions.markReady()

        // The studio opens the file: the page is handed a name, the shell keeps
        // the path.
        actions.importDocuments([original])
        settle()
        XCTAssertEqual(
            try evaluate("window.imported[0].name", in: webView) as? String,
            "rosette-study.svg"
        )
        XCTAssertEqual(
            try evaluate("Object.keys(window.imported[0]).sort().join(',')", in: webView) as? String,
            "name,svg",
            "the page is handed a name and the text — it has no path to send back"
        )

        // The artist edits it on the bed and saves.
        _ = try evaluate("window.saveFirst('<svg>edited on the bed</svg>')", in: webView)
        settle()

        XCTAssertEqual(
            try String(contentsOf: original, encoding: .utf8),
            "<svg>edited on the bed</svg>",
            "the design must go back over the file that was opened"
        )
        XCTAssertEqual(try evaluate("window.saveResults.length", in: webView) as? Int, 1)
        XCTAssertEqual(try evaluate("window.saveResults[0].ok", in: webView) as? Bool, true)
        XCTAssertEqual(
            try evaluate("window.saveResults[0].path", in: webView) as? String,
            original.path,
            "the studio says which file it wrote, so the artist can see where it went"
        )
    }

    func testADrawingWithNoOriginalIsToldSoRatherThanWrittenSomewhere() throws {
        let actions = WebActions()
        let coordinator = makeCoordinator(actions)
        let configuration = WKWebViewConfiguration()
        coordinator.installSettingsBridge(in: configuration.userContentController)
        let webView = WKWebView(frame: .zero, configuration: configuration)
        defer { coordinator.invalidate(webView: webView) }

        actions.attach(webView)
        load(webView)
        actions.markReady()

        _ = try evaluate(
            """
            window.imported = [{name: 'drawing-1.svg'}];
            window.saveFirst('<svg>made in the app</svg>');
            """,
            in: webView
        )
        settle()

        // The studio's answer is "save a copy instead", not an error the artist
        // has to interpret.
        XCTAssertEqual(try evaluate("window.saveResults[0].ok", in: webView) as? Bool, false)
        XCTAssertEqual(
            try evaluate("window.saveResults[0].reason", in: webView) as? String,
            "no-source"
        )
    }
}

private final class LoadProbe: NSObject, WKNavigationDelegate {
    private let finished: @MainActor () -> Void

    init(finished: @escaping @MainActor () -> Void) {
        self.finished = finished
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        MainActor.assumeIsolated { finished() }
    }
}
