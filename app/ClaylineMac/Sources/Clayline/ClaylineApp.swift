import SwiftUI

@main
struct ClaylineApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) private var appDelegate

    var body: some Scene {
        Window("Clayline", id: "main") {
            RootView(coordinator: appDelegate.coordinator)
        }
        .windowStyle(.titleBar)
        .defaultSize(width: 1_440, height: 900)
        .commands {
            ClaylineCommands(actions: appDelegate.coordinator.webActions)
        }
    }
}
