import asyncio

from PIL import Image
from pathlib import Path
from playwright.async_api import async_playwright

from .config import data_dir

vb_file = data_dir / "vb.png"

async def screenshot_vb_img() -> Path:
    url = "https://freethevbucks.com/timed-missions"
    
    try:
        browser = None
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url)  
            element = await page.query_selector('.infonotice')
            await element.screenshot(path=vb_file)  
    finally:
        if browser:
            await browser.close()
    
    with Image.open(vb_file) as img:
        width, height = img.size

        # 定义裁剪区域 (左, 上, 右, 下)
        left = 0
        top = 0
        right = width - 600
        bottom = height
        
        # 确保裁剪区域在图像范围内
        right = max(right, 0)  # 确保右边界不小于 0
        
        # 裁剪图像
        cropped_img = img.crop((left, top, right, bottom))
        cropped_img.save(vb_file)
    
    return vb_file
