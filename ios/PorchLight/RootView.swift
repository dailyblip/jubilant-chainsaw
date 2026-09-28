import SwiftUI

struct RootView: View {
    var body: some View {
        TabView {
            NavigationStack { ScenesView() }
                .tabItem { Label("Scenes", systemImage: "sparkles") }
            NavigationStack { LightsView() }
                .tabItem { Label("Lights", systemImage: "lightbulb.2.fill") }
            NavigationStack { SettingsView() }
                .tabItem { Label("Settings", systemImage: "gearshape.fill") }
        }
    }
}
