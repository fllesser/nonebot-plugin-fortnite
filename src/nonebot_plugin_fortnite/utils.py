from pathlib import Path

import aiofiles
from PIL import Image


async def save_img(img: Image.Image, path: Path, format: str = "PNG"):
    from io import BytesIO

    buffer = BytesIO()
    img.save(buffer, format=format)
    img_data = buffer.getvalue()
    async with aiofiles.open(path, "wb") as f:
        await f.write(img_data)
