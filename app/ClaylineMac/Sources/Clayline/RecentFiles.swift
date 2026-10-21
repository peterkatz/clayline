import AppKit
import Combine
import Foundation

/// One line of File → Open Recent: the file, and the name the menu shows it by.
struct RecentFileEntry: Identifiable, Equatable {
    let url: URL
    let title: String

    var id: String { url.path }
}

/// macOS's own list of recent documents, which the Dock icon's menu shows.
/// Clayline's menu is kept in its own store; this is a best-effort copy so the
/// Dock lists the same files other apps' Docks would. Replaceable so a test
/// never writes into the list of the process running it.
struct SystemRecentDocuments {
    let note: @MainActor (URL) -> Void
    let clear: @MainActor () -> Void

    static let shared = SystemRecentDocuments(
        note: { NSDocumentController.shared.noteNewRecentDocumentURL($0) },
        clear: { NSDocumentController.shared.clearRecentDocuments(nil) }
    )

    static let none = SystemRecentDocuments(note: { _ in }, clear: {})
}

/// File → Open Recent: the ten files most recently opened or saved, newest
/// first. Projects, models, drawings and print files go in; an exported print
/// file or mesh, a pattern, a reference photo and anything inside an app (the
/// gallery's example drawings, whose path breaks when the app moves) do not.
/// Nothing on this list is ever reopened by itself at launch: a relaunch stays
/// a clean slate (Pete 2026-07-26).
@MainActor
final class RecentFilesStore: ObservableObject {
    static let defaultsKey = "clayline.recent-files.v1"
    static let maximumCount = 10

    /// Newest first, each a standardized absolute path, never two the same.
    @Published private(set) var urls: [URL]

    private let defaults: UserDefaults
    private let system: SystemRecentDocuments

    init(defaults: UserDefaults = .standard, system: SystemRecentDocuments = .shared) {
        self.defaults = defaults
        self.system = system
        urls = Self.load(from: defaults)
    }

    /// What the menu shows, in its order.
    var entries: [RecentFileEntry] { Self.entries(for: urls) }

    /// A project, model, drawing or print file outside any app.
    static func isRecordable(_ url: URL) -> Bool {
        guard url.isFileURL, url.path.hasPrefix("/"),
              ClaylineFileTypes.kind(for: url) != nil
        else {
            return false
        }
        return !ClaylineGallery.isInsideAnApp(url.standardizedFileURL.deletingLastPathComponent())
    }

    /// Put a file at the top of the list, or move it there. Returns whether it
    /// went on.
    @discardableResult
    func note(_ url: URL) -> Bool {
        guard Self.isRecordable(url) else { return false }
        let file = url.standardizedFileURL
        var next = urls.filter { $0.path != file.path }
        next.insert(file, at: 0)
        store(Array(next.prefix(Self.maximumCount)))
        system.note(file)
        return true
    }

    func remove(_ url: URL) {
        let path = url.standardizedFileURL.path
        guard urls.contains(where: { $0.path == path }) else { return }
        store(urls.filter { $0.path != path })
    }

    /// Clear Menu: Clayline's list and the Dock's.
    func clear() {
        store([])
        system.clear()
    }

    /// The file a chosen entry opens, or nil when it is no longer there — and
    /// then it leaves the list, so the menu stops offering it.
    func fileToReopen(
        _ url: URL,
        fileExists: (String) -> Bool = { FileManager.default.fileExists(atPath: $0) }
    ) -> URL? {
        let file = url.standardizedFileURL
        guard fileExists(file.path) else {
            remove(file)
            return nil
        }
        return file
    }

    /// Each file by its name. Two files that share a name are told apart by
    /// the folder each sits in, and by as many folders above it as it takes
    /// for the two to read differently ("2025/Jobs", "2026/Jobs").
    static func entries(for urls: [URL]) -> [RecentFileEntry] {
        var sharing: [String: [Int]] = [:]
        for (index, url) in urls.enumerated() {
            sharing[url.lastPathComponent.lowercased(), default: []].append(index)
        }
        let folders = urls.map { $0.deletingLastPathComponent() }
        return urls.enumerated().map { index, url in
            let name = url.lastPathComponent
            let others = sharing[name.lowercased(), default: []].filter { $0 != index }
            guard !others.isEmpty else {
                return RecentFileEntry(url: url, title: name)
            }
            let folder = distinguishingFolder(folders[index], from: others.map { folders[$0] })
            return RecentFileEntry(url: url, title: "\(name) — \(folder)")
        }
    }

    /// The fewest trailing folders of `folder` that no other folder ends with
    /// the same way (whatever the case); the whole path once the folders run
    /// out.
    private static func distinguishingFolder(_ folder: URL, from others: [URL]) -> String {
        func label(_ folder: URL, depth: Int) -> String {
            let parts = folder.pathComponents.filter { $0 != "/" }
            guard depth < parts.count else { return folder.path }
            return parts.suffix(depth).joined(separator: "/")
        }
        let depthToWholePath = max(folder.pathComponents.filter { $0 != "/" }.count, 1)
        for depth in 1 ... depthToWholePath {
            let own = label(folder, depth: depth)
            let clashes = others.contains {
                label($0, depth: depth).lowercased() == own.lowercased()
            }
            if !clashes { return own }
        }
        return folder.path
    }

    private func store(_ next: [URL]) {
        urls = next
        defaults.set(next.map(\.path), forKey: Self.defaultsKey)
    }

    private static func load(from defaults: UserDefaults) -> [URL] {
        var seen = Set<String>()
        var loaded: [URL] = []
        for path in defaults.stringArray(forKey: defaultsKey) ?? [] {
            let url = URL(fileURLWithPath: path).standardizedFileURL
            guard path.hasPrefix("/"), isRecordable(url), seen.insert(url.path).inserted else {
                continue
            }
            loaded.append(url)
            if loaded.count == maximumCount { break }
        }
        return loaded
    }
}
