import Foundation
import XCTest
@testable import Clayline

final class GalleryTests: XCTestCase {
    private var scratch: URL!

    override func setUpWithError() throws {
        scratch = FileManager.default.temporaryDirectory
            .appendingPathComponent("ClaylineGalleryTests.\(UUID().uuidString)", isDirectory: true)
        try FileManager.default.createDirectory(at: scratch, withIntermediateDirectories: true)
    }

    override func tearDownWithError() throws {
        try? FileManager.default.removeItem(at: scratch)
    }

    /// A stand-in for the packaged app: `<name>.app/Contents/Resources`.
    private func makeApp(_ name: String = "Clayline") throws -> URL {
        let app = scratch.appendingPathComponent("\(name).app", isDirectory: true)
        try FileManager.default.createDirectory(
            at: app.appendingPathComponent("Contents/Resources", isDirectory: true),
            withIntermediateDirectories: true
        )
        return app
    }

    private func galleryPath(in app: URL) -> URL {
        app.appendingPathComponent("Contents/Resources/Gallery", isDirectory: true)
    }

    // MARK: The request the page sends

    func testOpenRequestParsesTheGalleryMarker() {
        let request = ClaylineOpenRequest(raw: "tiles:gallery")
        XCTAssertTrue(request.isGallery)
        XCTAssertEqual(request.mode, .tiles)
        XCTAssertFalse(request.isProject)
        XCTAssertFalse(request.isReferencePhoto)
        XCTAssertTrue(request.isDrawingPicker)

        XCTAssertFalse(ClaylineOpenRequest(raw: "tiles:").isGallery)
        XCTAssertFalse(ClaylineOpenRequest(raw: nil).isGallery)
        XCTAssertFalse(ClaylineOpenRequest(raw: "tiles:project").isGallery)
        XCTAssertFalse(ClaylineOpenRequest(raw: "tiles:reference-photo").isGallery)
        XCTAssertFalse(ClaylineOpenRequest(raw: "tiles:Gallery").isGallery)
        XCTAssertFalse(ClaylineOpenRequest(raw: "tiles:gallery ").isGallery)
    }

    func testAnUnknownRequestIsStillThePlainDrawingPicker() {
        let unknown = ClaylineOpenRequest(raw: "tiles:something-new")
        XCTAssertEqual(unknown.mode, .tiles)
        XCTAssertFalse(unknown.isGallery)
        XCTAssertFalse(unknown.isProject)
        XCTAssertFalse(unknown.isReferencePhoto)
        XCTAssertTrue(unknown.isDrawingPicker)
        XCTAssertEqual(unknown, ClaylineOpenRequest(raw: "tiles:"))
    }

    func testOnlyThePlainDrawingPickerFollowsARememberedFolder() {
        XCTAssertTrue(ClaylineOpenRequest(raw: "tiles:").isDrawingPicker)
        XCTAssertTrue(ClaylineOpenRequest(raw: nil).isDrawingPicker)
        XCTAssertFalse(ClaylineOpenRequest(raw: "tiles:project").isDrawingPicker)
        XCTAssertFalse(ClaylineOpenRequest(raw: "tiles:reference-photo").isDrawingPicker)
        XCTAssertFalse(ClaylineOpenRequest(raw: "weave:").isDrawingPicker)
        XCTAssertFalse(ClaylineOpenRequest(raw: "weave:project").isDrawingPicker)
        // Weave has no gallery: a stray marker there leaves Weave's picker alone.
        XCTAssertFalse(ClaylineOpenRequest(raw: "weave:gallery").isDrawingPicker)
    }

    // MARK: Where the gallery is

    func testBundledGalleryIsFoundInsideTheApp() throws {
        let app = try makeApp()
        try FileManager.default.createDirectory(
            at: galleryPath(in: app).appendingPathComponent("Celtic", isDirectory: true),
            withIntermediateDirectories: true
        )
        let bundle = try XCTUnwrap(Bundle(url: app))

        let found = try XCTUnwrap(ClaylineGallery.bundledURL(bundle: bundle))
        XCTAssertEqual(found.standardizedFileURL.path, galleryPath(in: app).standardizedFileURL.path)
    }

