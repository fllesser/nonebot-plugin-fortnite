import asyncio
import hashlib
from io import BytesIO
from typing import Any
from pathlib import Path
from functools import cache

import httpx
import aiofiles
from PIL import Image, ImageDraw, ImageFont
from fortnite_api import Client
from fortnite_api.enums import TimeWindow, StatsImageType
from fortnite_api.errors import FortniteAPIException

from .config import CHINESE_FONT_PATH, fconfig

API_KEY: str | None = fconfig.fortnite_api_key
STATS_BG_PATH = Path(__file__).parent / "resources" / "stats_bg.png"


@cache
def create_gradient_image_new() -> Image.Image:
    """从底图裁剪渐变图片"""
    left, top, right, bottom = 26, 90, 423, 230

    with Image.open(STATS_BG_PATH) as img:
        gradient_img = img.crop((left, top, right, bottom))
        gradient_img.load()
        return gradient_img


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
    time_window: Any = (
        TimeWindow.LIFETIME if cmd_header.startswith("生涯") else TimeWindow.SEASON
    )
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
    time_window: Any = (
        TimeWindow.LIFETIME if cmd_header.startswith("生涯") else TimeWindow.SEASON
    )
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

    img_bytes = await get_stats_img_by_url(stats.image.url, stats.user.name)

    hash_str = hashlib.md5(f"{name}{cmd_header}".encode()).hexdigest()
    file_path = fconfig.data_dir / f"{hash_str}.png"

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(img_bytes.getvalue())

    return file_path


async def get_stats_img_by_url(url: str, name: str) -> BytesIO:
    async with httpx.AsyncClient(verify=False, timeout=15) as client:
        # 发送GET请求获取图片数据
        response = await client.get(url)

        # 检查请求是否成功
        if response.status_code != 200:
            raise ValueError(f"无法获取图片, 状态码: {response.status_code}")

        # 将响应内容转换为字节流
        image_data = BytesIO(response.content)
    # 如果不包含中文名，返回原图
    if not contains_chinese(name):
        return image_data

    return await process_image_with_chinese(image_data, name)


def contains_chinese(text: str) -> bool:
    import re

    pattern = re.compile(r"[\u4e00-\u9fff]")
    return bool(pattern.search(text))


async def process_image_with_chinese(file: BytesIO, name: str) -> BytesIO:
    return await asyncio.to_thread(_process_image_with_chinese, file, name)


def _process_image_with_chinese(bytes_io: BytesIO, name: str) -> BytesIO:
    with Image.open(bytes_io, formats=["PNG"]) as img:
        draw = ImageDraw.Draw(img)

        # 矩形区域的坐标
        left, top, right, bottom = 26, 90, 423, 230

        # 创建渐变色并填充矩形区域
        # width = right - left, height = bottom - top
        gradient_img = create_gradient_image_new()
        img.paste(gradient_img, (left, top))
        # 指定字体
        font_size = 36
        font = ImageFont.truetype(CHINESE_FONT_PATH, font_size)

        # 计算字体坐标
        length = draw.textlength(name, font=font)
        x = left + (right - left - length) / 2
        y = top + (bottom - top - font_size) / 2
        draw.text((x, y), name, fill="#fafafa", font=font)

        output_bytes = BytesIO()
        # 保存处理后的图像到 BytesIO
        img.save(output_bytes, format="PNG", optimize=True)
        # 将指针重置到 BytesIO 对象的开头
        output_bytes.seek(0)

        return output_bytes
