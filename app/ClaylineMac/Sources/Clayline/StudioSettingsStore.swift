import Foundation
import WebKit

@MainActor
final class StudioSettingsStore {
    static let messageHandlerName = "claylineSettings"
    static let webStorageKey = "clayline-ui-state.v1"
    static let defaultsKey = "clayline.native-ui-state.v1"
    static let meshPathDefaultsKey = "clayline.native-weave-mesh-path.v1"
    static let projectPathDefaultsKey = "clayline.native-project-path.v1"
    /// The last folder of the artist's own that a drawing was opened from.
    /// Never a folder inside the gallery.
    static let drawingFolderDefaultsKey = "clayline.native-open-drawing-folder.v1"
    /// The last gallery folder a drawing was opened from, as its place inside
    /// the gallery ("Celtic", or "" for the gallery itself) — never a full
    /// path, because the app can sit somewhere else at the next launch.
    static let galleryFolderDefaultsKey = "clayline.native-open-gallery-folder.v1"
    static let maximumStoredBytes = 1_048_576

    private let defaults: UserDefaults

    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
    }

    func userScript() -> WKUserScript {
        WKUserScript(
            source: injectionSource(),
            injectionTime: .atDocumentStart,
            forMainFrameOnly: true
        )
    }

    func apply(messageBody: Any) -> Bool {
        guard let message = messageBody as? [String: Any],
              let operation = message["operation"] as? String
        else {
            return false
        }

        switch operation {
        case "set":
            guard let value = message["value"] as? String,
                  value.lengthOfBytes(using: .utf8) <= Self.maximumStoredBytes
            else {
                return false
            }
            defaults.set(value, forKey: Self.defaultsKey)
            return true
        case "remove":
            defaults.removeObject(forKey: Self.defaultsKey)
            return true
        default:
            return false
        }
    }

    func injectionSource() -> String {
        let initialValue = defaults.string(forKey: Self.defaultsKey)
        let payload: [String: Any] = ["value": initialValue ?? NSNull()]
        let data = try? JSONSerialization.data(withJSONObject: payload)
        let literal = data.flatMap { String(data: $0, encoding: .utf8) } ?? "{\"value\":null}"

        return """
        (() => {
          "use strict";
          const targetKey = \(Self.javascriptString(Self.webStorageKey));
          let currentValue = \(literal).value;
          const post = (operation, value) => {
            try {
              window.webkit.messageHandlers.\(Self.messageHandlerName).postMessage({ operation, value });
            } catch (_error) {
              // The studio remains usable if its native container is already closing.
            }
          };
          const storage = Object.freeze({
            getItem(key) {
              return key === targetKey ? currentValue : null;
            },
            setItem(key, value) {
              if (key !== targetKey) return;
              currentValue = String(value);
              post("set", currentValue);
            },
            removeItem(key) {
              if (key !== targetKey) return;
              currentValue = null;
              post("remove", null);
            },
          });
          Object.defineProperty(window, "claylineSettingsStorage", {
            value: storage,
            configurable: false,
            enumerable: false,
            writable: false,
          });
        })();
        """
    }

    func rememberMeshURL(_ url: URL) {
        defaults.set(url.standardizedFileURL.path, forKey: Self.meshPathDefaultsKey)
    }

    func restorableMeshURL() -> URL? {
        guard let path = defaults.string(forKey: Self.meshPathDefaultsKey) else {
            return nil
        }
        let url = URL(fileURLWithPath: path).standardizedFileURL
        guard ClaylineFileTypes.kind(for: url) == .mesh,
              FileManager.default.isReadableFile(atPath: url.path)
        else {
            forgetMeshURL()
            return nil
        }
        return url
    }

    func forgetMeshURL() {
        defaults.removeObject(forKey: Self.meshPathDefaultsKey)
    }

    /// Where the last project was saved or opened, so the next save panel
    /// starts in that folder. Nothing is reopened at launch: a relaunch stays
    /// a clean slate (Pete 2026-07-26).
    func rememberProjectURL(_ url: URL) {
        defaults.set(url.standardizedFileURL.path, forKey: Self.projectPathDefaultsKey)
    }

    func projectDirectoryURL() -> URL? {
        guard let path = defaults.string(forKey: Self.projectPathDefaultsKey) else {
            return nil
        }
        let directory = URL(fileURLWithPath: path)
            .standardizedFileURL
            .deletingLastPathComponent()
        var isDirectory: ObjCBool = false
        guard FileManager.default.fileExists(atPath: directory.path, isDirectory: &isDirectory),
              isDirectory.boolValue
        else {
            return nil
        }
        return directory
    }

    /// Note where a drawing was just opened from, so the next Open panel can
    /// start there. A folder inside the gallery is kept by its place in the
    /// gallery; anything else is the artist's own folder. The two are held
    /// apart, so browsing the examples never loses someone their own folder.
    func rememberDrawingFolder(for fileURL: URL, gallery: URL?) {
        let folder = fileURL.standardizedFileURL.deletingLastPathComponent()
        if let gallery,
           let subpath = ClaylineGallery.relativeSubpath(of: folder, in: gallery) {
            defaults.set(subpath, forKey: Self.galleryFolderDefaultsKey)
        } else {
            defaults.set(folder.path, forKey: Self.drawingFolderDefaultsKey)
        }
    }

    /// The artist's own last drawing folder, if it is still there.
    func drawingFolderURL(gallery: URL?) -> URL? {
        guard let path = defaults.string(forKey: Self.drawingFolderDefaultsKey) else {
            return nil
        }
        let folder = URL(fileURLWithPath: path, isDirectory: true).standardizedFileURL
        let isInsideGallery = gallery.map {
            ClaylineGallery.relativeSubpath(of: folder, in: $0) != nil
        } ?? false
        guard !path.isEmpty, !isInsideGallery else {
            forgetDrawingFolder()
            return nil
        }
        // A folder that is only absent right now (a drive not plugged in, a
        // share not mounted) is kept, so it is offered again when it returns.
        guard ClaylineGallery.isDirectory(folder) else { return nil }
        return folder
    }

    /// The gallery folder last opened from, found again inside wherever the
    /// gallery is now. A build without a gallery has nothing to find and
    /// leaves the note alone.
    func galleryFolderURL(gallery: URL?) -> URL? {
        guard let gallery,
              let subpath = defaults.string(forKey: Self.galleryFolderDefaultsKey)
        else {
            return nil
        }
        guard let folder = ClaylineGallery.folder(atSubpath: subpath, in: gallery) else {
            forgetGalleryFolder()
            return nil
        }
        return folder
    }

    func forgetDrawingFolder() {
        defaults.removeObject(forKey: Self.drawingFolderDefaultsKey)
    }

    func forgetGalleryFolder() {
        defaults.removeObject(forKey: Self.galleryFolderDefaultsKey)
    }

    private static func javascriptString(_ value: String) -> String {
        let data = try? JSONSerialization.data(withJSONObject: [value])
        guard let encoded = data.flatMap({ String(data: $0, encoding: .utf8) }),
              encoded.count >= 2
        else {
            return "\"\""
        }
        return String(encoded.dropFirst().dropLast())
    }
}
