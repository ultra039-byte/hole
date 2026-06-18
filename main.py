import asyncio
import sys
import os
import aiohttp
from aiohttp import web
from config import MAX_BOT_TOKEN, MAX_API_URL

# Render автоматически выдаёт правильный порт в переменную окружения PORT (обычно 10000)
PORT = int(os.getenv("PORT", 10000))

async def init_max_webhook():
    # Твоя ссылка на Render
    webhook_url = "https://mark-x-bot.onrender.com"
    
    # Каноничный запрос к VPoster: метод setWebhook, токен и URL передаются параметрами
    url = f"{MAX_API_URL}/setWebhook?token={MAX_BOT_TOKEN}&url={webhook_url}"
    
    print(f"📡 Регистрируем феншуйный вебхук на VPoster: {webhook_url}", flush=True)
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                result = await resp.json()
                print(f"📡 Ответ сервера VPoster на setWebhook: {result}", flush=True)
        except Exception as e:
            print(f"❌ Ошибка отправки запроса подписки: {e}", flush=True)

async def handle_webhook(request):
    try:
        data = await request.json()
        print(f"📩 УРА! ВПОСТЕР ПРИСЛАЛ СОБЫТИЕ: {data}", flush=True)
        return web.Response(text="OK", status=200)
    except Exception as e:
        print(f"❌ Ошибка парсинга события: {e}", flush=True)
        return web.Response(text="Error", status=500)

async def main():
    print(f"🔥 МАРК X ЗАПУСКАЕТСЯ НА RENDER (ПОРТ {PORT})... 🔥", flush=True)
    
    app = web.Application()
    app.router.add_post("/", handle_webhook)
    app.router.add_post("/{tail:.*}", handle_webhook)
    app.router.add_get("/", lambda r: web.Response(text="Бот МаркX онлайн на Render!"))

    runner = web.AppRunner(app)
    await runner.setup()
    
    # Слушаем порт, выделенный хостингом
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"🟢 Сервер слушает интерфейс 0.0.0.0:{PORT}", flush=True)
    
    # Сразу при старте пинаем VPoster, чтобы слал хуки сюда
    await init_max_webhook()
    
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Бот остановлен.")
        sys.exit(0)
