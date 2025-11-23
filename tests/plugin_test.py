from fake import fake_group_message_event_v11
from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment
from nonebug import App
import pytest


async def test_load():
    from nonebot import require

    assert require("nonebot_plugin_fortnite")


async def test_vb_img(app: App):
    import nonebot
    from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter

    from nonebot_plugin_fortnite import VB_FILE, vb_matcher

    if VB_FILE.exists():
        VB_FILE.unlink()

    texts = ["vb图", "VB图", "Vb图"]
    msg_events = [fake_group_message_event_v11(message=text) for text in texts]

    async with app.test_matcher(vb_matcher) as ctx:
        adapter = nonebot.get_adapter(OnebotV11Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        for event in msg_events:
            ctx.receive_event(bot, event)
            image = MessageSegment.image(VB_FILE)
            ctx.should_call_send(event, Message(image), result=None, bot=bot)
            ctx.should_finished()

    assert VB_FILE.exists()


async def test_shop_img(app: App):
    import nonebot
    from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter

    from nonebot_plugin_fortnite import SHOP_FILE, shop_matcher

    if SHOP_FILE.exists():
        SHOP_FILE.unlink()

    texts = ["商城", "商城。。。。"]
    msg_events = [fake_group_message_event_v11(message=text) for text in texts]

    async with app.test_matcher(shop_matcher) as ctx:
        adapter = nonebot.get_adapter(OnebotV11Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        for event in msg_events:
            ctx.receive_event(bot, event)
            # assert SHOP_FILE.exists()
            should_send = (
                MessageSegment.image(SHOP_FILE)
                + "可前往 https://www.fortnite.com/item-shop?lang=zh-Hans 购买"
            )
            ctx.should_call_send(
                event,
                Message(should_send),
                result=None,
                bot=bot,
            )
            ctx.should_finished()
    assert SHOP_FILE.exists()


async def test_stats_matcher(app: App):
    import nonebot
    from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter

    from nonebot_plugin_fortnite import stats_alc
    from nonebot_plugin_fortnite.config import fconfig
    from nonebot_plugin_fortnite.stats import get_stats_image

    if fconfig.fortnite_api_key is None:
        pytest.skip("api_key 未设置，跳过测试")

    commands = ["战绩", "生涯战绩"]
    msg_events = [fake_group_message_event_v11(message=cmd) for cmd in commands]

    group_info = {
        "group_id": msg_events[0].group_id,
        "group_name": "测试群",
        "group_memo": "测试群",
        "member_count": 100,
        "max_member_count": 2000,
    }

    group_member_info = {
        "user_id": msg_events[0].user_id,
        "group_id": msg_events[0].group_id,
        "nickname": "红桃QAQ",
        "card": "id:红桃QAQ",
        "role": "member",
        "level": 100,
    }

    async with app.test_matcher(stats_alc) as ctx:
        adapter = nonebot.get_adapter(OnebotV11Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        msg_event = msg_events[0]
        ctx.receive_event(bot, msg_event)
        stats_file = await get_stats_image("红桃QAQ", commands[0])
        ctx.should_call_api(
            "get_group_info", data={"group_id": msg_event.group_id}, result=group_info
        )
        ctx.should_call_api(
            "get_group_member_info",
            data={
                "group_id": msg_event.group_id,
                "user_id": msg_event.user_id,
                "no_cache": True,
            },
            result=group_member_info,
        )
        ctx.should_call_send(
            msg_event,
            Message(f"正在查询 红桃QAQ 的{commands[0]}，请稍后..."),
            result=None,
            bot=bot,
        )
        image = MessageSegment.image(stats_file)
        ctx.should_call_send(msg_event, Message(image), result=None, bot=bot)
        ctx.should_call_api(
            "delete_msg", data={"message_id": msg_event.message_id}, result=None
        )


async def test_stats_func():
    import aiofiles

    from nonebot_plugin_fortnite.config import cache_dir, fconfig
    from nonebot_plugin_fortnite.stats import get_stats_image

    if fconfig.fortnite_api_key is None:
        pytest.skip("api_key 未设置，跳过测试")

    bytes_io = await get_stats_image("别打好疼", "生涯")
    assert bytes_io is not None

    async with aiofiles.open(cache_dir / "stats_bieda_haoteng_image.png", "wb") as f:
        await f.write(bytes_io.getvalue())


async def test_check_font():
    from nonebot_plugin_fortnite import check_resources

    await check_resources()
