import AppKit

@MainActor
final class AppDelegate: NSObject, NSApplicationDelegate {
    let coordinator = AppCoordinator()
    private var terminationReplyPending = false

    func applicationDidFinishLaunching(_ notification: Notification) {
        coordinator.startIfNeeded()
    }

    /// Finder, the Dock and Open With: projects, models, drawings and print
    /// files, each routed by its kind, and each on File → Open Recent once it
    /// has opened.
    func application(_ application: NSApplication, open urls: [URL]) {
        coordinator.webActions.importDocuments(urls)
    }

    func applicationShouldTerminate(_ sender: NSApplication) -> NSApplication.TerminateReply {
        guard !terminationReplyPending else {
            return .terminateLater
        }
        terminationReplyPending = true
        coordinator.shutdown {
            sender.reply(toApplicationShouldTerminate: true)
        }
        return .terminateLater
    }
}
