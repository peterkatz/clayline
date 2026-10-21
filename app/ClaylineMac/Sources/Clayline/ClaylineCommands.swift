import SwiftUI

struct ClaylineCommands: Commands {
    @ObservedObject var actions: WebActions
    @ObservedObject var recentFiles: RecentFilesStore

    var body: some Commands {
        CommandGroup(replacing: .newItem) {
            Button("Open…") {
                actions.openDocuments()
            }
            .keyboardShortcut("o", modifiers: .command)
            .disabled(!actions.isReady)

            // As in other Mac apps: the last ten projects, models, drawings
            // and print files opened or saved, newest first. Choosing one
            // opens it as if it had been picked again.
            Menu("Open Recent") {
                ForEach(recentFiles.entries) { entry in
                    Button(entry.title) {
                        actions.openRecent(entry.url)
                    }
                }
                if !recentFiles.urls.isEmpty {
                    Divider()
                }
                Button("Clear Menu") {
                    recentFiles.clear()
                }
                .disabled(recentFiles.urls.isEmpty)
            }
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

        // The studio's own Undo and Redo, the same steps as the header
        // buttons: moves, settings, a model loaded, a drawing edit. See
        // HistoryMenuBridge for why one Command-Z steps exactly once.
        CommandGroup(replacing: .undoRedo) {
            Button("Undo") {
                actions.undo()
            }
            .keyboardShortcut("z", modifiers: .command)
            .disabled(!actions.isReady)

            Button("Redo") {
                actions.redo()
            }
            .keyboardShortcut("z", modifiers: [.command, .shift])
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

            // The printed coils as an OBJ: the object the slice window shows.
            Button("Export Mesh…") {
                actions.saveMesh()
            }
            .disabled(!actions.isReady)
        }
    }
}
