import AppKit
import Foundation
import SwiftUI
import UniformTypeIdentifiers
import WebKit

struct ClaylineWebView: NSViewRepresentable {
    let launch: EngineLaunch
    let actions: WebActions
    let onReady: @MainActor () -> Void
    let onFailure: @MainActor (String) -> Void

    func makeCoordinator() -> Coordinator {
        Coordinator(
            launch: launch,
            actions: actions,
            onReady: onReady,
            onFailure: onFailure
        )
    }

    func makeNSView(context: Context) -> WKWebView {
        let configuration = WKWebViewConfiguration()
        configuration.websiteDataStore = .nonPersistent()
        configuration.preferences.javaScriptCanOpenWindowsAutomatically = false
        configuration.defaultWebpagePreferences.allowsContentJavaScript = true
        context.coordinator.installSettingsBridge(in: configuration.userContentController)

        let webView = WKWebView(frame: .zero, configuration: configuration)
        webView.navigationDelegate = context.coordinator
        webView.uiDelegate = context.coordinator
        webView.allowsBackForwardNavigationGestures = false
        webView.allowsMagnification = true
        webView.isInspectable = false
        context.coordinator.begin(in: webView)
        return webView
    }

    func updateNSView(_ webView: WKWebView, context: Context) {}

    static func dismantleNSView(_ webView: WKWebView, coordinator: Coordinator) {
        coordinator.invalidate(webView: webView)
        webView.navigationDelegate = nil
        webView.uiDelegate = nil
        webView.stopLoading()
    }

