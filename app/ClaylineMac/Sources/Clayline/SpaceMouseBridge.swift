import AppKit
import Foundation
import WebKit

/// A 3Dconnexion 3D mouse turns, slides and zooms the studio's 3D view the
/// way it does in Refab.
///
/// Where it meets the driver this is Refab's SpaceMouseController unchanged:
/// the classic ConnexionClient C API, loaded with `dlopen` at run time so a
/// Mac without the 3Dconnexion driver is untouched (every call no-ops); a
/// wildcard client signature in take-over mode with all six axes, so motion
/// arrives whenever Clayline is frontmost; the axis array read at byte 30 of
/// `ConnexionDeviceState`; each axis clamped to ±500; the all-zero report
/// the driver sends on release dropped.
///
/// Each report goes to the page's `window.claylineSpaceMouse.motion`, which
/// holds Refab's mapping, smoothing, speed and camera factors
/// (viewport3d.js). At most one call is in flight: reports that arrive while
/// the page is still running the last one fold into the newest, with a count
/// of how many there were, so a busy page drops stale positions without
/// shortening how far the view travels.
@MainActor
final class SpaceMouseBridge {
    static let shared = SpaceMouseBridge()

    struct Motion: Equatable, Sendable {
        /// Driver axis order: tx slide left/right, ty push/pull, tz lift
        /// (the raw macOS frame is Z-up), then rx tilt forward/back, ry tilt
        /// left/right, rz twist. About ±350 at full deflection.
        var tx: Double
        var ty: Double
        var tz: Double
        var rx: Double
        var ry: Double
        var rz: Double
    }

    nonisolated static let frameworkPath = "/Library/Frameworks/3DconnexionClient.framework/3DconnexionClient"
    nonisolated static let deviceStateMessage: UInt32 = 0x3364_5352 // '3dSR'
    nonisolated static let modeTakeOver: UInt16 = 1
    nonisolated static let maskAllAxes: UInt32 = 0x3F00
    /// `ConnexionDeviceState` is `#pragma pack(push,2)`, so `uint64_t time`
    /// sits 2-byte aligned with no pad after `value`: version@0 client@2
    /// command@4 param@6 value@8 time@12 report@20 buttons8@28 axis@30
    /// (6 x int16) address@42 buttons@44. Refab once read the axes at 34,
    /// two slots too far, and fed the USB address and button bits to its
    /// camera while losing the slide axes; 30 is the verified offset.
    nonisolated static let axisByteOffset = 30
    nonisolated static let deviceStateByteCount = 48
    nonisolated static let axisLimit = 500.0
    /// The most reports one page call stands for, so a page that stalled
    /// for a moment is not thrown far when it catches up.
    nonisolated static let maxReportsPerCall = 10

    private typealias MessageHandler = @convention(c) (UInt32, UInt32, UnsafeMutableRawPointer?) -> Void
    private typealias SetHandlersFn = @convention(c) (
        MessageHandler?, (@convention(c) (UInt32) -> Void)?, (@convention(c) (UInt32) -> Void)?, Bool
    ) -> Int16
    private typealias RegisterFn = @convention(c) (UInt32, UnsafePointer<UInt8>?, UInt16, UInt32) -> UInt16
    private typealias UnregisterFn = @convention(c) (UInt16) -> Void
    private typealias CleanupFn = @convention(c) () -> Void

    private var clientID: UInt16 = 0
    private var unregister: UnregisterFn?
    private var cleanup: CleanupFn?
    private(set) var isActive = false

    private weak var webView: WKWebView?
    /// Tests stand in for the page here; nil sends to the attached web view.
    var evaluator: ((String, @escaping @MainActor () -> Void) -> Void)?
    private var pending: Motion?
    private var pendingReports = 0
    private var inFlight = false

    /// The 3D view lives in this web view from now on. Starts listening to
    /// the driver the first time; safe to call again.
    func attach(_ webView: WKWebView) {
        self.webView = webView
        start()
    }

    func detach(_ webView: WKWebView) {
        guard self.webView === webView else { return }
        self.webView = nil
        pending = nil
        pendingReports = 0
    }

