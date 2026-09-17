import XCTest
@testable import Clayline

final class SafeFilenameTests: XCTestCase {
    func testDownloadFilenameRemovesPathsControlsAndUnsafeCharacters() {
        XCTAssertEqual(
            SafeFilename.download("../../<evil>\r\n export.gcode"),
            "evil-export.gcode"
        )
        XCTAssertEqual(SafeFilename.download(#"C:\temp\tile.GCODE"#), "tile.gcode")
        XCTAssertEqual(SafeFilename.download("my tile (final)"), "my-tile-final.gcode")
    }

    func testDownloadFilenameHasSafeFallbackAndLengthLimit() {
        XCTAssertEqual(SafeFilename.download(nil), SafeFilename.fallback)
        XCTAssertEqual(SafeFilename.download("...gcode"), SafeFilename.fallback)

        let filename = SafeFilename.download(String(repeating: "a", count: 120))
        XCTAssertEqual(filename, String(repeating: "a", count: 80) + ".gcode")
    }

    func testSavedProjectsKeepTheirOwnName() {
        XCTAssertEqual(SafeFilename.download("lantern.clayline"), "lantern.clayline")
        XCTAssertEqual(SafeFilename.download("Lobed Tumbler.CLAYLINE"), "Lobed-Tumbler.clayline")
        XCTAssertEqual(SafeFilename.download("...clayline"), "clayline-project.clayline")
        // A pattern is still a pattern, not a project.
        XCTAssertEqual(
            SafeFilename.download("sine.clayline-weave.json"),
            "sine.clayline-weave.json"
        )
    }

    func testDownloadFilenameNeverAcceptsAnUnknownExtension() {
        XCTAssertEqual(SafeFilename.download("job.svg"), "job.svg.gcode")
        XCTAssertEqual(SafeFilename.download("job.gcode.exe"), "job.gcode.exe.gcode")
    }

    func testSavedPatternsKeepTheirJsonNameIntact() {
        // Regression (Pete 2026-07-20): the shell stamped `.gcode` onto the
        // app's own saved pattern, so the pattern picker greyed it out.
        XCTAssertEqual(
            SafeFilename.download("sine.clayline-weave.json"),
            "sine.clayline-weave.json"
        )
        XCTAssertEqual(SafeFilename.download("Pattern (v2).JSON"), "Pattern-v2.json")
        XCTAssertEqual(SafeFilename.download("...json"), "clayline-pattern.json")
    }
}
