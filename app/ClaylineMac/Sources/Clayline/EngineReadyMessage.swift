import Foundation

struct EngineReadyMessage: Codable, Equatable, Sendable {
    static let expectedSchema = "clayline.desktop.ready.v1"
    static let expectedHost = "127.0.0.1"
    static let maximumLineBytes = 4_096

    let schema: String
    let host: String
    let port: Int
    let pid: Int32

    static func parse(line: Data) throws -> EngineReadyMessage {
        guard !line.isEmpty else {
            throw EngineProtocolError.emptyReadinessMessage
        }
        guard line.count <= maximumLineBytes else {
            throw EngineProtocolError.readinessMessageTooLarge
        }

        let object = try JSONSerialization.jsonObject(with: line)
        guard let dictionary = object as? [String: Any] else {
            throw EngineProtocolError.invalidReadinessMessage
        }
        guard dictionary["token"] == nil else {
            throw EngineProtocolError.tokenLeakedInReadinessMessage
        }

        let message: EngineReadyMessage
        do {
            message = try JSONDecoder().decode(EngineReadyMessage.self, from: line)
        } catch {
            throw EngineProtocolError.invalidReadinessMessage
        }
        guard message.schema == expectedSchema else {
            throw EngineProtocolError.unsupportedSchema(message.schema)
        }
        guard message.host == expectedHost else {
            throw EngineProtocolError.unsafeHost(message.host)
        }
        guard (1 ... 65_535).contains(message.port) else {
            throw EngineProtocolError.invalidPort(message.port)
        }
        guard message.pid > 0 else {
            throw EngineProtocolError.invalidPID(message.pid)
        }
        return message
    }
}

enum EngineProtocolError: LocalizedError, Equatable {
    case emptyReadinessMessage
    case readinessMessageTooLarge
    case invalidReadinessMessage
    case tokenLeakedInReadinessMessage
    case unsupportedSchema(String)
    case unsafeHost(String)
    case invalidPort(Int)
    case invalidPID(Int32)
    case readinessTimedOut
    case engineClosedReadinessPipe

    var errorDescription: String? {
        switch self {
        case .emptyReadinessMessage, .invalidReadinessMessage:
            return "Clayline’s engine returned an invalid startup message."
        case .readinessMessageTooLarge:
            return "Clayline’s engine returned an oversized startup message."
        case .tokenLeakedInReadinessMessage:
            return "Clayline’s engine exposed private session material during startup."
        case .unsupportedSchema(let schema):
            return "The bundled engine uses an unsupported startup protocol (\(schema))."
        case .unsafeHost(let host):
            return "The bundled engine attempted to listen on an unsafe host (\(host))."
        case .invalidPort(let port):
            return "The bundled engine returned an invalid port (\(port))."
        case .invalidPID(let pid):
            return "The bundled engine returned an invalid process identifier (\(pid))."
        case .readinessTimedOut:
            return "Clayline’s engine did not become ready in time."
        case .engineClosedReadinessPipe:
            return "Clayline’s engine stopped before it became ready."
        }
    }
}