    /// Idempotent; does nothing on a Mac without the 3Dconnexion driver.
    func start() {
        guard !isActive else { return }
        guard FileManager.default.fileExists(atPath: Self.frameworkPath),
              let handle = dlopen(Self.frameworkPath, RTLD_LAZY)
        else { return }
        guard let setSym = dlsym(handle, "SetConnexionHandlers"),
              let registerSym = dlsym(handle, "RegisterConnexionClient")
        else { return }
        let setHandlers = unsafeBitCast(setSym, to: SetHandlersFn.self)
        let register = unsafeBitCast(registerSym, to: RegisterFn.self)
        if let unregisterSym = dlsym(handle, "UnregisterConnexionClient") {
            unregister = unsafeBitCast(unregisterSym, to: UnregisterFn.self)
        }
        if let cleanupSym = dlsym(handle, "CleanupConnexionHandlers") {
            cleanup = unsafeBitCast(cleanupSym, to: CleanupFn.self)
        }
        guard setHandlers(spaceMouseMessageFunnel, nil, nil, false) == 0 else { return }
        // Wildcard signature + take-over mode + all six axes: motion arrives
        // whenever Clayline is frontmost.
        clientID = register(0, nil, Self.modeTakeOver, Self.maskAllAxes)
        isActive = true
    }

    func stop() {
        guard isActive else { return }
        unregister?(clientID)
        cleanup?()
        isActive = false
    }

    // MARK: - Reports

    /// The six axis values of a `ConnexionDeviceState`, in driver order.
    nonisolated static func axes(fromDeviceState state: UnsafeRawPointer) -> [Int16] {
        (0..<6).map { index in
            state.loadUnaligned(fromByteOffset: axisByteOffset + index * 2, as: Int16.self)
        }
    }

    /// One report as motion, clamped to the device's range; nil for the
    /// all-zero report the driver sends when the cap is let go.
    nonisolated static func motion(fromAxes axis: [Int16]) -> Motion? {
        guard axis.count == 6 else { return nil }
        func sane(_ value: Int16) -> Double {
            max(-axisLimit, min(axisLimit, Double(value)))
        }
        let motion = Motion(
            tx: sane(axis[0]), ty: sane(axis[1]), tz: sane(axis[2]),
            rx: sane(axis[3]), ry: sane(axis[4]), rz: sane(axis[5])
        )
        guard motion.tx != 0 || motion.ty != 0 || motion.tz != 0
            || motion.rx != 0 || motion.ry != 0 || motion.rz != 0
        else { return nil }
        return motion
    }

    /// The page call for one motion standing for `reports` driver reports.
    nonisolated static func script(for motion: Motion, reports: Int) -> String {
        let values = [motion.tx, motion.ty, motion.tz, motion.rx, motion.ry, motion.rz]
            .map { String(Int(max(-axisLimit, min(axisLimit, $0)).rounded())) }
        let count = max(1, min(maxReportsPerCall, reports))
        return "window.claylineSpaceMouse && window.claylineSpaceMouse.motion("
            + values.joined(separator: ",") + ",\(count))"
    }

    func receive(_ motion: Motion) {
        pending = motion
        pendingReports += 1
        sendIfIdle()
    }

    private func sendIfIdle() {
        guard !inFlight, let motion = pending else { return }
        let reports = pendingReports
        pending = nil
        pendingReports = 0
        let script = Self.script(for: motion, reports: reports)
        let done: @MainActor () -> Void = { [weak self] in
            guard let self else { return }
            self.inFlight = false
            self.sendIfIdle()
        }
        if let evaluator {
            inFlight = true
            evaluator(script, done)
            return
        }
        guard let webView else { return }
        inFlight = true
        webView.evaluateJavaScript(script) { _, _ in done() }
    }
}

/// C-callback funnel: the classic API has no context pointer.
private func spaceMouseMessageFunnel(
    _ productID: UInt32, _ messageType: UInt32, _ argument: UnsafeMutableRawPointer?
) {
    guard messageType == SpaceMouseBridge.deviceStateMessage, let argument else { return }
    guard let motion = SpaceMouseBridge.motion(fromAxes: SpaceMouseBridge.axes(fromDeviceState: argument))
    else { return }
    if Thread.isMainThread {
        MainActor.assumeIsolated { SpaceMouseBridge.shared.receive(motion) }
    } else {
        DispatchQueue.main.async {
            MainActor.assumeIsolated { SpaceMouseBridge.shared.receive(motion) }
        }
    }
}
