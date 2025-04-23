from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageSegment
from nonebug import App
import pytest


def make_onebot_msg(message: Message) -> GroupMessageEvent:
    from time import time

    from nonebot.adapters.onebot.v11.event import Sender

    event = GroupMessageEvent(
        time=int(time()),
        sub_type="normal",
        self_id=123456,
        post_type="message",
        message_type="group",
        message_id=12345623,
        user_id=1234567890,
        group_id=1234567890,
        raw_message=message.extract_plain_text(),
        message=message,
        original_message=message,
        sender=Sender(),
        font=123456,
    )
    return event


@pytest.mark.asyncio
async def test_load():
    from nonebot import require

    assert require("nonebot_plugin_fortnite")


@pytest.mark.asyncio
async def test_vb_img(app: App):
    import nonebot
    from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter

    from nonebot_plugin_fortnite import vb_file, vb_matcher

    texts = ["/vb图", "/VB图"]
    msgs = [make_onebot_msg(Message(text)) for text in texts]

    async with app.test_matcher(vb_matcher) as ctx:
        adapter = nonebot.get_adapter(OnebotV11Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        for msg in msgs:
            ctx.receive_event(bot, msg)
            ctx.should_call_send(msg, Message(MessageSegment.image(vb_file)), result=None, bot=bot)
            ctx.should_finished()


@pytest.mark.asyncio
async def test_shop_img(app: App):
    import nonebot
    from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter

    from nonebot_plugin_fortnite import shop_file, shop_matcher

    texts = ["/商城", "/商城图"]
    msgs = [make_onebot_msg(Message(text)) for text in texts]

    async with app.test_matcher(shop_matcher) as ctx:
        adapter = nonebot.get_adapter(OnebotV11Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        for msg in msgs:
            ctx.receive_event(bot, msg)
            ctx.should_call_send(
                msg,
                Message(
                    MessageSegment.image(shop_file) + "可前往 https://www.fortnite.com/item-shop?lang=zh-Hans 购买"
                ),
                result=None,
                bot=bot,
            )
            ctx.should_finished()


@pytest.mark.asyncio
async def test_stats(app: App):
    import nonebot
    from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter

    from nonebot_plugin_fortnite import stats_alc
    from nonebot_plugin_fortnite.config import fconfig
    from nonebot_plugin_fortnite.stats import get_stats_image

    if fconfig.fortnite_api_key == "":
        pytest.skip("api_key 未设置，跳过测试")

    texts = ["战绩 红桃QAQ", "生涯战绩 红桃QAQ"]
    msgs = [make_onebot_msg(Message(text)) for text in texts]

    async with app.test_matcher(stats_alc) as ctx:
        adapter = nonebot.get_adapter(OnebotV11Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        for msg in msgs:
            ctx.receive_event(bot, msg)
            stats_file = await get_stats_image("红桃QAQ", "生涯")
            ctx.should_call_send(msg, Message(MessageSegment.image(stats_file)), result=None, bot=bot)
            ctx.should_finished()


@pytest.mark.asyncio
async def test_check_font():
    from nonebot_plugin_fortnite.stats import check_font_file

    assert await check_font_file()
