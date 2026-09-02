import XCTest
@testable import Clayline

/// WKDownload refuses to write over an existing file. The save panel already
/// collected "Replace?" consent, so the shell must remove the old file itself
/// — otherwise every re-export to the same name dies silently and the artist
/// keeps reading a stale file (Pete 2026-07-21: three calibrated re-exports
/// lost to one drape-era file).
final class ReplaceableDestinationTests: XCTestCase {
    func testExistingFileIsRemovedSoTheDownloadCanLand() throws {
        let directory = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: directory) }

        let destination = directory.appendingPathComponent("tile.gcode")
        try Data("stale drape export".utf8).write(to: destination)
        XCTAssertTrue(FileManager.default.fileExists(atPath: destination.path))

        let resolved = ClaylineWebView.Coordinator.replaceableDestination(destination)

        XCTAssertEqual(resolved, destination)
        XCTAssertFalse(
            FileManager.default.fileExists(atPath: destination.path),
            "the stale file must be gone so WKDownload can write the new one"
        )
    }

    func testFreshDestinationPassesThroughUntouched() throws {
        let destination = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
            .appendingPathComponent("new.gcode")
        XCTAssertEqual(ClaylineWebView.Coordinator.replaceableDestination(destination), destination)
    }

    func testNilStaysNil() {
        XCTAssertNil(ClaylineWebView.Coordinator.replaceableDestination(nil))
    }
}
