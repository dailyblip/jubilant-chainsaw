# Raspberry Pi hardware setup

This file is for the day the Pi arrives.

## Recommended initial Pi settings

- Raspberry Pi OS Lite 64-bit
- Hostname: `porchlight`
- Wi-Fi or Ethernet on the same LAN as the Hue Bridge and Govee H6860
- SSH enabled during Raspberry Pi Imager setup

## Install PorchLight

Copy this project folder to the Pi, enter the `pi` directory, then run:

```bash
sudo bash install.sh
```

The service will start in mock mode at:

`http://porchlight.local:8787/health`

## Pair Hue

1. Find the Hue Bridge IP in the Hue app or router.
2. Press the physical button on top of the Hue Bridge.
3. Within about 30 seconds, create a local API username with:

```bash
curl -k -X POST "https://BRIDGE_IP/api" \
  -H 'Content-Type: application/json' \
  -d '{"devicetype":"porchlight#raspberrypi"}'
```

4. Save the returned username in `/opt/porchlight/backend/.env` as `HUE_USERNAME` and the bridge IP as `HUE_BRIDGE_IP`.
5. List the Hue lights:

```bash
curl -k "https://BRIDGE_IP/api/HUE_USERNAME/lights"
```

6. Put the four A19 numeric IDs in `HUE_A19_IDS` and the four Lily numeric IDs in `HUE_LILY_IDS`.

## Connect Govee H6860

Create a Govee developer API key, then set:

- `GOVEE_API_KEY`
- `GOVEE_DEVICE_ID`
- `GOVEE_SKU=H6860`

Once connected, call:

```bash
curl -H "Authorization: Bearer YOUR_APP_TOKEN" \
  http://porchlight.local:8787/api/govee/discover
```

That response is what we use to map the H6860's real dynamic scenes/effects.

## Go live

In `.env`:

```text
MOCK_MODE=false
APP_TOKEN=<long-random-secret>
```

Restart:

```bash
sudo systemctl restart porchlight
```

## Remote access

Recommended: install Tailscale on both the Raspberry Pi and iPhone. Then use the Pi's Tailscale address/hostname in the app. This avoids exposing port 8787 to the public internet.
