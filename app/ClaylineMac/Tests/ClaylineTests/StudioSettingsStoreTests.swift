import Foundation
import Testing
@testable import Clayline

@MainActor
struct StudioSettingsStoreTests {
    @Test
    func setRemoveAndInputBounds() throws {
        let suiteName = "StudioSettingsStoreTests.\(UUID().uuidString)"
        let defaults = try #require(UserDefaults(suiteName: suiteName))
        defer { defaults.removePersistentDomain(forName: suiteName) }
        let store = StudioSettingsStore(defaults: defaults)

        #expect(store.apply(messageBody: ["operation": "set", "value": "saved"]))
        #expect(defaults.string(forKey: StudioSettingsStore.defaultsKey) == "saved")
        #expect(!store.apply(messageBody: ["operation": "set", "value": String(
            repeating: "x",
            count: StudioSettingsStore.maximumStoredBytes + 1
        )]))
        #expect(defaults.string(forKey: StudioSettingsStore.defaultsKey) == "saved")
        #expect(!store.apply(messageBody: ["operation": "unknown"]))
        #expect(store.apply(messageBody: ["operation": "remove"]))
        #expect(defaults.string(forKey: StudioSettingsStore.defaultsKey) == nil)
    }

    @Test
    func injectionIsSynchronousScopedAndSafelyEncoded() throws {
        let suiteName = "StudioSettingsStoreTests.\(UUID().uuidString)"
        let defaults = try #require(UserDefaults(suiteName: suiteName))
        defer { defaults.removePersistentDomain(forName: suiteName) }
        let stored = "{\"quote\":\"'\\n</script>\"}"
        defaults.set(stored, forKey: StudioSettingsStore.defaultsKey)
        let source = StudioSettingsStore(defaults: defaults).injectionSource()

        #expect(source.contains("claylineSettingsStorage"))
        #expect(source.contains("getItem(key)"))
        #expect(source.contains("key === targetKey"))
        #expect(source.contains("postMessage({ operation, value })"))
        #expect(source.contains("\\\\n<\\/script>"))
        #expect(!source.contains("let currentValue = {'quote'"))
    }

    @Test
    func remembersReadableMeshAndForgetsStalePath() throws {
        let suiteName = "StudioSettingsStoreTests.\(UUID().uuidString)"
        let defaults = try #require(UserDefaults(suiteName: suiteName))
        defer { defaults.removePersistentDomain(forName: suiteName) }
        let store = StudioSettingsStore(defaults: defaults)
        let directory = FileManager.default.temporaryDirectory
            .appendingPathComponent("ClaylineMeshRestore.\(UUID().uuidString)")
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: directory) }
        let mesh = directory.appendingPathComponent("remembered.obj")
        try Data("v 0 0 0\n".utf8).write(to: mesh)

        store.rememberMeshURL(mesh)

        #expect(defaults.string(forKey: StudioSettingsStore.meshPathDefaultsKey) == mesh.path)
        #expect(store.restorableMeshURL() == mesh.standardizedFileURL)

        try FileManager.default.removeItem(at: mesh)
        #expect(store.restorableMeshURL() == nil)
        #expect(defaults.string(forKey: StudioSettingsStore.meshPathDefaultsKey) == nil)
    }

    @Test
    func rejectsRememberedNonMeshPath() throws {
        let suiteName = "StudioSettingsStoreTests.\(UUID().uuidString)"
        let defaults = try #require(UserDefaults(suiteName: suiteName))
        defer { defaults.removePersistentDomain(forName: suiteName) }
        let store = StudioSettingsStore(defaults: defaults)
        let file = FileManager.default.temporaryDirectory
            .appendingPathComponent("not-a-mesh-\(UUID().uuidString).txt")
        try Data("not a mesh".utf8).write(to: file)
        defer { try? FileManager.default.removeItem(at: file) }

        store.rememberMeshURL(file)

        #expect(store.restorableMeshURL() == nil)
        #expect(defaults.string(forKey: StudioSettingsStore.meshPathDefaultsKey) == nil)
    }

    @Test
    func remembersTheProjectFolderAndForgetsOneThatIsGone() throws {
        let suiteName = "StudioSettingsStoreTests.\(UUID().uuidString)"
        let defaults = try #require(UserDefaults(suiteName: suiteName))
        defer { defaults.removePersistentDomain(forName: suiteName) }
        let store = StudioSettingsStore(defaults: defaults)

        #expect(store.projectDirectoryURL() == nil)

        let directory = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString, isDirectory: true)
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        let project = directory.appendingPathComponent("lantern.clayline")
        try Data("a saved project".utf8).write(to: project)

        store.rememberProjectURL(project)

        #expect(defaults.string(forKey: StudioSettingsStore.projectPathDefaultsKey) == project.path)
        #expect(store.projectDirectoryURL() == directory.standardizedFileURL)

        // The file may be renamed or moved; only the folder has to survive.
        try FileManager.default.removeItem(at: project)
        #expect(store.projectDirectoryURL() == directory.standardizedFileURL)

        try FileManager.default.removeItem(at: directory)
        #expect(store.projectDirectoryURL() == nil)
    }

    // MARK: Where the drawing Open panel starts

    /// A scratch tree with a stand-in gallery and a folder of the artist's own.
    private struct DrawingFolders {
        let root: URL
        let gallery: URL
        let celtic: URL
        let own: URL

        init() throws {
            root = FileManager.default.temporaryDirectory
                .appendingPathComponent("ClaylineDrawingFolders.\(UUID().uuidString)", isDirectory: true)
            gallery = root.appendingPathComponent(
                "Clayline.app/Contents/Resources/Gallery", isDirectory: true
            )
            celtic = gallery.appendingPathComponent("Celtic", isDirectory: true)
            own = root.appendingPathComponent("My Drawings", isDirectory: true)
            try FileManager.default.createDirectory(at: celtic, withIntermediateDirectories: true)
            try FileManager.default.createDirectory(at: own, withIntermediateDirectories: true)
        }

        func remove() { try? FileManager.default.removeItem(at: root) }
    }

    @Test
    func remembersTheArtistsOwnDrawingFolderAndForgetsOneThatIsGone() throws {
        let suiteName = "StudioSettingsStoreTests.\(UUID().uuidString)"
        let defaults = try #require(UserDefaults(suiteName: suiteName))
        defer { defaults.removePersistentDomain(forName: suiteName) }
        let store = StudioSettingsStore(defaults: defaults)
        let folders = try DrawingFolders()
        defer { folders.remove() }

        #expect(store.drawingFolderURL(gallery: folders.gallery) == nil)
        #expect(store.galleryFolderURL(gallery: folders.gallery) == nil)

        store.rememberDrawingFolder(
            for: folders.own.appendingPathComponent("leaf.svg"), gallery: folders.gallery
        )

        #expect(
            defaults.string(forKey: StudioSettingsStore.drawingFolderDefaultsKey)
                == folders.own.standardizedFileURL.path
        )
        #expect(defaults.string(forKey: StudioSettingsStore.galleryFolderDefaultsKey) == nil)
        #expect(
            store.drawingFolderURL(gallery: folders.gallery)?.path
                == folders.own.standardizedFileURL.path
        )
        // The folder is the artist's own whether or not this build has a gallery.
        #expect(store.drawingFolderURL(gallery: nil)?.path == folders.own.standardizedFileURL.path)

        // A folder that is only absent right now (a drive not plugged in) is
        // not offered, but it is kept, and offered again when it comes back.
        try FileManager.default.removeItem(at: folders.own)
        #expect(store.drawingFolderURL(gallery: folders.gallery) == nil)
        #expect(
            defaults.string(forKey: StudioSettingsStore.drawingFolderDefaultsKey)
                == folders.own.standardizedFileURL.path
        )
        try FileManager.default.createDirectory(at: folders.own, withIntermediateDirectories: true)
        #expect(
            store.drawingFolderURL(gallery: folders.gallery)?.path
                == folders.own.standardizedFileURL.path
        )
    }

    @Test
    func aFileWhereTheDrawingFolderWasIsNotOffered() throws {
        let suiteName = "StudioSettingsStoreTests.\(UUID().uuidString)"
        let defaults = try #require(UserDefaults(suiteName: suiteName))
        defer { defaults.removePersistentDomain(forName: suiteName) }
        let store = StudioSettingsStore(defaults: defaults)
        let folders = try DrawingFolders()
        defer { folders.remove() }

        store.rememberDrawingFolder(
            for: folders.own.appendingPathComponent("leaf.svg"), gallery: nil
        )
        try FileManager.default.removeItem(at: folders.own)
        try Data("now a file".utf8).write(to: folders.own)

        #expect(store.drawingFolderURL(gallery: nil) == nil)
    }

    @Test
    func aGalleryFolderIsKeptByItsPlaceAndFoundAgainAfterTheAppMoves() throws {
        let suiteName = "StudioSettingsStoreTests.\(UUID().uuidString)"
        let defaults = try #require(UserDefaults(suiteName: suiteName))
        defer { defaults.removePersistentDomain(forName: suiteName) }
        let store = StudioSettingsStore(defaults: defaults)
        let folders = try DrawingFolders()
        defer { folders.remove() }

        store.rememberDrawingFolder(
            for: folders.celtic.appendingPathComponent("celtic-cross.svg"),
            gallery: folders.gallery
        )

        // Only the place inside the gallery is kept — no path into the app.
        #expect(defaults.string(forKey: StudioSettingsStore.galleryFolderDefaultsKey) == "Celtic")
        #expect(defaults.string(forKey: StudioSettingsStore.drawingFolderDefaultsKey) == nil)
        for (_, value) in defaults.persistentDomain(forName: suiteName) ?? [:] {
            #expect(!((value as? String) ?? "").contains("Clayline.app"))
        }
        #expect(
            store.galleryFolderURL(gallery: folders.gallery)?.standardizedFileURL.path
                == folders.celtic.standardizedFileURL.path
        )

        // The same app, run from somewhere else at the next launch.
        let moved = folders.root.appendingPathComponent(
            "Translocated/d/Clayline.app/Contents/Resources/Gallery", isDirectory: true
        )
        let movedCeltic = moved.appendingPathComponent("Celtic", isDirectory: true)
        try FileManager.default.createDirectory(at: movedCeltic, withIntermediateDirectories: true)
        try FileManager.default.removeItem(
            at: folders.root.appendingPathComponent("Clayline.app", isDirectory: true)
        )

        #expect(
            store.galleryFolderURL(gallery: moved)?.standardizedFileURL.path
                == movedCeltic.standardizedFileURL.path
        )
        #expect(defaults.string(forKey: StudioSettingsStore.galleryFolderDefaultsKey) == "Celtic")
    }

    @Test
    func theGalleryItselfIsKeptAsAnEmptyPlace() throws {
        let suiteName = "StudioSettingsStoreTests.\(UUID().uuidString)"
        let defaults = try #require(UserDefaults(suiteName: suiteName))
        defer { defaults.removePersistentDomain(forName: suiteName) }
        let store = StudioSettingsStore(defaults: defaults)
        let folders = try DrawingFolders()
        defer { folders.remove() }

        store.rememberDrawingFolder(
            for: folders.gallery.appendingPathComponent("loose.svg"), gallery: folders.gallery
        )

        #expect(defaults.string(forKey: StudioSettingsStore.galleryFolderDefaultsKey) == "")
        #expect(
            store.galleryFolderURL(gallery: folders.gallery)?.standardizedFileURL.path
                == folders.gallery.standardizedFileURL.path
        )
    }

    @Test
    func aGalleryFolderThatIsGoneIsForgottenButAMissingGalleryForgetsNothing() throws {
        let suiteName = "StudioSettingsStoreTests.\(UUID().uuidString)"
        let defaults = try #require(UserDefaults(suiteName: suiteName))
        defer { defaults.removePersistentDomain(forName: suiteName) }
        let store = StudioSettingsStore(defaults: defaults)
        let folders = try DrawingFolders()
        defer { folders.remove() }

        store.rememberDrawingFolder(
            for: folders.celtic.appendingPathComponent("celtic-cross.svg"),
            gallery: folders.gallery
        )

        // A build without the example drawings has nothing to check against.
        #expect(store.galleryFolderURL(gallery: nil) == nil)
        #expect(defaults.string(forKey: StudioSettingsStore.galleryFolderDefaultsKey) == "Celtic")

        try FileManager.default.removeItem(at: folders.celtic)
        #expect(store.galleryFolderURL(gallery: folders.gallery) == nil)
        #expect(defaults.string(forKey: StudioSettingsStore.galleryFolderDefaultsKey) == nil)
    }

    @Test
    func aNeighbourOfTheGalleryIsTheArtistsOwnFolder() throws {
        let suiteName = "StudioSettingsStoreTests.\(UUID().uuidString)"
        let defaults = try #require(UserDefaults(suiteName: suiteName))
        defer { defaults.removePersistentDomain(forName: suiteName) }
        let store = StudioSettingsStore(defaults: defaults)
        let folders = try DrawingFolders()
        defer { folders.remove() }
        let neighbour = folders.gallery.deletingLastPathComponent()
            .appendingPathComponent("GalleryOld/Celtic", isDirectory: true)
        try FileManager.default.createDirectory(at: neighbour, withIntermediateDirectories: true)

        store.rememberDrawingFolder(
            for: neighbour.appendingPathComponent("celtic-cross.svg"), gallery: folders.gallery
        )

        #expect(defaults.string(forKey: StudioSettingsStore.galleryFolderDefaultsKey) == nil)
        #expect(
            store.drawingFolderURL(gallery: folders.gallery)?.path
                == neighbour.standardizedFileURL.path
        )
    }

    @Test
    func aPlaceThatLeadsOutOfTheGalleryIsIgnoredAndForgotten() throws {
        let folders = try DrawingFolders()
        defer { folders.remove() }
        try FileManager.default.createSymbolicLink(
            at: folders.gallery.appendingPathComponent("Escape"),
            withDestinationURL: folders.own
        )

        for escape in ["../", "..", "../../..", "Celtic/../..", folders.own.path, "Escape"] {
            let suiteName = "StudioSettingsStoreTests.\(UUID().uuidString)"
            let defaults = try #require(UserDefaults(suiteName: suiteName))
            defer { defaults.removePersistentDomain(forName: suiteName) }
            let store = StudioSettingsStore(defaults: defaults)
            defaults.set(escape, forKey: StudioSettingsStore.galleryFolderDefaultsKey)

            #expect(store.galleryFolderURL(gallery: folders.gallery) == nil, "\(escape)")
            #expect(
                defaults.string(forKey: StudioSettingsStore.galleryFolderDefaultsKey) == nil,
                "\(escape)"
            )
        }
    }

    @Test
    func visitingTheGalleryNeverLosesTheArtistsOwnFolder() throws {
        let suiteName = "StudioSettingsStoreTests.\(UUID().uuidString)"
        let defaults = try #require(UserDefaults(suiteName: suiteName))
        defer { defaults.removePersistentDomain(forName: suiteName) }
        let store = StudioSettingsStore(defaults: defaults)
        let folders = try DrawingFolders()
        defer { folders.remove() }

        store.rememberDrawingFolder(
            for: folders.own.appendingPathComponent("leaf.svg"), gallery: folders.gallery
        )
        store.rememberDrawingFolder(
            for: folders.celtic.appendingPathComponent("celtic-cross.svg"),
            gallery: folders.gallery
        )

        #expect(
            store.drawingFolderURL(gallery: folders.gallery)?.path
                == folders.own.standardizedFileURL.path
        )
        #expect(
            store.galleryFolderURL(gallery: folders.gallery)?.standardizedFileURL.path
                == folders.celtic.standardizedFileURL.path
        )

        // And the other way round: their own folder leaves the gallery place alone.
        store.rememberDrawingFolder(
            for: folders.own.appendingPathComponent("second.svg"), gallery: folders.gallery
        )
        #expect(defaults.string(forKey: StudioSettingsStore.galleryFolderDefaultsKey) == "Celtic")

        // Put together, a plain request keeps their folder and a gallery
        // request goes back to the examples.
        let own = store.drawingFolderURL(gallery: folders.gallery)
        let inGallery = store.galleryFolderURL(gallery: folders.gallery)
        #expect(
            ClaylineGallery.startingFolder(
                isGalleryRequest: false, rememberedOwn: own,
                rememberedGallery: inGallery, gallery: folders.gallery
            )?.path == folders.own.standardizedFileURL.path
        )
        #expect(
            ClaylineGallery.startingFolder(
                isGalleryRequest: true, rememberedOwn: own,
                rememberedGallery: inGallery, gallery: folders.gallery
            )?.standardizedFileURL.path == folders.celtic.standardizedFileURL.path
        )
    }

    @Test
    func aFullPathIntoTheGalleryIsNeverTrustedAsTheArtistsOwnFolder() throws {
        let suiteName = "StudioSettingsStoreTests.\(UUID().uuidString)"
        let defaults = try #require(UserDefaults(suiteName: suiteName))
        defer { defaults.removePersistentDomain(forName: suiteName) }
        let store = StudioSettingsStore(defaults: defaults)
        let folders = try DrawingFolders()
        defer { folders.remove() }
        defaults.set(folders.celtic.path, forKey: StudioSettingsStore.drawingFolderDefaultsKey)

        #expect(store.drawingFolderURL(gallery: folders.gallery) == nil)
        #expect(defaults.string(forKey: StudioSettingsStore.drawingFolderDefaultsKey) == nil)
    }
}
