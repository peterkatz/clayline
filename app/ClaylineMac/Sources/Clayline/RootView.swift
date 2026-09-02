import SwiftUI

struct RootView: View {
    @ObservedObject var coordinator: AppCoordinator

    var body: some View {
        ZStack {
            Color(red: 0.933, green: 0.914, blue: 0.875)
                .ignoresSafeArea()

            if let launch = coordinator.launch {
                ClaylineWebView(
                    launch: launch,
                    actions: coordinator.webActions,
                    onReady: {
                        coordinator.webViewDidBecomeReady(enginePID: launch.readiness.pid)
                    },
                    onFailure: { message in
                        coordinator.webViewDidFail(
                            enginePID: launch.readiness.pid,
                            message: message
                        )
                    }
                )
                .id(launch.readiness.pid)
            }

            switch coordinator.status {
            case .idle, .startingEngine:
                StartupPanel(
                    title: "Starting Clayline",
                    detail: "Preparing the private local slicing engine…"
                )
            case .loadingInterface:
                StartupPanel(
                    title: "Opening the studio",
                    detail: "Verifying the private session and loading local assets…"
                )
            case .ready:
                EmptyView()
            case .failed(let message):
                FailurePanel(message: message, retry: coordinator.retry)
            }
        }
        .frame(minWidth: 1_100, minHeight: 700)
    }
}

private struct StartupPanel: View {
    let title: String
    let detail: String

    var body: some View {
        VStack(spacing: 18) {
            ClaylineMark()
                .frame(width: 76, height: 76)
            ProgressView()
                .controlSize(.small)
            VStack(spacing: 7) {
                Text(title)
                    .font(.system(size: 20, weight: .semibold, design: .rounded))
                Text(detail)
                    .font(.system(size: 12))
                    .foregroundStyle(.secondary)
            }
        }
        .padding(34)
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
        .overlay {
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .stroke(.black.opacity(0.08), lineWidth: 1)
        }
    }
}

private struct FailurePanel: View {
    let message: String
    let retry: () -> Void

    var body: some View {
        VStack(spacing: 18) {
            Image(systemName: "exclamationmark.triangle")
                .font(.system(size: 34, weight: .medium))
                .foregroundStyle(Color(red: 0.66, green: 0.31, blue: 0.20))
            VStack(spacing: 8) {
                Text("Clayline could not start")
                    .font(.system(size: 20, weight: .semibold, design: .rounded))
                Text(message)
                    .font(.system(size: 12))
                    .foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)
                    .frame(maxWidth: 420)
            }
            Button("Try Again", action: retry)
                .buttonStyle(.borderedProminent)
                .tint(Color(red: 0.66, green: 0.31, blue: 0.20))
                .keyboardShortcut(.defaultAction)
        }
        .padding(34)
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
        .overlay {
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .stroke(.black.opacity(0.08), lineWidth: 1)
        }
    }
}

private struct ClaylineMark: View {
    // The quatrefoil from the tile family: four coil rings overlapping into a
    // four-petal flower (same mark as the app icon and web header).
    var body: some View {
        GeometryReader { proxy in
            let side = min(proxy.size.width, proxy.size.height)
            let radius = side * 0.22
            let offset = side * 0.147
            let stroke = side * 0.064
            let center = CGPoint(x: proxy.size.width / 2, y: proxy.size.height / 2)
            ZStack {
                RoundedRectangle(cornerRadius: side * 0.21, style: .continuous)
                    .fill(Color(red: 0.933, green: 0.914, blue: 0.875))
                ForEach(0..<4, id: \.self) { corner in
                    let dx = corner % 2 == 0 ? -offset : offset
                    let dy = corner < 2 ? -offset : offset
                    Circle()
                        .stroke(Color(red: 0.66, green: 0.31, blue: 0.20), lineWidth: stroke)
                        .frame(width: radius * 2, height: radius * 2)
                        .position(x: center.x + dx, y: center.y + dy)
                }
            }
        }
    }
}
