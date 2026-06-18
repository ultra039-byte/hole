import asyncio
import sys
import os
import aiohttp
from aiohttp import web
from config import MAX_BOT_TOKEN, MAX_API_URL

# Функция, которая регистрирует нашего бота в мессенджере Макс
async def register_webhook():
    # Хостинг автоматически выдает адрес в переменную WEBHOOK_URL
    webhook_url = os.getenv("WEBHOOK_URL")
    
    if not webhook_url:
        print("⚠️ Предупреждение: WEBHOOK_URL не найден в системе. Бот работает локально.", flush=True)
        return

    print(f"🔗 Попытка установить вебхук на адрес: {webhook_url}", flush=True)
    
    # Отправляем запрос в API Макса, чтобы он привязал этот адрес к боту
    # (Обычно это метод setWebhook, стандартный для таких платформ)
    url = f"{MAX_API_URL}/bot{MAX_BOT_TOKEN}/setWebhook"
    payload = {"url": webhook_url}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                result = await response.json()
                if response.status == 200 and result.get("ok"):
                    print("✅ ВЕБХУК УСПЕШНО ЗАРЕГИСТРИРОВАН В МАКСЕ!", flush=True)
                else:
                    print(f"❌ Ошибка регистрации вебхука в Максе: {result}", flush=True)
    except Exception as e:
        print(f"❌ Не удалось связаться с API Макса: {e}", flush=True)

# Эта функция срабатывает КАЖДЫЙ РАЗ, когда кто-то пишет боту в мессенджере
async def handle_webhook(request):
    try:
        data = await request.json()
        print(f"📩 Прилетело событие от Макса: {data}", flush=True)
        
        # Проверяем, есть ли текст сообщения в пришедших данных
        if "message" in data:
            msg = data["message"]
            text = msg.get("text", "")
            chat_id = msg.get("chat", {}).get("id")
            
            print(f"🤖 Вижу сообщение! Текст: '{text}' | От чата: {chat_id}", flush=True)
            
            # Сюда мы очень скоро пропишем ответ бота обратно пользователю или отправку в ВПостер!

        return web.Response(text="OK", status=200)
    except Exception as e:
        print(f"❌ Ошибка обработки входящего запроса: {e}", flush=True)
        return web.Response(text="Error", status=500)

async def main():
    print("🔥 МАРК X ИНИЦИАЛИЗИРУЕТ СЛУЖБЫ... 🔥", flush=True)
    
    # 1. Запускаем веб-сервер на порту 3000
    app = web.Application()
    app.router.add_post("/", handle_webhook)
    app.router.add_get("/", lambda r: web.Response(text="Бот МаркX запущен!"))

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 3000)
    await site.start()
    print("🟢 Локальный сервер запущен на порту 3000.", flush=True)
    
    # 2. Регистрируем этот сервер в мессенджере Макс
    await register_webhook()
    
    # Держим бота включенным
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Бот остановлен.")
        sys.exit(0)
