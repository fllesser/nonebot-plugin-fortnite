from nonebot import (
    require,
    get_driver, # @get_driver().on_startup 装饰启动时运行函数
    get_bots    # dict[str, BaseBot]
)
from nonebot.log import logger
from nonebot.plugin import PluginMetadata

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

from .config import Config
from .matcher import *
from .pve import screenshot_vb_img

__plugin_meta__ = PluginMetadata(
    name="堡垒之夜游戏插件",
    description="堡垒之夜战绩，季卡，商城，vb图查询",
    usage="季卡/生涯季卡/战绩/生涯战绩/商城/vb图",
    type="application",
    config=Config,
    homepage="https://github.com/fllesser/nonebot-plugin-fortnite",
    supported_adapters={ "~onebot.v11" }
)


@scheduler.scheduled_job(
    "cron",
    id = 'fortnite_pve_vb'
    hour = 8,
    minute = 10,
)
async def _():
    await screenshot_vb_img()