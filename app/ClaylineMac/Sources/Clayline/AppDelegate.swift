import AppKit

@MainActor
final class AppDelegate: NSObject, NSApplicationDelegate {
    let coordinator = AppCoordinator()
    private var terminationReplyPending = false

    func applicationDidFinishLaunching(_ notification: Notification) {
        coordinator.startIfNeeded()
    }

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
