import SwiftUI

@main
struct PorchLightApp: App {
    @StateObject private var store = LightingStore()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(store)
                .task { await store.refresh() }
        }
    }
}
