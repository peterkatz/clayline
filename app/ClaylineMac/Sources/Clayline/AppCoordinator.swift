import Combine
import Foundation

@MainActor
final class AppCoordinator: ObservableObject {
    enum Status: Equatable {
        case idle
        case startingEngine
        case loadingInterface
        case ready
        case failed(String)
    }

    @Published private(set) var status: Status = .idle
    @Published private(set) var launch: EngineLaunch?
    let webActions = WebActions()

    private var attemptID = UUID()
    private var shuttingDown = false

    private lazy var engine = EngineProcess { [weak self] status in
        Task { @MainActor [weak self] in
            self?.engineExitedUnexpectedly(status: status)
        }
    }

    func startIfNeeded() {
        guard status == .idle else { return }
        startEngine()
    }

    func retry() {
        let retryID = UUID()
        attemptID = retryID
        launch = nil
        status = .startingEngine
        engine.stop(timeout: 2) { [weak self] in
            Task { @MainActor [weak self] in
                guard let self, self.attemptID == retryID, !self.shuttingDown else { return }
                self.startEngine()
            }
        }
    }

    func webViewDidBecomeReady(enginePID: Int32) {
        guard launch?.readiness.pid == enginePID, status == .loadingInterface else { return }
        status = .ready
    }

    func webViewDidFail(enginePID: Int32, message: String) {
        guard launch?.readiness.pid == enginePID else { return }
        attemptID = UUID()
        launch = nil
        status = .failed(message)
        engine.stop(timeout: 2)
    }

    func shutdown(completion: @escaping @MainActor () -> Void) {
        guard !shuttingDown else {
            completion()
            return
        }
        shuttingDown = true
        attemptID = UUID()
        launch = nil
        engine.stop(timeout: 2) {
            Task { @MainActor in
                completion()
            }
        }
    }

    private func startEngine() {
        let startID = UUID()
        attemptID = startID
        launch = nil
        status = .startingEngine
        engine.start { [weak self] result in
            Task { @MainActor [weak self] in
                guard let self, self.attemptID == startID, !self.shuttingDown else { return }
                switch result {
                case .success(let launch):
                    self.launch = launch
                    self.status = .loadingInterface
                case .failure(let error):
                    self.launch = nil
                    self.status = .failed(error.localizedDescription)
                }
            }
        }
    }

    private func engineExitedUnexpectedly(status exitStatus: Int32) {
        guard !shuttingDown, launch != nil else { return }
        attemptID = UUID()
        launch = nil
        status = .failed("Clayline’s local engine stopped unexpectedly (status \(exitStatus)).")
    }
}
