#!/usr/bin/env python3
"""
截图脚本，用于 CI 环境中每日自动截图
"""

import sys

import nonebot
from nonebot import get_driver


def main():
    """运行截图任务"""
    # 导入必要的模块
    nonebot.init()
    nonebot.load_plugin("nonebot_plugin_fortnite")
    from nonebot_plugin_fortnite import daily_update

    @get_driver().on_startup
    async def _daily_update():
        await daily_update()
        sys.exit(0)

    nonebot.run()


if __name__ == "__main__":
    main()
