#!/usr/bin/env python3
"""
截图脚本，用于 CI 环境中每日自动截图
"""

import asyncio

import nonebot
from nonebot import logger


async def main():
    """运行截图任务"""
    # 导入必要的模块
    nonebot.init()
    nonebot.load_plugin("nonebot_plugin_fortnite")

    from nonebot_plugin_fortnite.pve import screenshot_vb_img
    from nonebot_plugin_fortnite.shop import screenshot_shop_img

    logger.info("开始执行截图任务...")

    # 并发运行两个截图任务
    shop_file, vb_file = await asyncio.gather(
        screenshot_shop_img(),
        screenshot_vb_img(),
    )

    logger.success(f"✓ 商城截图已保存: {shop_file}")
    logger.success(f"✓ VB图截图已保存: {vb_file}")

    # 验证文件是否存在
    if not shop_file.exists():
        raise FileNotFoundError(f"商城截图文件不存在: {shop_file}")
    if not vb_file.exists():
        raise FileNotFoundError(f"VB图截图文件不存在: {vb_file}")

    logger.info("✓ 所有截图任务完成!")


if __name__ == "__main__":
    asyncio.run(main())
