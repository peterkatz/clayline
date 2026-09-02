// swift-tools-version: 6.0

import PackageDescription

let package = Package(
    name: "ClaylineMac",
    platforms: [
        .macOS(.v14)
    ],
    products: [
        .executable(name: "Clayline", targets: ["Clayline"])
    ],
    targets: [
        .executableTarget(name: "Clayline"),
        .testTarget(
            name: "ClaylineTests",
            dependencies: ["Clayline"]
        )
    ],
    swiftLanguageModes: [.v5]
)
