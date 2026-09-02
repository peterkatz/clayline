import Darwin
import Foundation

enum EngineProcessError: LocalizedError {
    case alreadyStarted
    case executableMissing(URL)
    case executableNotRunnable(URL)
    case stoppedDuringStartup

    var errorDescription: String? {
        switch self {
        case .alreadyStarted:
            return "Clayline’s engine is already running."
        case .executableMissing(let url):
            return "The Clayline engine is missing from \(url.path)."
        case .executableNotRunnable(let url):
            return "The bundled Clayline engine is not executable at \(url.path)."
        case .stoppedDuringStartup:
            return "Clayline’s engine was stopped during startup."
        }
    }
}

final class EngineProcess: @unchecked Sendable {
    typealias StartCompletion = @Sendable (Result<EngineLaunch, Error>) -> Void
    typealias ExitHandler = @Sendable (Int32) -> Void

    private enum Lifecycle {
        case idle
        case starting
        case running
        case stopping
        case stopped
    }

    private let executableURL: URL
    private let stateLock = NSLock()
    private let startupQueue = DispatchQueue(label: "com.clayline.engine.startup", qos: .userInitiated)
    private let shutdownQueue = DispatchQueue(label: "com.clayline.engine.shutdown", qos: .userInitiated)
    private let onUnexpectedExit: ExitHandler

    private var lifecycle: Lifecycle = .idle
    private var process: Process?
    private var stdinWriteHandle: FileHandle?
    private var stdoutReadHandle: FileHandle?
    private var enginePID: Int32?

    init(
        executableURL: URL = EngineProcess.bundledExecutableURL(),
        onUnexpectedExit: @escaping ExitHandler = { _ in }
    ) {
        self.executableURL = executableURL
        self.onUnexpectedExit = onUnexpectedExit
    }

    static func bundledExecutableURL(bundle: Bundle = .main) -> URL {
        let configured = bundle.object(forInfoDictionaryKey: "ClaylineEngineExecutable") as? String
            ?? "Resources/Engine/ClaylineEngine"
        return bundle.bundleURL
            .appending(path: "Contents", directoryHint: .isDirectory)
            .appending(path: configured, directoryHint: .notDirectory)
    }

    func start(readinessTimeout: TimeInterval = 15, completion: @escaping StartCompletion) {
        startupQueue.async { [self] in
            do {
                completion(.success(try startBlocking(readinessTimeout: readinessTimeout)))
            } catch {
                stopBlocking(timeout: 0.5)
                completion(.failure(error))
            }
        }
    }

    func stop(timeout: TimeInterval = 2, completion: (@Sendable () -> Void)? = nil) {
        shutdownQueue.async { [self] in
            stopBlocking(timeout: timeout)
            completion?()
        }
    }

    private func startBlocking(readinessTimeout: TimeInterval) throws -> EngineLaunch {
        stateLock.lock()
        guard lifecycle == .idle || lifecycle == .stopped else {
            stateLock.unlock()
            throw EngineProcessError.alreadyStarted
        }
        lifecycle = .starting
        stateLock.unlock()

        guard FileManager.default.fileExists(atPath: executableURL.path) else {
            throw EngineProcessError.executableMissing(executableURL)
        }
        guard FileManager.default.isExecutableFile(atPath: executableURL.path) else {
            throw EngineProcessError.executableNotRunnable(executableURL)
        }

        let token = try SessionToken.generate()
        let child = Process()
        let input = Pipe()
        let output = Pipe()
        child.executableURL = executableURL
        child.standardInput = input
        child.standardOutput = output
        child.standardError = FileHandle.nullDevice
        child.environment = [
            "HOME": NSHomeDirectory(),
            "LANG": ProcessInfo.processInfo.environment["LANG"] ?? "en_US.UTF-8",
            "LC_ALL": ProcessInfo.processInfo.environment["LC_ALL"] ?? "en_US.UTF-8",
            "PATH": "/usr/bin:/bin",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONNOUSERSITE": "1",
            "PYTHONUNBUFFERED": "1",
            "TMPDIR": FileManager.default.temporaryDirectory.path,
        ]
        child.terminationHandler = { [weak self] process in
            self?.processDidTerminate(status: process.terminationStatus)
        }

        stateLock.lock()
        process = child
        stdinWriteHandle = input.fileHandleForWriting
        stdoutReadHandle = output.fileHandleForReading
        stateLock.unlock()

        try child.run()
        try input.fileHandleForWriting.write(contentsOf: Data("\(token)\n".utf8))

        let line = try Self.readLine(
            from: output.fileHandleForReading,
            timeout: readinessTimeout,
            maximumBytes: EngineReadyMessage.maximumLineBytes
        )
        let readiness = try EngineReadyMessage.parse(line: line)
        guard readiness.pid == child.processIdentifier else {
            throw EngineProtocolError.invalidPID(readiness.pid)
        }

        stateLock.lock()
        guard lifecycle == .starting, child.isRunning else {
            stateLock.unlock()
            throw EngineProcessError.stoppedDuringStartup
        }
        lifecycle = .running
        enginePID = readiness.pid
        stateLock.unlock()
        return EngineLaunch(readiness: readiness, token: token)
    }

