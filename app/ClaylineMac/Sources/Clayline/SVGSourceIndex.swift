import Foundation

/// Remembers which file each imported design was read from, so a design edited
/// on the drawing surface can be written back over the file the artist opened
/// rather than landing in Downloads as a copy.
///
/// The page works in names, not paths: it was handed `rosette-study.svg` at
/// import and that is all it ever knows. The shell is the side that opened the
/// file, so the shell is the side that remembers where it lives.
struct SVGSourceIndex {
    private var byName: [String: URL] = [:]

    /// The name the page knows a file by: exactly what `importSVGs` sends.
    static func key(for url: URL) -> String { url.lastPathComponent }

    mutating func remember(_ url: URL) {
        byName[Self.key(for: url)] = url
    }

    mutating func remember(_ urls: [URL]) {
        urls.forEach { remember($0) }
    }

    /// Where a design should be saved back to, or nil when the studio has never
    /// been told about a file by that name — a drawing made in the app, or one
    /// dropped onto the page by the browser, has no original to overwrite.
    ///
    /// Two files with the same basename from different folders collapse onto
    /// the last one imported, which is the same name the page is showing.
    func url(named name: String) -> URL? {
        guard let url = byName[name] else { return nil }
        // A remembered file that has since been moved or deleted is not a
        // target: writing would recreate it somewhere the artist is no longer
        // looking, which is worse than asking them where it should go.
        return FileManager.default.fileExists(atPath: url.path) ? url : nil
    }

    var count: Int { byName.count }
}

/// What happened when the page asked to save a design over its original.
enum SVGSaveOutcome: Equatable {
    case wrote(URL)
    /// No original to write over — the caller should offer a save panel instead.
    case noKnownSource
    case tooLarge
    case failed(String)

    var savedPath: String? {
        if case let .wrote(url) = self { return url.path }
        return nil
    }
}

enum SVGSaver {
    /// Write `svg` over the file `name` was imported from.
    ///
    /// Atomic, because a half-written file is a lost drawing: the artist's only
    /// copy of that design may be the one being replaced.
    static func saveOverOriginal(
        name: String,
        svg: String,
        in index: SVGSourceIndex,
        limit: Int = WebActions.maximumSVGBytes
    ) -> SVGSaveOutcome {
        let data = Data(svg.utf8)
        guard data.count <= limit else { return .tooLarge }
        guard let url = index.url(named: name) else { return .noKnownSource }
        do {
            try data.write(to: url, options: .atomic)
            return .wrote(url)
        } catch {
            return .failed(error.localizedDescription)
        }
    }
}
