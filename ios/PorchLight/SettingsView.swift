import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var store: LightingStore

    var body: some View {
        Form {
            Section("Controller") {
                TextField("http://porchlight.local:8787", text: $store.serverAddress)
                    .textInputAutocapitalization(.never)
                    .autocorrectionDisabled()
                SecureField("Access token", text: $store.token)
                Button("Test Connection") { Task { await store.refresh() } }
            }
            Section("Hardware") {
                LabeledContent("Hue", value: "4 A19 + 4 Lily")
                LabeledContent("Govee", value: "H6860 C9 × 1")
                Text("Additional C9 strings can be added later without changing the app layout.")
                    .font(.footnote).foregroundStyle(.secondary)
            }
            Section("Remote Access") {
                Text("V1 is designed to work locally with porchlight.local. For away-from-home control, point this address at the Pi through a private VPN such as Tailscale rather than exposing the Pi directly to the internet.")
                    .font(.footnote)
            }
        }
        .navigationTitle("Settings")
    }
}
