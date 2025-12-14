import re
import asyncio
from pathlib import Path

from nonebot import require, get_driver, on_command, on_startswith
from nonebot.log import logger
from nonebot.plugin import PluginMetadata
from nonebot.plugin.load import inherit_supported_adapters

require("nonebot_plugin_uninfo")
require("nonebot_plugin_alconna")
require("nonebot_plugin_apscheduler")
require("nonebot_plugin_localstore")
require("nonebot_plugin_htmlrender")
from nonebot_plugin_apscheduler import scheduler

from .config import CHINESE_FONT_PATH, Config, fconfig

__plugin_meta__ = PluginMetadata(
    name="堡垒之夜游戏插件",
    description="堡垒之夜战绩, 季卡, 商城, vb图查询",
    usage="季卡/生涯季卡/战绩/生涯战绩/商城/vb图",
    type="application",
    config=Config,
    homepage="https://github.com/fllesser/nonebot-plugin-fortnite",
    supported_adapters=inherit_supported_adapters(
        "nonebot_plugin_alconna", "nonebot_plugin_uninfo"
    ),
)

from . import pve, shop, stats, utils


@get_driver().on_startup
async def check_resources():
    import httpx
    import aiofiles

    paths = [CHINESE_FONT_PATH]

    async def dwonload_file(path: Path):
        url = f"{fconfig.raw_base_url}/master/resources/{path.name}"
        logger.info(f"文件 {path.name} 不存在，开始从 {url} 下载...")
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.get(url)
            response.raise_for_status()
            font_data = response.content

            async with aiofiles.open(path, "wb") as f:
                await f.write(font_data)

            size = utils.get_size_in_mb(path)
            logger.success(f"文件 {path.name} 下载成功，文件大小: {size:.2f} MB")
        except Exception:
            logger.exception("文件下载失败")
            logger.warning(f"请前往仓库下载资源文件到 {path}")

    await asyncio.gather(*[dwonload_file(path) for path in paths if not path.exists()])


@scheduler.scheduled_job(
    "cron",
    id="fortnite",
    hour="8",
    minute="0",
    misfire_grace_time=300,
)
async def daily_update():
    if fconfig.github_token is not None:
        await utils.dispatch_screenshot_action()
        await asyncio.sleep(120)

    logger.info("开始更新商城/VB图...")
    try:
        await shop.update_shop_img()
    except Exception:
        logger.exception("商城更新失败")
    try:
        await pve.update_vb_img()
    except Exception:
        logger.exception("vb图更新失败")


from arclet.alconna import Args, Alconna, Arparma
from nonebot.permission import SUPERUSER
from nonebot_plugin_uninfo import Uninfo
from nonebot_plugin_alconna import Match, AlconnaMatcher, on_alconna
from nonebot_plugin_alconna.uniseg import Text, Image, UniMessage

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
    "{:At(user, $event.get_user_id())} 请发送游戏名称\n"
    "群昵称设置如下可快速查询:\n"
    "    id:name\n"
    "    ID name"
)


@battle_pass_alc.got_path("name", prompt=name_prompt)
async def _(arp: Arparma, name: str):
    header: str = arp.header_match.result
    receipt = await UniMessage.text(f"正在查询 {name} 的{header}，请稍后...").send()
    level_info = await stats.get_level(name, header)
    await UniMessage(Text(level_info)).send()
    await receipt.recall(delay=1)


@stats_alc.got_path("name", prompt=name_prompt)
async def _(arp: Arparma, name: str):
    header: str = arp.header_match.result
    receipt = await UniMessage.text(f"正在查询 {name} 的{header}，请稍后...").send()
    try:
        file = await stats.get_stats_image(name, header)
    except Exception as e:
        if isinstance(e, ValueError):
            await UniMessage(Text(str(e))).finish()
        logger.exception("查询失败")
        await UniMessage(Text("查询失败")).finish()
    await UniMessage(Image(path=file)).send()
    await receipt.recall(delay=1)
    file.unlink(missing_ok=True)


shop_matcher = on_startswith("商城")


@shop_matcher.handle()
async def _():
    if not shop.SHOP_FILE.exists():
        logger.info("商城图不存在, 开始更新商城...")
        try:
            await shop.update_shop_img()
            size = utils.get_size_in_mb(shop.SHOP_FILE)
            logger.success(f"商城更新成功，文件大小: {size:.2f} MB")
        except Exception:
            logger.exception("商城更新失败")
    await UniMessage(
        Image(path=shop.SHOP_FILE)
        + Text("可前往 https://www.fortnite.com/item-shop?lang=zh-Hans 购买")
    ).send()


@on_startswith("更新商城", permission=SUPERUSER).handle()
async def _():
    receipt = await UniMessage.text("正在更新商城，请稍后...").send()
    try:
        await shop.update_shop_img()
        await UniMessage(Text("手动更新商城成功") + Image(path=shop.SHOP_FILE)).send()
    except Exception:
        logger.exception("手动更新商城失败")
        await UniMessage(Text("手动更新商城失败")).send()
    finally:
        await receipt.recall(delay=1)


vb_matcher = on_startswith(("vb图", "VB图", "Vb图"))


@vb_matcher.handle()
async def _():
    if not pve.VB_FILE.exists():
        logger.info("vb 图不存在, 开始更新vb图...")
        try:
            await pve.update_vb_img()
            size = utils.get_size_in_mb(pve.VB_FILE)
            logger.success(f"vb图更新成功, 文件大小: {size:.2f} MB")
        except Exception as e:
            logger.warning(f"vb图更新失败: {e}")
    await UniMessage(Image(path=pve.VB_FILE)).send()


@on_startswith("更新vb图", permission=SUPERUSER).handle()
async def _():
    receipt = await UniMessage.text("正在更新vb图, 请稍后...").send()
    try:
        await pve.update_vb_img()
        await UniMessage(Text("手动更新 VB 图成功") + Image(path=pve.VB_FILE)).send()
    except Exception as e:
        await UniMessage(Text(f"手动更新 VB 图失败 | {e}")).send()
    finally:
        await receipt.recall(delay=1)


if fconfig.github_token is not None:
    action_matcher = on_command("fnaction", permission=SUPERUSER)

    @action_matcher.handle()
    async def _():
        await utils.dispatch_screenshot_action()
        await UniMessage(Text("trigger screenshot github workflow successfully")).send()
        await asyncio.sleep(120)

        await shop.update_shop_img()
        await pve.update_vb_img()

        await UniMessage(Text("更新商城图, VB 图成功")).send()
