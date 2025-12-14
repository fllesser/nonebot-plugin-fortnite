import time
import asyncio
from pathlib import Path
from contextlib import ExitStack

import httpx
import aiofiles
from PIL import Image, ImageDraw, ImageFont
from nonebot.log import logger
from playwright.async_api import Route
from nonebot_plugin_htmlrender import get_new_page
from nonebot_plugin_htmlrender.browser import Page

from . import utils
from .config import fconfig

VB_FILE_NAME = "vb.png"
VB_FILE = fconfig.data_dir / VB_FILE_NAME
VB_FONT_PATH = Path(__file__).parent / "resources" / "LuckiestGuy.woff"


async def update_vb_img():
    """更新 VB 图片（根据配置决定下载或截图）"""

    if fconfig.fortnite_screenshot_from_github:
        logger.info("从 GitHub 分支下载 VB 图片...")
        await download_vb_img_from_github()
    else:
        await screenshot_vb_img()

    size = utils.get_size_in_mb(VB_FILE)
    logger.success(f"vb图更新成功, 文件大小: {size:.2f} MB")


@utils.retry(retries=3, delay=10)
async def download_vb_img_from_github():
    """从 GitHub 分支下载 VB 图片"""

    url = f"{fconfig.raw_base_url}/screenshots/{VB_FILE_NAME}"

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url)
        response.raise_for_status()

    async with aiofiles.open(VB_FILE, "wb") as f:
        await f.write(response.content)


async def screenshot_vb_img():
    async with get_new_page(device_scale_factor=1) as page:
        await _screenshot_vb_img(page)
    await combine_imgs()


_SELECTOR_MAP = {
    "hot_info_1.png": ("div.hot-info", 0),
    "container_hidden_xs.png": ("div.container.hidden-xs", 0),
    "hot_info_2.png": ("div.hot-info", 1),
}


@utils.retry(retries=3, delay=10)
async def _screenshot_vb_img(page: Page):
    url = "https://freethevbucks.com/timed-missions"

    # 拦截广告
    async def ad_block_handler(route: Route):
        ad_domains = [
            "googlesyndication.com",
            "doubleclick.net",
            "adnxs.com",
            "google-analytics.com",
            "facebook.com",
            "amazon-adsystem.com",
            "adform.net",
            "googleadservices.com",
            "doubleclick.net",
        ]
        if any(ad_domain in route.request.url for ad_domain in ad_domains):
            await route.abort()
        else:
            await route.continue_()

    await page.route("**/*", ad_block_handler)
    await page.goto(url)

    # 截图
    async def screenshot(filename: str, selector: str, nth: int = 0) -> None:
        locator = page.locator(selector).nth(nth)
        # 检查元素内容是否为空
        content = await locator.inner_html()
        path = fconfig.cache_dir / filename
        if content.strip():
            await asyncio.wait_for(locator.screenshot(path=path), timeout=5)
        else:
            logger.warning(f"Locator for {path.name} is empty.")

    await asyncio.gather(*[screenshot(file, *sn) for file, sn in _SELECTOR_MAP.items()])


async def combine_imgs():
    await asyncio.to_thread(_combine_imgs)


def _combine_imgs():
    # 打开截图文件（如果存在）
    img_paths = [fconfig.cache_dir / file for file in _SELECTOR_MAP.keys()]
    img_paths = [path for path in img_paths if path.exists()]
    if not img_paths:
        raise Exception("所有选择器的截图文件均不存在")
    # 先添加时间
    try:
        with ExitStack() as stack:
            # 动态打开所有图片
            images: list[Image.Image] = [
                stack.enter_context(Image.open(path)) for path in img_paths
            ]

            # 获取尺寸并创建新图像
            widths, heights = zip(*(img.size for img in images))
            total_width = max(widths)
            total_height = sum(heights)

            # 如果 img1.width < total_width，则拉伸最右侧像素到 total_width
            if (img1 := images[0]) and img1.width < total_width:
                images[0] = resize_img_with_right_pixel(img1, total_width)

            # 填充更新时间
            draw_time_text(img1, total_width)
            with Image.new("RGB", (total_width, total_height)) as combined_image:
                # 将截图粘贴到新图像中
                y_offset = 0
                for img in images:
                    combined_image.paste(img, (0, y_offset))
                    y_offset += img.height

                # 保存合并后的图像
                combined_image.save(VB_FILE)
    finally:
        # 关闭并删除所有截图文件
        for img_path in img_paths:
            img_path.unlink()


def draw_time_text(img: Image.Image, width: int = 1126):
    draw = ImageDraw.Draw(img)
    font_size = 26
    font = ImageFont.truetype(VB_FONT_PATH, font_size)
    time_text = time.strftime("Updated: %Y-%m-%d %H:%M:%S", time.localtime())
    time_text_width = draw.textlength(time_text, font=font)
    x = width - time_text_width - 10
    draw.text((x, 12), time_text, font=font, fill=(80, 80, 80))


def resize_img_with_right_pixel(img: Image.Image, width: int = 1126):
    new_img = Image.new("RGB", (width, img.height))
    new_img.paste(img, (0, 0))
    # 横向取 img 最右侧像素点，填充到 new_img 的 width - 1 到 width 的像素点
    for x in range(img.width - 50, width):
        for y in range(img.height):
            color = img.getpixel((img.width - 50, y))
            assert color is not None
            new_img.putpixel((x, y), color)
    return new_img
