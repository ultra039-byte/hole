import asyncio
import sys
import aiohttp
from aiohttp import web
from config import MAX_BOT_TOKEN, MAX_API_URL

# Сюда MAX сам пришлет сообщение, когда тебе кто-то напишет
async def handle_webhook(request):
    try:
        data = await request.json()
        print(f"📩 Прилетело сообщение от MAX: {data}", flush=True)
        return web.Response(text="OK", status=200)
    except Exception as e:
        print(f"❌ Ошибка: {e}", flush=True)
        return web.Response(text="Error", status=500)

async def main():
    print("🔥 МАРК X ПЕРЕВЕДЕН В РЕЖИМ ОЖИДАНИЯ (ТИШИНА) 🔥", flush=True)
    
    app = web.Application()
    app.router.add_post("/", handle_webhook)
    app.router.add_get("/", lambda r: web.Response(text="Бот МаркX готов."))

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 3000)
    await site.start()
    print("🟢 Сервер спит на порту 3000 и не спамит запросами. Наступила тишина.", flush=True)
    
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Бот остановлен.")
        sys.exit(0)
