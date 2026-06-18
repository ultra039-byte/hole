import asyncio
import sys
import aiohttp
from aiohttp import web
from config import MAX_BOT_TOKEN, MAX_API_URL

async def init_max_integration():
    headers = {
        "Authorization": MAX_BOT_TOKEN,
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        # Проверяем, что там сейчас думает MAX про наш вебхук
        print("🔍 Запрашиваем у MAX статус нашей подписки...", flush=True)
        try:
            async with session.get(f"{MAX_API_URL}/subscriptions", headers=headers) as resp:
                result = await resp.json()
                print(f"📡 Статус подписок от MAX: {result}", flush=True)
        except Exception as e:
            print(f"❌ Не удалось проверить статус подписок: {e}", flush=True)

async def handle_webhook(request):
    try:
        data = await request.json()
        print(f"📩 МАКС ПРИСЛАЛ СОБЫТИЕ: {data}", flush=True)
        return web.Response(text="OK", status=200)
    except Exception as e:
        print(f"❌ Ошибка парсинга события: {e}", flush=True)
        return web.Response(text="Error", status=500)

async def main():
    print("🔥 МАРК X ЗАПУСКАЕТ ДИАГНОСТИКУ... 🔥", flush=True)
    
    app = web.Application()
    # Слушаем и корень, и любые вложенные пути на случай, если MAX стучится туда
    app.router.add_post("/", handle_webhook)
    app.router.add_post("/{tail:.*}", handle_webhook)
    app.router.add_get("/", lambda r: web.Response(text="МаркX запущен."))

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 3000)
    await site.start()
    print("🟢 Локальный веб-сервер поднят на порту 3000.", flush=True)
    
    await init_max_integration()
    
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Бот остановлен.")
        sys.exit(0)
