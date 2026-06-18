import asyncio
import sys
from aiohttp import web

async def handle_webhook(request):
    try:
        data = await request.json()
        print(f"📩 МАКС ПРИСЛАЛ СОБЫТИЕ: {data}", flush=True)
        return web.Response(text="OK", status=200)
    except Exception as e:
        print(f"❌ Ошибка: {e}", flush=True)
        return web.Response(text="Error", status=500)

async def main():
    print("🔥 МАРК X ГОТОВ И ЖДЕТ СООБЩЕНИЙ В ТИШИНЕ... 🔥", flush=True)
    
    app = web.Application()
    app.router.add_post("/", handle_webhook)
    app.router.add_get("/", lambda r: web.Response(text="МаркX онлайн."))

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 3000)
    await site.start()
    print("🟢 Сервер поднят на порту 3000 и слушает входящие запросы.", flush=True)
    
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Бот остановлен.")
        sys.exit(0)
