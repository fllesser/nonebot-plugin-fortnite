import pytest
from fake import fake_group_message_event_v11 as fake_gme
from nonebug import App
from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment

NAME = "红桃QAQ"
GROUP_INFO = {
    "group_name": "测试群",
    "group_memo": "测试群",
    "member_count": 100,
    "max_member_count": 2000,
}
GROUP_MEMBER_INFO = {
    "nickname": NAME,
    "card": f"id:{NAME}",
    "role": "member",
    "level": 100,
}


async def test_battle_pass_with_nickname(app: App):
    import nonebot
    from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter

    from nonebot_plugin_fortnite import stats_alc
    from nonebot_plugin_fortnite.stats import get_stats_image
    from nonebot_plugin_fortnite.config import fconfig

    if fconfig.fortnite_api_key is None:
        pytest.skip("api_key 未设置，跳过测试")

    cmd = "季卡"
    event = fake_gme(message=cmd)
    group_info = {
        "group_id": event.group_id,
        **GROUP_INFO,
    }
    group_member_info = {
        "user_id": event.user_id,
        "group_id": event.group_id,
        **GROUP_MEMBER_INFO,
    }

    async with app.test_matcher(stats_alc) as ctx:
        adapter = nonebot.get_adapter(OnebotV11Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        ctx.receive_event(bot, event)
        stats_file = await get_stats_image(NAME, cmd)
        ctx.should_call_api(
            "get_group_info",
            data={"group_id": event.group_id},
            result=group_info,
        )
        ctx.should_call_api(
            "get_group_member_info",
            data={
                "group_id": event.group_id,
                "user_id": event.user_id,
                "no_cache": True,
            },
            result=group_member_info,
        )
        ctx.should_call_send(
            event,
            Message(f"正在查询 {NAME} 的{cmd}，请稍后..."),
            result=None,
            bot=bot,
        )

        image = MessageSegment.image(stats_file)
        ctx.should_call_send(
            event,
            Message(image),
            result=None,
            bot=bot,
        )

        ctx.should_call_api(
            "delete_msg",
            data={"message_id": event.message_id},
            result=None,
        )


async def test_battle_pass_with_arg_name(app: App):
    import nonebot
    from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter

    from nonebot_plugin_fortnite import stats_alc
    from nonebot_plugin_fortnite.stats import get_level
    from nonebot_plugin_fortnite.config import fconfig

    if fconfig.fortnite_api_key is None:
        pytest.skip("api_key 未设置，跳过测试")

    cmd = "生涯季卡"
    event = fake_gme(message=f"{cmd} {NAME}")
    group_info = {
        "group_id": event.group_id,
        **GROUP_INFO,
    }
    group_member_info = {
        "user_id": event.user_id,
        "group_id": event.group_id,
        **GROUP_MEMBER_INFO,
    }

    async with app.test_matcher(stats_alc) as ctx:
        adapter = nonebot.get_adapter(OnebotV11Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        ctx.receive_event(bot, event)
        level = await get_level(NAME, cmd)
        ctx.should_call_api(
            "get_group_info",
            data={"group_id": event.group_id},
            result=group_info,
        )

        ctx.should_call_api(
            "get_group_member_info",
            data={
                "group_id": event.group_id,
                "user_id": event.user_id,
                "no_cache": True,
            },
            result=group_member_info,
        )

        ctx.should_call_send(
            event,
            Message(f"正在查询 {NAME} 的{cmd}，请稍后..."),
            result=None,
            bot=bot,
        )

        ctx.should_call_send(
            event,
            Message(level),
            result=None,
            bot=bot,
        )

        ctx.should_call_api(
            "delete_msg",
            data={"message_id": event.message_id},
            result=None,
        )


async def test_stats_with_nickname(app: App):
    import nonebot
    from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter

    from nonebot_plugin_fortnite import stats_alc
    from nonebot_plugin_fortnite.stats import get_stats_image
    from nonebot_plugin_fortnite.config import fconfig

    if fconfig.fortnite_api_key is None:
        pytest.skip("api_key 未设置，跳过测试")

    cmd = "战绩"
    event = fake_gme(message=cmd)
    group_info = {
        "group_id": event.group_id,
        **GROUP_INFO,
    }
    group_member_info = {
        "user_id": event.user_id,
        "group_id": event.group_id,
        **GROUP_MEMBER_INFO,
    }

    async with app.test_matcher(stats_alc) as ctx:
        adapter = nonebot.get_adapter(OnebotV11Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        ctx.receive_event(bot, event)
        stats_file = await get_stats_image("红桃QAQ", cmd)
        ctx.should_call_api(
            "get_group_info",
            data={"group_id": event.group_id},
            result=group_info,
        )
        ctx.should_call_api(
            "get_group_member_info",
            data={
                "group_id": event.group_id,
                "user_id": event.user_id,
                "no_cache": True,
            },
            result=group_member_info,
        )
        ctx.should_call_send(
            event,
            Message(f"正在查询 红桃QAQ 的{cmd}，请稍后..."),
            result=None,
            bot=bot,
        )

        image = MessageSegment.image(stats_file)
        ctx.should_call_send(
            event,
            Message(image),
            result=None,
            bot=bot,
        )

        ctx.should_call_api(
            "delete_msg",
            data={"message_id": event.message_id},
            result=None,
        )


async def test_stats_with_arg_name(app: App):
    import nonebot
    from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter

    from nonebot_plugin_fortnite import stats_alc
    from nonebot_plugin_fortnite.stats import get_stats_image
    from nonebot_plugin_fortnite.config import fconfig

    if fconfig.fortnite_api_key is None:
        pytest.skip("api_key 未设置，跳过测试")

    cmd = "生涯战绩"
    event = fake_gme(message=f"{cmd} {NAME}")
    group_info = {
        "group_id": event.group_id,
        **GROUP_INFO,
    }
    group_member_info = {
        "user_id": event.user_id,
        "group_id": event.group_id,
        **GROUP_MEMBER_INFO,
    }

    async with app.test_matcher(stats_alc) as ctx:
        adapter = nonebot.get_adapter(OnebotV11Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        ctx.receive_event(bot, event)
        stats_file = await get_stats_image(NAME, cmd)
        ctx.should_call_api(
            "get_group_info",
            data={"group_id": event.group_id},
            result=group_info,
        )

        ctx.should_call_api(
            "get_group_member_info",
            data={
                "group_id": event.group_id,
                "user_id": event.user_id,
                "no_cache": True,
            },
            result=group_member_info,
        )

        ctx.should_call_send(
            event,
            Message(f"正在查询 {NAME} 的{cmd}，请稍后..."),
            result=None,
            bot=bot,
        )

        image = MessageSegment.image(stats_file)
        ctx.should_call_send(
            event,
            Message(image),
            result=None,
            bot=bot,
        )

        ctx.should_call_api(
            "delete_msg",
            data={"message_id": event.message_id},
            result=None,
        )
