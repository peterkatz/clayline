import Foundation
import WebKit

@MainActor
final class StudioSettingsStore {
    static let messageHandlerName = "claylineSettings"
    static let webStorageKey = "clayline-ui-state.v1"
    static let defaultsKey = "clayline.native-ui-state.v1"
    static let meshPathDefaultsKey = "clayline.native-weave-mesh-path.v1"
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