    func testAnAppWithoutAGalleryHasNone() throws {
        let bundle = try XCTUnwrap(Bundle(url: try makeApp()))
        XCTAssertNil(ClaylineGallery.bundledURL(bundle: bundle))
    }

    func testAFileNamedGalleryIsNotAGallery() throws {
        let app = try makeApp()
        try Data("not a folder".utf8).write(to: galleryPath(in: app))
        let bundle = try XCTUnwrap(Bundle(url: app))
        XCTAssertNil(ClaylineGallery.bundledURL(bundle: bundle))
    }

    func testTheGalleryIsLookedUpAfreshEachTime() throws {
        let app = try makeApp()
        let bundle = try XCTUnwrap(Bundle(url: app))
        XCTAssertNil(ClaylineGallery.bundledURL(bundle: bundle))

        try FileManager.default.createDirectory(
            at: galleryPath(in: app), withIntermediateDirectories: true
        )
        XCTAssertNotNil(ClaylineGallery.bundledURL(bundle: bundle))

        try FileManager.default.removeItem(at: galleryPath(in: app))
        XCTAssertNil(ClaylineGallery.bundledURL(bundle: bundle))
    }

    // MARK: Where the Open panel starts

    func testStartingFolderForEveryCombination() {
        let own = URL(fileURLWithPath: "/Users/potter/Drawings", isDirectory: true)
        let gallery = URL(
            fileURLWithPath: "/Applications/Clayline.app/Contents/Resources/Gallery",
            isDirectory: true
        )
        let celtic = gallery.appendingPathComponent("Celtic", isDirectory: true)

        // (asked for the gallery, own folder, gallery folder, gallery, expected)
        let table: [(Bool, URL?, URL?, URL?, URL?)] = [
            // A plain request.
            (false, nil, nil, nil, nil),
            (false, nil, nil, gallery, gallery),
            (false, nil, celtic, nil, nil),
            (false, nil, celtic, gallery, celtic),
            (false, own, nil, nil, own),
            (false, own, nil, gallery, own),
            (false, own, celtic, nil, own),
            (false, own, celtic, gallery, own),
            // Asked for the gallery.
            (true, nil, nil, nil, nil),
            (true, nil, nil, gallery, gallery),
            (true, nil, celtic, nil, nil),
            (true, nil, celtic, gallery, celtic),
            // With no gallery in this build it is the same as a plain request;
            // with one, the artist's own folder is passed over this once.
            (true, own, nil, nil, own),
            (true, own, nil, gallery, gallery),
            (true, own, celtic, nil, own),
            (true, own, celtic, gallery, celtic),
        ]
        XCTAssertEqual(table.count, 16)
        for (index, row) in table.enumerated() {
            XCTAssertEqual(
                ClaylineGallery.startingFolder(
                    isGalleryRequest: row.0,
                    rememberedOwn: row.1,
                    rememberedGallery: row.2,
                    gallery: row.3
                ),
                row.4,
                "row \(index)"
            )
        }
    }

    // MARK: Inside or outside the gallery

    func testRelativeSubpathNamesAFoldersPlaceInTheGallery() throws {
        let gallery = galleryPath(in: try makeApp())
        let nested = gallery.appendingPathComponent("Celtic/Knots", isDirectory: true)
        try FileManager.default.createDirectory(at: nested, withIntermediateDirectories: true)

        XCTAssertEqual(ClaylineGallery.relativeSubpath(of: gallery, in: gallery), "")
        XCTAssertEqual(
            ClaylineGallery.relativeSubpath(
                of: gallery.appendingPathComponent("Celtic", isDirectory: true), in: gallery
            ),
            "Celtic"
        )
        XCTAssertEqual(ClaylineGallery.relativeSubpath(of: nested, in: gallery), "Celtic/Knots")
        // Spelled with a trailing slash or a detour, it is the same folder.
        XCTAssertEqual(
            ClaylineGallery.relativeSubpath(
                of: URL(fileURLWithPath: gallery.path + "/Celtic/../Celtic/"), in: gallery
            ),
            "Celtic"
        )
        XCTAssertNil(ClaylineGallery.relativeSubpath(of: scratch, in: gallery))
        XCTAssertNil(
            ClaylineGallery.relativeSubpath(of: gallery.deletingLastPathComponent(), in: gallery)
        )
    }

