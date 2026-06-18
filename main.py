import asyncio
import sys
import os
import aiohttp
from aiohttp import web
from config import MAX_BOT_TOKEN, MAX_API_URL

# Автоматически берем порт 3000 от хостинга
PORT = int(os.getenv("PORT", 3000))

async def init_max_webhook():
    # Переводим бота на официальный веб-домен хостинга с заменой знаков на дефисы
    bot_id = "bot_1781808655_2628_nemrito".replace("_", "-")
    webhook_url = f"https://{bot_id}.bothost.tech"
    
    headers = {
        "Authorization": MAX_BOT_TOKEN,
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": webhook_url
    }
    
    print(f"📡 Пробуем выделить вебхук на домене .TECH: {webhook_url}", flush=True)
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{MAX_API_URL}/subscriptions", json=payload, headers=headers) as resp:
                result = await resp.json()
                print(f"📡 Ответ сервера MAX на подписку: {result}", flush=True)
        except Exception as e:
            print(f"❌ Ошибка отправки запроса подписки: {e}", flush=True)

async def handle_webhook(request):
    try:
        data = await request.json()
        print(f"📩 УРА! МАКС ПРИСЛАЛ СОБЫТИЕ: {data}", flush=True)
        return web.Response(text="OK", status=200)
    except Exception as e:
        print(f"❌ Ошибка парсинга события: {e}", flush=True)
        return web.Response(text="Error", status=500)

async def main():
    print(f"🔥 МАРК X ЗАПУСКАЕТСЯ НА ПОРТУ {PORT}... 🔥", flush=True)
    
    app = web.Application()
    app.router.add_post("/", handle_webhook)
    app.router.add_post("/{tail:.*}", handle_webhook)
    app.router.add_get("/", lambda r: web.Response(text="Бот МаркX онлайн."))

    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"🟢 Сервер слушает интерфейс 0.0.0.0:{PORT}", flush=True)
    
    await init_max_webhook()
    
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Бот остановлен.")
        sys.exit(0)