    private func processDidTerminate(status: Int32) {
        stateLock.lock()
        let previous = lifecycle
        lifecycle = .stopped
        process = nil
        stdinWriteHandle = nil
        stdoutReadHandle = nil
        enginePID = nil
        stateLock.unlock()

        if previous == .running {
            onUnexpectedExit(status)
        }
    }

    private func stopBlocking(timeout: TimeInterval) {
        stateLock.lock()
        if lifecycle == .idle || lifecycle == .stopped {
            lifecycle = .stopped
            stateLock.unlock()
            return
        }
        lifecycle = .stopping
        let child = process
        let input = stdinWriteHandle
        let readyPID = enginePID
        stdinWriteHandle = nil
        stateLock.unlock()

        try? input?.close()
        if child?.isRunning == true {
            child?.terminate()
        }

        let deadline = DispatchTime.now().uptimeNanoseconds
            + UInt64(max(0, timeout) * 1_000_000_000)
        while child?.isRunning == true && DispatchTime.now().uptimeNanoseconds < deadline {
            usleep(20_000)
        }

        if child?.isRunning == true {
            if let readyPID, readyPID > 0 {
                _ = Darwin.kill(readyPID, SIGKILL)
            }
            if let processPID = child?.processIdentifier, processPID > 0, processPID != readyPID {
                _ = Darwin.kill(processPID, SIGKILL)
            }
        }

        let killDeadline = DispatchTime.now().uptimeNanoseconds + 500_000_000
        while child?.isRunning == true && DispatchTime.now().uptimeNanoseconds < killDeadline {
            usleep(10_000)
        }

        stateLock.lock()
        lifecycle = .stopped
        process = nil
        stdoutReadHandle = nil
        enginePID = nil
        stateLock.unlock()
    }

    private static func readLine(
        from handle: FileHandle,
        timeout: TimeInterval,
        maximumBytes: Int
    ) throws -> Data {
        let descriptor = handle.fileDescriptor
        let started = DispatchTime.now().uptimeNanoseconds
        let timeoutNanoseconds = UInt64(max(0, timeout) * 1_000_000_000)
        let deadline = started + timeoutNanoseconds
        var result = Data()

        while result.count <= maximumBytes {
            let now = DispatchTime.now().uptimeNanoseconds
            guard now < deadline else {
                throw EngineProtocolError.readinessTimedOut
            }
            let remainingNanoseconds = deadline - now
            let remainingMilliseconds = max(1, min(
                Int64(Int32.max),
                Int64((remainingNanoseconds + 999_999) / 1_000_000)
            ))
            var descriptorState = pollfd(
                fd: descriptor,
                events: Int16(POLLIN | POLLHUP),
                revents: 0
            )
            let pollResult = Darwin.poll(&descriptorState, 1, Int32(remainingMilliseconds))
            if pollResult == 0 {
                throw EngineProtocolError.readinessTimedOut
            }
            if pollResult < 0 {
                if errno == EINTR { continue }
                throw CocoaError(.fileReadUnknown)
            }

            var byte: UInt8 = 0
            let byteCount = Darwin.read(descriptor, &byte, 1)
            if byteCount == 0 {
                throw EngineProtocolError.engineClosedReadinessPipe
            }
            if byteCount < 0 {
                if errno == EINTR || errno == EAGAIN { continue }
                throw CocoaError(.fileReadUnknown)
            }
            if byte == 0x0a {
                if result.last == 0x0d {
                    result.removeLast()
                }
                return result
            }
            result.append(byte)
        }
        throw EngineProtocolError.readinessMessageTooLarge
    }
}
