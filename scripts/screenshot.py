import os

import nonebot
from nonebot import get_driver


def main():
    nonebot.init()
    nonebot.load_plugin("nonebot_plugin_fortnite")

    from nonebot_plugin_apscheduler import scheduler

    scheduler.remove_all_jobs()

    from nonebot_plugin_fortnite import pve, shop

    @get_driver().on_startup
    async def _():
        await shop.update_shop_img()
        await pve.update_vb_img()
        os._exit(0)

    nonebot.run()


if __name__ == "__main__":
    main()