    func testANeighbourSharingTheSpellingIsNotInsideTheGallery() throws {
        let app = try makeApp()
        let gallery = galleryPath(in: app)
        let neighbour = app.appendingPathComponent("Contents/Resources/GalleryOld", isDirectory: true)
        try FileManager.default.createDirectory(at: gallery, withIntermediateDirectories: true)
        try FileManager.default.createDirectory(at: neighbour, withIntermediateDirectories: true)

        XCTAssertNil(ClaylineGallery.relativeSubpath(of: neighbour, in: gallery))
        XCTAssertNil(
            ClaylineGallery.relativeSubpath(
                of: neighbour.appendingPathComponent("Celtic", isDirectory: true), in: gallery
            )
        )
    }

    func testAFolderReachedThroughASymlinkIsJudgedByWhereItReallyIs() throws {
        let gallery = galleryPath(in: try makeApp())
        let celtic = gallery.appendingPathComponent("Celtic", isDirectory: true)
        try FileManager.default.createDirectory(at: celtic, withIntermediateDirectories: true)
        let shortcut = scratch.appendingPathComponent("shortcut")
        try FileManager.default.createSymbolicLink(at: shortcut, withDestinationURL: celtic)

        XCTAssertEqual(ClaylineGallery.relativeSubpath(of: shortcut, in: gallery), "Celtic")
    }

    func testASubpathCannotLeadOutOfTheGallery() throws {
        let app = try makeApp()
        let gallery = galleryPath(in: app)
        let celtic = gallery.appendingPathComponent("Celtic", isDirectory: true)
        try FileManager.default.createDirectory(at: celtic, withIntermediateDirectories: true)
        let outside = scratch.appendingPathComponent("Outside", isDirectory: true)
        try FileManager.default.createDirectory(at: outside, withIntermediateDirectories: true)
        try FileManager.default.createSymbolicLink(
            at: gallery.appendingPathComponent("Escape"), withDestinationURL: outside
        )

        XCTAssertEqual(
            ClaylineGallery.folder(atSubpath: "", in: gallery)?.standardizedFileURL.path,
            gallery.standardizedFileURL.path
        )
        XCTAssertEqual(
            ClaylineGallery.folder(atSubpath: "Celtic", in: gallery)?.standardizedFileURL.path,
            celtic.standardizedFileURL.path
        )
        for escape in [
            "..", "../..", "Celtic/..", "Celtic/../..", "../Gallery/Celtic", "./Celtic",
            "/", outside.path, "/Celtic", "~", "~/Documents", "Celtic//", "Escape", "Missing",
        ] {
            XCTAssertNil(ClaylineGallery.folder(atSubpath: escape, in: gallery), escape)
        }
        // A file is not a folder to start in.
        try Data("<svg/>".utf8).write(to: celtic.appendingPathComponent("knot.svg"))
        XCTAssertNil(ClaylineGallery.folder(atSubpath: "Celtic/knot.svg", in: gallery))
        // And without a gallery there is nothing to resolve against.
        XCTAssertNil(
            ClaylineGallery.folder(
                atSubpath: "", in: scratch.appendingPathComponent("no-gallery", isDirectory: true)
            )
        )
    }

    // MARK: What the page is told

    func testThePageIsToldAboutTheGalleryOnlyWhenItIsThere() throws {
        let withGallery = try makeApp("WithGallery")
        try FileManager.default.createDirectory(
            at: galleryPath(in: withGallery), withIntermediateDirectories: true
        )
        let without = try makeApp("Without")
        let asAFile = try makeApp("AsAFile")
        try Data("not a folder".utf8).write(to: galleryPath(in: asAFile))

        let source = try XCTUnwrap(
            ClaylineGallery.availabilityScriptSource(bundle: try XCTUnwrap(Bundle(url: withGallery)))
        )
        XCTAssertTrue(source.contains("document.documentElement"))
        XCTAssertTrue(source.contains("dataset.claylineGallery = \"available\""))
        // The page is never handed a path into the app.
        XCTAssertFalse(source.contains(scratch.lastPathComponent))
        XCTAssertFalse(source.contains("Contents"))

        XCTAssertNil(
            ClaylineGallery.availabilityScriptSource(bundle: try XCTUnwrap(Bundle(url: without)))
        )
        XCTAssertNil(
            ClaylineGallery.availabilityScriptSource(bundle: try XCTUnwrap(Bundle(url: asAFile)))
        )
    }

