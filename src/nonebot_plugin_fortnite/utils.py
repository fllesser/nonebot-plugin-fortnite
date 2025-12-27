import time
import asyncio
from pathlib import Path

import httpx
import aiofiles
from PIL import Image
from nonebot import logger

from .config import fconfig

TRIGGER_SCREENSHOT_TIP = (
    "Trigger screenshot action, "
    "https://github.com/fllesser/nonebot-plugin-fortnite/actions/workflows/screenshot.yml"
)


async def trigger_screenshot_action():
    url = "https://api.github.com/repos/fllesser/nonebot-plugin-fortnite/actions/workflows/screenshot.yml/dispatches"
    headers = {"Authorization": f"token {fconfig.github_token}"}
    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.post(url, json={"ref": "master"})
        response.raise_for_status()

    logger.info(TRIGGER_SCREENSHOT_TIP)


async def save_img(img: Image.Image, path: Path, format: str = "PNG"):
    from io import BytesIO

    buffer = BytesIO()
    img.save(buffer, format=format)
    img_data = buffer.getvalue()
    async with aiofiles.open(path, "wb") as f:
        await f.write(img_data)


def get_size_in_mb(path: Path):
    return path.stat().st_size / 1024 / 1024


def retry(times: int = 3, delay: float = 5):
    from functools import wraps

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for i in range(times):
                try:
                    return await func(*args, **kwargs)
                except Exception:
                    logger.warning(f"Error in {func.__name__}, retry {i + 1}/{times}")
                    if i == times - 1:
                        raise
                    await asyncio.sleep(delay)

        return wrapper

    return decorator


def get_utc_day() -> str:
    """获取当前 UTC 日期字符串，格式为 YYYY-MM-DD"""
    return time.strftime("%Y-%m-%d", time.gmtime())


def get_github_file_url(file_name: str) -> str:
    return f"{fconfig.raw_base_url}/screenshots/{file_name}"


def clear_files_with_prefix(prefix: str):
    for file in fconfig.data_dir.glob(f"{prefix}*.png"):
        file.unlink()
