import WebKit
import XCTest

@testable import Clayline

/// The reference lightbox, importing inside the environment the packaged app
/// actually runs: a `WKWebView` with an EPHEMERAL website data store, exactly
/// as `ClaylineWebView.makeNSView` configures it. In that store IndexedDB may
/// refuse to exist at all — a photo that decoded must place anyway, because
/// the studio's own persistence model needs nothing beyond the session
/// (restart is a clean slate). A browser-side test cannot see this; only the
/// real WebKit store can (Pete 2026-08-01: "whenever I do it says reference
/// not placed").
@MainActor
final class ReferenceStoreEphemeralTests: XCTestCase {
    private static func staticFile(_ name: String) throws -> String {
        let root = URL(fileURLWithPath: #filePath)
            .deletingLastPathComponent()  // this file → ClaylineTests
            .deletingLastPathComponent()  // → Tests
            .deletingLastPathComponent()  // → ClaylineMac
            .deletingLastPathComponent()  // → app
            .deletingLastPathComponent()  // → repository root
        let url = root
            .appendingPathComponent("src/clayline/webui/static")
            .appendingPathComponent(name)
        return try String(contentsOf: url, encoding: .utf8)
    }

    private func load(_ webView: WKWebView) {
        let expectation = expectation(description: "page loaded")
        let probe = ReferenceLoadProbe { expectation.fulfill() }
        webView.navigationDelegate = probe
        webView.loadHTMLString(
            "<!doctype html><meta charset=\"utf-8\"><body></body>",
            baseURL: URL(string: "http://127.0.0.1:49152/")!
        )
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

    /// Polls the page until the async probe posts its outcome.
    private func outcome(in webView: WKWebView) throws -> [String: Any] {
        for _ in 0..<50 {
            if let raw = try evaluate(
                "window.outcome ? JSON.stringify(window.outcome) : null",
                in: webView
            ) as? String,
                let data = raw.data(using: .utf8),
                let parsed = try JSONSerialization.jsonObject(with: data) as? [String: Any]
            {
                return parsed
            }
            let tick = expectation(description: "tick")
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) { tick.fulfill() }
            wait(for: [tick], timeout: 5)
        }
        XCTFail("importImage never settled")
        return [:]
    }

    func testAPickedPhotoPlacesEvenWhenTheEphemeralStoreHasNoIndexedDB() throws {
        let configuration = WKWebViewConfiguration()
        configuration.websiteDataStore = .nonPersistent()
        configuration.defaultWebpagePreferences.allowsContentJavaScript = true
        let webView = WKWebView(frame: .zero, configuration: configuration)

        load(webView)
        _ = try evaluate(try Self.staticFile("reference-store.js"), in: webView)
        _ = try evaluate(
            """
            window.outcome = null;
            (async () => {
              try {
                const canvas = document.createElement("canvas");
                canvas.width = 8; canvas.height = 8;
                const context = canvas.getContext("2d");
                context.fillStyle = "#a52"; context.fillRect(0, 0, 8, 8);
                const blob = await new Promise((r) => canvas.toBlob(r, "image/png"));
                const file = new File([blob], "probe.png", { type: "image/png" });
                const imported = await window.ClaylineReferenceStore.importImage(file);
                const drawable = window.ClaylineReferenceStore.bitmap(imported.imageId, () => {});
                window.outcome = {
                  ok: true,
                  width: imported.width,
                  height: imported.height,
                  cached: Boolean(drawable),
                };
              } catch (error) {
                window.outcome = { ok: false, message: String(error) };
              }
            })();
            null;
            """,
            in: webView
        )

        let result = try outcome(in: webView)
        XCTAssertEqual(result["ok"] as? Bool, true, "\(result)")
        XCTAssertEqual(result["width"] as? Int, 8)
        XCTAssertEqual(result["height"] as? Int, 8)
        XCTAssertEqual(result["cached"] as? Bool, true, "session cache must hold the drawable")
    }
}

private final class ReferenceLoadProbe: NSObject, WKNavigationDelegate {
    private let onFinish: () -> Void

    init(onFinish: @escaping () -> Void) {
        self.onFinish = onFinish
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        DispatchQueue.main.async(execute: onFinish)
    }
}
