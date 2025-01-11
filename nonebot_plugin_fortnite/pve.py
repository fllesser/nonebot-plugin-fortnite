import asyncio
from PIL import Image
from pathlib import Path
from playwright.async_api import async_playwright
from .config import data_dir

vb_file = data_dir / "vb.png"
hot_info_1_path = data_dir / 'hot_info_1.png'
container_hidden_xs_path = data_dir / 'container_hidden_xs.png'
hot_info_2_path = data_dir / 'hot_info_2.png'

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
                 
                    # 检查元素内容是否为空
                    content = await locator.inner_html()
                    if content.strip():  # 如果内容不为空
                        await asyncio.wait_for(locator.screenshot(path=path), timeout=5)
                    else:
                        logger.warning(f"Locator for {path.name} is empty.")
                except Exception:
                    pass
                    
            
            # 截取第一个 <div class="hot-info">
            hot_info_1 = page.locator('div.hot-info').nth(0)
            await take_screenshot(hot_info_1, hot_info_1_path)
            
            # 截取 <div class="container hidden-xs">
            container_hidden_xs = page.locator('div.container.hidden-xs')
            await take_screenshot(container_hidden_xs, container_hidden_xs_path)
            
            # 截取第二个 <div class="hot-info">
            hot_info_2 = page.locator('div.hot-info').nth(1)
            await take_screenshot(hot_info_2, hot_info_2_path)
            
            combine_imgs()
    finally:
        if browser:
            await browser.close()
    
    return vb_file

def combine_imgs():
    try:
        # 打开截图文件（如果存在）
        images = []
        image_paths = [hot_info_1_path, container_hidden_xs_path, hot_info_2_path]
        for image_path in image_paths:
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
        for img_path in image_paths:
            if img_path.exists():
                img_path.filename.unlink()
        combined_image.close()
