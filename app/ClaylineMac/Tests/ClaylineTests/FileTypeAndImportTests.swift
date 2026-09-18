import Foundation
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
}
