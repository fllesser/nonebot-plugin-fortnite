import time
import asyncio
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from nonebot import logger
from playwright.async_api import Page
from nonebot_plugin_htmlrender import get_new_page

from . import utils
from .config import fconfig

GG_FONT_PATH = Path(__file__).parent / "resources" / "burbankbigregular-black.woff2"


def get_shop_file() -> Path:
    # Shop-2025-12-27.png
    today = utils.get_utc_day()
    return fconfig.data_dir / f"SHOP-{today}.png"


async def update_shop_img(shop_file: Path | None = None):
    """更新商城图片（根据配置决定下载或截图）"""
    shop_file = shop_file or get_shop_file()

    if fconfig.fortnite_screenshot_from_github:
        logger.info("从 GitHub Screenshots 分支下载商城图片...")
        await download_shop_img_from_github(shop_file)
    else:
        logger.info("从 Fortnite 网站截图商城图片...")
        await screenshot_shop_img(shop_file)

    size = utils.get_size_in_mb(shop_file)
    logger.success(f"商城更新成功，文件大小: {size:.2f} MB")
    return shop_file


@utils.retry(times=10, delay=10)
async def download_shop_img_from_github(shop_file: Path):
    """从 GitHub 分支下载商城图片"""
    import httpx
    import aiofiles

    url = utils.get_github_file_url(shop_file.name)

    async with httpx.AsyncClient(timeout=30) as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            # 流式写入文件
            async with aiofiles.open(shop_file, "wb") as f:
                async for chunk in response.aiter_bytes(8192):
                    await f.write(chunk)


async def screenshot_shop_img(shop_file: Path):
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
    async with get_new_page(device_scale_factor=1, extra_http_headers=headers) as page:
        await _screenshot_shop_img(page, shop_file)
    _add_update_time(shop_file)


@utils.retry()
async def _screenshot_shop_img(page: Page, shop_file: Path):
    url = "https://fortnite.gg/shop"
    await page.add_style_tag(
        content="* { transition: none !important; animation: none !important; }"
    )
    await page.goto(url)

    async def wait_for_load():
        await page.wait_for_load_state("networkidle", timeout=60000)

    async def scroll_page():
        for _ in range(20):
            await page.evaluate("""() => {
                window.scrollBy(0, document.body.scrollHeight / 20);
            }""")
            await asyncio.sleep(0.5)  # 等待 0.5 秒以加载内容

    await asyncio.gather(wait_for_load(), scroll_page())
    await page.screenshot(path=shop_file, full_page=True)


def _add_update_time(shop_file: Path):
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
