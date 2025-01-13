from nonebot import (
    require,
    get_driver, # @get_driver().on_startup 装饰启动时运行函数
    get_bots   # dict[str, BaseBot]
)
from nonebot.log import logger
from nonebot.plugin import PluginMetadata
from nonebot.plugin.load import inherit_supported_adapters

require("nonebot_plugin_uninfo")
require("nonebot_plugin_alconna")
require("nonebot_plugin_apscheduler")
require("nonebot_plugin_localstore")
from nonebot_plugin_apscheduler import scheduler

from .config import Config
from .matcher import *
from .pve import screenshot_vb_img
from .shop import screenshot_shop_img

__plugin_meta__ = PluginMetadata(
    name="堡垒之夜游戏插件",
    description="堡垒之夜战绩，季卡，商城，vb图查询",
    usage="季卡/生涯季卡/战绩/生涯战绩/商城/vb图",
    type="application",
    config=Config,
    homepage="https://github.com/fllesser/nonebot-plugin-fortnite",
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna", "nonebot_plugin_uninfo")
)


@scheduler.scheduled_job(
    "cron",
    id = 'fortnite',
    hour = 8,
    minute = 5,
)
async def _():
    try:
        await screenshot_shop_img()
    except Exception as e:
        logger.warning(f'商城更新失败: {e}')
    try:
        await screenshot_vb_img()
    except Exception:
        logger.warning(f'vb图更新失败: {e}')