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
            # 截取第一个 <div class="hot-info">
            hot_info_1 = await page.locator('div.hot-info').nth(0)
            await hot_info_1.screenshot(path=data_dir / 'hot_info_1.png')
    
            # 截取 <div class="container hidden-xs">
            container_hidden_xs = await page.locator('div.container.hidden-xs')
            await container_hidden_xs.screenshot(path=data_dir / 'container_hidden_xs.png')
            # 截取第二个 <div class="hot-info">
            hot_info_2 = await page.locator('div.hot-info').nth(1)
            await hot_info_2.screenshot(path=data_dir / 'hot_info_2.png')
            combine()
    finally:
        if browser:
            await browser.close()
    
    return vb_file


        
def combine():
    try:
        # 打开三个截图
        hot_info_1 = Image.open(data_dir / 'hot_info_1.png')
        container_hidden_xs = Image.open(data_dir / 'container_hidden_xs.png')
        hot_info_2 = Image.open(data_dir / 'hot_info_2.png')
        
        # 获取每个截图的尺寸
        width1, height1 = hot_info_1.size
        width2, height2 = container_hidden_xs.size
        width3, height3 = hot_info_2.size
        
        # 创建一个新的图像，宽度为最宽的截图宽度，高度为三个截图高度之和
        total_width = max(width1, width2, width3)
        total_height = height1 + height2 + height3
        combined_image = Image.new('RGB', (total_width, total_height))
        
        # 将每个截图粘贴到新的图像中
        combined_image.paste(hot_info_1, (0, 0))
        combined_image.paste(container_hidden_xs, (0, height1))
        combined_image.paste(hot_info_2, (0, height1 + height2))
        
        # 保存合并后的图像
        combined_image.save(vb_file)
    finally:
        # 关闭所有打开的图像资源
        hot_info_1.close()
        container_hidden_xs.close()
        hot_info_2.close()
        combined_image.close()

async def screenshot_vb_img_old() -> Path:
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