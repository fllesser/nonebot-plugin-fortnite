import asyncio

from PIL import Image
from pathlib import Path
from playwright.async_api import async_playwright

from .config import data_dir

shop_file = data_dir / "shop.png"

async def screenshot_shop_img() -> Path:
    url = "https://fnitemshop.com"
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)  # 启动无头模式的 Chromium 浏览器
            context = await browser.new_context(
                viewport={"width": 1320, "height": 2868},  # 设.
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A5341f Safari/604.1"
            )
            page = await context.new_page()
            await page.goto(url)
            await page.wait_for_load_state('load')  # 等待页面加载完毕
            await page.screenshot(path=shop_file, full_page=True)
            await browser.close()
        except Exception as e:
            raise e
        finally:
            await browser.close()
            
    return shop_file 



# async def solve_turnstile(logger: 'loguru.Logger', url: str, user_agent: str, user_data_path: str = None):
#     import asyncio
#     from DrissionPage import ChromiumPage, ChromiumOptions
#     options = (
#         ChromiumOptions()
#         .auto_port()
#         .headless()
#         .incognito(True)
#         .set_user_agent(user_agent)
#         .set_argument('--guest')
#         .set_argument('--no-sandbox')
#         .set_argument('--disable-gpu')
#     )
#     if user_data_path:
#         options.set_user_data_path(user_data_path)
#     page = ChromiumPage(options)
#     page.screencast.set_save_path('turnstile')
#     page.screencast.set_mode.video_mode()
#     page.screencast.start()
#     page.get(url)
#     logger.debug('waiting for turnstile')
#     await asyncio.sleep(2)
#     divs = page.eles('tag:div', timeout=10)
#     iframe = None
#     for div in divs:
#         if div.shadow_root:
#             iframe = div.shadow_root.ele(
#                 "xpath://iframe[starts-with(@src, 'https://challenges.cloudflare.com/')]",
#                 timeout=0
#             )
#             if iframe:
#                 break
#             break
#     body_element = iframe.ele('tag:body', timeout=10).shadow_root
#     logger.debug('waiting for text:Verify you are human')
#     verify_element = body_element.ele("text:Verify you are human", timeout=10)
#     await asyncio.sleep(1)
#     logger.debug('click verify')
#     verify_element.offset(10, 10).click(by_js=False)
#     logger.debug('waiting for deleted')
#     verify_element.wait.deleted(timeout=10)
#     await asyncio.sleep(1)
#     page.screencast.stop()
#     page.close()