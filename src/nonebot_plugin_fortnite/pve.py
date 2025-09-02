import asyncio
from pathlib import Path
import time

from nonebot.log import logger
from nonebot_plugin_htmlrender import get_browser
from PIL import Image, ImageDraw, ImageFont
from playwright.async_api import BrowserContext, Locator, Route

from .config import VB_FONT_PATH, cache_dir, data_dir

vb_file = data_dir / "vb.png"
hot_info_1_path = cache_dir / "hot_info_1.png"
container_hidden_xs_path = cache_dir / "container_hidden_xs.png"
hot_info_2_path = cache_dir / "hot_info_2.png"


async def screenshot_vb_img() -> Path:
    browser = await get_browser(headless=True)
    context = await browser.new_context()

    try:
        await _screenshot_vb_img(context)
    finally:
        await context.close()
    await combine_imgs()
    return vb_file


async def _screenshot_vb_img(context: BrowserContext):
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

    await context.route("**/*", ad_block_handler)

    page = await context.new_page()
    await page.goto(url)

    # 截图函数，超时则跳过
    async def take_screenshot(locator: Locator, path: Path) -> None:
        try:
            # 检查元素内容是否为空
            content = await locator.inner_html()
            if content.strip():
                await asyncio.wait_for(locator.screenshot(path=path), timeout=5)
            else:
                logger.warning(f"Locator for {path.name} is empty.")
        except Exception:
            pass

    # 截取第一个 <div class="hot-info">
    hot_info_1 = page.locator("div.hot-info").nth(0)
    await take_screenshot(hot_info_1, hot_info_1_path)

    # 截取 <div class="container hidden-xs">
    container_hidden_xs = page.locator("div.container.hidden-xs")
    await take_screenshot(container_hidden_xs, container_hidden_xs_path)

    # 截取第二个 <div class="hot-info">
    hot_info_2 = page.locator("div.hot-info").nth(1)
    await take_screenshot(hot_info_2, hot_info_2_path)


async def combine_imgs():
    await asyncio.to_thread(_combine_imgs)


def _combine_imgs():
    # 打开截图文件（如果存在）
    combined_image = None
    img_paths = [hot_info_1_path, container_hidden_xs_path, hot_info_2_path]
    img_paths = [i for i in img_paths if i.exists()]
    if not img_paths:
        raise Exception("所有选择器的截图文件均不存在")
    # 先添加时间
    try:
        # images = [Image.open(img_path) for img_path in img_paths]
        with (
            Image.open(img_paths[0]) as img1,
            Image.open(img_paths[1]) as img2,
            Image.open(img_paths[2]) as img3,
        ):
            # 填充更新时间
            images = [img1, img2, img3]
            # 获取尺寸并创建新图像
            widths, heights = zip(*(img.size for img in images))
            total_width = max(widths)
            total_height = sum(heights)

            fill_img_with_time(img1, total_width)
            combined_image = Image.new("RGB", (total_width, total_height))

            # 将截图粘贴到新图像中
            y_offset = 0
            for img in images:
                combined_image.paste(img, (0, y_offset))
                y_offset += img.height

            # 保存合并后的图像
            combined_image.save(vb_file)
    finally:
        # 关闭并删除所有截图文件
        for img_path in img_paths:
            img_path.unlink()
        if combined_image:
            combined_image.close()


def fill_img_with_time(img: Image.Image, width: int = 1126):
    draw = ImageDraw.Draw(img)
    font_size = 26
    font = ImageFont.truetype(VB_FONT_PATH, font_size)
    time_text = time.strftime("Updated: %Y-%m-%d %H:%M:%S", time.localtime())
    time_text_width = draw.textlength(time_text, font=font)
    x = width - time_text_width - 10
    draw.text((x, 12), time_text, font=font, fill=(80, 80, 80))
