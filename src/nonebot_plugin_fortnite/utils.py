import asyncio
from pathlib import Path

import httpx
import aiofiles
from PIL import Image
from nonebot import logger

from .config import fconfig


async def dispatch_screenshot_action():
    url = "https://api.github.com/repos/fllesser/nonebot-plugin-fortnite/actions/workflows/screenshot.yml/dispatches"
    headers = {"Authorization": f"token {fconfig.github_token}"}
    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.post(url, json={"ref": "master"})
        response.raise_for_status()
        logger.info("trigger screenshot github workflow successfully")


async def save_img(img: Image.Image, path: Path, format: str = "PNG"):
    from io import BytesIO

    buffer = BytesIO()
    img.save(buffer, format=format)
    img_data = buffer.getvalue()
    async with aiofiles.open(path, "wb") as f:
        await f.write(img_data)


def get_size_in_mb(path: Path):
    return path.stat().st_size / 1024 / 1024


def retry(retries: int = 3, delay: float = 3):
    from functools import wraps

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for i in range(retries):
                try:
                    return await func(*args, **kwargs)
                except Exception:
                    logger.warning(f"Error in {func.__name__}, retry {i + 1}/{retries}")
                    if i == retries - 1:
                        raise
                    await asyncio.sleep(delay)

        return wrapper

    return decorator