    @MainActor
    final class Coordinator: NSObject, WKNavigationDelegate, WKUIDelegate, WKDownloadDelegate,
        WKScriptMessageHandler
    {
        private let launch: EngineLaunch
        private let policy: NavigationPolicy
        private let actions: WebActions
        private let settingsStore: StudioSettingsStore
        private let onReady: @MainActor () -> Void
        private let onFailure: @MainActor (String) -> Void
        private var healthSession: URLSession?
        private var didBegin = false
        private var didFinishInitialNavigation = false
        private var invalidated = false

        init(
            launch: EngineLaunch,
            actions: WebActions,
            onReady: @escaping @MainActor () -> Void,
            onFailure: @escaping @MainActor (String) -> Void
        ) {
            self.launch = launch
            self.policy = NavigationPolicy(origin: launch.originURL)
            self.actions = actions
            self.settingsStore = StudioSettingsStore()
            self.onReady = onReady
            self.onFailure = onFailure
        }

        /// The page asks to save a design back over the file it was opened
        /// from through this name.
        static let saveSVGHandlerName = "claylineSaveSVG"

        func installSettingsBridge(in userContentController: WKUserContentController) {
            userContentController.addUserScript(settingsStore.userScript())
            userContentController.add(self, name: StudioSettingsStore.messageHandlerName)
            userContentController.add(self, name: Self.saveSVGHandlerName)
        }

        func begin(in webView: WKWebView) {
            guard !didBegin else { return }
            didBegin = true
            actions.attach(webView)
            actions.onMeshSelected = { [weak self] url in
                self?.settingsStore.rememberMeshURL(url)
            }

            guard let cookie = Self.sessionCookie(for: launch) else {
                fail("Clayline could not create its private local session.")
                return
            }

            // The private cookie is installed in WebKit before any health or page request.
            webView.configuration.websiteDataStore.httpCookieStore.setCookie(cookie) { [weak self, weak webView] in
                DispatchQueue.main.async {
                    guard let self, let webView, !self.invalidated else { return }
                    self.checkAuthenticatedHealth(thenLoadIn: webView)
                }
            }
        }

        func invalidate(webView: WKWebView) {
            invalidated = true
            healthSession?.invalidateAndCancel()
            healthSession = nil
            actions.detach(webView)
            webView.configuration.userContentController.removeScriptMessageHandler(
                forName: StudioSettingsStore.messageHandlerName
            )
            webView.configuration.userContentController.removeScriptMessageHandler(
                forName: Self.saveSVGHandlerName
            )
        }

        func userContentController(
            _ userContentController: WKUserContentController,
            didReceive message: WKScriptMessage
        ) {
            if message.name == Self.saveSVGHandlerName {
                handleSaveSVG(message.body)
                return
            }
            guard message.name == StudioSettingsStore.messageHandlerName else { return }
            _ = settingsStore.apply(messageBody: message.body)
        }

        /// Save a design over the file it was imported from. The body carries
        /// the name the page was given at import and the SVG text; the shell
        /// looks the name up in what it opened, because the page has no path.
        private func handleSaveSVG(_ body: Any) {
            guard let payload = body as? [String: Any],
                  let name = payload["name"] as? String,
                  let svg = payload["svg"] as? String
            else {
                report(saveOutcome: .failed("malformed save request"), for: "")
                return
            }
            report(saveOutcome: actions.saveSVGOverOriginal(name: name, svg: svg), for: name)
        }

        private func report(saveOutcome: SVGSaveOutcome, for name: String) {
            let payload: [String: Any] = [
                "name": name,
                "ok": saveOutcome.savedPath != nil,
                "path": saveOutcome.savedPath ?? NSNull(),
                "reason": {
                    switch saveOutcome {
                    case .wrote: return NSNull()
                    case .noKnownSource: return "no-source"
                    case .tooLarge: return "too-large"
                    case let .failed(message): return message
                    }
                }() as Any,
            ]
            guard let data = try? JSONSerialization.data(withJSONObject: payload),
                  let json = String(data: data, encoding: .utf8)
            else { return }
            actions.reportSVGSaveResult(json)
        }

        private static func sessionCookie(for launch: EngineLaunch) -> HTTPCookie? {
            HTTPCookie(properties: [
                .originURL: launch.originURL,
                .domain: EngineReadyMessage.expectedHost,
                .path: "/",
                .name: "clayline_session",
                .value: launch.token,
                .discard: "TRUE",
                .sameSitePolicy: "Strict",
                HTTPCookiePropertyKey("HttpOnly"): "TRUE"
            ])
        }

        private func checkAuthenticatedHealth(thenLoadIn webView: WKWebView) {
            let configuration = URLSessionConfiguration.ephemeral
            configuration.httpShouldSetCookies = false
            configuration.httpCookieAcceptPolicy = .never
            let session = URLSession(configuration: configuration)
            healthSession = session

            pollAuthenticatedHealth(
                session: session,
                webView: webView,
                deadline: Date().addingTimeInterval(15)
            )
        }

        private func pollAuthenticatedHealth(
            session: URLSession,
            webView: WKWebView,
            deadline: Date
        ) {
            var request = URLRequest(url: launch.healthURL)
            request.cachePolicy = .reloadIgnoringLocalAndRemoteCacheData
            request.timeoutInterval = 1
            request.setValue("clayline_session=\(launch.token)", forHTTPHeaderField: "Cookie")

            session.dataTask(with: request) { [weak self, weak webView] data, response, error in
                DispatchQueue.main.async {
                    guard let self, let webView, !self.invalidated else { return }
                    let healthy = (response as? HTTPURLResponse)?.statusCode == 200
                        && data.flatMap {
                            try? JSONSerialization.jsonObject(with: $0) as? [String: Any]
                        }?["status"] as? String == "ok"
                    if healthy {
                        self.healthSession?.finishTasksAndInvalidate()
                        self.healthSession = nil
                        webView.load(URLRequest(url: self.launch.originURL))
                    } else if Date() < deadline {
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) { [weak self, weak webView] in
                            guard let self, let webView, !self.invalidated else { return }
                            self.pollAuthenticatedHealth(
                                session: session,
                                webView: webView,
                                deadline: deadline
                            )
                        }
                    } else {
                        let detail = error?.localizedDescription
                            ?? "the authenticated health check did not pass"
                        self.fail("Clayline’s local engine did not become ready: \(detail).")
                    }
                }
            }.resume()
        }

