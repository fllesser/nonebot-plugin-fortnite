from fake import fake_group_message_event_v11 as fake_gme
from nonebug import App
from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment


async def test_vb_img(app: App):
    import nonebot
    from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter

    from nonebot_plugin_fortnite import pve, vb_matcher

    vb_file = pve.get_vb_file()
    if vb_file.exists():
        vb_file.unlink()

    await pve.update_vb_img()

    texts = ["vb图", "VB图", "Vb图"]
    msg_events = [fake_gme(message=text) for text in texts]

    async with app.test_matcher(vb_matcher) as ctx:
        adapter = nonebot.get_adapter(OnebotV11Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        for event in msg_events:
            ctx.receive_event(bot, event)
            image = MessageSegment.image(vb_file)
            ctx.should_call_send(
                event,
                Message(image),
                result=None,
                bot=bot,
            )
            ctx.should_finished()

    assert vb_file.exists()


async def test_shop_img(app: App):
    import nonebot
    from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter

    from nonebot_plugin_fortnite import shop, shop_matcher

    shop_file = shop.get_shop_file()
    if shop_file.exists():
        shop_file.unlink()

    await shop.update_shop_img()

    texts = ["商城", "商城。。。。"]
    msg_events = [fake_gme(message=text) for text in texts]

    async with app.test_matcher(shop_matcher) as ctx:
        adapter = nonebot.get_adapter(OnebotV11Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        for event in msg_events:
            ctx.receive_event(bot, event)
            # assert SHOP_FILE.exists()
            should_send = (
                MessageSegment.image(shop_file)
                + "可前往 https://www.fortnite.com/item-shop?lang=zh-Hans 购买"
            )
            ctx.should_call_send(
                event,
                Message(should_send),
                result=None,
                bot=bot,
            )
            ctx.should_finished()
    assert shop_file.exists()


async def test_check_font():
    from nonebot_plugin_fortnite import check_resources

    await check_resources()
