import Foundation

struct EngineLaunch: Equatable, Sendable {
    let readiness: EngineReadyMessage
    let token: String

    var originURL: URL {
        var components = URLComponents()
        components.scheme = "http"
        components.host = readiness.host
        components.port = readiness.port
        // Validation performed by EngineReadyMessage makes failure impossible.
        return components.url!
    }

    var healthURL: URL {
        originURL.appending(path: "api/health")
    }
}
