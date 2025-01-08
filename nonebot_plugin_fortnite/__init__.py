from nonebot import (
    require,
    get_driver, # @get_driver().on_startup 装饰启动时运行函数
    get_bots    # dict[str, BaseBot]
)
from nonebot.log import logger
from nonebot.plugin import PluginMetadata

require("nonebot_plugin_localstore")
import nonebot_plugin_localstore as store

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="堡垒之夜游戏插件",
    description="堡垒之夜战绩，季卡，商城，vb图查询",
    usage="略",
    type="application",
    config=Config,
    homepage="https://github.com/fllesser/nonebot-plugin-fortnite",
    supported_adapters={ "~onebot.v11" }
)

