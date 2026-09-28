import SwiftUI

struct DeviceView: View {
    @EnvironmentObject var store: LightingStore
    let deviceID: String
    @State private var brightness: Double = 75

    private var device: DeviceState? { store.devices.first { $0.id == deviceID } }

    var body: some View {
        Form {
            if let device {
                Section {
                    Toggle("Power", isOn: Binding(
                        get: { device.on },
                        set: { value in Task { await store.setPower(device, on: value) } }
                    ))
                }
                Section("Brightness") {
                    Slider(value: $brightness, in: 1...100, step: 1) { editing in
                        if !editing { Task { await store.setBrightness(device, value: Int(brightness)) } }
                    }
                    Text("\(Int(brightness))%")
                }
                Section("Quick Colors") {
                    HStack {
                        ColorDot(rgb: RGB(r: 255,g: 255,b: 255), device: device)
                        ColorDot(rgb: RGB(r: 255,g: 30,b: 30), device: device)
                        ColorDot(rgb: RGB(r: 30,g: 200,b: 70), device: device)
                        ColorDot(rgb: RGB(r: 255,g: 100,b: 0), device: device)
                        ColorDot(rgb: RGB(r: 120,g: 40,b: 210), device: device)
                    }
                }
            } else {
                ContentUnavailableView("Light unavailable", systemImage: "lightbulb.slash")
            }
        }
        .navigationTitle(device?.name ?? "Light")
        .onAppear { brightness = Double(device?.brightness ?? 75) }
    }
}

struct ColorDot: View {
    @EnvironmentObject var store: LightingStore
    let rgb: RGB
    let device: DeviceState

    var body: some View {
        Button {
            Task { await store.setColor(device, rgb: rgb) }
        } label: {
            Circle()
                .fill(Color(red: Double(rgb.r)/255, green: Double(rgb.g)/255, blue: Double(rgb.b)/255))
                .frame(width: 38, height: 38)
                .overlay(Circle().stroke(.secondary.opacity(0.3)))
        }
        .buttonStyle(.plain)
    }
}
