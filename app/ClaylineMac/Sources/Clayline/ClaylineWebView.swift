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
        /// Every download in flight, by the WKDownload that is writing it.
        private var stagedDownloads: [ObjectIdentifier: StagedDownload] = [:]
        /// A project the Open panel has handed to the page but the page has
        /// not read yet. It becomes the window's document only if it opens.
        private var projectAwaitingThePage: URL?
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

        /// The page tells the shell a project has been read through and is on
        /// the bed, so a file it refuses never renames the window.
        static let projectOpenedHandlerName = "claylineProjectOpened"

        func installSettingsBridge(in userContentController: WKUserContentController) {
            userContentController.addUserScript(settingsStore.userScript())
            // The page shows its gallery buttons only when the shell says the
            // example drawings are really here.
            if let galleryScript = ClaylineGallery.userScript() {
                userContentController.addUserScript(galleryScript)
            }
            userContentController.add(self, name: StudioSettingsStore.messageHandlerName)
            userContentController.add(self, name: Self.saveSVGHandlerName)
            userContentController.add(self, name: Self.projectOpenedHandlerName)
        }

        func begin(in webView: WKWebView) {
            guard !didBegin else { return }
            didBegin = true
            actions.attach(webView)
            actions.onMeshSelected = { [weak self] url in
                self?.settingsStore.rememberMeshURL(url)
            }
            actions.onProjectOpened = { [weak self] url in
                self?.rememberProject(url)
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
            webView.configuration.userContentController.removeScriptMessageHandler(
                forName: Self.projectOpenedHandlerName
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
            if message.name == Self.projectOpenedHandlerName {
                handleProjectOpened(message.body)
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

        /// The page has finished with the project it was handed — opened, or
        /// turned down. Only an open gives the window its name and starts the
        /// next save panel in its folder; a damaged or foreign file leaves
        /// both alone. Either way the shell lets go of the file here, so a
        /// project chosen later cannot inherit the refused one's folder by
        /// happening to share its name.
        private func handleProjectOpened(_ body: Any) {
            guard let url = projectAwaitingThePage else { return }
            projectAwaitingThePage = nil
            let payload = body as? [String: Any]
            guard payload?["ok"] as? Bool ?? true else { return }
            let name = payload?["name"] as? String ?? ""
            guard name.isEmpty || name == url.lastPathComponent else { return }
            actions.projectWasOpened(at: url)
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
            // One read answers both questions — mode, and what the page opened
            // the picker for — and clears the one-shot marker so a later SVG
            // picker never inherits it.
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
            if request.isProject {
                panel.title = "Open a Clayline Project"
                panel.allowedContentTypes = ClaylineFileTypes.projectTypes
                panel.allowsMultipleSelection = false
            } else if request.isReferencePhoto {
                panel.title = "Open a Reference Photo"
                panel.allowedContentTypes = ClaylineFileTypes.referencePhotoTypes
                panel.allowsMultipleSelection = false
            } else if request.isPrintFile {
                panel.title = "Open a Clayline Print File"
                panel.allowedContentTypes = ClaylineFileTypes.printFileTypes
                panel.allowsMultipleSelection = false
            } else {
                panel.title = mode == .weave
                    ? "Open One Mesh, Project, or Print File"
                    : "Open Drawings"
                panel.allowedContentTypes = ClaylineFileTypes.allowedContentTypes(for: mode)
                panel.allowsMultipleSelection =
                    mode == .tiles && parameters.allowsMultipleSelection
            }
            if request.isDrawingPicker {
                // The gallery sits inside the app, and the app can be somewhere
                // else at every launch, so it is found afresh here each time.
                let gallery = ClaylineGallery.bundledURL()
                if request.isGallery, gallery != nil {
                    panel.title = "Open an Example Drawing"
                }
                if let start = ClaylineGallery.startingFolder(
                    isGalleryRequest: request.isGallery,
                    rememberedOwn: settingsStore.drawingFolderURL(gallery: gallery),
                    rememberedGallery: settingsStore.galleryFolderURL(gallery: gallery),
                    gallery: gallery
                ) {
                    panel.directoryURL = start
                }
            } else if let rescue = ClaylineGallery.rescuedStartingFolder(
                panelDefault: panel.directoryURL,
                candidates: ClaylineGallery.ownFolders(settingsStore: settingsStore)
            ) {
                // A gallery visit leaves macOS's shared "last folder" inside the
                // app; no other panel may start there.
                panel.directoryURL = rescue
            }
            panel.prompt = "Open"
            panel.canChooseDirectories = false
            panel.canChooseFiles = true
            panel.resolvesAliases = true

            let remember: ([URL]?) -> Void = { [weak self] urls in
                guard let url = urls?.first else { return }
                if request.isProject {
                    // The page has not read a byte of it yet; it reports back
                    // when it has, and the window follows it only then.
                    self?.projectAwaitingThePage = url
                } else if mode == .weave, !request.isReferencePhoto {
                    self?.settingsStore.rememberMeshURL(url)
                } else if request.isDrawingPicker {
                    self?.settingsStore.rememberDrawingFolder(
                        for: url,
                        gallery: ClaylineGallery.bundledURL()
                    )
                }
            }

            if let window = webView.window {
                panel.beginSheetModal(for: window) { response in
                    let urls = response == .OK ? panel.urls : nil
                    remember(urls)
                    completionHandler(urls)
                }
            } else {
                panel.begin { response in
                    let urls = response == .OK ? panel.urls : nil
                    remember(urls)
                    completionHandler(urls)
                }
            }
        }

        /// A project just saved or opened becomes the window's document and
        /// the folder the next save panel starts in.
        private func rememberProject(_ url: URL) {
            settingsStore.rememberProjectURL(url)
            guard let window = NSApp.keyWindow ?? NSApp.mainWindow else { return }
            window.representedURL = url
            window.title = url.deletingPathExtension().lastPathComponent
        }

        func download(
            _ download: WKDownload,
            decideDestinationUsing response: URLResponse,
            suggestedFilename: String,
            completionHandler: @escaping (URL?) -> Void
        ) {
            let safeName = SafeFilename.download(suggestedFilename)
            let lowered = safeName.lowercased()
            let isProject = lowered.hasSuffix(".\(ClaylineFileTypes.projectExtension)")
            let isPattern = lowered.hasSuffix(".json")
            let panel = NSSavePanel()
            panel.title = isProject
                ? "Save Clayline Project"
                : (isPattern ? "Save Clayline pattern" : "Save Clayline G-code")
            panel.prompt = "Save"
            panel.allowedContentTypes = isProject
                ? ClaylineFileTypes.projectTypes
                : (isPattern ? [.json] : [ClaylineFileTypes.gcode])
            panel.allowsOtherFileTypes = false
            panel.canCreateDirectories = true
            panel.isExtensionHidden = false
            panel.nameFieldStringValue = safeName
            if isProject, let directory = settingsStore.projectDirectoryURL() {
                panel.directoryURL = directory
            } else if let rescue = ClaylineGallery.rescuedStartingFolder(
                panelDefault: panel.directoryURL,
                candidates: ClaylineGallery.ownFolders(settingsStore: settingsStore)
            ) {
                // Never offer to save inside the app: a gallery visit leaves
                // macOS's shared "last folder" there.
                panel.directoryURL = rescue
            }

            if let window = NSApp.keyWindow ?? NSApp.mainWindow {
                panel.beginSheetModal(for: window) { [weak self] result in
                    completionHandler(
                        self?.stage(
                            download,
                            at: result == .OK ? panel.url : nil,
                            isProject: isProject
                        )
                    )
                }
            } else {
                panel.begin { [weak self] result in
                    completionHandler(
                        self?.stage(
                            download,
                            at: result == .OK ? panel.url : nil,
                            isProject: isProject
                        )
                    )
                }
            }
        }

        /// Hand WebKit a working file to write into, and remember where those
        /// bytes are meant to land.
        private func stage(
            _ download: WKDownload,
            at destination: URL?,
            isProject: Bool
        ) -> URL? {
            guard let destination else {
                // A cancelled panel is not a failure; the page's "Saving
                // project…" line is simply cleared.
                if isProject {
                    actions.reportProjectSaveResult(ok: false, name: nil)
                }
                return nil
            }
            let staged = StagedDownload(destination: destination, isProject: isProject)
            stagedDownloads[ObjectIdentifier(download)] = staged
            return staged.staging
        }

        // WKDownload refuses to write over an existing file. Deleting the
        // chosen file first honoured the panel's "Replace?" consent but threw
        // the artist's only copy away before a single byte arrived, so a
        // failed write left nothing at all. Every download now writes to a
        // sibling working file and takes the chosen name only once the bytes
        // are all there (Pete 2026-07-21: three calibrated re-exports lost to
        // one drape-era file — that fix must not cost a whole project).
        func downloadDidFinish(_ download: WKDownload) {
            guard let staged = stagedDownloads.removeValue(forKey: ObjectIdentifier(download)) else {
                return
            }
            let landed = StagedDownload.commit(staging: staged.staging, destination: staged.destination)
            guard staged.isProject else {
                if !landed { presentSaveFailure("The file was not written.") }
                return
            }
            if landed {
                rememberProject(staged.destination)
                actions.reportProjectSaveResult(ok: true, name: staged.destination.lastPathComponent)
            } else {
                presentSaveFailure("Clayline kept the project that was already there.")
                actions.reportProjectSaveResult(ok: false, name: nil)
            }
        }

        func download(_ download: WKDownload, didFailWithError error: Error, resumeData: Data?) {
            let staged = stagedDownloads.removeValue(forKey: ObjectIdentifier(download))
            if let staged {
                StagedDownload.discard(staging: staged.staging)
                if staged.isProject {
                    actions.reportProjectSaveResult(ok: false, name: nil)
                }
            }
            presentSaveFailure(error.localizedDescription)
        }

        private func presentSaveFailure(_ detail: String) {
            let alert = NSAlert()
            alert.alertStyle = .warning
            alert.messageText = "Saving the file failed"
            alert.informativeText = detail
            alert.runModal()
        }
    }
}

/// One download in flight. WebKit writes the bytes into `staging`, a sibling
/// working file, and the artist's chosen `destination` is only touched once
/// the whole file has arrived — so a failed or cancelled write leaves what
/// was already on disk byte-identical.
struct StagedDownload: Equatable {
    let destination: URL
    let staging: URL
    let isProject: Bool

    init(destination: URL, isProject: Bool) {
        let target = destination.standardizedFileURL
        self.destination = target
        self.staging = target
            .deletingLastPathComponent()
            .appendingPathComponent(".clayline-writing-\(UUID().uuidString)")
        self.isProject = isProject
    }

    /// Move the finished bytes onto the chosen name. The old file is only
    /// replaced here, at the last possible moment.
    @discardableResult
    static func commit(staging: URL, destination: URL) -> Bool {
        let manager = FileManager.default
        guard manager.fileExists(atPath: staging.path) else { return false }
        do {
            if manager.fileExists(atPath: destination.path) {
                _ = try manager.replaceItemAt(destination, withItemAt: staging)
            } else {
                try manager.moveItem(at: staging, to: destination)
            }
            return true
        } catch {
            discard(staging: staging)
            return false
        }
    }

    /// Nothing usable was written: drop the working file and leave the
    /// artist's own file alone.
    static func discard(staging: URL) {
        try? FileManager.default.removeItem(at: staging)
    }
}
