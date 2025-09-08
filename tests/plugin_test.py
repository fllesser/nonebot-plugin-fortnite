from fake import fake_group_message_event_v11
from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment
from nonebug import App
import pytest


@pytest.mark.asyncio
async def test_load():
    from nonebot import require

    assert require("nonebot_plugin_fortnite")


@pytest.mark.asyncio
async def test_vb_img(app: App):
    import nonebot
    from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter

    from nonebot_plugin_fortnite import vb_file, vb_matcher

    if vb_file.exists():
        vb_file.unlink()

    texts = ["vb图", "VB图", "Vb图"]
    msg_events = [fake_group_message_event_v11(message=text) for text in texts]

    async with app.test_matcher(vb_matcher) as ctx:
        adapter = nonebot.get_adapter(OnebotV11Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        for event in msg_events:
            ctx.receive_event(bot, event)
            ctx.should_call_send(event, Message(MessageSegment.image(vb_file)), result=None, bot=bot)
            ctx.should_finished()

    assert vb_file.exists()


@pytest.mark.asyncio
async def test_shop_img(app: App):
    import nonebot
    from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter

    from nonebot_plugin_fortnite import shop_file, shop_matcher

    if shop_file.exists():
        shop_file.unlink()

    texts = ["商城", "商城。。。。"]
    msg_events = [fake_group_message_event_v11(message=text) for text in texts]

    async with app.test_matcher(shop_matcher) as ctx:
        adapter = nonebot.get_adapter(OnebotV11Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        for event in msg_events:
            ctx.receive_event(bot, event)
            # assert shop_file.exists()
            should_send = (
                MessageSegment.image(shop_file) + "可前往 https://www.fortnite.com/item-shop?lang=zh-Hans 购买"
            )
            ctx.should_call_send(
                event,
                Message(should_send),
                result=None,
                bot=bot,
            )
            ctx.should_finished()
    assert shop_file.exists()


@pytest.mark.asyncio
async def test_stats_matcher(app: App):
    import nonebot
    from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter

    from nonebot_plugin_fortnite import stats_alc
    from nonebot_plugin_fortnite.config import fconfig
    from nonebot_plugin_fortnite.stats import get_stats_image

    if fconfig.fortnite_api_key is None:
        pytest.skip("api_key 未设置，跳过测试")

    texts = ["战绩 红桃QAQ", "生涯战绩 红桃QAQ"]
    msg_events = [fake_group_message_event_v11(message=text) for text in texts]

    async with app.test_matcher(stats_alc) as ctx:
        adapter = nonebot.get_adapter(OnebotV11Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        for msg_event in msg_events:
            ctx.receive_event(bot, msg_event)
            stats_file = await get_stats_image("红桃QAQ", "生涯")
            ctx.should_call_send(
                msg_event, Message(MessageSegment.text("正在查询红桃QAQ的战绩，请稍后...")), result=None, bot=bot
            )
            ctx.should_call_send(msg_event, Message(MessageSegment.image(stats_file)), result=None, bot=bot)
            ctx.should_finished()


@pytest.mark.asyncio
async def test_stats_func():
    import aiofiles

    from nonebot_plugin_fortnite.config import cache_dir, fconfig
    from nonebot_plugin_fortnite.stats import get_stats_image

    if fconfig.fortnite_api_key is None:
        pytest.skip("api_key 未设置，跳过测试")

    bytes_io = await get_stats_image("红桃QAQ", "生涯")
    assert bytes_io is not None

    async with aiofiles.open(cache_dir / "test_stats_image.png", "wb") as f:
        await f.write(bytes_io.getvalue())


@pytest.mark.asyncio
async def test_check_font():
    from nonebot_plugin_fortnite import check_font_file

    await check_font_file()


@pytest.mark.asyncio
async def test_fill_img_with_time():
    import asyncio

    from PIL import Image

    from nonebot_plugin_fortnite.config import cache_dir
    from nonebot_plugin_fortnite.pve import fill_img_with_time, vb_file
    from nonebot_plugin_fortnite.utils import save_img

    with Image.open(vb_file) as img:
        await asyncio.to_thread(fill_img_with_time, img)
        await save_img(img, cache_dir / "test_fill_img_with_time.png")
