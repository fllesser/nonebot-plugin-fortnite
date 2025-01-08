from pydantic import BaseModel
from typing import Optional
from nonebot import get_plugin_config

# from pathlib import Path
# require("nonebot_plugin_localstore")
# import nonebot_plugin_localstore as store


class Config(BaseModel):
    fortnite_api_key: Optional[str] = ""
    
fconfig: Config = get_plugin_config(Config)

# cache_dir: Path = store.get_plugin_cache_dir()