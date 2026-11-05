import Foundation
import UniformTypeIdentifiers
import XCTest
@testable import Clayline

final class FileTypeAndImportTests: XCTestCase {
    func testModeFiltersRegisterEverySupportedDocumentType() {
        XCTAssertEqual(ClaylineFileTypes.allowedContentTypes(for: .tiles), [ClaylineFileTypes.svg])
        XCTAssertEqual(
            Set(ClaylineFileTypes.allowedContentTypes(for: .weave).map(\.identifier)),
            [
                "public.geometry-definition-format",
                "public.standard-tesselated-geometry-format",
                "com.clayline.mesh.3mf",
                "public.polygon-file-format",
                "com.clayline.project",
                "com.clayline.gcode",
            ]
        )
    }

    /// The Model box says it takes a print file, so the panel it opens has to
    /// offer one; the page takes the pattern out of whatever is chosen there.
    func testPrintFileTypeIsOwnedByClaylineAndReachesTheWeavePanel() {
        XCTAssertEqual(ClaylineFileTypes.printFileTypes.map(\.identifier), ["com.clayline.gcode"])
        XCTAssertTrue(
            ClaylineFileTypes.allowedContentTypes(for: .weave).contains(ClaylineFileTypes.gcode)
        )
        XCTAssertFalse(
            ClaylineFileTypes.allowedContentTypes(for: .tiles).contains(ClaylineFileTypes.gcode)
        )
    }

    func testProjectTypeIsOwnedByClaylineAndKeepsItsOwnExtension() {
        XCTAssertEqual(
            ClaylineFileTypes.projectTypes.map(\.identifier),
            ["com.clayline.project"]
        )
        XCTAssertEqual(ClaylineFileTypes.projectExtension, "clayline")
    }

    func testExtensionRoutingIsCaseInsensitiveAndRejectsLookalikes() {
        XCTAssertEqual(ClaylineFileTypes.kind(for: URL(fileURLWithPath: "/tmp/tile.SVG")), .svg)
        for fileExtension in ["obj", "STL", "3mf", "PlY"] {
            XCTAssertEqual(
                ClaylineFileTypes.kind(for: URL(fileURLWithPath: "/tmp/form.\(fileExtension)")),
                .mesh
            )
        }
        XCTAssertEqual(
            ClaylineFileTypes.kind(for: URL(fileURLWithPath: "/tmp/lantern.CLAYLINE")),
            .project
        )
        XCTAssertNil(ClaylineFileTypes.kind(for: URL(fileURLWithPath: "/tmp/form.obj.txt")))
        XCTAssertNil(ClaylineFileTypes.kind(for: URL(fileURLWithPath: "/tmp/no-extension")))
        XCTAssertNil(ClaylineFileTypes.kind(for: URL(fileURLWithPath: "/tmp/lantern.clayline.zip")))
    }

    func testFinderSelectionUsesFirstSupportedModeAndOnlyOneMesh() throws {
        let urls = ["form.obj", "other.stl", "tile.svg"].map {
            URL(fileURLWithPath: "/tmp/\($0)")
        }
        let selection = try XCTUnwrap(ClaylineFileTypes.importSelection(from: urls))

        XCTAssertEqual(selection.mode, .weave)
        XCTAssertEqual(selection.urls, [urls[0]])
        XCTAssertEqual(selection.ignoredCount, 2)
    }

    func testFinderSelectionOpensOneProjectAndCarriesNoModeOfItsOwn() throws {
        // A project names its own rail inside the file, so the shell does not
        // choose one for it.
        let urls = ["lantern.clayline", "second.clayline", "tile.svg"].map {
            URL(fileURLWithPath: "/tmp/\($0)")
        }
        let selection = try XCTUnwrap(ClaylineFileTypes.importSelection(from: urls))

        XCTAssertEqual(selection.kind, .project)
        XCTAssertNil(selection.mode)
        XCTAssertEqual(selection.urls, [urls[0]])
        XCTAssertEqual(selection.ignoredCount, 2)
    }

    func testFinderSVGBatchRetainsTilesFlowAndCap() throws {
        let urls = [
            URL(fileURLWithPath: "/tmp/first.svg"),
            URL(fileURLWithPath: "/tmp/form.ply"),
            URL(fileURLWithPath: "/tmp/second.SVG"),
        ]
        let selection = try XCTUnwrap(
            ClaylineFileTypes.importSelection(from: urls, maximumSVGCount: 1)
        )

        XCTAssertEqual(selection.mode, .tiles)
        XCTAssertEqual(selection.urls, [urls[0]])
        XCTAssertEqual(selection.ignoredCount, 2)
    }

