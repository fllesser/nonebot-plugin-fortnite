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
            
            # 截图函数，超时则跳过
            async def take_screenshot(locator, path):
                try:
                    await locator.scroll_into_view_if_needed()
                    await locator.wait_for_element_state('visible', timeout=5000)
                    await locator.screenshot(path=path)
                except Exception:
                    pass
            
            # 截取第一个 <div class="hot-info">
            hot_info_1 = page.locator('div.hot-info').nth(0)
            await take_screenshot(hot_info_1, data_dir / 'hot_info_1.png')
            
            # 截取 <div class="container hidden-xs">
            container_hidden_xs = page.locator('div.container.hidden-xs')
            await take_screenshot(container_hidden_xs, data_dir / 'container_hidden_xs.png')
            
            # 截取第二个 <div class="hot-info">
            hot_info_2 = page.locator('div.hot-info').nth(1)
            await take_screenshot(hot_info_2, data_dir / 'hot_info_2.png')
            
            combine_imgs()
    finally:
        if browser:
            await browser.close()
    
    return vb_file

def combine_imgs():
    try:
        # 打开截图文件（如果存在）
        images = []
        for img_name in ['hot_info_1.png', 'container_hidden_xs.png', 'hot_info_2.png']:
            img_path = data_dir / img_name
            if img_path.exists():
                images.append(Image.open(img_path))
        
        # 获取尺寸并创建新图像
        widths, heights = zip(*(img.size for img in images))
        total_width = max(widths)
        total_height = sum(heights)
        combined_image = Image.new('RGB', (total_width, total_height))
        
        # 将截图粘贴到新图像中
        y_offset = 0
        for img in images:
            combined_image.paste(img, (0, y_offset))
            y_offset += img.height
        
        # 保存合并后的图像
        combined_image.save(vb_file)
    finally:
        # 关闭并删除所有截图文件
        for img in images:
            img.close()
            img_path = data_dir / img.filename
            if img_path.exists():
                img_path.unlink()
        combined_image.close()
