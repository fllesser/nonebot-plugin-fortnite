import httpx
import asyncio

from PIL import Image
from pathlib import Path
from nonebot.log import logger
from playwright.async_api import async_playwright

from .config import data_dir, fconfig

shop_file = data_dir / "shop.png"

async def screenshot_shop_img() -> Path:
    url = "https://www.fortnite.com/item-shop?lang=zh-Hans"
    
    headers = {
      'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
      'Accept-Encoding': "gzip, deflate",
      'x-requested-with': "mark.chromium",
      'sec-fetch-site': "same-origin",
      'sec-fetch-mode': "no-cors",
      'sec-fetch-dest': "script",
      'referer': "https://www.fortnite.com/item-shop?lang=zh-Hans&__cf_chl_rt_tk=GXIQhKBq1Ku4R0Ko9ZdwpqowaqwQSkpbUVGJgkTRCEI-1736398895-1.0.1.1-NTcB9ua43wQOy7ZxZKSXFQvXTl7SZ1rqFLHgyHlddeE",
      'accept-language': "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
      'Cookie': "__cf_bm=q._ofOdPilOvXtYR92Rb.I_Uzruy8VSGbmr0uY_z0bs-1736398895-1.0.1.1-OrXATO8Ca2pzun3u5BLtaNQbgQwf8rABYQ4On6g4fKe.QZvGyoIWdAbAzAHdBq4OmFcgo_r.cwt1.bKh8cUGWQ"
    }
    
    token = await cf_token()
    logger.info(token)
    
    async with async_playwright() as p:
        async with p.chromium.launch(headless=True) as browser: 
            context = await browser.new_context()
            context.set_extra_http_headers(headers)
            # 设置 Cookie
            await context.add_cookies([{
                'name': "cf_clearance",
                'value': token,
                'url': url, # 确保与目标 URL 相匹配
                'domain': "www.fortnite.com" #
            }])

            page = await context.new_page()
            page.on('requestfailed', lambda request: logger.warning(f'Request failed: {request.url}'))
            await page.add_style_tag(content='* { transition: none !important; animation: none !important; }')
            await page.goto(url, wait_until='networkidle', timeout=60000)
            # await page.wait_for_load_state('load')  # 等待页面加载完毕
            await page.screenshot(path=shop_file, full_page=True)
            return shop_file


async def cf_token():
    url = "https://api.scrapeless.com/api/v1/createTask"
    token = fconfig.captcha_api_key
    headers = {"x-api-token": token}
    input = {
        "version": "v1",
        "pageURL": "https://www.fortnite.com/item-shop?lang=zh-Hans",
        "siteKey": "0x4AAAAAAADnPIDROrmt1Wwj",
    }
    payload = {
        "actor": "captcha.turnstile",
        "input": input
    }

    # Create task
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload, headers=headers)
    result = resp.json()    
    taskId = result.get("taskId")
    if not taskId:
        raise Exception(f"Failed to create task:, {result}")

    # Poll for result
    async with httpx.AsyncClient() as client:
        for i in range(30):
            await asyncio.sleep(1)
            url = "https://api.scrapeless.com/api/v1/getTaskResult/" + taskId
            resp = await client.get(url, headers=headers)
            result = resp.json()
            if resp.status_code != 200:
                raise Exception(str(resp))
            if result.get("success"):
                return result["solution"]["token"]
