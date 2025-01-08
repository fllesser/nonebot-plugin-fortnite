import re
from nonebot.log import logger
from nonebot.adapters import Bot, Event
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

name_args = Args["name?", str]

battle_pass = on_alconna(
    Alconna("季卡", name_args)
)

stats = on_alconna(
    Alconna('战绩', name_args)
)

@battle_pass.handle()
@stats.handle()
async def _(
    matcher: AlconnaMatcher,
    session: Uninfo,
    name: Math[str]
):
    if name.available:
        matcher.set_path_args('name', name.result)
        return
    # 获取群昵称
    if not session.member or not session.member.nick:
        return
    pattern = r'(?:id:|id\s)(.+)'
    if match := re.match(pattern, session.member.nick):
        matcher.set_path_args('name', match.group(1))
        
        
name_prompt = UniMessage.template("{:At(user, $event.get_user_id())} 请发送游戏名称(群昵称设置为id:name可快速查询)")
        
@battle_pass.got_path('name', prompt=name_prompt)
async def _(name: str):
    level_info = await get_level(name)
    await battle_pass.finish(level_info)

@stats.got_path('name', prompt=name_prompt)
async def _(name: str):
    stats_img = await get_stats_image(name)
    await stats.finish(await UniMessage(Image(url=stats_img)).export())