        private func fail(_ message: String) {
            guard !invalidated else { return }
            invalidated = true
            healthSession?.invalidateAndCancel()
            healthSession = nil
            onFailure(message)
        }

        func webView(
            _ webView: WKWebView,
            decidePolicyFor navigationAction: WKNavigationAction,
            decisionHandler: @escaping (WKNavigationActionPolicy) -> Void
        ) {
            if navigationAction.shouldPerformDownload,
               policy.allowsDownload(from: navigationAction.request.url) {
                decisionHandler(.download)
                return
            }
            guard navigationAction.targetFrame != nil,
                  policy.allowsNavigation(to: navigationAction.request.url)
            else {
                decisionHandler(.cancel)
                return
            }
            decisionHandler(.allow)
        }

        func webView(
            _ webView: WKWebView,
            decidePolicyFor navigationResponse: WKNavigationResponse,
            decisionHandler: @escaping (WKNavigationResponsePolicy) -> Void
        ) {
            if !navigationResponse.canShowMIMEType,
               policy.allowsDownload(from: navigationResponse.response.url) {
                decisionHandler(.download)
                return
            }
            guard policy.allowsNavigation(to: navigationResponse.response.url) else {
                decisionHandler(.cancel)
                return
            }
            decisionHandler(.allow)
        }

        func webView(_ webView: WKWebView, navigationAction: WKNavigationAction, didBecome download: WKDownload) {
            download.delegate = self
        }

        func webView(_ webView: WKWebView, navigationResponse: WKNavigationResponse, didBecome download: WKDownload) {
            download.delegate = self
        }

