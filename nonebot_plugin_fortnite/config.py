from pydantic import BaseModel
from typing import Optional
from nonebot import get_plugin_config

class Config(BaseModel):
    fortnite_api_key: Optional[str]
    
fconfig: Config = get_plugin_config(Config)
