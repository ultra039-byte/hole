import asyncio
import sys
import aiohttp
from aiohttp import web
from config import MAX_BOT_TOKEN, MAX_API_URL

# Новая правильная функция регистрации вебхука по доке MAX
async def register_max_service():
    bot_id = "bot_1781808655_2628_nemrito"
    webhook_url = f"https://{bot_id}.bothost.ru"
    
    print(f"📡 Подключаем службу сообщений MAX к хостингу: {webhook_url}", flush=True)
    
    # Для бизнес-служб MAX базовый эндпоинт управления подписками
    url = f"{MAX_API_URL}/v1/events/subscriptions"
    
    headers = {
        "Authorization": f"Bearer {MAX_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Говорим Максу, что хотим слушать входящие сообщения (message.new или message.send)
    payload = {
        "url": webhook_url,
        "events": ["message.new", "message.received"] 
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                result = await response.json()
                if response.status in [200, 201]:
                    print("✅ СЛУЖБА MAX УСПЕШНО АКТИВИРОВАНА!", flush=True)
                else:
                    # Если этот эндпоинт выдаст 404, мы попробуем альтернативный (/v1/services)
                    print(f"ℹ️ Эндпоинт subscriptions вернул статус {response.status}. Пробуем альтернативный путь...", flush=True)
                    alt_url = f"{MAX_API_URL}/v1/services"
                    async with session.post(alt_url, json={"webhook_url": webhook_url}, headers=headers) as alt_resp:
                        alt_result = await alt_resp.json()
                        print(f"📡 Ответ от /v1/services (Статус {alt_resp.status}): {alt_result}", flush=True)
    except Exception as e:
        print(f"❌ Ошибка при связывании служб: {e}", flush=True)

# Приёмщик входящих пакетов
async def handle_webhook(request):
    try:
        data = await request.json()
        print(f"📩 МАКС ПРИСЛАЛ СОБЫТИЕ: {data}", flush=True)
        return web.Response(text="OK", status=200)
    except Exception as e:
        print(f"❌ Ошибка парсинга входящего запроса: {e}", flush=True)
        return web.Response(text="Error", status=500)

async def main():
    print("🔥 МАРК X ЗАПУСКАЕТ СЛУЖБУ ИНТЕГРАЦИИ... 🔥", flush=True)
    
    app = web.Application()
    app.router.add_post("/", handle_webhook)
    app.router.add_get("/", lambda r: web.Response(text="МаркX готов к приему."))

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 3000)
    await site.start()
    print("🟢 Веб-сервер развернут на порту 3000.", flush=True)
    
    # Пытаемся связаться с платформой
    await register_max_service()
    
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Бот остановлен.")
        sys.exit(0)
