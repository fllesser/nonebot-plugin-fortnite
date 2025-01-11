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
            
            # Check and screenshot the first <div class="hot-info">
            hot_info_1 = page.locator('div.hot-info').nth(0)
            if await hot_info_1.count() > 0:
                await hot_info_1.screenshot(path=data_dir / 'hot_info_1.png')
            
            # Check and screenshot <div class="container hidden-xs">
            container_hidden_xs = page.locator('div.container.hidden-xs')
            if await container_hidden_xs.count() > 0:
                await container_hidden_xs.screenshot(path=data_dir / 'container_hidden_xs.png')
            
            # Check and screenshot the second <div class="hot-info">
            hot_info_2 = page.locator('div.hot-info').nth(1)
            if await hot_info_2.count() > 0:
                await hot_info_2.screenshot(path=data_dir / 'hot_info_2.png')
            
            combine_imgs()
    finally:
        if browser:
            await browser.close()
    
    return vb_file

def combine_imgs():
    try:
        # Open the screenshots if they exist
        images = []
        for img_name in ['hot_info_1.png', 'container_hidden_xs.png', 'hot_info_2.png']:
            img_path = data_dir / img_name
            if img_path.exists():
                images.append(Image.open(img_path))
        
        # Get dimensions and create a new image
        widths, heights = zip(*(img.size for img in images))
        total_width = max(widths)
        total_height = sum(heights)
        combined_image = Image.new('RGB', (total_width, total_height))
        
        # Paste images into the new image
        y_offset = 0
        for img in images:
            combined_image.paste(img, (0, y_offset))
            y_offset += img.height
        
        # Save the combined image
        combined_image.save(vb_file)
    finally:
        # Close all opened images
        for img in images:
            img.close()
        combined_image.close()
