import httpx
import asyncio

# from pathlib import Path
from .config import fconfig
from .other import exception_handler
from fortnite_api import (
    Client,
    StatsImageType,
    TimeWindow
)

api_key = fconfig.fortnite_api_key

@exception_handler()
async def get_level(name: str, time_window: str) -> int:
    async with Client(api_key=api_key) as client:
        stats = await client.fetch_br_stats(
            name=name,
            time_window=TimeWindow.LIFETIME if time_window else TimeWindow.SEASON
        )
    bp = stats.battle_pass
    return f'等级: {bp.level} 下一级进度: {bp.progress}%'

@exception_handler()
async def get_stats_image(name: str, time_window: str) -> str:
    async with Client(api_key=api_key) as client:
        stats = await client.fetch_br_stats(
            name=name,
            image=StatsImageType.ALL,
            time_window=TimeWindow.LIFETIME if time_window else TimeWindow.SEASON
        )
    return stats.image.url
      

# async def write_cn_name(url: str, nickname: str):
#     # 打开原始图像
#     image = Image.open(IMG_PATH / "zhanji.png")
#     async with httpx.AsyncClient() as client:
#         resp = await client.get(url)
#     im = Image.open(BytesIO(resp.content))
#     draw = ImageDraw.Draw(im)
    
#     # 矩形区域的坐标
#     left, top, right, bottom = 26, 90, 423, 230
#     # 获取渐变色的起始和结束颜色
#     start_color = image.getpixel((left, top))
#     end_color = image.getpixel((right, bottom))
    
#     # 创建渐变色并填充矩形区域
#     width = right - left
#     height = bottom - top
    
#     for i in range(width):
#         for j in range(height):
#             r = int(start_color[0] + (end_color[0] - start_color[0]) * (i + j) / (width + height))
#             g = int(start_color[1] + (end_color[1] - start_color[1]) * (i + j) / (width + height))
#             b = int(start_color[2] + (end_color[2] - start_color[2]) * (i + j) / (width + height))
#             draw.point((left + i, top + j), fill=(r, g, b))

#     font_size = 36
#     hansans = (FONT_PATH / "SourceHanSansSC-Bold-2.otf").absolute()
#     font = ImageFont.truetype(hansans, font_size)
#     length = draw.textlength(nickname, font=font)
#     x = left + (right - left - length) / 2
#     y = top + (bottom - top - font_size) / 2
#     draw.text((x, y), nickname, fill = "#fafafa", font = font)
#     buffered = BytesIO() 
#     im.save(buffered, format="PNG") 
#     return base64.b64encode(buffered.getvalue()).decode()
