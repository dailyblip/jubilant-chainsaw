import SwiftUI

struct LightsView: View {
    @EnvironmentObject var store: LightingStore

    var body: some View {
        List {
            lightSection("A19 Bulbs", family: "hue_a19")
            lightSection("Lily Uplights", family: "hue_lily")
            lightSection("C9 Strings", family: "govee_c9")
        }
        .navigationTitle("Lights")
        .refreshable { await store.refresh() }
    }

    @ViewBuilder
    private func lightSection(_ title: String, family: String) -> some View {
        Section(title) {
            ForEach(store.devices.filter { $0.family == family }) { device in
                NavigationLink {
                    DeviceView(deviceID: device.id)
                } label: {
                    HStack {
                        Image(systemName: family == "govee_c9" ? "lightswitch.on" : "lightbulb.fill")
                        VStack(alignment: .leading) {
                            Text(device.name)
                            Text(device.on ? "On · \(device.brightness)%" : "Off")
                                .font(.caption).foregroundStyle(.secondary)
                        }
                    }
                }
            }
        }
    }
}
