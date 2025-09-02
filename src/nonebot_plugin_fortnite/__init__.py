from nonebot import get_driver, require
from nonebot.log import logger
from nonebot.plugin import PluginMetadata
from nonebot.plugin.load import inherit_supported_adapters

require("nonebot_plugin_uninfo")
require("nonebot_plugin_alconna")
require("nonebot_plugin_apscheduler")
require("nonebot_plugin_localstore")
require("nonebot_plugin_htmlrender")
from nonebot_plugin_apscheduler import scheduler

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="堡垒之夜游戏插件",
    description="堡垒之夜战绩，季卡，商城，vb图查询",
    usage="季卡/生涯季卡/战绩/生涯战绩/商城/vb图",
    type="application",
    config=Config,
    homepage="https://github.com/fllesser/nonebot-plugin-fortnite",
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna", "nonebot_plugin_uninfo"),
)

from .pve import screenshot_vb_img, vb_file
from .shop import screenshot_shop_img, shop_file
from .stats import get_level, get_stats_image


@get_driver().on_startup
async def check_font_file():
    from pathlib import Path

    from .config import CHINESE_FONT_PATH, GG_FONT_PATH, VB_FONT_PATH

    async def dwonload_font(path: Path):
        import aiofiles
        import httpx

        url_base = "https://raw.githubusercontent.com/fllesser/nonebot-plugin-fortnite/master/fonts/"
        url = url_base + path.name
        logger.info(f"字体文件 {path.name} 不存在，开始从 {url} 下载字体...")
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.get(url)
            response.raise_for_status()
            font_data = response.content

            async with aiofiles.open(path, "wb") as f:
                await f.write(font_data)

            logger.success(f"字体 {path.name} 下载成功，文件大小: {path.stat().st_size / 1024 / 1024:.2f} MB")
        except Exception:
            logger.exception("字体下载失败")
            logger.warning(f"请前往仓库下载字体到 {path}")

    if not CHINESE_FONT_PATH.exists():
        await dwonload_font(CHINESE_FONT_PATH)
    if not GG_FONT_PATH.exists():
        await dwonload_font(GG_FONT_PATH)
    if not VB_FONT_PATH.exists():
        await dwonload_font(VB_FONT_PATH)


@scheduler.scheduled_job(
    "cron",
    id="fortnite",
    hour=8,
    minute=5,
    misfire_grace_time=300,
)
async def _():
    logger.info("开始更新商城/VB图...")
    try:
        await screenshot_shop_img()
        logger.success(f"商城更新成功，文件大小: {shop_file.stat().st_size / 1024 / 1024:.2f} MB")
    except Exception as e:
        logger.warning(f"商城更新失败: {e}")
    try:
        await screenshot_vb_img()
        logger.success(f"vb图更新成功，文件大小: {vb_file.stat().st_size / 1024 / 1024:.2f} MB")
    except Exception as e:
        logger.warning(f"vb图更新失败: {e}")


import re

from arclet.alconna import Alconna, Args, Arparma
from nonebot import on_startswith
from nonebot.permission import SUPERUSER
from nonebot_plugin_alconna import AlconnaMatcher, Match, on_alconna
from nonebot_plugin_alconna.uniseg import Image, Text, UniMessage
from nonebot_plugin_uninfo import Uninfo

timewindow_prefix = ["生涯", ""]
name_args = Args["name?", str]


battle_pass_alc = on_alconna(Alconna(timewindow_prefix, "季卡", name_args))
stats_alc = on_alconna(Alconna(timewindow_prefix, "战绩", name_args))


@battle_pass_alc.handle()
@stats_alc.handle()
async def _(matcher: AlconnaMatcher, session: Uninfo, name: Match[str]):
    if name.available:
        matcher.set_path_arg("name", name.result)
        return
    # 获取群昵称
    if not session.member or not session.member.nick:
        return
    pattern = r"(?:id:|id\s)(.+)"
    if matched := re.match(pattern, session.member.nick, re.IGNORECASE):
        matcher.set_path_arg("name", matched.group(1))


name_prompt = UniMessage.template(
    "{:At(user, $event.get_user_id())} 请发送游戏名称\n群昵称设置如下可快速查询:\n    id:name\n    ID name"
)


@battle_pass_alc.got_path("name", prompt=name_prompt)
async def _(arp: Arparma, name: str):
    header: str = arp.header_match.result
    receipt = await UniMessage.text(f"正在查询 {name} 的{header}，请稍后...").send()
    level_info = await get_level(name, header)
    await UniMessage(Text(level_info)).send()
    await receipt.recall(delay=1)


@stats_alc.got_path("name", prompt=name_prompt)
async def _(arp: Arparma, name: str):
    header: str = arp.header_match.result
    receipt = await UniMessage.text(f"正在查询 {name} 的{header}，请稍后...").send()
    try:
        res = await get_stats_image(name, header)
    except Exception as e:
        await UniMessage(Text(f"查询失败 | {e}")).finish()
    await UniMessage(Image(path=res)).send()
    await receipt.recall(delay=1)


shop_matcher = on_startswith("商城")


@shop_matcher.handle()
async def _():
    if not shop_file.exists():
        logger.info("商城图不存在, 开始更新商城...")
        try:
            await screenshot_shop_img()
            logger.success(f"商城更新成功，文件大小: {shop_file.stat().st_size / 1024 / 1024:.2f} MB")
        except Exception as e:
            logger.warning(f"商城更新失败: {e}")
    await UniMessage(Image(path=shop_file) + Text("可前往 https://www.fortnite.com/item-shop?lang=zh-Hans 购买")).send()


@on_startswith("更新商城", permission=SUPERUSER).handle()
async def _():
    receipt = await UniMessage.text("正在更新商城，请稍后...").send()
    try:
        file = await screenshot_shop_img()
        await UniMessage(Text("手动更新商城成功") + Image(path=file)).send()
    except Exception as e:
        await UniMessage(Text(f"手动更新商城失败 | {e}")).send()
    finally:
        await receipt.recall(delay=1)


vb_matcher = on_startswith(("vb图", "VB图", "Vb图"))


@vb_matcher.handle()
async def _():
    if not vb_file.exists():
        logger.info("vb 图不存在, 开始更新vb图...")
        try:
            await screenshot_vb_img()
            logger.success(f"vb图更新成功, 文件大小: {vb_file.stat().st_size / 1024 / 1024:.2f} MB")
        except Exception as e:
            logger.warning(f"vb图更新失败: {e}")
    await UniMessage(Image(path=vb_file)).send()


@on_startswith("更新vb图", permission=SUPERUSER).handle()
async def _():
    receipt = await UniMessage.text("正在更新vb图，请稍后...").send()
    try:
        file = await screenshot_vb_img()
        await UniMessage(Text("手动更新 VB 图成功") + Image(path=file)).send()
    except Exception as e:
        await UniMessage(Text(f"手动更新 VB 图失败 | {e}")).send()
    finally:
        await receipt.recall(delay=1)
