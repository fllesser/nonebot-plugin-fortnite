#!/usr/bin/env python3
"""
截图脚本，用于 CI 环境中每日自动截图
"""

import os

import nonebot
from nonebot import logger, get_driver


def main():
    nonebot.init()
    nonebot.load_plugin("nonebot_plugin_fortnite")
    from nonebot_plugin_fortnite import pve, shop, get_size_in_mb

    @get_driver().on_startup
    async def _():
        await shop.update_shop_img()
        size = get_size_in_mb(shop.SHOP_FILE)
        logger.success(f"商城更新成功，文件大小: {size:.2f} MB")
        await pve.update_vb_img()
        size = get_size_in_mb(pve.VB_FILE)
        logger.success(f"vb图更新成功, 文件大小: {size:.2f} MB")
        os._exit(0)

    nonebot.run()


if __name__ == "__main__":
    main()
