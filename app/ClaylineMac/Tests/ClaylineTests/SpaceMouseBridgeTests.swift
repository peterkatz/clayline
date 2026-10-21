import JavaScriptCore
import XCTest

@testable import Clayline

/// The 3D mouse, from the driver's bytes to the studio's view: the device
/// state read at byte 30, Refab's clamp and release drop, the page call, the
/// one-call-in-flight folding, and Refab's own mapping tests run against the
/// mapping the studio really ships (viewport3d.js, in JavaScriptCore).
@MainActor
final class SpaceMouseBridgeTests: XCTestCase {
    // MARK: - ConnexionDeviceState

    /// A device-state buffer laid out as the packed SDK struct is, with every
    /// field around the axes filled so a wrong offset reads something else.
    private func deviceState(axes: [Int16]) -> [UInt8] {
        var bytes = [UInt8](repeating: 0, count: SpaceMouseBridge.deviceStateByteCount)
        bytes.withUnsafeMutableBytes { raw in
            raw.storeBytes(of: UInt16(33), toByteOffset: 0, as: UInt16.self)      // version
            raw.storeBytes(of: UInt16(7), toByteOffset: 2, as: UInt16.self)       // client
            raw.storeBytes(of: UInt16(3), toByteOffset: 4, as: UInt16.self)       // command
            raw.storeBytes(of: Int16(1), toByteOffset: 6, as: Int16.self)         // param
            raw.storeBytes(of: Int32(9), toByteOffset: 8, as: Int32.self)         // value
            raw.storeBytes(of: UInt64(0x1122_3344_5566_7788), toByteOffset: 12, as: UInt64.self) // time
            for index in 0..<8 { raw[20 + index] = 0xA0 + UInt8(index) }         // report
            raw.storeBytes(of: UInt16(0x0101), toByteOffset: 28, as: UInt16.self) // buttons8
            for (index, value) in axes.enumerated() {
                raw.storeBytes(of: value, toByteOffset: 30 + index * 2, as: Int16.self)
            }
            raw.storeBytes(of: UInt16(0x7777), toByteOffset: 42, as: UInt16.self) // address
            raw.storeBytes(of: UInt32(0x0000_0003), toByteOffset: 44, as: UInt32.self) // buttons
        }
        return bytes
    }

    func testTheSixAxesAreReadAtByteThirtyInDriverOrder() {
        let sent: [Int16] = [120, -230, 45, -310, 77, -5]
        let bytes = deviceState(axes: sent)
        let read = bytes.withUnsafeBytes { SpaceMouseBridge.axes(fromDeviceState: $0.baseAddress!) }
        XCTAssertEqual(SpaceMouseBridge.axisByteOffset, 30)
        XCTAssertEqual(read, sent)
        // Refab's old offset 34 read {z, rx, ry, rz, address, buttons}.
        let wrong: [Int16] = bytes.withUnsafeBytes { raw in
            (0..<6).map { raw.loadUnaligned(fromByteOffset: 34 + $0 * 2, as: Int16.self) }
        }
        XCTAssertEqual(Array(wrong.prefix(4)), Array(sent.suffix(4)))
        XCTAssertEqual(wrong[4], 0x7777)
    }

    func testEachAxisIsClampedToFiveHundred() {
        let motion = SpaceMouseBridge.motion(fromAxes: [32_767, -32_768, 499, -501, 0, 350])
        XCTAssertEqual(motion, .init(tx: 500, ty: -500, tz: 499, rx: -500, ry: 0, rz: 350))
    }

    func testTheAllZeroReleaseReportIsDropped() {
        XCTAssertNil(SpaceMouseBridge.motion(fromAxes: [0, 0, 0, 0, 0, 0]))
        XCTAssertNil(SpaceMouseBridge.motion(fromAxes: [1, 2, 3]))
        XCTAssertNotNil(SpaceMouseBridge.motion(fromAxes: [0, 0, 0, 0, 0, 1]))
    }

