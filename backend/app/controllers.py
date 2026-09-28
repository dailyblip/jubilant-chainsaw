from __future__ import annotations

import colorsys
import httpx
from dataclasses import dataclass
from .config import settings
from .models import LightCommand, RGB


def rgb_to_hue(rgb: RGB) -> tuple[int, int]:
    r, g, b = rgb.r / 255.0, rgb.g / 255.0, rgb.b / 255.0
    h, s, _ = colorsys.rgb_to_hsv(r, g, b)
    return int(h * 65535), int(s * 254)


def kelvin_to_mired(k: int) -> int:
    return max(153, min(500, int(1_000_000 / k)))


@dataclass
class HueController:
    async def list_lights(self) -> dict:
        if settings.mock_mode:
            lights = {}
            for idx in range(1, 5):
                lights[str(idx)] = {"name": f"A19 {idx}", "state": {"on": True, "bri": 204}}
            for idx in range(5, 9):
                lights[str(idx)] = {"name": f"Lily {idx-4}", "state": {"on": False, "bri": 204}}
            return lights
        url = f"https://{settings.hue_bridge_ip}/api/{settings.hue_username}/lights"
        async with httpx.AsyncClient(verify=False, timeout=5) as client:
            r = await client.get(url)
            r.raise_for_status()
            return r.json()

    async def set_light(self, light_id: str, cmd: LightCommand) -> None:
        if settings.mock_mode:
            return
        payload: dict = {}
        if cmd.on is not None:
            payload["on"] = cmd.on
        if cmd.brightness is not None:
            payload["bri"] = max(1, min(254, round(cmd.brightness * 2.54)))
        if cmd.color is not None:
            hue, sat = rgb_to_hue(cmd.color)
            payload.update({"hue": hue, "sat": sat})
        if cmd.kelvin is not None:
            payload["ct"] = kelvin_to_mired(cmd.kelvin)
        url = f"https://{settings.hue_bridge_ip}/api/{settings.hue_username}/lights/{light_id}/state"
        async with httpx.AsyncClient(verify=False, timeout=5) as client:
            r = await client.put(url, json=payload)
            r.raise_for_status()

    async def set_many(self, ids: list[str], cmd: LightCommand) -> None:
        for light_id in ids:
            await self.set_light(light_id, cmd)


@dataclass
class GoveeController:
    base_url: str = "https://openapi.api.govee.com/router/api/v1"

    async def _control(self, capability_type: str, instance: str, value) -> None:
        if settings.mock_mode:
            return
        payload = {
            "requestId": "porchlight-v1",
            "payload": {
                "sku": settings.govee_sku,
                "device": settings.govee_device_id,
                "capability": {
                    "type": capability_type,
                    "instance": instance,
                    "value": value,
                },
            },
        }
        headers = {"Govee-API-Key": settings.govee_api_key}
        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.post(f"{self.base_url}/device/control", headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            if data.get("code") not in (None, 200):
                raise RuntimeError(f"Govee error: {data}")

    async def set(self, cmd: LightCommand) -> None:
        if cmd.on is not None:
            await self._control("devices.capabilities.on_off", "powerSwitch", 1 if cmd.on else 0)
        if cmd.brightness is not None:
            await self._control("devices.capabilities.range", "brightness", cmd.brightness)
        if cmd.color is not None:
            rgb = (cmd.color.r << 16) | (cmd.color.g << 8) | cmd.color.b
            await self._control("devices.capabilities.color_setting", "colorRgb", rgb)
        if cmd.kelvin is not None:
            await self._control("devices.capabilities.color_setting", "colorTemperatureK", cmd.kelvin)

    async def discover(self) -> dict:
        if settings.mock_mode:
            return {"sku": "H6860", "device": "MOCK-C9", "name": "Front Porch C9"}
        headers = {"Govee-API-Key": settings.govee_api_key}
        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.get(f"{self.base_url}/user/devices", headers=headers)
            r.raise_for_status()
            return r.json()
