from pathlib import Path
from typing import Any

import aiofiles
from fortnite_api import Client
from fortnite_api.enums import StatsImageType, TimeWindow
from fortnite_api.errors import FortniteAPIException
import httpx
from PIL import Image, ImageDraw, ImageFont

from .config import cache_dir, data_dir, fconfig

API_KEY: str = fconfig.fortnite_api_key


def handle_fortnite_api_exception(e: FortniteAPIException) -> str:
    err_msg = str(e)
    if "public" in err_msg:
        return "战绩未公开"
    elif "exist" in err_msg:
        return "用户不存在"
    elif "match" in err_msg:
        return "该玩家当前赛季没有进行过任何对局"
    elif "timed out" in err_msg:
        return "请求超时, 请稍后再试"
    elif "failed to fetch" in err_msg:
        return "拉取账户信息失败, 稍后再试"
    else:
        return f"未知错误: {err_msg}"


async def get_level(name: str, cmd_header: str) -> str:
    time_window: Any = TimeWindow.LIFETIME if cmd_header.startswith("生涯") else TimeWindow.SEASON
    try:
        async with Client(api_key=API_KEY) as client:
            stats = await client.fetch_br_stats(name=name, time_window=time_window)
    except FortniteAPIException as e:
        return handle_fortnite_api_exception(e)
    bp = stats.battle_pass
    if bp is None:
        return f"未查询到 {stats.user.name} 的季卡等级"
    return f"{stats.user.name}: Lv{bp.level} | {bp.progress}% to Lv{bp.level + 1}"


async def get_stats_image(name: str, cmd_header: str) -> Path:
    time_window: Any = TimeWindow.LIFETIME if cmd_header.startswith("生涯") else TimeWindow.SEASON
    image_type: Any = StatsImageType.ALL
    try:
        async with Client(api_key=API_KEY) as client:
            stats = await client.fetch_br_stats(
                name=name,
                time_window=time_window,
                image=image_type,
            )
    except FortniteAPIException as e:
        raise ValueError(handle_fortnite_api_exception(e))
    if stats.image is None:
        raise ValueError(f"未查询到 {stats.user.name} 的战绩")
    return await get_stats_img_by_url(stats.image.url, stats.user.name)


font_path: Path = data_dir / "SourceHanSansSC-Bold-2.otf"


async def check_font_file() -> bool:
    from nonebot import logger

    if not font_path.exists():
        # 下载 字体 githubraw https://github.com/fllesser/nonebot-plugin-fortnite/blob/master/fonts/SourceHanSansSC-Bold-2.otf
        import aiofiles
        import httpx

        url = (
            "https://raw.githubusercontent.com/fllesser/nonebot-plugin-fortnite/master/fonts/SourceHanSansSC-Bold-2.otf"
        )
        logger.info(f"字体文件不存在，开始从 {url} 下载字体...")
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.get(url)
            response.raise_for_status()
            font_data = response.content

            async with aiofiles.open(font_path, "wb") as f:
                await f.write(font_data)

            logger.success(f"字体 {font_path.name} 下载成功，文件大小: {font_path.stat().st_size / 1024 / 1024:.2f} MB")
        except Exception as e:
            logger.error(f"字体下载失败: {e}")
            logger.warning(f"请前往仓库下载字体到 {data_dir}/，否则战绩查询可能无法显示中文名称")
            return False
    return True


async def get_stats_img_by_url(url: str, name: str) -> Path:
    file = cache_dir / f"{name}.png"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
    resp.raise_for_status()

    async with aiofiles.open(file, "wb") as f:
        await f.write(resp.content)
    # 如果不包含中文名，返回原图
    if not (await check_font_file()) or not contains_chinese(name):
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
        draw.text((x, y), name, fill="#fafafa", font=font)

        # 保存
        img.save(file)
        return file


def contains_chinese(text):
    import re

    pattern = re.compile(r"[\u4e00-\u9fff]")
    return bool(pattern.search(text))
