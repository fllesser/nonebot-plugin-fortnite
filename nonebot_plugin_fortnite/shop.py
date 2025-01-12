import httpx
import asyncio

from PIL import Image
from pathlib import Path
from nonebot.log import logger
from playwright.async_api import async_playwright

from .config import data_dir

shop_file = data_dir / "shop.png"

async def screenshot_shop_img() -> Path:
    # url = "https://www.fortnite.com/item-shop?lang=zh-Hans"
    url = "https://fortnite.gg/shop"
    
    headers = {
      'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
      'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
      'Accept-Encoding': "gzip, deflate",
      'upgrade-insecure-requests': "1",
      'dnt': "1",
      'x-requested-with': "mark.via",
      'sec-fetch-site': "none",
      'sec-fetch-mode': "navigate",
      'sec-fetch-user': "?1",
      'sec-fetch-dest': "document",
      'accept-language': "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
      'Cookie': "_sharedid=f02028dd-dce2-4b07-bba9-301d54e68dbd; _sharedid_cst=zix7LPQsHA%3D%3D; _lr_env_src_ats=false; hb_insticator_uid=799b5897-b5a3-48c4-a46f-8bb8bf9082ac"
    }
        
    # token = await cf_token()
    # logger.info(token)
    browser = None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(extra_http_headers = headers)
            page = await context.new_page()
            # page.on('requestfailed', lambda request: logger.warning(f'Request failed: {request.url}'))
            await page.add_style_tag(content='* { transition: none !important; animation: none !important; }')
            await page.goto(url)

            async def wait_for_load():
                await page.wait_for_load_state('networkidle', timeout=90000)            
            
            async def scroll_page():
                for _ in range(20):
                    await page.evaluate("""() => {
                        window.scrollBy(0, document.body.scrollHeight / 20);
                    }""")
                    await asyncio.sleep(1)  # 等待1秒以加载内容
            
            await asyncio.gather(
                wait_for_load(),
                scroll_page()
            )
            
            await page.screenshot(path=shop_file, full_page=True)
            return shop_file
    finally:
        await browser.close()

