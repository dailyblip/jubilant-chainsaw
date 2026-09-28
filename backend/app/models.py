from pydantic import BaseModel, Field
from typing import Literal


SceneName = Literal[
    "christmas",
    "halloween",
    "warm_white",
    "new_years",
    "all_off",
    "c9_off",
    "normal",
]


class RGB(BaseModel):
    r: int = Field(ge=0, le=255)
    g: int = Field(ge=0, le=255)
    b: int = Field(ge=0, le=255)


class LightCommand(BaseModel):
    on: bool | None = None
    brightness: int | None = Field(default=None, ge=1, le=100)
    color: RGB | None = None
    kelvin: int | None = Field(default=None, ge=2000, le=6500)


class SceneRequest(BaseModel):
    scene: SceneName


class DeviceState(BaseModel):
    id: str
    name: str
    family: Literal["hue_a19", "hue_lily", "govee_c9"]
    on: bool
    brightness: int = 100
    color: RGB | None = None
    kelvin: int | None = None


class SystemState(BaseModel):
    mode: str
    devices: list[DeviceState]
