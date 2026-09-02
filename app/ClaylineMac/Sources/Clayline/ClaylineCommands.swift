import SwiftUI

struct ClaylineCommands: Commands {
    @ObservedObject var actions: WebActions

    var body: some Commands {
        CommandGroup(replacing: .newItem) {
            Button("Open…") {
                actions.openDocuments()
            }
            .keyboardShortcut("o", modifiers: .command)
            .disabled(!actions.isReady)
        }

        CommandGroup(replacing: .saveItem) {
            Button("Export G-code…") {
                actions.saveGCode()
            }
            .keyboardShortcut("s", modifiers: .command)
            .disabled(!actions.isReady)
        }
    }
}
