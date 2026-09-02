import Foundation
import Security

enum SessionTokenError: LocalizedError {
    case randomGenerationFailed(OSStatus)
    case wrongByteCount(Int)

    var errorDescription: String? {
        switch self {
        case .randomGenerationFailed(let status):
            return "Could not create a secure Clayline session token (Security status \(status))."
        case .wrongByteCount(let count):
            return "Clayline session tokens require exactly 32 bytes, not \(count)."
        }
    }
}

enum SessionToken {
    static let byteCount = 32

    static func generate() throws -> String {
        var bytes = [UInt8](repeating: 0, count: byteCount)
        let status = SecRandomCopyBytes(kSecRandomDefault, bytes.count, &bytes)
        guard status == errSecSuccess else {
            throw SessionTokenError.randomGenerationFailed(status)
        }
        return try lowercaseHex(bytes: bytes)
    }

    static func lowercaseHex(bytes: [UInt8]) throws -> String {
        guard bytes.count == byteCount else {
            throw SessionTokenError.wrongByteCount(bytes.count)
        }
        let digits = Array("0123456789abcdef".utf8)
        var encoded = [UInt8]()
        encoded.reserveCapacity(byteCount * 2)
        for byte in bytes {
            encoded.append(digits[Int(byte >> 4)])
            encoded.append(digits[Int(byte & 0x0f)])
        }
        return String(decoding: encoded, as: UTF8.self)
    }
}
