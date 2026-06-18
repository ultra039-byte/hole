import asyncio
import sys
import os
import aiohttp
from aiohttp import web
from config import MAX_BOT_TOKEN, MAX_API_URL

PORT = int(os.getenv("PORT", 10000))

async def init_max_webhook():
    webhook_url = "https://mark-x-bot.onrender.com"
    
    # Три разных варианта эндпоинтов, которые бывают у VPoster
    urls_to_try = [
        f"https://vposter.ru/api/bot/set-webhook?token={MAX_BOT_TOKEN}&url={webhook_url}",
        f"https://vposter.ru/api/v1/set-webhook?token={MAX_BOT_TOKEN}&url={webhook_url}",
        f"{MAX_API_URL}/set-webhook?token={MAX_BOT_TOKEN}&url={webhook_url}"
    ]
    
    headers = {"Authorization": f"Bearer {MAX_BOT_TOKEN}"}
    
    async with aiohttp.ClientSession() as session:
        for i, url in enumerate(urls_to_try, 1):
            print(f"📡 Пробуем вариант №{i}: {url}", flush=True)
            try:
                async with session.get(url, headers=headers) as resp:
                    text_resp = await resp.text()
                    print(f"📡 Ответ на вариант №{i}: {text_resp}", flush=True)
                    if "success" in text_resp or '"code":"ok"' in text_resp or "true" in text_resp.lower():
                        print(f"🎉 ПОБЕДА! Вебхук успешно встал на варианте №{i}!", flush=True)
                        return
            except Exception as e:
                print(f"❌ Ошибка на варианте №{i}: {e}", flush=True)

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
    
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"🟢 Сервер слушает интерфейс 0.0.0.0:{PORT}", flush=True)
    
    # Запускаем веерную рассылку по эндпоинтам
    await init_max_webhook()
    
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Бот остановлен.")
        sys.exit(0)
