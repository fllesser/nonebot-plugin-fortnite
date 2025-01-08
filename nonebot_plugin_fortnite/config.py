from pydantic import BaseModel
from typing import Optinal
from nonebot import get_plugin_config

class Config(BaseModel):
    fortnite_api_key: Optinal[str]
    
fconfig: Config = get_plugin_config(Config)