    func testThePageCallCarriesTheAxesInDriverOrderAndTheReportCount() {
        let motion = SpaceMouseBridge.Motion(tx: 10, ty: -20, tz: 30, rx: -40, ry: 50, rz: -60)
        XCTAssertEqual(
            SpaceMouseBridge.script(for: motion, reports: 1),
            "window.claylineSpaceMouse && window.claylineSpaceMouse.motion(10,-20,30,-40,50,-60,1)"
        )
        XCTAssertTrue(SpaceMouseBridge.script(for: motion, reports: 40).hasSuffix(",-60,10)"))
        XCTAssertTrue(SpaceMouseBridge.script(for: motion, reports: 0).hasSuffix(",-60,1)"))
    }

    // MARK: - One call in flight

    func testReportsWhileThePageIsBusyFoldIntoTheNewestWithTheirCount() {
        let bridge = SpaceMouseBridge()
        var sent: [String] = []
        var finish: [@MainActor () -> Void] = []
        bridge.evaluator = { script, done in
            sent.append(script)
            finish.append(done)
        }
        func report(_ rz: Double) {
            bridge.receive(.init(tx: 0, ty: 0, tz: 0, rx: 0, ry: 0, rz: rz))
        }

        report(1)
        XCTAssertEqual(sent.count, 1)
        XCTAssertTrue(sent[0].hasSuffix("motion(0,0,0,0,0,1,1)"))

        report(2)
        report(3)
        report(4)
        XCTAssertEqual(sent.count, 1, "nothing more goes while the first call runs")

        finish.removeFirst()()
        XCTAssertEqual(sent.count, 2)
        XCTAssertTrue(sent[1].hasSuffix("motion(0,0,0,0,0,4,3)"), "the newest report, standing for three")

        finish.removeFirst()()
        XCTAssertEqual(sent.count, 2, "nothing waiting, nothing sent")

        report(5)
        XCTAssertEqual(sent.count, 3)
        XCTAssertTrue(sent[2].hasSuffix("motion(0,0,0,0,0,5,1)"))
    }

    func testAReportWithNoPageIsDroppedAndDoesNotJamTheNextOne() {
        let bridge = SpaceMouseBridge()
        bridge.receive(.init(tx: 1, ty: 0, tz: 0, rx: 0, ry: 0, rz: 0))
        XCTAssertFalse(bridge.isActive, "a test never starts the driver")
        var sent: [String] = []
        bridge.evaluator = { script, _ in sent.append(script) }
        bridge.receive(.init(tx: 2, ty: 0, tz: 0, rx: 0, ry: 0, rz: 0))
        XCTAssertEqual(sent, ["window.claylineSpaceMouse && window.claylineSpaceMouse.motion(2,0,0,0,0,0,1)"])
    }

    // MARK: - Refab's mapping tests, against the shipped mapping

