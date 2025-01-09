import asyncio

from PIL import Image
from pathlib import Path
from playwright.async_api import async_playwright

from .config import data_dir

shop_file = data_dir / "shop.png"

async def screenshot_shop_img() -> Path:
    url = "https://fortnite.gg/shop"
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)  # 启动无头模式的 Chromium 浏览器
            # page = await browser.new_page()
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
            )
            page = await context.new_page()
            await page.goto(url, timeout=60000)  # 增加超时时间
            await page.mouse.move(100, 100)
            await page.mouse.click(100, 100)
            await page.wait_for_load_state('networkidle')  # 等待页面加载完成
            await page.screenshot(path=shop_file, full_page=True)  # 截取整个页面
        except Exception as e:
            raise e
        finally:
            await browser.close()
            
    return shop_file 

