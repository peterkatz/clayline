import Foundation
import XCTest
@testable import Clayline

final class NavigationPolicyTests: XCTestCase {
    private let origin = URL(string: "http://127.0.0.1:49152")!

    func testNavigationRequiresExactSchemeHostAndPort() {
        let policy = NavigationPolicy(origin: origin)

        XCTAssertTrue(policy.allowsNavigation(to: URL(string: "http://127.0.0.1:49152/")))
        XCTAssertTrue(policy.allowsNavigation(to: URL(string: "http://127.0.0.1:49152/static/app.js")))
        XCTAssertFalse(policy.allowsNavigation(to: URL(string: "http://localhost:49152/")))
        XCTAssertFalse(policy.allowsNavigation(to: URL(string: "http://127.0.0.1:49153/")))
        XCTAssertFalse(policy.allowsNavigation(to: URL(string: "https://127.0.0.1:49152/")))
        XCTAssertFalse(policy.allowsNavigation(to: URL(string: "file:///tmp/job.svg")))
        XCTAssertFalse(policy.allowsNavigation(to: URL(string: "http://user@127.0.0.1:49152/")))
        XCTAssertFalse(policy.allowsNavigation(to: nil))
    }

    func testDownloadsAllowOnlyExactOriginAndItsBlobURLs() {
        let policy = NavigationPolicy(origin: origin)

        XCTAssertTrue(policy.allowsDownload(from: URL(string: "http://127.0.0.1:49152/api/export")))
        XCTAssertTrue(policy.allowsDownload(from: URL(string: "blob:http://127.0.0.1:49152/93D58C65-8910-4FF9-A8A1-FCDD89D5D663")))
        XCTAssertFalse(policy.allowsDownload(from: URL(string: "blob:http://localhost:49152/93D58C65")))
        XCTAssertFalse(policy.allowsDownload(from: URL(string: "blob:https://127.0.0.1:49152/93D58C65")))
        XCTAssertFalse(policy.allowsDownload(from: URL(string: "https://example.com/job.gcode")))
    }
}
