import UniformTypeIdentifiers

enum ClaylineDocumentMode: String, Equatable {
    case tiles
    case weave
}

enum ClaylineDocumentKind: Equatable {
    case svg
    case mesh

    var mode: ClaylineDocumentMode {
        switch self {
        case .svg: .tiles
        case .mesh: .weave
        }
    }
}

struct ClaylineImportSelection: Equatable {
    let mode: ClaylineDocumentMode
    let urls: [URL]
    let ignoredCount: Int
}

/// One file-picker request from the web layer: the document mode the page is
/// in, plus whether the picker was opened for a reference photo. draw.js
/// stamps `body.dataset.claylineFileRequest` right before clicking its file
/// input, and the delegate's read script clears the one-shot marker so a
/// later SVG picker can never inherit it.
struct ClaylineOpenRequest: Equatable {
    let mode: ClaylineDocumentMode
    let isReferencePhoto: Bool

    init(raw: String?) {
        let parts = (raw ?? "").split(
            separator: ":", maxSplits: 1, omittingEmptySubsequences: false
        )
        let modeToken = parts.first.map(String.init) ?? ""
        mode = modeToken == ClaylineDocumentMode.weave.rawValue ? .weave : .tiles
        let requestToken = parts.count > 1 ? String(parts[1]) : ""
        isReferencePhoto = requestToken == "reference-photo"
    }
}

enum ClaylineFileTypes {
    static let svg = UTType.svg
    static let obj = UTType("public.geometry-definition-format")!
    static let stl = UTType("public.standard-tesselated-geometry-format")!
    static let threeMF = UTType(
        importedAs: "com.clayline.mesh.3mf",
        conformingTo: .threeDContent
    )
    static let ply = UTType("public.polygon-file-format")!
    static let gcode = UTType(exportedAs: "com.clayline.gcode", conformingTo: .plainText)

    static let meshTypes = [obj, stl, threeMF, ply]
    static let meshExtensions: Set<String> = ["obj", "stl", "3mf", "ply"]

    /// The reference lightbox's photo formats, matching the web layer's
    /// REFERENCE_TYPES in draw.js — a photo traced over, never printed.
    static let referencePhotoTypes: [UTType] = {
        var types: [UTType] = [.png, .jpeg, .webP, .heic]
        if let heif = UTType("public.heif") {
            types.append(heif)
        }
        return types
    }()

    static func allowedContentTypes(for mode: ClaylineDocumentMode) -> [UTType] {
        mode == .weave ? meshTypes : [svg]
    }

    static func kind(for url: URL) -> ClaylineDocumentKind? {
        let fileExtension = url.pathExtension.lowercased()
        if fileExtension == "svg" {
            return .svg
        }
        if meshExtensions.contains(fileExtension) {
            return .mesh
        }
        return nil
    }

    /// Routes one Finder handoff without ever treating mesh bytes as text.
    /// SVG batches retain the existing 32-file cap. Weave deliberately accepts
    /// one mesh; callers surface `ignoredCount` instead of silently pretending
    /// a multi-mesh selection was imported.
    static func importSelection(
        from urls: [URL],
        maximumSVGCount: Int = 32
    ) -> ClaylineImportSelection? {
        let recognized = urls.compactMap { url in
            kind(for: url).map { (url, $0) }
        }
        guard let first = recognized.first else { return nil }

        let selected: [URL]
        switch first.1 {
        case .mesh:
            selected = [first.0]
        case .svg:
            selected = Array(
                recognized.lazy
                    .filter { $0.1 == .svg }
                    .prefix(max(0, maximumSVGCount))
                    .map(\.0)
            )
        }
        return ClaylineImportSelection(
            mode: first.1.mode,
            urls: selected,
            ignoredCount: max(0, urls.count - selected.count)
        )
    }
}
