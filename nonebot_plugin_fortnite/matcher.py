from nonebot.log import logger
from nonebot.rule import Rule

require("nonebot_plugin_alconna")
from nonebot_plugin_alconna import on_alconna
from .rank import (
    get_level,
    get_stats_image
)

from arclet.alconna import (
    Alconna,
    Args,
    Subcommand, 
    Option
)

alc = Alconna(
    "季卡",
    Args["name", str]
)




