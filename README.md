# PorchLight V1

A unified front-porch lighting controller for:

- Philips Hue Bridge
- 4 Hue A19 bulbs
- 4 Hue Lily uplights
- 1 Govee H6860 C9 string (architecture supports more later)
- iPhone control on home Wi-Fi and, later, private remote access

## What is implemented

### iPhone app
SwiftUI app with three tabs:

- **Scenes**: Christmas, Halloween, Warm White, New Year's, All Off, C9 Off, Normal
- **Lights**: each A19, Lily, and C9 device can be controlled individually
- **Settings**: controller address and access token

**Normal** is intentionally defined as:
- A19 bulbs ON, warm white, 75%
- Lily uplights OFF
- C9 OFF

### Raspberry Pi controller
FastAPI service intended to run continuously on the Pi.

It exposes a tiny API to the iPhone and translates commands into:
- Hue local Bridge API commands
- Govee OpenAPI commands for H6860

It starts in **mock mode**, so the iPhone UI can be developed/tested before the Pi and real lights are paired.

## Current Govee behavior

V1 supports power, brightness, RGB color, and color temperature through Govee's official API. The H6860's exact available dynamic-scene/effect values are deliberately **not hard-coded**. When the real device is connected, `/api/govee/discover` can be used to inspect its advertised capabilities; then Christmas/Halloween/New Year's can be upgraded from color fallbacks to actual moving C9 effects.

## Run the controller on a Mac now (mock mode)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
./run.sh
```

Then the API is at `http://localhost:8787`.

## Run tests

```bash
cd backend
PYTHONPATH=. pytest -q
```

## Open the iPhone app

Open `ios/PorchLight.xcodeproj` in Xcode 16 or later. Set your Apple development team and choose an iPhone simulator/device.

For simulator testing against a controller running on the same Mac, change the app's controller address to `http://127.0.0.1:8787`.

For a real iPhone and Raspberry Pi later, the intended local address is `http://porchlight.local:8787`.

## Hardware hookup stage

When the Raspberry Pi arrives:

1. Install Raspberry Pi OS Lite.
2. Give it the hostname `porchlight`.
3. Install Python 3 and this backend.
4. Pair the Hue Bridge by pressing the physical bridge button, then create a Hue API username.
5. Put the Hue IDs for the 4 A19s and 4 Lilys into `.env`.
6. Create/use a Govee developer API key and add the H6860 device ID.
7. Set `MOCK_MODE=false`.
8. Set a long random `APP_TOKEN`, then enter the same token in the iPhone app.

## Remote access

Do not port-forward the Pi directly to the public internet. V1 is designed to use a private overlay VPN such as Tailscale for remote access. Once installed on the Pi and iPhone, use the Pi's private Tailscale hostname/address in the app Settings screen.

## Next hardware-specific step

Once the real H6860 is connected, inspect its returned `dynamic_scene` capabilities. That tells us exactly which moving effects Govee permits on this model. We can then map your holiday buttons to genuine animations rather than inventing undocumented effect IDs.