        func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
            guard !didFinishInitialNavigation else { return }
            didFinishInitialNavigation = true
            actions.markReady()
            // A restart is a clean slate — the launch-time last-mesh restore
            // (2026-07-23) was the third stale-state path and the one that
            // survived the web-side cleanup, because it lives in the native
            // shell (Pete 2026-07-26: "why did this fucking load on open").
            // Files load when the artist drops them, never by memory.
            settingsStore.forgetMeshURL()
            onReady()
        }

        func webView(
            _ webView: WKWebView,
            didFail navigation: WKNavigation!,
            withError error: Error
        ) {
            fail("Clayline’s interface could not load: \(error.localizedDescription)")
        }

        func webView(
            _ webView: WKWebView,
            didFailProvisionalNavigation navigation: WKNavigation!,
            withError error: Error
        ) {
            fail("Clayline’s interface could not connect: \(error.localizedDescription)")
        }

        func webViewWebContentProcessDidTerminate(_ webView: WKWebView) {
            fail("Clayline’s interface process stopped unexpectedly.")
        }

        func webView(
            _ webView: WKWebView,
            createWebViewWith configuration: WKWebViewConfiguration,
            for navigationAction: WKNavigationAction,
            windowFeatures: WKWindowFeatures
        ) -> WKWebView? {
            nil
        }

        func webView(
            _ webView: WKWebView,
            runOpenPanelWith parameters: WKOpenPanelParameters,
            initiatedByFrame frame: WKFrameInfo,
            completionHandler: @escaping ([URL]?) -> Void
        ) {
            // One read answers both questions — mode, and whether the page
            // opened the picker for a reference photo — and clears the
            // one-shot photo marker so a later SVG picker never inherits it.
            let script = """
            (() => {
              const body = document.body;
              const request = body.dataset.claylineFileRequest || "";
              delete body.dataset.claylineFileRequest;
              return (body.dataset.claylineMode || "tiles") + ":" + request;
            })()
            """
            webView.evaluateJavaScript(script) { [weak self, weak webView] value, _ in
                guard let self, let webView, !self.invalidated else {
                    completionHandler(nil)
                    return
                }
                self.presentOpenPanel(
                    for: ClaylineOpenRequest(raw: value as? String),
                    webView: webView,
                    parameters: parameters,
                    completionHandler: completionHandler
                )
            }
        }

        private func presentOpenPanel(
            for request: ClaylineOpenRequest,
            webView: WKWebView,
            parameters: WKOpenPanelParameters,
            completionHandler: @escaping ([URL]?) -> Void
        ) {
            let mode = request.mode
            let panel = NSOpenPanel()
            if request.isReferencePhoto {
                panel.title = "Open a Reference Photo"
                panel.allowedContentTypes = ClaylineFileTypes.referencePhotoTypes
                panel.allowsMultipleSelection = false
            } else {
                panel.title = mode == .weave ? "Open One Mesh" : "Open Centerline SVGs"
                panel.allowedContentTypes = ClaylineFileTypes.allowedContentTypes(for: mode)
                panel.allowsMultipleSelection =
                    mode == .tiles && parameters.allowsMultipleSelection
            }
            panel.prompt = "Open"
            panel.canChooseDirectories = false
            panel.canChooseFiles = true
            panel.resolvesAliases = true

            if let window = webView.window {
                panel.beginSheetModal(for: window) { [weak self] response in
                    let urls = response == .OK ? panel.urls : nil
                    if mode == .weave, !request.isReferencePhoto, let url = urls?.first {
                        self?.settingsStore.rememberMeshURL(url)
                    }
                    completionHandler(urls)
                }
            } else {
                panel.begin { [weak self] response in
                    let urls = response == .OK ? panel.urls : nil
                    if mode == .weave, !request.isReferencePhoto, let url = urls?.first {
                        self?.settingsStore.rememberMeshURL(url)
                    }
                    completionHandler(urls)
                }
            }
        }

        func download(
            _ download: WKDownload,
            decideDestinationUsing response: URLResponse,
            suggestedFilename: String,
            completionHandler: @escaping (URL?) -> Void
        ) {
            let safeName = SafeFilename.download(suggestedFilename)
            let isPattern = safeName.lowercased().hasSuffix(".json")
            let panel = NSSavePanel()
            panel.title = isPattern ? "Save Clayline pattern" : "Save Clayline G-code"
            panel.prompt = "Save"
            panel.allowedContentTypes = isPattern ? [.json] : [ClaylineFileTypes.gcode]
            panel.allowsOtherFileTypes = false
            panel.canCreateDirectories = true
            panel.isExtensionHidden = false
            panel.nameFieldStringValue = safeName

            if let window = NSApp.keyWindow ?? NSApp.mainWindow {
                panel.beginSheetModal(for: window) { result in
                    completionHandler(result == .OK ? Self.replaceableDestination(panel.url) : nil)
                }
            } else {
                panel.begin { result in
                    completionHandler(result == .OK ? Self.replaceableDestination(panel.url) : nil)
                }
            }
        }

        // WKDownload refuses to write over an existing file, so honoring the
        // save panel's "Replace?" consent requires removing the old file
        // ourselves — otherwise every re-export to the same name dies and
        // the artist keeps reading a stale file (Pete 2026-07-21: three
        // calibrated re-exports silently lost to one drape-era file).
        nonisolated static func replaceableDestination(_ url: URL?) -> URL? {
            guard let url else { return nil }
            // If removal fails, still hand the URL to WKDownload: its failure
            // then surfaces through the didFailWithError alert instead of a
            // silent cancel.
            if FileManager.default.fileExists(atPath: url.path) {
                try? FileManager.default.removeItem(at: url)
            }
            return url
        }

        func download(_ download: WKDownload, didFailWithError error: Error, resumeData: Data?) {
            let alert = NSAlert()
            alert.alertStyle = .warning
            alert.messageText = "Saving the file failed"
            alert.informativeText = error.localizedDescription
            alert.runModal()
        }
    }
}
