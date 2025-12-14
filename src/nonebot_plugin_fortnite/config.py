from pathlib import Path

import nonebot_plugin_localstore as store
from nonebot import get_plugin_config
from pydantic import BaseModel

_cache_dir: Path = store.get_plugin_cache_dir()
_data_dir: Path = store.get_plugin_data_dir()

CHINESE_FONT_PATH: Path = _data_dir / "SourceHanSansSC-Bold-2.otf"
GITHUB_RAW = "https://raw.githubusercontent.com/fllesser/nonebot-plugin-fortnite"


class Config(BaseModel):
    fortnite_api_key: str | None = None
    fortnite_screenshot_from_github: bool = False
    fortnite_github_proxy_url: str | None = None  # "https://gh-proxy.org"
    fortnite_github_token: str | None = None

    @property
    def api_key(self) -> str | None:
        return self.fortnite_api_key

    @property
    def screenshot_from_github(self) -> bool:
        return self.fortnite_screenshot_from_github

    @property
    def raw_base_url(self) -> str:
        if self.fortnite_github_proxy_url is None:
            return GITHUB_RAW

        proxy = self.fortnite_github_proxy_url.rstrip("/")
        return f"{proxy}/{GITHUB_RAW}"

    @property
    def cache_dir(self) -> Path:
        return _cache_dir

    @property
    def data_dir(self) -> Path:
        return _data_dir

    @property
    def chinese_font_path(self) -> Path:
        return CHINESE_FONT_PATH

    @property
    def github_token(self) -> str | None:
        return self.fortnite_github_token


fconfig: Config = get_plugin_config(Config)
