import re

from nonebot import require
from nonebot.plugin.on import on_command

require("nonebot_plugin_uninfo")
from nonebot_plugin_uninfo import (
    get_session,
    Uninfo
)
require("nonebot_plugin_alconna")
from nonebot_plugin_alconna import (
    on_alconna,
    AlconnaMatcher,
    Match
)
from arclet.alconna import (
    Alconna,
    Args,
    Subcommand,
    Arparma,
    Option
)
from nonebot_plugin_alconna.uniseg import (
    UniMessage,
    Image
)

from .stats import (
    get_level,
    get_stats_image
)

timewindow_prefix = ["生涯", ""]
name_args = Args["name?", str]


battle_pass = on_alconna(
    Alconna(timewindow_prefix, "季卡", name_args)
)

stats = on_alconna(
    Alconna(timewindow_prefix, '战绩', name_args)
)

@battle_pass.handle()
@stats.handle()
async def _(
    matcher: AlconnaMatcher,
    session: Uninfo,
    name: Match[str]
):
    if name.available:
        matcher.set_path_arg('name', name.result)
        return
    # 获取群昵称
    if not session.member or not session.member.nick:
        return
    pattern = r'(?:id:|id\s)(.+)'
    if match := re.match(
        pattern,
        session.member.nick,
        re.IGNORECASE
    ):
        matcher.set_path_arg('name', match.group(1))
        
        
name_prompt = UniMessage.template("{:At(user, $event.get_user_id())} 请发送游戏名称(群昵称设置为id:name/ID name可快速查询)")

@battle_pass.got_path('name', prompt=name_prompt)
async def _(arp: Arparma, name: str):
    level_info = await get_level(name, arp.header_match.result)
    await battle_pass.finish(level_info)

@stats.got_path('name', prompt=name_prompt)
async def _(arp: Arparma, name: str):
    stats_img = await get_stats_image(name, arp.header_match.result)
    if stats_img.startswith('http'):
        res = await UniMessage(Image(url=stats_img)).export()
    else:
        res = stats_img
    await stats.finish(res)


shop = on_command('商城')

@shop.handle()
async def _():
    await shop.finish('https://www.fortnite.com/item-shop?lang=zh-Hans')