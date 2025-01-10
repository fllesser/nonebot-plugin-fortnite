import httpx
import asyncio

from io import BytesIO
from pathlib import Path
from nonebot import get_driver
from nonebot.log import logger

from PIL import (
    Image,
    ImageFont, 
    ImageDraw
)

from .config import (
    fconfig,
    cache_dir, 
    data_dir
)

from fortnite_api import (
    Client,
    BrPlayerStats,
    StatsImageType,
    TimeWindow
)

from .other import exception_handler

api_key = fconfig.fortnite_api_key

async def get_stats(
    name: str, 
    time_window: TimeWindow = TimeWindow.SEASON,
    image_type: StatsImageType = None
) -> BrPlayerStats:
    params = {
        'name': name,
        'time_window': time_window
    }
    if image_type:
        params['image'] = image_type
    async with Client(api_key=api_key) as client:
        return await client.fetch_br_stats(**params)

@exception_handler()        
async def get_level(name: str, time_window: str) -> int:
    time_window = TimeWindow.LIFETIME if time_window.startswith("生涯") else TimeWindow.SEASON
    stats = await get_stats(name, time_window)
    bp = stats.battle_pass
    return f'{stats.user.name}: Lv{bp.level} | {bp.progress}% to Lv{bp.level + 1}'

@exception_handler()
async def get_stats_image(name: str, time_window: str) -> Path:
    time_window = TimeWindow.LIFETIME if time_window.startswith("生涯") else TimeWindow.SEASON
    stats = await get_stats(name, time_window, StatsImageType.ALL)
    return await get_stats_img_by_url(stats.image.url, stats.user.name)
    

font_path: Path | None = None

@get_driver().on_startup
async def _():
    hans = data_dir / "SourceHanSansSC-Bold-2.otf"
    global font_path
    if hans.exists():
        font_path = hans
        logger.info(f'战绩绘图将使用字体: {font_path.name}')
    else:
        logger.warning(f"请前往仓库下载字体到 {data_dir}/，否则战绩查询可能无法显示中文名称")
    
async def get_stats_img_by_url(url: str, name: str) -> Path:
    file = cache_dir / f"{name}.png"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()
        
    with open(file, "wb") as f:
        f.write(resp.content)
    # 如果不包含中文名，返回
    if not font_path or not contains_chinese(name):
        return file
    
    with Image.open(file) as img:
        draw = ImageDraw.Draw(img)

        # 矩形区域的坐标
        left, top, right, bottom = 26, 90, 423, 230

        # 创建渐变色并填充矩形区域
        width = right - left
        height = bottom - top
        
        start_color = (0, 33, 69, 255)
        end_color = (0, 82, 106, 255)
        for i in range(width):
            for j in range(height):
                r = int(start_color[0] + (end_color[0] - start_color[0]) * (i + j) / (width + height))
                g = int(start_color[1] + (end_color[1] - start_color[1]) * (i + j) / (width + height))
                b = int(start_color[2] + (end_color[2] - start_color[2]) * (i + j) / (width + height))
                draw.point((left + i, top + j), fill=(r, g, b))
        
        # 指定字体
        font_size = 36
        # hansans = data_dir / "SourceHanSansSC-Bold-2.otf"
        font = ImageFont.truetype(font_path, font_size)
        
        # 计算字体坐标
        length = draw.textlength(name, font=font)
        x = left + (right - left - length) / 2
        y = top + (bottom - top - font_size) / 2
        draw.text((x, y), name, fill = "#fafafa", font = font)
        
        # 保存
        img.save(file)
        return file
    
def contains_chinese(text):
    import re
    pattern = re.compile(r'[\u4e00-\u9fff]')
    return bool(pattern.search(text))