    private static func staticFile(_ name: String) throws -> String {
        let root = URL(fileURLWithPath: #filePath)
            .deletingLastPathComponent()  // this file → ClaylineTests
            .deletingLastPathComponent()  // → Tests
            .deletingLastPathComponent()  // → ClaylineMac
            .deletingLastPathComponent()  // → app
            .deletingLastPathComponent()  // → repository root
        let url = root.appendingPathComponent("src/clayline/webui/static").appendingPathComponent(name)
        return try String(contentsOf: url, encoding: .utf8)
    }

    private static var studio: JSContext?

    private func studioMapping() throws -> JSValue {
        if Self.studio == nil {
            let context = try XCTUnwrap(JSContext())
            var failure: String?
            context.exceptionHandler = { _, exception in failure = exception?.toString() }
            context.evaluateScript("var window = globalThis; var console = { log() {}, warn() {}, error() {} };")
            context.evaluateScript(try Self.staticFile("three.min.js"))
            context.evaluateScript(try Self.staticFile("viewport3d.js"))
            XCTAssertNil(failure)
            Self.studio = context
        }
        return try XCTUnwrap(Self.studio?.evaluateScript("window.claylineSpaceMouse"))
    }

    private struct Deltas {
        var orbitX = 0.0, orbitY = 0.0, roll = 0.0, panX = 0.0, panY = 0.0, zoom = 0.0
    }

    private func deltas(
        tx: Double = 0, ty: Double = 0, tz: Double = 0,
        rx: Double = 0, ry: Double = 0, rz: Double = 0
    ) throws -> Deltas {
        let mapping = try studioMapping()
        let value = try XCTUnwrap(mapping.invokeMethod("deltas", withArguments: [tx, ty, tz, rx, ry, rz]))
        func read(_ key: String) -> Double { value.forProperty(key).toDouble() }
        return Deltas(
            orbitX: read("orbitX"), orbitY: read("orbitY"), roll: read("roll"),
            panX: read("panX"), panY: read("panY"), zoom: read("zoom")
        )
    }

    // Left/right pair: slide (tx) MOVES, tilt/roll (ry) ROLLS — different actions.
    func testSlideMovesHorizontally() throws {
        let d = try deltas(tx: 200)
        XCTAssertNotEqual(d.panX, 0)
        XCTAssertTrue(d.orbitX == 0 && d.orbitY == 0 && d.roll == 0 && d.panY == 0 && d.zoom == 0)
    }

    func testTiltLeftRightRollsNotYaw() throws {
        let d = try deltas(ry: 200)
        XCTAssertNotEqual(d.roll, 0)
        XCTAssertEqual(d.orbitX, 0)  // NOT yaw — roll is its own axis
        XCTAssertTrue(d.orbitY == 0 && d.panX == 0 && d.panY == 0 && d.zoom == 0)
    }

    func testTwistYawsNotRoll() throws {
        let d = try deltas(rz: 200)
        XCTAssertNotEqual(d.orbitX, 0)
        XCTAssertEqual(d.roll, 0)  // twist and tilt-L/R are DISTINCT
        XCTAssertTrue(d.orbitY == 0 && d.panX == 0 && d.panY == 0 && d.zoom == 0)
    }

    // Forward/back pair: push (ty) zooms, tilt (rx) pitches.
    func testPushPullZoomsNotPitch() throws {
        let d = try deltas(ty: 150)
        XCTAssertNotEqual(d.zoom, 0)
        XCTAssertTrue(d.orbitY == 0 && d.roll == 0 && d.panX == 0 && d.panY == 0 && d.orbitX == 0)
    }

    func testTiltForwardBackPitches() throws {
        let d = try deltas(rx: 150)
        XCTAssertNotEqual(d.orbitY, 0)
        XCTAssertTrue(d.orbitX == 0 && d.roll == 0 && d.panX == 0 && d.panY == 0 && d.zoom == 0)
    }

    // Vertical: lift (tz) pans vertically, never zooms.
    func testLiftPansVerticallyNotZoom() throws {
        let d = try deltas(tz: 200)
        XCTAssertNotEqual(d.panY, 0)
        XCTAssertTrue(d.zoom == 0 && d.panX == 0 && d.roll == 0)
    }

    /// Refab's gains and signs exactly: orbit 0.02, pan 0.015, zoom -0.012.
    func testTheGainsAndSignsAreRefabs() throws {
        let d = try deltas(tx: 100, ty: 100, tz: 100, rx: 100, ry: 100, rz: 100)
        XCTAssertEqual(d.orbitX, 2, accuracy: 1e-12)
        XCTAssertEqual(d.orbitY, 2, accuracy: 1e-12)
        XCTAssertEqual(d.roll, 2, accuracy: 1e-12)
        XCTAssertEqual(d.panX, 1.5, accuracy: 1e-12)
        XCTAssertEqual(d.panY, 1.5, accuracy: 1e-12)
        XCTAssertEqual(d.zoom, -1.2, accuracy: 1e-12)
        let tuning = try studioMapping().forProperty("tuning")!
        XCTAssertEqual(tuning.forProperty("smoothing").toDouble(), 0.6)
        XCTAssertEqual(tuning.forProperty("speed").toDouble(), 1.0)
    }
}
