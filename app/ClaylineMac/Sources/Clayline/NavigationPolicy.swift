import Foundation

struct NavigationPolicy: Equatable, Sendable {
    let origin: URL

    init(origin: URL) {
        self.origin = origin
    }

    func allowsNavigation(to candidate: URL?) -> Bool {
        guard let candidate else { return false }
        return hasExactOrigin(candidate)
    }

    func allowsDownload(from candidate: URL?) -> Bool {
        guard let candidate else { return false }
        if hasExactOrigin(candidate) {
            return true
        }
        guard candidate.scheme?.lowercased() == "blob" else {
            return false
        }
        return candidate.absoluteString.hasPrefix("blob:\(normalizedOriginString)/")
    }

    private func hasExactOrigin(_ candidate: URL) -> Bool {
        guard let expected = URLComponents(url: origin, resolvingAgainstBaseURL: false),
              let actual = URLComponents(url: candidate, resolvingAgainstBaseURL: false)
        else {
            return false
        }
        return actual.scheme?.lowercased() == expected.scheme?.lowercased()
            && actual.host?.lowercased() == expected.host?.lowercased()
            && effectivePort(actual) == effectivePort(expected)
            && actual.user == nil
            && actual.password == nil
    }

    private var normalizedOriginString: String {
        var components = URLComponents()
        components.scheme = origin.scheme?.lowercased()
        components.host = origin.host?.lowercased()
        components.port = origin.port
        return components.string ?? origin.absoluteString.trimmingCharacters(in: CharacterSet(charactersIn: "/"))
    }

    private func effectivePort(_ components: URLComponents) -> Int? {
        if let port = components.port {
            return port
        }
        switch components.scheme?.lowercased() {
        case "http": return 80
        case "https": return 443
        default: return nil
        }
    }
}
