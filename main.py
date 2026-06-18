import asyncio
import sys
import aiohttp
from aiohttp import web
from config import MAX_BOT_TOKEN, MAX_API_URL

# Функция настройки вебхука по официальной документации MAX
async def init_max_integration():
    bot_id = "bot_1781808655_2628_nemrito"
    webhook_url = f"https://{bot_id}.bothost.ru"
    
    # Заголовок авторизации строго по доке: "Authorization: <token>"
    headers = {
        "Authorization": MAX_BOT_TOKEN,
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        # Шаг 1. Проверяем, живой ли токен (запрос к /me)
        print("🔍 Проверяем токен на сервере MAX...", flush=True)
        try:
            async with session.get(f"{MAX_API_URL}/me", headers=headers) as resp:
                if resp.status == 200:
                    me_data = await resp.json()
                    print(f"✅ Токен валиден! Бот на связи.", flush=True)
                else:
                    print(f"❌ Ошибка авторизации токена (Статус {resp.status})", flush=True)
                    return
        except Exception as e:
            print(f"❌ Не удалось достучаться до /me: {e}", flush=True)
            return

        # Шаг 2. Регистрируем вебхук через POST /subscriptions
        print(f"📡 Отправляем запрос на привязку вебхука: {webhook_url}", flush=True)
        payload = {
            "url": webhook_url
        }
        
        try:
            async with session.post(f"{MAX_API_URL}/subscriptions", json=payload, headers=headers) as resp:
                result = await resp.json()
                if resp.status in [200, 201]:
                    print("🎉 УРА! ВЕБХУК УСПЕШНО ЗАРЕГИСТРИРОВАН В MAX!", flush=True)
                else:
                    print(f"⚠️ Сервер MAX не принял вебхук (Статус {resp.status}): {result}", flush=True)
        except Exception as e:
            print(f"❌ Ошибка отправки вебхука в /subscriptions: {e}", flush=True)

# Функция приёма сообщений (сюда MAX будет присылать данные)
async def handle_webhook(request):
    try:
        data = await request.json()
        print(f"📩 МАКС ПРИСЛАЛ СОБЫТИЕ: {data}", flush=True)
        return web.Response(text="OK", status=200)
    except Exception as e:
        print(f"❌ Ошибка парсинга события: {e}", flush=True)
        return web.Response(text="Error", status=500)

async def main():
    print("🔥 МАРК X ИНИЦИАЛИЗИРУЕТ ИНТЕГРАЦИЮ С MAX... 🔥", flush=True)
    
    app = web.Application()
    app.router.add_post("/", handle_webhook)
    app.router.add_get("/", lambda r: web.Response(text="МаркX запущен."))

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 3000)
    await site.start()
    print("🟢 Локальный веб-сервер поднят на порту 3000.", flush=True)
    
    # Запускаем официальную регистрацию
    await init_max_integration()
    
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Бот остановлен.")
        sys.exit(0)
