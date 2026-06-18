import asyncio
import sys
import os
import aiohttp
from aiohttp import web
from config import MAX_BOT_TOKEN, MAX_API_URL

# Функция автоматической регистрации вебхука по правилам MAX API
async def set_max_webhook():
    # Наш внешний URL-адрес на хостинге BotHost
    bot_id = "bot_1781808655_2628_nemrito"
    webhook_url = f"https://{bot_id}.bothost.ru"
    
    print(f"📡 Регистрируем вебхук на платформе MAX... Адрес: {webhook_url}", flush=True)
    
    # Официальный эхо-путь для установки вебхука (обычно /v1/webhook или /webhooks)
    # Попробуем базовый универсальный эндпоинт для подписки
    url = f"{MAX_API_URL}/v1/webhook"
    
    # Токен в корпоративных API почти всегда передается в Headers
    headers = {
        "Authorization": f"Bearer {MAX_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": webhook_url
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                result = await response.json()
                if response.status in [200, 201]:
                    print("✅ МАКС ПОДТВЕРДИЛ ВЕБХУК! Связь успешно настроена.", flush=True)
                else:
                    print(f"⚠️ Ответ сервера MAX (Статус {response.status}): {result}", flush=True)
                    print("💡 Если статус 404, бот всё равно будет принимать сообщения, если вебхук настроен в панели разработчика MAX.", flush=True)
    except Exception as e:
        print(f"❌ Ошибка отправки запроса вебхука: {e}", flush=True)

# Приём сообщений
async def handle_webhook(request):
    try:
        data = await request.json()
        print(f"📩 Входящее событие от MAX: {data}", flush=True)
        return web.Response(text="OK", status=200)
    except Exception as e:
        print(f"❌ Ошибка парсинга: {e}", flush=True)
        return web.Response(text="Error", status=500)

async def main():
    print("🔥 МАРК X ЗАПУСКАЕТ ВЕБ-СЕРВЕР ДЛЯ ВЕБХУКОВ... 🔥", flush=True)
    
    app = web.Application()
    app.router.add_post("/", handle_webhook)
    app.router.add_get("/", lambda r: web.Response(text="Бот МаркX на связи."))

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 3000)
    await site.start()
    print("🟢 Сервер слушает порт 3000.", flush=True)
    
    # Запускаем регистрацию в фоне
    await set_max_webhook()
    
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Бот остановлен.")
        sys.exit(0)
