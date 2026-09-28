from __future__ import annotations

from .config import settings
from .controllers import HueController, GoveeController
from .models import LightCommand, RGB, SceneName

hue = HueController()
govee = GoveeController()

SCENES: dict[SceneName, dict] = {
    "christmas": {
        "a19": LightCommand(on=True, brightness=65, color=RGB(r=220, g=35, b=35)),
        "lily": LightCommand(on=True, brightness=75, color=RGB(r=20, g=170, b=55)),
        "c9": LightCommand(on=True, brightness=100, color=RGB(r=220, g=35, b=35)),
    },
    "halloween": {
        "a19": LightCommand(on=True, brightness=55, color=RGB(r=255, g=80, b=0)),
        "lily": LightCommand(on=True, brightness=70, color=RGB(r=125, g=35, b=190)),
        "c9": LightCommand(on=True, brightness=100, color=RGB(r=255, g=80, b=0)),
    },
    "warm_white": {
        "a19": LightCommand(on=True, brightness=75, kelvin=2700),
        "lily": LightCommand(on=True, brightness=45, kelvin=2700),
        "c9": LightCommand(on=True, brightness=55, kelvin=2700),
    },
    "new_years": {
        "a19": LightCommand(on=True, brightness=80, kelvin=3000),
        "lily": LightCommand(on=True, brightness=80, color=RGB(r=255, g=195, b=35)),
        "c9": LightCommand(on=True, brightness=100, color=RGB(r=255, g=225, b=120)),
    },
    "all_off": {
        "a19": LightCommand(on=False),
        "lily": LightCommand(on=False),
        "c9": LightCommand(on=False),
    },
    "c9_off": {
        "a19": None,
        "lily": None,
        "c9": LightCommand(on=False),
    },
    "normal": {
        "a19": LightCommand(on=True, brightness=75, kelvin=2700),
        "lily": LightCommand(on=False),
        "c9": LightCommand(on=False),
    },
}


async def apply_scene(name: SceneName) -> None:
    scene = SCENES[name]
    if scene["a19"]:
        await hue.set_many(settings.a19_ids, scene["a19"])
    if scene["lily"]:
        await hue.set_many(settings.lily_ids, scene["lily"])
    if scene["c9"]:
        await govee.set(scene["c9"])
