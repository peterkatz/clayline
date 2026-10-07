import WebKit
import XCTest

@testable import Clayline

/// Edit → Undo and Edit → Redo, driven the way the menu drives them: a real
/// `WKWebView` with the shell's real bridge installed, and a page shaped like
/// the studio's `claylineDesktop`.
@MainActor
final class HistoryMenuBridgeTests: XCTestCase {
    private func makeCoordinator(_ actions: WebActions) -> ClaylineWebView.Coordinator {
        let launch = EngineLaunch(
            readiness: EngineReadyMessage(
                schema: EngineReadyMessage.expectedSchema,
                host: EngineReadyMessage.expectedHost,
                port: 49_152,
                pid: 4_321
            ),
            token: String(repeating: "b", count: 32)
        )
        return ClaylineWebView.Coordinator(
            launch: launch,
            actions: actions,
            onReady: {},
            onFailure: { _ in }
        )
    }

    /// Counts every step the shell asks for and answers the way the studio
    /// does. `window.answer` says what the page reports back.
    private let page = """
    <!doctype html><meta charset="utf-8"><body><script>
    window.flagAtLoad = window.claylineNativeHistoryMenu === true;
    window.steps = [];
    window.answer = "done";
    window.claylineDesktop = {
      undo: () => { window.steps.push("undo"); return window.answer; },
      redo: () => { window.steps.push("redo"); return window.answer; },
    };
    // The studio's key handler, reduced to its guard: in the app the menu owns
    // Command-Z, so the page leaves the key alone.
    window.keySteps = 0;
    window.addEventListener("keydown", (event) => {
      if (!(event.metaKey || event.ctrlKey) || event.key.toLowerCase() !== "z") return;
      if (window.claylineNativeHistoryMenu === true) return;
      window.keySteps += 1;
      event.preventDefault();
    });
    </script></body>
    """

    private func load(_ webView: WKWebView) {
        let expectation = expectation(description: "page loaded")
        let probe = HistoryLoadProbe { expectation.fulfill() }
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
        let expectation = expectation(description: "page answered")
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.4) { expectation.fulfill() }
        wait(for: [expectation], timeout: 5)
    }

    private func makeStudio() -> (WebActions, ClaylineWebView.Coordinator, WKWebView) {
        let actions = WebActions()
        let coordinator = makeCoordinator(actions)
        let configuration = WKWebViewConfiguration()
        coordinator.installSettingsBridge(in: configuration.userContentController)
        let webView = WKWebView(frame: .zero, configuration: configuration)
        actions.attach(webView)
        load(webView)
        return (actions, coordinator, webView)
    }

    func testTheBridgeNamesThePageHistoryAndReadsItsAnswer() {
        XCTAssertEqual(
            HistoryMenuBridge.script(for: .undo),
            "window.claylineDesktop && window.claylineDesktop.undo()"
        )
        XCTAssertEqual(
            HistoryMenuBridge.script(for: .redo),
            "window.claylineDesktop && window.claylineDesktop.redo()"
        )
        XCTAssertEqual(HistoryMenuBridge.outcome(of: "done"), .stepped)
        XCTAssertEqual(HistoryMenuBridge.outcome(of: "none"), .nothingToStep)
        XCTAssertEqual(HistoryMenuBridge.outcome(of: "native"), .nativeText)
        XCTAssertEqual(HistoryMenuBridge.outcome(of: nil), .nothingToStep)
        XCTAssertEqual(HistoryMenuBridge.outcome(of: true), .nothingToStep)
        XCTAssertEqual(HistoryMenuBridge.nativeSelector(for: .undo), Selector(("undo:")))
        XCTAssertEqual(HistoryMenuBridge.nativeSelector(for: .redo), Selector(("redo:")))
    }

    func testThePageHearsTheMenuOwnsCommandZBeforeItsOwnScriptsRun() throws {
        let (_, coordinator, webView) = makeStudio()
        defer { coordinator.invalidate(webView: webView) }
        XCTAssertEqual(try evaluate("window.flagAtLoad", in: webView) as? Bool, true)
    }

    func testEditMenuUndoAndRedoEachStepThePageOnce() throws {
        let (actions, coordinator, webView) = makeStudio()
        defer { coordinator.invalidate(webView: webView) }
        var native: [HistoryMenuBridge.Direction] = []
        actions.performNativeHistory = { native.append($0) }

        // Before the page is ready the menu does nothing at all.
        actions.undo()
        settle()
        XCTAssertEqual(try evaluate("window.steps.length", in: webView) as? Int, 0)

        actions.markReady()
        actions.undo()
        settle()
        XCTAssertEqual(try evaluate("window.steps.join(',')", in: webView) as? String, "undo")
        actions.redo()
        settle()
        XCTAssertEqual(try evaluate("window.steps.join(',')", in: webView) as? String, "undo,redo")
        XCTAssertEqual(native, [], "a step the page took is never also a native text undo")
    }

    func testAKeyPressReachesThePageHandlerNotAtAllInTheApp() throws {
        let (actions, coordinator, webView) = makeStudio()
        defer { coordinator.invalidate(webView: webView) }
        actions.markReady()
        // The same Command-Z the menu answers: the page's own handler must not
        // also step, or one press would undo twice.
        _ = try evaluate(
            """
            window.dispatchEvent(new KeyboardEvent("keydown", {key: "z", metaKey: true}));
            window.keySteps
            """,
            in: webView
        )
        actions.undo()
        settle()
        XCTAssertEqual(try evaluate("window.keySteps", in: webView) as? Int, 0)
        XCTAssertEqual(try evaluate("window.steps.length", in: webView) as? Int, 1)
    }

    func testFreeTextKeepsItsOwnNativeUndo() throws {
        let (actions, coordinator, webView) = makeStudio()
        defer { coordinator.invalidate(webView: webView) }
        var native: [HistoryMenuBridge.Direction] = []
        actions.performNativeHistory = { native.append($0) }
        actions.markReady()
        _ = try evaluate("window.answer = 'native'; true", in: webView)

        actions.undo()
        settle()
        actions.redo()
        settle()
        XCTAssertEqual(native, [.undo, .redo])
    }
}

private final class HistoryLoadProbe: NSObject, WKNavigationDelegate {
    private let finished: @MainActor () -> Void

    init(finished: @escaping @MainActor () -> Void) {
        self.finished = finished
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        MainActor.assumeIsolated { finished() }
    }
}