    func testBoundedMeshReaderAcceptsOpaqueBytesAtLimitAndRejectsOneByteOver() throws {
        let directory = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString, isDirectory: true)
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: directory) }

        let exact = directory.appendingPathComponent("exact.stl")
        let oversized = directory.appendingPathComponent("oversized.stl")
        let opaque = Data([0xff, 0x00, 0x80, 0x42])
        try opaque.write(to: exact)
        try (opaque + Data([0x99])).write(to: oversized)

        XCTAssertEqual(
            WebActions.readBoundedBinaryFile(exact, maximumBytes: opaque.count),
            opaque
        )
        XCTAssertNil(
            WebActions.readBoundedBinaryFile(oversized, maximumBytes: opaque.count)
        )
    }

    func testReferencePhotoTypesCoverEveryFormatTheLightboxReads() {
        // Matching draw.js REFERENCE_TYPES: the native picker must let the
        // artist choose exactly what the web layer can decode.
        let identifiers = Set(ClaylineFileTypes.referencePhotoTypes.map(\.identifier))
        XCTAssertTrue(identifiers.contains("public.png"))
        XCTAssertTrue(identifiers.contains("public.jpeg"))
        XCTAssertTrue(identifiers.contains("org.webmproject.webp") || identifiers.contains("public.webp"))
        XCTAssertTrue(identifiers.contains("public.heic"))
    }

    func testProjectHandoffIsBoundedAtNinetySixMebibytes() {
        XCTAssertEqual(WebActions.maximumProjectBytes, 96 * 1_024 * 1_024)
    }

    func testOpenRequestParsesModeAndOneShotPhotoMarker() {
        XCTAssertEqual(
            ClaylineOpenRequest(raw: "tiles:reference-photo"),
            ClaylineOpenRequest(raw: "tiles:reference-photo")
        )
        XCTAssertTrue(ClaylineOpenRequest(raw: "tiles:reference-photo").isReferencePhoto)
        XCTAssertEqual(ClaylineOpenRequest(raw: "tiles:reference-photo").mode, .tiles)
        XCTAssertFalse(ClaylineOpenRequest(raw: "tiles:").isReferencePhoto)
        XCTAssertEqual(ClaylineOpenRequest(raw: "weave:").mode, .weave)
        XCTAssertFalse(ClaylineOpenRequest(raw: "weave:").isReferencePhoto)
        // A missing or malformed readback opens the ordinary SVG picker.
        XCTAssertEqual(ClaylineOpenRequest(raw: nil).mode, .tiles)
        XCTAssertFalse(ClaylineOpenRequest(raw: nil).isReferencePhoto)
        XCTAssertFalse(ClaylineOpenRequest(raw: "tiles").isReferencePhoto)
        XCTAssertFalse(ClaylineOpenRequest(raw: "tiles:reference-photo").isProject)
        XCTAssertFalse(ClaylineOpenRequest(raw: nil).isProject)
    }

    func testOpenRequestParsesTheProjectMarkerFromEitherRail() {
        for raw in ["tiles:project", "weave:project"] {
            let request = ClaylineOpenRequest(raw: raw)
            XCTAssertTrue(request.isProject)
            XCTAssertFalse(request.isReferencePhoto)
        }
        XCTAssertEqual(ClaylineOpenRequest(raw: "weave:project").mode, .weave)
        XCTAssertFalse(ClaylineOpenRequest(raw: "tiles:projects").isProject)
    }

    /// Restore pattern from G-code… stamps its own one-shot marker, so the
    /// panel it opens shows print files instead of meshes — and no other
    /// picker inherits it.
    func testOpenRequestParsesThePrintFileMarker() {
        let request = ClaylineOpenRequest(raw: "weave:gcode")
        XCTAssertTrue(request.isPrintFile)
        XCTAssertFalse(request.isProject)
        XCTAssertFalse(request.isReferencePhoto)
        XCTAssertFalse(request.isDrawingPicker)
        XCTAssertEqual(request.mode, .weave)
        for raw in ["weave:", "weave:project", "tiles:reference-photo", "tiles:gcodes"] {
            XCTAssertFalse(ClaylineOpenRequest(raw: raw).isPrintFile, raw)
        }
        XCTAssertFalse(ClaylineOpenRequest(raw: nil).isPrintFile)
    }

    /// Upload image… stamps its own one-shot marker. Without it the panel fell
    /// to the Model box's meshes, projects and print files, where every image
    /// was greyed out. A picture is no document, so it goes nowhere the shell
    /// keeps documents, and no other picker inherits it.
    func testOpenRequestParsesTheImageMarker() throws {
        let request = ClaylineOpenRequest(raw: "weave:image")
        XCTAssertTrue(request.isImage)
        XCTAssertEqual(request.mode, .weave)
        XCTAssertFalse(request.isProject)
        XCTAssertFalse(request.isReferencePhoto)
        XCTAssertFalse(request.isPrintFile)
        XCTAssertFalse(request.isPattern)
        XCTAssertFalse(request.isGallery)
        XCTAssertFalse(request.isDrawingPicker)
        XCTAssertFalse(request.addsToOpenRecent)

        let folder = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString, isDirectory: true)
        try FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)
        addTeardownBlock { try? FileManager.default.removeItem(at: folder) }
        let picture = folder.appendingPathComponent("relief.psd")
        XCTAssertTrue(FileManager.default.createFile(atPath: picture.path, contents: Data([0])))
        XCTAssertFalse(request.awaitsThePage(picture))
        XCTAssertFalse(request.notesOnPick(picture))

        for raw in ["weave:", "weave:gcode", "weave:pattern", "weave:project", "tiles:reference-photo", "tiles:", "tiles:gallery", "weave:images", "weave:Image"] {
            XCTAssertFalse(ClaylineOpenRequest(raw: raw).isImage, raw)
        }
        XCTAssertFalse(ClaylineOpenRequest(raw: nil).isImage)
    }

    func testTheImagePanelOffersEveryFormatTheEngineReads() {
        XCTAssertEqual(ClaylineFileTypes.imagePanelTitle, "Choose an Image")
        XCTAssertEqual(
            Set(ClaylineFileTypes.imageTypes.map(\.identifier)),
            [
                "public.png", "public.jpeg", "public.tiff", "org.webmproject.webp",
                "com.microsoft.bmp", "public.heic", "public.heif",
                "com.adobe.photoshop-image",
            ]
        )
        // The panel filters by these types, so each real file name has to
        // land on one of them, the two TIFF and two JPEG spellings included.
        for name in ["a.png", "a.jpg", "a.jpeg", "a.tif", "a.tiff", "a.webp", "a.bmp", "a.heic", "a.heif", "a.psd"] {
            let type = UTType(filenameExtension: (name as NSString).pathExtension)
            XCTAssertTrue(
                ClaylineFileTypes.imageTypes.contains { type?.conforms(to: $0) == true },
                name
            )
        }
    }

    /// Adding the image panel left every other panel's list as it was.
    func testTheOtherPanelsOfferWhatTheyAlwaysDid() {
        XCTAssertEqual(ClaylineFileTypes.allowedContentTypes(for: .tiles), [ClaylineFileTypes.svg])
        XCTAssertEqual(
            ClaylineFileTypes.allowedContentTypes(for: .weave),
            ClaylineFileTypes.meshTypes + ClaylineFileTypes.projectTypes + ClaylineFileTypes.printFileTypes
        )
        XCTAssertEqual(ClaylineFileTypes.projectTypes, [ClaylineFileTypes.project])
        XCTAssertEqual(ClaylineFileTypes.printFileTypes, [ClaylineFileTypes.gcode])
        XCTAssertEqual(ClaylineFileTypes.patternTypes, [.json])
        let photos = Set(ClaylineFileTypes.referencePhotoTypes.map(\.identifier))
        XCTAssertEqual(
            photos,
            ["public.png", "public.jpeg", "org.webmproject.webp", "public.heic", "public.heif"]
        )
        for type in ClaylineFileTypes.imageTypes {
            XCTAssertFalse(ClaylineFileTypes.allowedContentTypes(for: .weave).contains(type))
        }
    }

    /// Load pattern stamps its own one-shot marker, so the panel it opens
    /// offers saved pattern files instead of the Model box's meshes, projects
    /// and print files (where a pattern was greyed out), and a pattern never
    /// goes on File → Open Recent.
    func testOpenRequestParsesThePatternMarker() {
        let request = ClaylineOpenRequest(raw: "weave:pattern")
        XCTAssertTrue(request.isPattern)
        XCTAssertFalse(request.isPrintFile)
        XCTAssertFalse(request.isProject)
        XCTAssertFalse(request.isReferencePhoto)
        XCTAssertFalse(request.isDrawingPicker)
        XCTAssertFalse(request.addsToOpenRecent)
        XCTAssertEqual(request.mode, .weave)
        for raw in ["weave:", "weave:gcode", "weave:project", "tiles:patterns"] {
            XCTAssertFalse(ClaylineOpenRequest(raw: raw).isPattern, raw)
        }
        XCTAssertFalse(ClaylineOpenRequest(raw: nil).isPattern)
        XCTAssertEqual(ClaylineFileTypes.patternTypes, [.json])
        // A saved pattern is named name.clayline-weave.json and is JSON.
        let saved = UTType(filenameExtension: "json")
        XCTAssertEqual(saved, .json)
        XCTAssertFalse(ClaylineFileTypes.allowedContentTypes(for: .weave).contains(.json))
    }
}
