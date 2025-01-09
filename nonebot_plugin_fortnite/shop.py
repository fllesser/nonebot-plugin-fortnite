import httpx
import asyncio

from PIL import Image
from pathlib import Path
from playwright.async_api import async_playwright

from .config import data_dir, fconfig

shop_file = data_dir / "shop.png"

async def screenshot_shop_img() -> Path:
    url = "https://fortnite.gg/shop"
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)  # 启动无头模式的 Chromium 浏览器
            # page = await browser.new_page()
            context = await browser.new_context()
            
            token = await cf_token()
            # 设置 Cookie
            await context.add_cookies([{
                'name': "cf_clearance",
                'value': token,
                'url': url, # 确保与目标 URL 相匹配
                'domain': "fortnite.gg" #
            }])

            page = await context.new_page()
            await page.goto(url)
            await page.wait_for_load_state('load')  # 等待页面加载完毕
            await page.screenshot(path=shop_file, full_page=True)
        except Exception as e:
            raise e
        finally:
            await browser.close()
            
    return shop_file


async def cf_token():
    url = "https://api.scrapeless.com/api/v1/createTask"
    token = fconfig.captcha_api_key
    headers = {"x-api-token": token}
    input = {
        "version": "{{version}}",
        "pageURL": "https://fortnite.gg/shop",
        "siteKey": "1x00000000000000000000AA",
        "action": "",
        "cdata": ""
    }
    payload = {
        "actor": "captcha.turnstile",
        "input": input
    }

    # Create task
    async with httpx.AsyncClient() as client:
        result = await client.post(url, json=payload, headers=headers).json()
    taskId = result.get("taskId")
    if not taskId:
        # print("Failed to create task:", result)
        return

    # Poll for result
    for i in range(10):
        asyncio.sleep(0)
        url = "https://api.scrapeless.com/api/v1/getTaskResult/" + taskId
        resp = requests.get(url, headers=headers)
        result = resp.json()
        if resp.status_code != 200:
            return
        if result.get("success"):
            return result["solution"]["token"]





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