import Foundation
import Testing
@testable import Clayline

@MainActor
struct StudioSettingsStoreTests {
    @Test
    func setRemoveAndInputBounds() throws {
        let suiteName = "StudioSettingsStoreTests.\(UUID().uuidString)"
        let defaults = try #require(UserDefaults(suiteName: suiteName))
        defer { defaults.removePersistentDomain(forName: suiteName) }
        let store = StudioSettingsStore(defaults: defaults)

        #expect(store.apply(messageBody: ["operation": "set", "value": "saved"]))
        #expect(defaults.string(forKey: StudioSettingsStore.defaultsKey) == "saved")
        #expect(!store.apply(messageBody: ["operation": "set", "value": String(
            repeating: "x",
            count: StudioSettingsStore.maximumStoredBytes + 1
        )]))
        #expect(defaults.string(forKey: StudioSettingsStore.defaultsKey) == "saved")
        #expect(!store.apply(messageBody: ["operation": "unknown"]))
        #expect(store.apply(messageBody: ["operation": "remove"]))
        #expect(defaults.string(forKey: StudioSettingsStore.defaultsKey) == nil)
    }

    @Test
    func injectionIsSynchronousScopedAndSafelyEncoded() throws {
        let suiteName = "StudioSettingsStoreTests.\(UUID().uuidString)"
        let defaults = try #require(UserDefaults(suiteName: suiteName))
        defer { defaults.removePersistentDomain(forName: suiteName) }
        let stored = "{\"quote\":\"'\\n</script>\"}"
        defaults.set(stored, forKey: StudioSettingsStore.defaultsKey)
        let source = StudioSettingsStore(defaults: defaults).injectionSource()

        #expect(source.contains("claylineSettingsStorage"))
        #expect(source.contains("getItem(key)"))
        #expect(source.contains("key === targetKey"))
        #expect(source.contains("postMessage({ operation, value })"))
        #expect(source.contains("\\\\n<\\/script>"))
        #expect(!source.contains("let currentValue = {'quote'"))
    }

    @Test
    func remembersReadableMeshAndForgetsStalePath() throws {
        let suiteName = "StudioSettingsStoreTests.\(UUID().uuidString)"
        let defaults = try #require(UserDefaults(suiteName: suiteName))
        defer { defaults.removePersistentDomain(forName: suiteName) }
        let store = StudioSettingsStore(defaults: defaults)
        let directory = FileManager.default.temporaryDirectory
            .appendingPathComponent("ClaylineMeshRestore.\(UUID().uuidString)")
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: directory) }
        let mesh = directory.appendingPathComponent("remembered.obj")
        try Data("v 0 0 0\n".utf8).write(to: mesh)

        store.rememberMeshURL(mesh)

        #expect(defaults.string(forKey: StudioSettingsStore.meshPathDefaultsKey) == mesh.path)
        #expect(store.restorableMeshURL() == mesh.standardizedFileURL)

        try FileManager.default.removeItem(at: mesh)
        #expect(store.restorableMeshURL() == nil)
        #expect(defaults.string(forKey: StudioSettingsStore.meshPathDefaultsKey) == nil)
    }

    @Test
    func rejectsRememberedNonMeshPath() throws {
        let suiteName = "StudioSettingsStoreTests.\(UUID().uuidString)"
        let defaults = try #require(UserDefaults(suiteName: suiteName))
        defer { defaults.removePersistentDomain(forName: suiteName) }
        let store = StudioSettingsStore(defaults: defaults)
        let file = FileManager.default.temporaryDirectory
            .appendingPathComponent("not-a-mesh-\(UUID().uuidString).txt")
        try Data("not a mesh".utf8).write(to: file)
        defer { try? FileManager.default.removeItem(at: file) }

        store.rememberMeshURL(file)

        #expect(store.restorableMeshURL() == nil)
        #expect(defaults.string(forKey: StudioSettingsStore.meshPathDefaultsKey) == nil)
    }
}
