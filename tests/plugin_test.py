from nonebug import App
import pytest


@pytest.mark.asyncio
async def test_load_plugin(app: App):
    from nonebot import require

    assert require("nonebot_plugin_fortnite")

    from nonebot_plugin_fortnite import check_files

    await check_files()
