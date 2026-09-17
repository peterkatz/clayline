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

            // Only a copy of the app that carries the example drawings
            // offers them. Shift-Command-O already belongs to Open Project…
            // below, so the gallery takes Option-Command-O.
            if actions.hasGallery {
                Button("Open from Gallery…") {
                    actions.openGallery()
                }
                .keyboardShortcut("o", modifiers: [.command, .option])
                .disabled(!actions.isReady)
            }

            Button("Open Project…") {
                actions.openProject()
            }
            .keyboardShortcut("o", modifiers: [.command, .shift])
            .disabled(!actions.isReady)
        }

        CommandGroup(replacing: .saveItem) {
            Button("Save Project…") {
                actions.saveProject()
            }
            .keyboardShortcut("s", modifiers: .command)
            .disabled(!actions.isReady)

            Button("Export G-code…") {
                actions.saveGCode()
            }
            .keyboardShortcut("e", modifiers: [.command, .shift])
            .disabled(!actions.isReady)
        }
    }
}
