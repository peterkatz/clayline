import Foundation
import WebKit

/// The example drawings that ship inside the app, sorted into folders by
/// style. They are read where they sit: nothing is copied out, and the
/// folder's place on disk is looked up afresh every time it is needed,
/// because macOS can run the app from a different path on every launch.
enum ClaylineGallery {
    /// Where the gallery sits under the app's `Contents` folder.
    static let relativePath = "Resources/Gallery"

    /// The page shows its gallery buttons only when the document element
    /// carries this value under `data-clayline-gallery`.
    static let availabilityDatasetKey = "claylineGallery"
    static let availabilityValue = "available"

    /// The gallery inside this copy of the app, or nil when this build has
    /// none (a plain `swift run`, or a package assembled without it).
    static func bundledURL(bundle: Bundle = .main) -> URL? {
        let url = bundle.bundleURL
            .appending(path: "Contents", directoryHint: .isDirectory)
            .appending(path: relativePath, directoryHint: .isDirectory)
        return isDirectory(url) ? url : nil
    }

    /// Which folder the drawing Open panel starts in.
    ///
    /// - Asked for the gallery: the gallery folder last opened from, else the
    ///   gallery itself.
    /// - Asked plainly: the artist's own last folder if there is one, and
    ///   otherwise exactly what a gallery request gets — so a first launch
    ///   lands among the examples and someone with their own folder keeps it.
    /// - No gallery in this build: a gallery request is a plain one.
    ///
    /// nil leaves the panel to macOS.
    static func startingFolder(
        isGalleryRequest: Bool,
        rememberedOwn: URL?,
        rememberedGallery: URL?,
        gallery: URL?
    ) -> URL? {
        guard let gallery else { return rememberedOwn }
        if !isGalleryRequest, let rememberedOwn {
            return rememberedOwn
        }
        return rememberedGallery ?? gallery
    }

    /// `folder`'s place inside `gallery`: "" for the gallery itself, "Celtic"
    /// for a folder within it, nil for anywhere else. Whole path components
    /// are compared after symlinks are resolved, so a neighbour that merely
    /// shares the spelling (".../GalleryOld") is not inside.
    static func relativeSubpath(of folder: URL, in gallery: URL) -> String? {
        let root = canonicalComponents(gallery)
        let inner = canonicalComponents(folder)
        guard inner.count >= root.count, Array(inner.prefix(root.count)) == root else {
            return nil
        }
        return inner.dropFirst(root.count).joined(separator: "/")
    }

    /// The gallery folder a remembered sub-path names, against wherever the
    /// gallery is today. nil when the folder is gone, is not a folder, or
    /// would lead out of the gallery ("..", an absolute path, a symlink).
    static func folder(atSubpath subpath: String, in gallery: URL) -> URL? {
        guard isDirectory(gallery) else { return nil }
        if subpath.isEmpty { return gallery }
        let parts = subpath.split(separator: "/", omittingEmptySubsequences: false)
        guard !subpath.hasPrefix("/"),
              !subpath.hasPrefix("~"),
              !parts.contains(where: { $0.isEmpty || $0 == "." || $0 == ".." })
        else {
            return nil
        }
        let candidate = gallery
            .appending(path: subpath, directoryHint: .isDirectory)
            .standardizedFileURL
        guard isDirectory(candidate),
              relativeSubpath(of: candidate, in: gallery) != nil
        else {
            return nil
        }
        return candidate
    }

    /// The script that tells the page a gallery is there, or nil when it is
    /// not — so the plain browser studio and any build without the example
    /// drawings never show a button that leads nowhere.
    static func availabilityScriptSource(bundle: Bundle = .main) -> String? {
        guard bundledURL(bundle: bundle) != nil else { return nil }
        return """
        (() => {
          "use strict";
          const root = document.documentElement;
          if (root) root.dataset.\(availabilityDatasetKey) = "\(availabilityValue)";
        })();
        """
    }

    static func userScript(bundle: Bundle = .main) -> WKUserScript? {
        availabilityScriptSource(bundle: bundle).map {
            WKUserScript(source: $0, injectionTime: .atDocumentStart, forMainFrameOnly: true)
        }
    }

    /// True when a folder lies inside any app package. macOS keeps one
    /// "last folder" for all of an app's Open and Save panels, so after a visit
    /// to the gallery every other panel would start inside Clayline itself,
    /// where a saved file is hidden from Finder, breaks the app's seal, and is
    /// lost at the next update. The check is by whole path component, so it
    /// also catches a gallery in another copy of the app.
    static func isInsideAnApp(_ folder: URL) -> Bool {
        folder.standardizedFileURL.pathComponents.contains {
            $0.lowercased().hasSuffix(".app")
        }
    }

    /// Where a panel with no folder of its own should start instead, when the
    /// folder macOS is about to use lies inside an app. Nil means "leave the
    /// panel alone", which keeps every other case exactly as it was.
    static func rescuedStartingFolder(
        panelDefault: URL?,
        candidates: [URL?],
        isDirectory: (URL) -> Bool = ClaylineGallery.isDirectory
    ) -> URL? {
        guard let panelDefault, isInsideAnApp(panelDefault) else { return nil }
        return candidates
            .compactMap { $0 }
            .first { !isInsideAnApp($0) && isDirectory($0) }
    }

    /// The artist's own places, best first: where they last opened a drawing
    /// from, where their project lives, then Documents and the home folder.
    @MainActor
    static func ownFolders(settingsStore: StudioSettingsStore) -> [URL?] {
        let files = FileManager.default
        return [
            settingsStore.drawingFolderURL(gallery: bundledURL()),
            settingsStore.projectDirectoryURL(),
            files.urls(for: .documentDirectory, in: .userDomainMask).first,
            files.homeDirectoryForCurrentUser,
        ]
    }

    static func isDirectory(_ url: URL) -> Bool {
        var isDirectory: ObjCBool = false
        return FileManager.default.fileExists(atPath: url.path, isDirectory: &isDirectory)
            && isDirectory.boolValue
    }

    private static func canonicalComponents(_ url: URL) -> [String] {
        url.standardizedFileURL.resolvingSymlinksInPath().pathComponents
    }
}
