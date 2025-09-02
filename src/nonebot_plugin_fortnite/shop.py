import asyncio
from pathlib import Path

from nonebot_plugin_htmlrender import get_browser
from playwright.async_api import BrowserContext

from .config import GG_FONT_PATH, data_dir

shop_file = data_dir / "shop.png"


async def screenshot_shop_img() -> Path:
    # url = "https://www.fortnite.com/item-shop?lang=zh-Hans"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",  # noqa: E501
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",  # noqa: E501
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
    browser = await get_browser(headless=True)
    context = await browser.new_context(extra_http_headers=headers)

    try:
        await _screenshot_shop_img(context)
    finally:
        await context.close()
    await add_update_time()
    return shop_file


async def _screenshot_shop_img(context: BrowserContext):
    url = "https://fortnite.gg/shop"
    page = await context.new_page()
    # page.on('requestfailed', lambda request: logger.warning(f'Request failed: {request.url}'))
    await page.add_style_tag(content="* { transition: none !important; animation: none !important; }")
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

    await page.screenshot(path=shop_file, full_page=True)


async def add_update_time():
    await asyncio.to_thread(_add_update_time)


def _add_update_time():
    import time

    from PIL import Image, ImageDraw, ImageFont

    font = ImageFont.truetype(GG_FONT_PATH, 88)
    with Image.open(shop_file) as img:
        draw = ImageDraw.Draw(img)
        # 先填充 rgb(47,49,54) 背景 1280 * 100
        draw.rectangle((0, 0, 1280, 270), fill=(47, 49, 54))
        # 1280 宽，19个数字居中 x 坐标
        time_text = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        time_text_width = draw.textlength(time_text, font=font)
        x = (1280 - time_text_width) / 2
        draw.text((x, 100), time_text, font=font, fill=(255, 255, 255))
        img.save(shop_file)
