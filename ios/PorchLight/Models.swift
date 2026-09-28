import Foundation

struct RGB: Codable, Hashable {
    var r: Int
    var g: Int
    var b: Int
}

struct DeviceState: Codable, Identifiable, Hashable {
    var id: String
    var name: String
    var family: String
    var on: Bool
    var brightness: Int
    var color: RGB?
    var kelvin: Int?
}

struct SystemState: Codable {
    var mode: String
    var devices: [DeviceState]
}

struct LightCommand: Codable {
    var on: Bool?
    var brightness: Int?
    var color: RGB?
    var kelvin: Int?
}

enum LightingScene: String, CaseIterable, Identifiable {
    case christmas
    case halloween
    case warmWhite = "warm_white"
    case newYears = "new_years"
    case allOff = "all_off"
    case c9Off = "c9_off"
    case normal

    var id: String { rawValue }

    var title: String {
        switch self {
        case .christmas: return "Christmas"
        case .halloween: return "Halloween"
        case .warmWhite: return "Warm White"
        case .newYears: return "New Year's"
        case .allOff: return "All Off"
        case .c9Off: return "C9 Off"
        case .normal: return "Normal"
        }
    }

    var symbol: String {
        switch self {
        case .christmas: return "gift.fill"
        case .halloween: return "moon.stars.fill"
        case .warmWhite: return "sun.max.fill"
        case .newYears: return "sparkles"
        case .allOff: return "power"
        case .c9Off: return "lightbulb.slash.fill"
        case .normal: return "house.fill"
        }
    }
}
