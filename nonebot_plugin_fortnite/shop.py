import asyncio

from PIL import Image
from pathlib import Path
from playwright.async_api import async_playwright

from .config import data_dir

shop_file = data_dir / "shop.png"

async def screenshot_shop_img() -> Path:
    url = "https://www.fortnite.com/item-shop?lang=zh-Hans"
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)  # 启动无头模式的 Chromium 浏览器
            page = await browser.new_page()
            await page.goto('https://www.fortnite.com/item-shop?lang=zh-Hans', timeout=60000)  # 增加超时时间
            await page.wait_for_load_state('networkidle')  # 等待页面加载完成
            await page.screenshot(path=shop_file, full_page=True)  # 截取整个页面
        except Exception as e:
            raise e
        finally:
            await browser.close()
            
    return shop_file 
