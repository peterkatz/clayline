import XCTest
@testable import Clayline

/// WKDownload refuses to write over an existing file. Deleting the chosen
/// file first honoured the save panel's "Replace?" consent but threw the only
/// copy away before a byte arrived, so a failed write left nothing at all.
/// Downloads now write to a sibling working file and take the chosen name
/// only when the bytes are all there — a project that fails to save leaves
/// the saved project untouched.
final class StagedDownloadTests: XCTestCase {
    private func makeDirectory() throws -> URL {
        let directory = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString, isDirectory: true)
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        addTeardownBlock { try? FileManager.default.removeItem(at: directory) }
        return directory
    }

    func testTheWorkingFileIsASiblingAndNeverTheChosenName() throws {
        let directory = try makeDirectory()
        let destination = directory.appendingPathComponent("lantern.clayline")
        let staged = StagedDownload(destination: destination, isProject: true)

        XCTAssertEqual(staged.destination, destination.standardizedFileURL)
        XCTAssertEqual(staged.staging.deletingLastPathComponent(), directory.standardizedFileURL)
        XCTAssertNotEqual(staged.staging, staged.destination)
        XCTAssertTrue(staged.isProject)
        XCTAssertNotEqual(
            StagedDownload(destination: destination, isProject: true).staging,
            staged.staging,
            "two saves to the same name must not share one working file"
        )
    }

    func testAFailedWriteLeavesTheExistingFileByteIdentical() throws {
        let directory = try makeDirectory()
        let destination = directory.appendingPathComponent("lantern.clayline")
        let saved = Data("the project the artist already has".utf8)
        try saved.write(to: destination)

        let staged = StagedDownload(destination: destination, isProject: true)
        try Data("half a project".utf8).write(to: staged.staging)
        StagedDownload.discard(staging: staged.staging)

        XCTAssertEqual(try Data(contentsOf: destination), saved)
        XCTAssertFalse(FileManager.default.fileExists(atPath: staged.staging.path))
    }

    func testNothingWrittenMeansNothingIsReplaced() throws {
        let directory = try makeDirectory()
        let destination = directory.appendingPathComponent("lantern.clayline")
        let saved = Data("the project the artist already has".utf8)
        try saved.write(to: destination)

        let staged = StagedDownload(destination: destination, isProject: true)
        XCTAssertFalse(StagedDownload.commit(staging: staged.staging, destination: destination))
        XCTAssertEqual(try Data(contentsOf: destination), saved)
    }

    func testASuccessfulWriteReplacesTheFileContents() throws {
        let directory = try makeDirectory()
        let destination = directory.appendingPathComponent("lantern.clayline")
        try Data("the older project".utf8).write(to: destination)

        let staged = StagedDownload(destination: destination, isProject: true)
        let fresh = Data("the project just saved".utf8)
        try fresh.write(to: staged.staging)

        XCTAssertTrue(StagedDownload.commit(staging: staged.staging, destination: destination))
        XCTAssertEqual(try Data(contentsOf: destination), fresh)
        XCTAssertFalse(FileManager.default.fileExists(atPath: staged.staging.path))
    }

    func testAFreshDestinationPassesThrough() throws {
        let directory = try makeDirectory()
        let destination = directory.appendingPathComponent("first-save.gcode")
        let staged = StagedDownload(destination: destination, isProject: false)
        let bytes = Data("G1 X0 Y0\n".utf8)
        try bytes.write(to: staged.staging)

        XCTAssertTrue(StagedDownload.commit(staging: staged.staging, destination: destination))
        XCTAssertEqual(try Data(contentsOf: destination), bytes)
        XCTAssertFalse(FileManager.default.fileExists(atPath: staged.staging.path))
        XCTAssertFalse(staged.isProject)
    }
}
