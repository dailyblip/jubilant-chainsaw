import Foundation

struct APIClient {
    var baseURL: URL
    var token: String

    private func request(path: String, method: String = "GET", body: Data? = nil) throws -> URLRequest {
        guard let url = URL(string: path, relativeTo: baseURL) else { throw URLError(.badURL) }
        var req = URLRequest(url: url)
        req.httpMethod = method
        req.timeoutInterval = 8
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        if !token.isEmpty { req.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization") }
        req.httpBody = body
        return req
    }

    func state() async throws -> SystemState {
        let (data, response) = try await URLSession.shared.data(for: request(path: "/api/state"))
        try validate(response)
        return try JSONDecoder().decode(SystemState.self, from: data)
    }

    func activate(_ scene: LightingScene) async throws {
        let payload = try JSONSerialization.data(withJSONObject: ["scene": scene.rawValue])
        let (_, response) = try await URLSession.shared.data(for: request(path: "/api/scenes", method: "POST", body: payload))
        try validate(response)
    }

    func control(deviceID: String, command: LightCommand) async throws {
        let encoder = JSONEncoder()
        let body = try encoder.encode(command)
        let (_, response) = try await URLSession.shared.data(for: request(path: "/api/devices/\(deviceID)", method: "POST", body: body))
        try validate(response)
    }

    private func validate(_ response: URLResponse) throws {
        guard let http = response as? HTTPURLResponse, (200..<300).contains(http.statusCode) else {
            throw URLError(.badServerResponse)
        }
    }
}
