import AppKit
import Combine
import Foundation
import WebKit

@MainActor
final class WebActions: ObservableObject {
    static let maximumSVGBytes = 8 * 1_024 * 1_024
    static let maximumMeshBytes = 64 * 1_024 * 1_024

    @Published private(set) var isReady = false
    var onMeshSelected: ((URL) -> Void)?
    var hasPendingImports: Bool { !pendingImports.isEmpty }
    private weak var webView: WKWebView?
    private var pendingImports: [ClaylineImportSelection] = []
    /// Where each imported design was read from, so an edit can be written back
    /// over the artist's own file instead of copied into Downloads.
    private var svgSources = SVGSourceIndex()

    func attach(_ webView: WKWebView) {
        self.webView = webView
        isReady = false
    }

    func markReady() {
        isReady = true
        let queued = pendingImports
        pendingImports = []
        queued.forEach(deliver)
    }

    func detach(_ webView: WKWebView) {
        guard self.webView === webView else { return }
        self.webView = nil
        isReady = false
        onMeshSelected = nil
    }

    func openDocuments() {
        guard isReady else { return }
        webView?.evaluateJavaScript("window.claylineDesktop && window.claylineDesktop.open()")
    }

    func saveGCode() {
        guard isReady else { return }
        webView?.evaluateJavaScript("window.claylineDesktop && window.claylineDesktop.exportGcode()")
    }

    func importDocuments(_ urls: [URL]) {
        guard let selection = ClaylineFileTypes.importSelection(from: urls) else { return }
        guard isReady, webView != nil else {
            pendingImports.append(selection)
            return
        }
        deliver(selection)
    }

    private func deliver(_ selection: ClaylineImportSelection) {
        switch selection.mode {
        case .tiles:
            importSVGs(selection.urls)
        case .weave:
            if let url = selection.urls.first {
                onMeshSelected?(url)
                importMesh(url)
            }
        }
        if selection.ignoredCount > 0 {
            presentIgnoredFilesNotice(selection)
        }
    }

    /// The file a design was imported from, by the name the page knows it by.
    func svgSourceURL(named name: String) -> URL? { svgSources.url(named: name) }

    func saveSVGOverOriginal(name: String, svg: String) -> SVGSaveOutcome {
        SVGSaver.saveOverOriginal(name: name, svg: svg, in: svgSources)
    }

    /// Hand the result back to the page, which is still showing "Saving…".
    func reportSVGSaveResult(_ json: String) {
        guard isReady else { return }
        webView?.evaluateJavaScript(
            "window.claylineDesktop && window.claylineDesktop.svgSaveResult(\(json))"
        )
    }

    private func importSVGs(_ urls: [URL]) {
        guard isReady, let webView else { return }

        let files = urls.compactMap { url -> [String: String]? in
            guard let data = try? Data(contentsOf: url),
                  data.count <= Self.maximumSVGBytes,
                  let svg = String(data: data, encoding: .utf8)
            else {
                return nil
            }
            // Recorded before the page is told about it, because the page will
            // ask to save by this same name and only the shell knows the path.
            svgSources.remember(url)
            return ["name": url.lastPathComponent, "svg": svg]
        }
        guard !files.isEmpty,
              let data = try? JSONSerialization.data(withJSONObject: files),
              let json = String(data: data, encoding: .utf8)
        else {
            return
        }
        webView.evaluateJavaScript("window.claylineDesktop.importFiles(\(json))")
    }

    func restoreMesh(_ url: URL) {
        importMesh(url, showFailure: false)
    }

    private func importMesh(_ url: URL, showFailure: Bool = true) {
        guard isReady,
              let webView,
              ClaylineFileTypes.kind(for: url) == .mesh
        else {
            return
        }

        let filename = url.lastPathComponent
        let maximumBytes = Self.maximumMeshBytes
        Task { @MainActor [weak self, weak webView] in
            let base64 = await Task.detached(priority: .userInitiated) {
                Self.readBoundedBinaryFile(url, maximumBytes: maximumBytes)?
                    .base64EncodedString()
            }.value
            guard let self,
                  let webView,
                  self.isReady,
                  self.webView === webView
            else {
                return
            }
            guard let base64 else {
                if showFailure {
                    self.presentMeshImportFailure()
                }
                return
            }

            // Passing the payload as a WebKit argument avoids interpolating a
            // local filename or megabytes of encoded data into executable
            // source. JavaScript decodes the bounded bytes into one File and
            // posts the same octet-stream body as browser drag-and-drop.
            let payload: [String: Any] = [
                "name": filename,
                "base64": base64,
            ]
            do {
                let accepted = try await webView.callAsyncJavaScript(
                    "return window.claylineDesktop && window.claylineDesktop.importMesh(payload)",
                    arguments: ["payload": payload],
                    in: nil,
                    contentWorld: .page
                ) as? Bool
                if accepted != true, showFailure {
                    self.presentMeshImportFailure()
                }
            } catch {
                if showFailure {
                    self.presentMeshImportFailure()
                }
            }
        }
    }

    nonisolated static func readBoundedBinaryFile(_ url: URL, maximumBytes: Int) -> Data? {
        guard maximumBytes >= 0,
              let handle = try? FileHandle(forReadingFrom: url)
        else {
            return nil
        }
        defer { try? handle.close() }

        var data = Data()
        let chunkSize = 1_024 * 1_024
        do {
            while data.count <= maximumBytes {
                let remainingWithSentinel = maximumBytes - data.count + 1
                let next = try handle.read(upToCount: min(chunkSize, remainingWithSentinel)) ?? Data()
                if next.isEmpty { break }
                data.append(next)
            }
        } catch {
            return nil
        }
        return data.count <= maximumBytes ? data : nil
    }

    private func presentIgnoredFilesNotice(_ selection: ClaylineImportSelection) {
        let alert = NSAlert()
        alert.alertStyle = .informational
        alert.messageText = selection.mode == .weave
            ? "Weave opens one mesh at a time"
            : "Some files were not opened"
        alert.informativeText = selection.mode == .weave
            ? "Clayline opened the first supported mesh and ignored \(selection.ignoredCount) other file(s)."
            : "Clayline opened the supported SVG batch and ignored \(selection.ignoredCount) other file(s)."
        alert.addButton(withTitle: "OK")
        if let window = webView?.window {
            alert.beginSheetModal(for: window)
        } else {
            alert.runModal()
        }
    }

    private func presentMeshImportFailure() {
        let alert = NSAlert()
        alert.alertStyle = .warning
        alert.messageText = "Mesh could not be opened"
        alert.informativeText = "Choose one readable OBJ, STL, 3MF, or PLY file no larger than 64 MiB."
        alert.addButton(withTitle: "OK")
        if let window = webView?.window {
            alert.beginSheetModal(for: window)
        } else {
            alert.runModal()
        }
    }
}
