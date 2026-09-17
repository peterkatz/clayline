import UniformTypeIdentifiers

enum ClaylineDocumentMode: String, Equatable {
    case tiles
    case weave
}

enum ClaylineDocumentKind: Equatable {
    case svg
    case mesh
    case project

    /// A project carries its own mode inside it, so the shell has none to
    /// choose for it: the page switches rails once it has read the file.
    var mode: ClaylineDocumentMode? {
        switch self {
        case .svg: .tiles
        case .mesh: .weave
        case .project: nil
        }
    }
}

struct ClaylineImportSelection: Equatable {
    let kind: ClaylineDocumentKind
    let urls: [URL]
    let ignoredCount: Int

    var mode: ClaylineDocumentMode? { kind.mode }
}

/// One file-picker request from the web layer: the document mode the page is
/// in, plus whether the picker was opened for a reference photo, for a
/// project, or for the gallery of example drawings. draw.js and app.js stamp
/// `body.dataset.claylineFileRequest` right before clicking their file inputs,
/// and the delegate's read script clears the one-shot marker so a later SVG
/// picker can never inherit it.
struct ClaylineOpenRequest: Equatable {
    let mode: ClaylineDocumentMode
    let isReferencePhoto: Bool
    let isProject: Bool
    /// The page asked for the example drawings rather than the artist's own
    /// folder. It only changes where the drawing picker starts.
    let isGallery: Bool

    /// The Draw in Clay picker for drawings — the one panel that starts in a
    /// remembered folder or in the gallery. Weave's picker, the project
    /// picker and the reference-photo picker are none of its business.
    var isDrawingPicker: Bool {
        mode == .tiles && !isProject && !isReferencePhoto
    }

    init(raw: String?) {
        let parts = (raw ?? "").split(
            separator: ":", maxSplits: 1, omittingEmptySubsequences: false
        )
        let modeToken = parts.first.map(String.init) ?? ""
        mode = modeToken == ClaylineDocumentMode.weave.rawValue ? .weave : .tiles
        let requestToken = parts.count > 1 ? String(parts[1]) : ""
        isReferencePhoto = requestToken == "reference-photo"
        isProject = requestToken == "project"
        isGallery = requestToken == "gallery"
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
    /// One saved job — the object and every setting of its mode — in the
    /// container the page writes and reads.
    static let project = UTType(exportedAs: "com.clayline.project", conformingTo: .data)

    static let meshTypes = [obj, stl, threeMF, ply]
    static let meshExtensions: Set<String> = ["obj", "stl", "3mf", "ply"]
    static let projectExtension = "clayline"
    static let projectTypes = [project]

    /// The reference lightbox's photo formats, matching the web layer's
    /// REFERENCE_TYPES in draw.js — a photo traced over, never printed.
    static let referencePhotoTypes: [UTType] = {
        var types: [UTType] = [.png, .jpeg, .webP, .heic]
        if let heif = UTType("public.heif") {
            types.append(heif)
        }
        return types
    }()

    /// The Weave drop zone's box says it takes a project as well as a mesh,
    /// and its input accepts one, so the panel that box opens must offer one
    /// too; the page routes a chosen `.clayline` by its suffix. Draw's picker
    /// is a multi-select of SVGs and keeps its own project button.
    static func allowedContentTypes(for mode: ClaylineDocumentMode) -> [UTType] {
        mode == .weave ? meshTypes + projectTypes : [svg]
    }

    static func kind(for url: URL) -> ClaylineDocumentKind? {
        let fileExtension = url.pathExtension.lowercased()
        if fileExtension == "svg" {
            return .svg
        }
        if meshExtensions.contains(fileExtension) {
            return .mesh
        }
        if fileExtension == projectExtension {
            return .project
        }
        return nil
    }

    /// Routes one Finder handoff without ever treating mesh bytes as text.
    /// SVG batches retain the existing 32-file cap. Weave deliberately accepts
    /// one mesh, and a project opens one at a time the same way; callers
    /// surface `ignoredCount` instead of silently pretending a multi-mesh or
    /// multi-project selection was imported.
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
        case .mesh, .project:
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
            kind: first.1,
            urls: selected,
            ignoredCount: max(0, urls.count - selected.count)
        )
    }
}
