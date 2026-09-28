import Foundation

@MainActor
final class LightingStore: ObservableObject {
    @Published var devices: [DeviceState] = []
    @Published var currentMode = "normal"
    @Published var isBusy = false
    @Published var errorMessage: String?

    @Published var serverAddress: String {
        didSet { UserDefaults.standard.set(serverAddress, forKey: "serverAddress") }
    }
    @Published var token: String {
        didSet { Keychain.save(token, service: "PorchLight", account: "controllerToken") }
    }

    init() {
        serverAddress = UserDefaults.standard.string(forKey: "serverAddress") ?? "http://porchlight.local:8787"
        token = Keychain.read(service: "PorchLight", account: "controllerToken")
    }

    private var client: APIClient? {
        let normalized = serverAddress.hasSuffix("/") ? String(serverAddress.dropLast()) : serverAddress
        guard let url = URL(string: normalized + "/") else { return nil }
        return APIClient(baseURL: url, token: token)
    }

    func refresh() async {
        guard let client else { return }
        do {
            let state = try await client.state()
            devices = state.devices
            currentMode = state.mode
            errorMessage = nil
        } catch {
            errorMessage = "Cannot reach the porch controller."
        }
    }

    func activate(_ scene: LightingScene) async {
        guard let client else { return }
        isBusy = true
        defer { isBusy = false }
        do {
            try await client.activate(scene)
            currentMode = scene.rawValue
            errorMessage = nil
            await refresh()
        } catch {
            errorMessage = "Scene command failed."
        }
    }

    func setPower(_ device: DeviceState, on: Bool) async {
        guard let client else { return }
        do {
            try await client.control(deviceID: device.id, command: LightCommand(on: on, brightness: nil, color: nil, kelvin: nil))
            await refresh()
        } catch { errorMessage = "Light command failed." }
    }

    func setBrightness(_ device: DeviceState, value: Int) async {
        guard let client else { return }
        do {
            try await client.control(deviceID: device.id, command: LightCommand(on: true, brightness: value, color: nil, kelvin: nil))
            await refresh()
        } catch { errorMessage = "Brightness command failed." }
    }

    func setColor(_ device: DeviceState, rgb: RGB) async {
        guard let client else { return }
        do {
            try await client.control(deviceID: device.id, command: LightCommand(on: true, brightness: nil, color: rgb, kelvin: nil))
            await refresh()
        } catch { errorMessage = "Color command failed." }
    }
}
