from __future__ import annotations

import json
import ssl
from pathlib import Path
import httpx

ROOT = Path(__file__).resolve().parents[1]
ENV = ROOT / "backend" / ".env"


def read_env() -> dict[str, str]:
    data = {}
    if ENV.exists():
        for line in ENV.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            data[k.strip()] = v.strip()
    return data


def write_env(values: dict[str, str]) -> None:
    order = [
        "MOCK_MODE","APP_TOKEN","HUE_BRIDGE_IP","HUE_USERNAME",
        "GOVEE_API_KEY","GOVEE_DEVICE_ID","GOVEE_SKU",
        "HUE_A19_IDS","HUE_LILY_IDS"
    ]
    lines = []
    for key in order:
        lines.append(f"{key}={values.get(key, '')}")
    ENV.write_text("\n".join(lines) + "\n")


def choose_ids(prompt: str, valid_ids: set[str]) -> str:
    while True:
        value = input(prompt).strip()
        ids = [x.strip() for x in value.split(",") if x.strip()]
        if ids and all(x in valid_ids for x in ids):
            return ",".join(ids)
        print("Please enter valid comma-separated light IDs shown above.")


def main():
    env = read_env()
    env.setdefault("APP_TOKEN", "change-me")
    env.setdefault("GOVEE_SKU", "H6860")

    print("\nPorchLight Mac setup")
    print("====================")
    print("Finding your Hue Bridge...")

    bridge_ip = env.get("HUE_BRIDGE_IP", "")
    try:
        bridges = httpx.get("https://discovery.meethue.com/", timeout=10).json()
        if bridges:
            bridge_ip = bridges[0].get("internalipaddress") or bridge_ip
    except Exception:
        pass

    if not bridge_ip:
        bridge_ip = input("Enter your Hue Bridge IP address: ").strip()

    print(f"Found Hue Bridge at {bridge_ip}")
    input("\nPress the large round button on top of your Hue Bridge, then press RETURN here... ")

    with httpx.Client(verify=False, timeout=10) as client:
        r = client.post(f"https://{bridge_ip}/api", json={"devicetype":"porchlight#mac"})
        r.raise_for_status()
        result = r.json()

        if not result or "success" not in result[0]:
            print("\nHue pairing failed.")
            print(json.dumps(result, indent=2))
            print("Press the Hue Bridge button and run this setup again.")
            raise SystemExit(1)

        username = result[0]["success"]["username"]
        print("Hue Bridge paired successfully.")

        lights = client.get(f"https://{bridge_ip}/api/{username}/lights").json()

    print("\nHue lights found:")
    valid_ids = set()
    for light_id, info in lights.items():
        valid_ids.add(str(light_id))
        name = info.get("name", "Unnamed")
        product = info.get("productname") or info.get("modelid") or ""
        print(f"  {light_id}: {name}  {product}")

    print("\nEnter the IDs for your four A19 bulbs and four Lily uplights.")
    a19 = choose_ids("A19 IDs (example 1,2,3,4): ", valid_ids)
    lily = choose_ids("Lily IDs (example 5,6,7,8): ", valid_ids)

    env["HUE_BRIDGE_IP"] = bridge_ip
    env["HUE_USERNAME"] = username
    env["HUE_A19_IDS"] = a19
    env["HUE_LILY_IDS"] = lily
    env["MOCK_MODE"] = "false"

    print("\nGovee H6860 setup")
    print("You can skip this for now and test Hue first.")
    api_key = input("Paste your Govee API key, or press RETURN to skip: ").strip()

    if api_key:
        try:
            headers = {"Govee-API-Key": api_key}
            r = httpx.get("https://openapi.api.govee.com/router/api/v1/user/devices", headers=headers, timeout=10)
            r.raise_for_status()
            data = r.json()
            devices = data.get("data", [])
            matches = [d for d in devices if d.get("sku") == "H6860"]

            if not matches:
                print("No H6860 was returned by Govee. Hue setup will still work.")
            else:
                print("\nH6860 devices found:")
                for i, d in enumerate(matches, 1):
                    print(f"  {i}: {d.get('deviceName','H6860')}  {d.get('device')}")
                choice = 1
                if len(matches) > 1:
                    choice = int(input("Choose device number: ").strip())
                d = matches[choice - 1]
                env["GOVEE_API_KEY"] = api_key
                env["GOVEE_DEVICE_ID"] = d["device"]
                env["GOVEE_SKU"] = d["sku"]
                print("Govee H6860 connected.")
        except Exception as e:
            print(f"Govee setup failed: {e}")
            print("Hue setup will still work. We can add Govee later.")

    write_env(env)
    print("\nConfiguration saved.")
    print("PorchLight is ready to start on this Mac.")


if __name__ == "__main__":
    main()
