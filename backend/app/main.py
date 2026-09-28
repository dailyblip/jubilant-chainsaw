from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .controllers import HueController, GoveeController
from .models import DeviceState, LightCommand, RGB, SceneRequest, SystemState
from .scenes import apply_scene

app = FastAPI(title="PorchLight Controller", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

hue = HueController()
govee = GoveeController()
_current_mode = "normal"

ROOT = Path(__file__).resolve().parents[2]
WEB_DIR = ROOT / "web"


def auth(authorization: str | None):
    if settings.app_token == "change-me":
        return
    expected = f"Bearer {settings.app_token}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/health")
async def health():
    return {"ok": True, "mock_mode": settings.mock_mode, "version": app.version}


@app.get("/api/state", response_model=SystemState)
async def state(authorization: str | None = Header(default=None)):
    auth(authorization)
    devices: list[DeviceState] = []
    if settings.mock_mode:
        for i in range(1, 5):
            devices.append(DeviceState(id=f"a19-{i}", name=f"A19 {i}", family="hue_a19", on=True, brightness=75, kelvin=2700))
        for i in range(1, 5):
            devices.append(DeviceState(id=f"lily-{i}", name=f"Lily {i}", family="hue_lily", on=False, brightness=75, color=RGB(r=255,g=255,b=255)))
        devices.append(DeviceState(id="c9-front", name="Front Porch C9", family="govee_c9", on=False, brightness=100, color=RGB(r=255,g=255,b=255)))
    else:
        lights = await hue.list_lights()
        for light_id, light in lights.items():
            family = "hue_a19" if light_id in settings.a19_ids else "hue_lily"
            state_obj = light.get("state", {})
            devices.append(DeviceState(
                id=f"hue-{light_id}",
                name=light.get("name", f"Hue {light_id}"),
                family=family,
                on=state_obj.get("on", False),
                brightness=max(1, round(state_obj.get("bri", 254) / 2.54)),
            ))
        devices.append(DeviceState(id="c9-front", name="Front Porch C9", family="govee_c9", on=True, brightness=100))
    return SystemState(mode=_current_mode, devices=devices)


@app.post("/api/scenes")
async def scene(req: SceneRequest, authorization: str | None = Header(default=None)):
    global _current_mode
    auth(authorization)
    await apply_scene(req.scene)
    _current_mode = req.scene
    return {"ok": True, "mode": _current_mode}


@app.post("/api/devices/{device_id}")
async def control_device(device_id: str, cmd: LightCommand, authorization: str | None = Header(default=None)):
    auth(authorization)
    if device_id.startswith("a19-"):
        idx = int(device_id.split("-")[1]) - 1
        if idx < 0 or idx >= len(settings.a19_ids):
            if settings.mock_mode:
                return {"ok": True}
            raise HTTPException(404, "Unknown A19")
        await hue.set_light(settings.a19_ids[idx], cmd)
    elif device_id.startswith("lily-"):
        idx = int(device_id.split("-")[1]) - 1
        if idx < 0 or idx >= len(settings.lily_ids):
            if settings.mock_mode:
                return {"ok": True}
            raise HTTPException(404, "Unknown Lily")
        await hue.set_light(settings.lily_ids[idx], cmd)
    elif device_id == "c9-front":
        await govee.set(cmd)
    else:
        raise HTTPException(404, "Unknown device")
    return {"ok": True}


@app.get("/api/govee/discover")
async def govee_discover(authorization: str | None = Header(default=None)):
    auth(authorization)
    return await govee.discover()


@app.get("/")
async def web_index():
    return FileResponse(WEB_DIR / "index.html")


if WEB_DIR.exists():
    app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
