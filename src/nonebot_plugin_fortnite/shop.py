import asyncio
from pathlib import Path

from nonebot import logger
from nonebot_plugin_htmlrender import get_new_page
from nonebot_plugin_htmlrender.browser import Page

from . import utils
from .config import fconfig

SHOP_FILE_NAME = "shop.png"
SHOP_FILE = fconfig.data_dir / SHOP_FILE_NAME
GG_FONT_PATH = Path(__file__).parent / "resources" / "burbankbigregular-black.woff2"


async def update_shop_img():
    """更新商城图片（根据配置决定下载或截图）"""

    if fconfig.fortnite_screenshot_from_github:
        logger.info("从 GitHub 下载商城图片...")
        await download_shop_img_from_github()
    else:
        await screenshot_shop_img()

    size = utils.get_size_in_mb(SHOP_FILE)
    logger.success(f"商城更新成功，文件大小: {size:.2f} MB")


@utils.retry(retries=3, delay=10)
async def download_shop_img_from_github():
    """从 GitHub 分支下载商城图片"""
    import httpx
    import aiofiles

    url = f"{fconfig.raw_base_url}/screenshots/{SHOP_FILE_NAME}"

    async with httpx.AsyncClient(timeout=60) as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            # 流式写入文件
            async with aiofiles.open(SHOP_FILE, "wb") as f:
                async for chunk in response.aiter_bytes(8192):
                    await f.write(chunk)


async def screenshot_shop_img():
    # url = "https://www.fortnite.com/item-shop?lang=zh-Hans"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,"
            "image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        ),
        "Accept-Encoding": "gzip, deflate",
        "upgrade-insecure-requests": "1",
        "dnt": "1",
        "x-requested-with": "mark.via",
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    # browser = await get_browser(headless=True)
    # context = await browser.new_context(extra_http_headers=headers)
    async with get_new_page(device_scale_factor=1, extra_http_headers=headers) as page:
        await _screenshot_shop_img(page)
    await add_update_time()


@utils.retry(3, 10)
async def _screenshot_shop_img(page: Page):
    url = "https://fortnite.gg/shop"
    await page.add_style_tag(
        content="* { transition: none !important; animation: none !important; }"
    )
    await page.goto(url)

    async def wait_for_load():
        await page.wait_for_load_state("networkidle", timeout=90000)

    async def scroll_page():
        for _ in range(20):
            await page.evaluate("""() => {
                window.scrollBy(0, document.body.scrollHeight / 20);
            }""")
            await asyncio.sleep(1)  # 等待1秒以加载内容

    await asyncio.gather(wait_for_load(), scroll_page())
    await page.screenshot(path=SHOP_FILE, full_page=True)


async def add_update_time():
    await asyncio.to_thread(_add_update_time)


def _add_update_time():
    import time

    from PIL import Image, ImageDraw, ImageFont

    font = ImageFont.truetype(GG_FONT_PATH, 88)
    with Image.open(SHOP_FILE) as img:
        draw = ImageDraw.Draw(img)
        # 先填充 rgb(47,49,54) 背景 1280 * 100
        draw.rectangle((0, 0, 1280, 270), fill=(47, 49, 54))
        # 1280 宽，19个数字居中 x 坐标
        time_text = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        time_text_width = draw.textlength(time_text, font=font)
        x = (1280 - time_text_width) / 2
        draw.text((x, 100), time_text, font=font, fill=(255, 255, 255))
        img.save(SHOP_FILE)
