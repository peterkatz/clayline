import XCTest

@testable import Clayline

/// A design edited on the drawing surface should be able to go back over the
/// file the artist opened, instead of landing in Downloads as a copy they then
/// have to reconcile by hand. The page only ever knows a name, so the shell has
/// to be the side that remembers the path.
final class SVGSourceIndexTests: XCTestCase {
    private func scratch() throws -> URL {
        let directory = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        addTeardownBlock { try? FileManager.default.removeItem(at: directory) }
        return directory
    }

    func testAnImportedDesignIsSavedBackOverItsOwnFile() throws {
        let file = try scratch().appendingPathComponent("rosette-study.svg")
        try Data("<svg>original</svg>".utf8).write(to: file)

        var index = SVGSourceIndex()
        index.remember(file)

        let outcome = SVGSaver.saveOverOriginal(
            name: "rosette-study.svg",
            svg: "<svg>edited on the bed</svg>",
            in: index
        )

        XCTAssertEqual(outcome, .wrote(file))
        XCTAssertEqual(try String(contentsOf: file, encoding: .utf8), "<svg>edited on the bed</svg>")
    }

    func testADrawingMadeInTheAppHasNoOriginalToOverwrite() throws {
        var index = SVGSourceIndex()
        index.remember(try scratch().appendingPathComponent("rosette-study.svg"))

        // Nothing was ever imported under this name, so the studio must be told
        // to ask where it goes rather than inventing a destination.
        XCTAssertEqual(
            SVGSaver.saveOverOriginal(name: "drawing-1.svg", svg: "<svg/>", in: index),
            .noKnownSource
        )
    }

    func testAFileThatHasMovedIsNotRecreatedWhereItUsedToBe() throws {
        let file = try scratch().appendingPathComponent("moved.svg")
        try Data("<svg/>".utf8).write(to: file)
        var index = SVGSourceIndex()
        index.remember(file)
        try FileManager.default.removeItem(at: file)

        // Writing here would put the drawing somewhere the artist is no longer
        // looking, which is worse than asking them.
        XCTAssertEqual(
            SVGSaver.saveOverOriginal(name: "moved.svg", svg: "<svg/>", in: index),
            .noKnownSource
        )
        XCTAssertFalse(FileManager.default.fileExists(atPath: file.path))
    }

    func testTheSameNameFromASecondFolderTakesOverTheName() throws {
        let first = try scratch().appendingPathComponent("rosette.svg")
        let second = try scratch().appendingPathComponent("rosette.svg")
        try Data("<svg>first</svg>".utf8).write(to: first)
        try Data("<svg>second</svg>".utf8).write(to: second)

        var index = SVGSourceIndex()
        index.remember([first, second])

        // The page is showing the one imported last, and that is the one saved.
        XCTAssertEqual(index.url(named: "rosette.svg"), second)
        XCTAssertEqual(index.count, 1)
    }

    func testAnOversizedDrawingIsRefusedRatherThanTruncated() throws {
        let file = try scratch().appendingPathComponent("huge.svg")
        try Data("<svg>original</svg>".utf8).write(to: file)
        var index = SVGSourceIndex()
        index.remember(file)

        let outcome = SVGSaver.saveOverOriginal(
            name: "huge.svg",
            svg: String(repeating: "x", count: 64),
            in: index,
            limit: 8
        )

        XCTAssertEqual(outcome, .tooLarge)
        XCTAssertEqual(
            try String(contentsOf: file, encoding: .utf8),
            "<svg>original</svg>",
            "a refused save must leave the artist's file alone"
        )
    }
}
