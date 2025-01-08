import asyncio

from PIL import Image
from pathlib import Path
from playwright.async_api import async_playwright

from .config import cache_dir

vb_file = cache_dir / "vb.png"

async def screenshot_vb_img() -> Path:
    url = "https://freethevbucks.com/timed-missions"
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)  # 启动无头模式的 Chromium 浏览器
            page = await browser.new_page()
            await page.goto(url)  # 打开指定 URL
            element = await page.query_selector('.infonotice')
            await element.screenshot(path=vb_file)  # 截取整个页面
        except Exception as e:
            raise e
        finally:
            await browser.close()
    
    with Image.open(vb_file) as img:
        width, height = img.size

        # 定义裁剪区域 (左, 上, 右, 下)
        left = 0
        top = 0
        right = width - 500
        bottom = height
        
        # 确保裁剪区域在图像范围内
        right = max(right, 0)  # 确保右边界不小于 0
        
        # 裁剪图像
        cropped_img = img.crop((left, top, right, bottom))
        cropped_img.save(vb_file)
    
    return vb_file



# import time
# import httpx

# from bs4 import BeautifulSoup
# from PIL import (
#     Image,
#     ImageFont
# )
# from PIL.Image import Resampling
# from io import BytesIO
# from pathlib import Path

# from .config import cache_dir, data_dir

# ele_icon_file: Path = data_dir / 'ele_icon.png'
# vb_icon_file: Path = data_dir / 'vb_icon.png'

# async def update_daily_vb() -> str:
#     url = "https://freethevbucks.com/timed-missions/"
#     vb_url = "https://freethevbucks.com/wp-content/uploads/cropped-v-bucks-3-32x32.png"
#     ele_url = "https://img.icons8.com/office/30/000000/lightning-bolt.png"
    
#     # 爬去数据，下载图标
#     async with httpx.AsyncClient() as client:
#         free_resp = await client.get(url)
#         if not ele_icon_file.exists():
#             ele_resp = await client.get(ele_url)
#             with open(ele_icon_file, 'wb') as f:
#                 f.write(ele_resp.content)
#         if not vb_icon_file.exists():
#             vb_resp = await client.get(vb_url)
#             with open(vb_icon_file, 'wb') as f:
#                 f.write(vb_resp.content)
#     # bs4 解析html
#     soup = BeautifulSoup(free_resp.content, "lxml")
    
#     # 电力图标
#     ele_icon_img = Image.open(ele_icon_file)
#     ele_icon_img = ele_img.resize((15, 15), Resampling.LANCZOS)
#     # vb图标
#     vb_icon_img = Image.open(vb_icon_file)
#     vb_icon_img = vb_icon.resize((15, 15), Resampling.LANCZOS)
#     # vb图
#     img = BuildImage(width=256, height=220, font_size=15,
#                     color=(36, 44, 68), font= FONT_PATH / "gorga.otf")
#     # 起始纵坐标
#     Y = 30
#     timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#     await img.text(pos=(0, 185), text=timestr, center_type="width", fill=(255, 255, 255))
#     for item in soup.find_all("p"):
#         if item.span is not None and item.span.b is not None:
#             if not item.img:
#                 continue
#             storm_src = item.img.get("src")  # 风暴图标链接
#             async with httpx.AsyncClient() as client:
#                 resp = await client.get(storm_src)
#             storm_img = Image.open(BytesIO(resp.content))
#             await img.paste(image=storm_img, pos=(40, Y))  # 风暴图标
#             # 电力
#             await img.text(text=item.b.string, pos=(70, Y - 3), fill=(255, 255, 255))
#             await img.paste(image=ele_img, pos=(88, Y + 2))  # 电力图标
#             vb_num: str = item.span.text.split(",")[0]
#             await img.paste(image=vb_icon, pos=(113, Y + 2)) 
#             await img.text(pos=(130, Y - 3), text=vb_num, fill=(255, 255, 255))
#             Y += 30
#     if Y == 30:
#         img.font = ImageFont.truetype(str(FONT_PATH / "SourceHanSansSC-Bold-2.otf"), 30)
#         await img.text(pos=(0, 80), text="今天没有vb图捏", center_type="width", fill=(255, 255, 255))
#     await img.save(IMG_PATH / "fn_stw.png")
#     return "fn_stw.png"