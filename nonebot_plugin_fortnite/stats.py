import asyncio
from .config import fconfig

api_key = fconfig.fortnite_api_key

from fortnite_api import (
    Client,
    StatsImageType
)

async def get_level(name: str = "墨茶OfficiaI") -> int:
    async with Client(api_key=api_key) as client:
        stats = await client.fetch_br_stats(name=name)
        bp = stats.battle_pass
        return f'等级: {bp.level} 进度: {bp.progress}%'

async def get_stats_image(name: str = "墨茶OfficiaI") -> str:
    async with Client(api_key=api_key) as client:
        stats = await client.fetch_br_stats(name=name, image=StatsImageType.ALL)
        return stats.image.url
        

# async def main():
#   print(await get_level())
#   print(await get_stats_image())

# if __name__ == "__main__":
#   asyncio.run(main())
   