    @MainActor
    func testTheGalleryScriptRunsAtDocumentStartInTheMainFrameOnly() throws {
        let app = try makeApp()
        try FileManager.default.createDirectory(
            at: galleryPath(in: app), withIntermediateDirectories: true
        )
        let script = try XCTUnwrap(
            ClaylineGallery.userScript(bundle: try XCTUnwrap(Bundle(url: app)))
        )
        XCTAssertEqual(script.injectionTime, .atDocumentStart)
        XCTAssertTrue(script.isForMainFrameOnly)

        XCTAssertNil(
            ClaylineGallery.userScript(bundle: try XCTUnwrap(Bundle(url: try makeApp("Bare"))))
        )
    }

    @MainActor
    func testTheSettingsScriptNeverClaimsAGallery() throws {
        let suiteName = "GalleryTests.\(UUID().uuidString)"
        let defaults = try XCTUnwrap(UserDefaults(suiteName: suiteName))
        defer { defaults.removePersistentDomain(forName: suiteName) }
        let source = StudioSettingsStore(defaults: defaults).injectionSource()
        XCTAssertFalse(source.contains("claylineGallery"))
    }

    // MARK: - No other panel may start inside the app

    func testAFolderInsideAnyAppIsRecognisedByWholePathComponent() {
        XCTAssertTrue(ClaylineGallery.isInsideAnApp(
            URL(fileURLWithPath: "/Applications/Clayline.app/Contents/Resources/Gallery/Celtic")))
        XCTAssertTrue(ClaylineGallery.isInsideAnApp(
            URL(fileURLWithPath: "/private/var/folders/x/AppTranslocation/1/d/Clayline.APP/Contents")))
        XCTAssertFalse(ClaylineGallery.isInsideAnApp(URL(fileURLWithPath: "/Users/potter/Drawings")))
        // A folder that merely mentions an app in its name is the potter's own.
        XCTAssertFalse(ClaylineGallery.isInsideAnApp(
            URL(fileURLWithPath: "/Users/potter/Clayline.app notes/tiles")))
    }

    func testAPanelAboutToStartInsideAnAppIsSentToThePottersOwnFolder() {
        let inside = URL(fileURLWithPath: "/Applications/Clayline.app/Contents/Resources/Gallery")
        let own = URL(fileURLWithPath: "/Users/potter/Drawings")
        let documents = URL(fileURLWithPath: "/Users/potter/Documents")
        let exists: (URL) -> Bool = { $0 == own || $0 == documents }

        XCTAssertEqual(
            ClaylineGallery.rescuedStartingFolder(
                panelDefault: inside, candidates: [own, documents], isDirectory: exists),
            own)
        // A missing first choice falls through to the next one that exists.
        XCTAssertEqual(
            ClaylineGallery.rescuedStartingFolder(
                panelDefault: inside,
                candidates: [nil, URL(fileURLWithPath: "/Volumes/Unplugged"), documents],
                isDirectory: exists),
            documents)
        // A candidate that is itself inside an app is never chosen.
        XCTAssertEqual(
            ClaylineGallery.rescuedStartingFolder(
                panelDefault: inside,
                candidates: [inside, documents],
                isDirectory: { _ in true }),
            documents)
    }

    func testAPanelStartingAnywhereElseIsLeftExactlyAsItWas() {
        let own = URL(fileURLWithPath: "/Users/potter/Drawings")
        XCTAssertNil(ClaylineGallery.rescuedStartingFolder(
            panelDefault: URL(fileURLWithPath: "/Users/potter/Dropbox/tiles"),
            candidates: [own], isDirectory: { _ in true }))
        XCTAssertNil(ClaylineGallery.rescuedStartingFolder(
            panelDefault: nil, candidates: [own], isDirectory: { _ in true }))
    }
}
