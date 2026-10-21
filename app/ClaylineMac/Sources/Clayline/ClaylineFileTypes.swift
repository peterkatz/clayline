import UniformTypeIdentifiers

enum ClaylineDocumentMode: String, Equatable {
    case tiles
    case weave
}

enum ClaylineDocumentKind: Equatable {
    case svg
    case mesh
    case project
    /// A print file, Clayline's own or another slicer's. Weave takes it the
    /// way its Model box takes one: Clayline's brings back its whole job, and
    /// another slicer's is rebuilt into a form.
    case printFile

    /// A project carries its own mode inside it, so the shell has none to
    /// choose for it: the page switches rails once it has read the file.
    var mode: ClaylineDocumentMode? {
        switch self {
        case .svg: .tiles
        case .mesh, .printFile: .weave
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
/// project, for a print file, or for the gallery of example drawings. draw.js,
/// app.js and weave.js stamp `body.dataset.claylineFileRequest` right before
/// clicking their file inputs, and the delegate's read script clears the
/// one-shot marker so a later SVG picker can never inherit it.
struct ClaylineOpenRequest: Equatable {
    let mode: ClaylineDocumentMode
    let isReferencePhoto: Bool
    let isProject: Bool
    /// The Weave pattern section asked for a print file Clayline saved, to
    /// take its pattern out. Nothing else in that file is read.
    let isPrintFile: Bool
    /// The Weave pattern section's Load pattern asked for a saved pattern
    /// file. It loads onto the form already on the table; it is not a job.
    let isPattern: Bool
    /// The page asked for the example drawings rather than the artist's own
    /// folder. It only changes where the drawing picker starts.
    let isGallery: Bool

    /// Whether what this panel opens goes on File → Open Recent as soon as it
    /// is chosen. A photo to trace over is not a document, and a print file
    /// chosen for its pattern alone would come back from the menu as a whole
    /// job. The Open Project panel's file is noted once the page has opened
    /// it, through `WebActions.projectWasOpened(at:)`.
    var addsToOpenRecent: Bool {
        !isProject && !isReferencePhoto && !isPrintFile && !isPattern
    }

    /// A project chosen here waits for the page, whichever panel it was
    /// chosen in — the Open Project panel or Weave's Model box. Only once the
    /// page says it opened does it name the window, give the next save its
    /// folder and go on File → Open Recent; a damaged or foreign file the
    /// page turns down does none of these.
    func awaitsThePage(_ url: URL) -> Bool {
        isProject || ClaylineFileTypes.kind(for: url) == .project
    }

    /// Whether a file chosen here goes on File → Open Recent the moment the
    /// panel closes: only from a panel that adds to the list, never a project
    /// (it waits for the page), and only a file the menu could open again.
    /// The page reads a picked file with no bound of its own, so a drawing
    /// or model larger than the shell hands over would otherwise sit on the
    /// list and never open from it.
    func notesOnPick(_ url: URL) -> Bool {
        addsToOpenRecent && !awaitsThePage(url) && WebActions.reopenRouteCanCarry(url)
    }

    /// The Draw in Clay picker for drawings — the one panel that starts in a
    /// remembered folder or in the gallery. Weave's picker, the project
    /// picker, the print-file picker and the reference-photo picker are none
    /// of its business.
    var isDrawingPicker: Bool {
        mode == .tiles && !isProject && !isReferencePhoto && !isPrintFile && !isPattern
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
        isPrintFile = requestToken == "gcode"
        isPattern = requestToken == "pattern"
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
    static let printFileExtension = "gcode"
    static let projectTypes = [project]
    /// One print file Clayline wrote, opened only to take its pattern out.
    static let printFileTypes = [gcode]
    /// A saved pattern (`name.clayline-weave.json`), as Save pattern writes it.
    static let patternTypes: [UTType] = [.json]

    /// The reference lightbox's photo formats, matching the web layer's
    /// REFERENCE_TYPES in draw.js — a photo traced over, never printed.
    static let referencePhotoTypes: [UTType] = {
        var types: [UTType] = [.png, .jpeg, .webP, .heic]
        if let heif = UTType("public.heif") {
            types.append(heif)
        }
        return types
    }()

    /// The Weave drop zone's box says it takes a project and a print file as
    /// well as a mesh, and its input accepts all three, so the panel that box
    /// opens must offer them too; the page routes a chosen `.clayline` or
    /// `.gcode` by its suffix. Draw's picker is a multi-select of SVGs and
    /// keeps its own project button.
    static func allowedContentTypes(for mode: ClaylineDocumentMode) -> [UTType] {
        mode == .weave ? meshTypes + projectTypes + printFileTypes : [svg]
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
        if fileExtension == printFileExtension {
            return .printFile
        }
        return nil
    }

    /// Routes one Finder handoff without ever treating mesh bytes as text.
    /// SVG batches retain the existing 32-file cap. Weave deliberately accepts
    /// one mesh, and a project and a print file open one at a time the same
    /// way; callers surface `ignoredCount` instead of silently pretending a
    /// multi-mesh or multi-project selection was imported.
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
        case .mesh, .project, .printFile:
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
