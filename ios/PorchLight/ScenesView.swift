import SwiftUI

struct ScenesView: View {
    @EnvironmentObject var store: LightingStore
    private let columns = [GridItem(.flexible()), GridItem(.flexible())]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Front Porch").font(.largeTitle.bold())
                    Text("Hue + Govee").foregroundStyle(.secondary)
                }

                Button {
                    Task { await store.activate(.normal) }
                } label: {
                    HStack {
                        Image(systemName: "house.fill").font(.title2)
                        VStack(alignment: .leading) {
                            Text("Normal").font(.headline)
                            Text("A19s on · Lilys off · C9 off").font(.caption)
                        }
                        Spacer()
                        if store.currentMode == LightingScene.normal.rawValue { Image(systemName: "checkmark.circle.fill") }
                    }
                    .padding()
                    .frame(maxWidth: .infinity)
                    .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 18))
                }
                .buttonStyle(.plain)

                LazyVGrid(columns: columns, spacing: 12) {
                    ForEach([LightingScene.christmas, .halloween, .warmWhite, .newYears, .c9Off, .allOff]) { scene in
                        SceneButton(scene: scene)
                    }
                }

                if let message = store.errorMessage {
                    Text(message).font(.footnote).foregroundStyle(.red)
                }
            }
            .padding()
        }
        .navigationTitle("PorchLight")
        .refreshable { await store.refresh() }
        .overlay { if store.isBusy { ProgressView().controlSize(.large) } }
    }
}

struct SceneButton: View {
    @EnvironmentObject var store: LightingStore
    let scene: LightingScene

    var body: some View {
        Button {
            Task { await store.activate(scene) }
        } label: {
            VStack(alignment: .leading, spacing: 16) {
                HStack {
                    Image(systemName: scene.symbol).font(.title2)
                    Spacer()
                    if store.currentMode == scene.rawValue { Image(systemName: "checkmark.circle.fill") }
                }
                Text(scene.title).font(.headline)
                Text(subtitle).font(.caption).foregroundStyle(.secondary).lineLimit(2)
            }
            .padding()
            .frame(maxWidth: .infinity, minHeight: 128, alignment: .leading)
            .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 18))
        }
        .buttonStyle(.plain)
    }

    private var subtitle: String {
        switch scene {
        case .christmas: return "Holiday red + green"
        case .halloween: return "Orange + purple"
        case .warmWhite: return "Soft warm porch"
        case .newYears: return "Gold + white"
        case .allOff: return "Everything off"
        case .c9Off: return "Keep Hue unchanged"
        case .normal: return "Everyday lighting"
        }
    }
}
