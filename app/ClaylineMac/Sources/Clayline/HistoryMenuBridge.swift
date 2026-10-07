import AppKit
import WebKit

/// Edit → Undo and Edit → Redo reach the studio's own history, the same steps
/// the header buttons take, through the page's `claylineDesktop` bridge.
///
/// One Command-Z must never step twice. WebKit offers a key equivalent to the
/// page first and passes it on to the menu only when the page leaves it
/// unhandled, and nothing promises AppKit will not offer it to the menu first.
/// So the shell tells the page before it loads (`claylineNativeHistoryMenu`)
/// that the menu owns Command-Z and Shift-Command-Z, and the page's own key
/// handler stands aside without handling the key. In either order the menu
/// item is then the only thing that steps, once per press.
enum HistoryMenuBridge {
    enum Direction: String {
        case undo
        case redo
    }

    enum Outcome: Equatable {
        /// The page took one step back or forward.
        case stepped
        /// There was no step to take.
        case nothingToStep
        /// Focus is in free text, which keeps its own native text undo.
        case nativeText
    }

    /// The page reads this before deciding whether its own key handler acts.
    static let ownershipFlag = "claylineNativeHistoryMenu"

    static var userScriptSource: String { "window.\(ownershipFlag) = true;" }

    static func userScript() -> WKUserScript {
        WKUserScript(
            source: userScriptSource,
            injectionTime: .atDocumentStart,
            forMainFrameOnly: true
        )
    }

    static func script(for direction: Direction) -> String {
        "window.claylineDesktop && window.claylineDesktop.\(direction.rawValue)()"
    }

    static func outcome(of value: Any?) -> Outcome {
        switch value as? String {
        case "done": return .stepped
        case "native": return .nativeText
        default: return .nothingToStep
        }
    }

    /// The stock Edit menu's own actions, for a free-text field.
    static func nativeSelector(for direction: Direction) -> Selector {
        direction == .undo ? Selector(("undo:")) : Selector(("redo:"))
    }
}
