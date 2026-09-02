import Foundation
import XCTest
@testable import Clayline

final class SessionAndReadinessTests: XCTestCase {
    func testSessionTokenIsThirtyTwoBytesOfLowercaseHex() throws {
        let token = try SessionToken.generate()

        XCTAssertEqual(token.count, 64)
        XCTAssertNotNil(token.range(of: "^[0-9a-f]{64}$", options: .regularExpression))
    }

    func testSessionTokenEncodingIsStableAndRejectsWrongSize() throws {
        let bytes = Array(UInt8(0) ... UInt8(31))

        XCTAssertEqual(
            try SessionToken.lowercaseHex(bytes: bytes),
            "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f"
        )
        XCTAssertThrowsError(try SessionToken.lowercaseHex(bytes: [0]))
    }

    func testValidReadinessMessageParsesWithoutToken() throws {
        let data = Data(#"{"schema":"clayline.desktop.ready.v1","host":"127.0.0.1","port":49152,"pid":4321}"#.utf8)

        XCTAssertEqual(
            try EngineReadyMessage.parse(line: data),
            EngineReadyMessage(
                schema: EngineReadyMessage.expectedSchema,
                host: EngineReadyMessage.expectedHost,
                port: 49_152,
                pid: 4_321
            )
        )
    }

    func testReadinessMessageRejectsTokenLeakAndUnsafeEndpoint() throws {
        let tokenLeak = Data(#"{"schema":"clayline.desktop.ready.v1","host":"127.0.0.1","port":49152,"pid":4321,"token":"secret"}"#.utf8)
        XCTAssertThrowsError(try EngineReadyMessage.parse(line: tokenLeak)) { error in
            XCTAssertEqual(error as? EngineProtocolError, .tokenLeakedInReadinessMessage)
        }

        let unsafeHost = Data(#"{"schema":"clayline.desktop.ready.v1","host":"0.0.0.0","port":49152,"pid":4321}"#.utf8)
        XCTAssertThrowsError(try EngineReadyMessage.parse(line: unsafeHost)) { error in
            XCTAssertEqual(error as? EngineProtocolError, .unsafeHost("0.0.0.0"))
        }

        let invalidPort = Data(#"{"schema":"clayline.desktop.ready.v1","host":"127.0.0.1","port":0,"pid":4321}"#.utf8)
        XCTAssertThrowsError(try EngineReadyMessage.parse(line: invalidPort)) { error in
            XCTAssertEqual(error as? EngineProtocolError, .invalidPort(0))
        }
    }
}
