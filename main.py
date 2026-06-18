import asyncio
import aiohttp
import sys
from config import MAX_BOT_TOKEN, MAX_API_URL

async def main():
    print("🚀 [МаркX] Бот успешно запущен и готов к работе!")
    print(f"📡 Токен связи подгружен: {str(MAX_BOT_TOKEN)[:5]}***")

    async with aiohttp.ClientSession() as session:
        while True:
            await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Бот остановлен.")
        sys.exit(0)
