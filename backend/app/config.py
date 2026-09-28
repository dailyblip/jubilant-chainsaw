from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mock_mode: bool = True
    app_token: str = "change-me"

    hue_bridge_ip: str = ""
    hue_username: str = ""

    govee_api_key: str = ""
    govee_device_id: str = ""
    govee_sku: str = "H6860"

    hue_a19_ids: str = ""
    hue_lily_ids: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def a19_ids(self) -> list[str]:
        return [x.strip() for x in self.hue_a19_ids.split(",") if x.strip()]

    @property
    def lily_ids(self) -> list[str]:
        return [x.strip() for x in self.hue_lily_ids.split(",") if x.strip()]


settings = Settings()
