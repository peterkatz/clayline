import Foundation

enum SafeFilename {
    static let fallback = "clayline-job.gcode"
    private static let maximumStemCharacters = 80
    /// Extensions the studio legitimately downloads. Anything else keeps the
    /// historical G-code default — but a saved pattern must never come back
    /// as `name.json.gcode` (Pete 2026-07-20: the picker greyed out the
    /// app's own file).
    static let knownExtensions = ["gcode", "json"]

    static func download(_ proposed: String?) -> String {
        let raw = (proposed ?? "")
            .replacingOccurrences(of: "\\", with: "/")
            .split(separator: "/", omittingEmptySubsequences: true)
            .last
            .map(String.init)?
            .trimmingCharacters(in: .whitespacesAndNewlines) ?? ""

        var stem = raw
        var fileExtension = "gcode"
        for candidate in knownExtensions where raw.lowercased().hasSuffix(".\(candidate)") {
            stem = String(raw.dropLast(candidate.count + 1))
            fileExtension = candidate
            break
        }

        var sanitized = ""
        var lastWasReplacement = false
        for scalar in stem.unicodeScalars {
            let safe = scalar.isASCII && (
                CharacterSet.alphanumerics.contains(scalar)
                    || scalar == "."
                    || scalar == "_"
                    || scalar == "-"
            )
            if safe {
                sanitized.unicodeScalars.append(scalar)
                lastWasReplacement = false
            } else if !lastWasReplacement {
                sanitized.append("-")
                lastWasReplacement = true
            }
        }
        sanitized = sanitized.trimmingCharacters(in: CharacterSet(charactersIn: "-._"))
        sanitized = String(sanitized.prefix(maximumStemCharacters))
            .trimmingCharacters(in: CharacterSet(charactersIn: "-._"))
        guard !sanitized.isEmpty else {
            return fileExtension == "gcode" ? fallback : "clayline-pattern.\(fileExtension)"
        }
        return "\(sanitized).\(fileExtension)"
    }
}
