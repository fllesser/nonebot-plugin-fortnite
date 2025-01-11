import re

from pathlib import Path
from nonebot import require
from nonebot.plugin.on import on_command
from nonebot.permission import SUPERUSER
from nonebot_plugin_uninfo import (
    get_session,
    Uninfo
)
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
    Image,
    Text
)

from .stats import (
    get_level,
    get_stats_image
)
from .pve import screenshot_vb_img, vb_file
from .shop import screenshot_shop_img, shop_file

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
        
        
name_prompt = UniMessage.template("{:At(user, $event.get_user_id())} 请发送游戏名称\n群昵称设置如下可快速查询:\n    id:name\n    ID name")

@battle_pass.got_path('name', prompt=name_prompt)
async def _(arp: Arparma, name: str):
    header = arp.header_match.result
    receipt = await UniMessage.text(f'正在查询 {name} 的{header}，请稍后...').send()
    level_info = await get_level(name, header)
    await battle_pass.send(level_info)
    await receipt.recall(delay=1)

@stats.got_path('name', prompt=name_prompt)
async def _(arp: Arparma, name: str):
    header = arp.header_match.result
    receipt = await UniMessage.text(f'正在查询 {name} 的{header}，请稍后...').send()
    res = await get_stats_image(name, header)
    if isinstance(res, Path):
        res = await UniMessage(Image(path=res)).export()
    await stats.send(res)
    await receipt.recall(delay=1)

shop = on_command('商城')

@shop.handle()
async def _():
    await shop.send(await UniMessage(Image(path=shop_file) + Text('https://www.fortnite.com/item-shop?lang=zh-Hans')).export())
    # await shop.finish('https://www.fortnite.com/item-shop?lang=zh-Hans' + "\n\n" + 'https://fortnite.gg/shop')
    
update_shop = on_command('更新商城', permission=SUPERUSER)

@update_shop.handle()
async def _():
    try:
        receipt = await UniMessage.text("正在更新商城，请稍后...").send()
        file = await screenshot_shop_img()
        await update_vb.send(await UniMessage(Text('手动更新商城成功') + Image(path=file)).export())
    except Exception as e:
        await update_vb.send(f'手动更新商城失败 | {e}')
    finally:
        await receipt.recall(delay=1)
        
vb = on_command('vb图', aliases={"VB图"})

@vb.handle()
async def _():
    await vb.finish(await UniMessage(Image(path=vb_file)).export())
    
update_vb = on_command('更新vb图', permission=SUPERUSER)

@update_vb.handle()
async def _():
    try:
        receipt = await UniMessage.text("正在更新vb图，请稍后...").send()
        file = await screenshot_vb_img()
        await update_vb.send(await UniMessage(Text('手动更新vb图成功') + Image(path=file)).export())
    except Exception as e:
        await update_vb.send(f'手动更新vb图失败 | {e}')
    finally:
        await receipt.recall(delay=1)