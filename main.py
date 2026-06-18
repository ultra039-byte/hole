import asyncio
import sys
import os
import aiohttp
from aiohttp import web
from config import MAX_BOT_TOKEN, MAX_API_URL

PORT = int(os.getenv("PORT", 10000))

# Функция отправки ответа обратно в мессенджер
async def send_message(chat_id, text):
    url = f"{MAX_API_URL}/sendMessage" # Или актуальный эндпоинт отправки
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    headers = {"Authorization": f"Bearer {MAX_BOT_TOKEN}", "Content-Type": "application/json"}
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload, headers=headers) as resp:
                print(f"📤 Отправлено сообщение в {chat_id}. Статус: {resp.status}", flush=True)
        except Exception as e:
            print(f"❌ Ошибка отправки сообщения: {e}", flush=True)

# Главный обработчик входящих процессов (Постинг, Изменение и т.д.)
async def handle_webhook(request):
    try:
        data = await request.json()
        print(f"📩 Входящее событие: {data}", flush=True)
        
        # Определяем тип события (структура зависит от API, обычно есть 'event' или 'type')
        event_type = data.get("event") or data.get("type")
        message = data.get("message", {})
        chat_id = message.get("chat", {}).get("id") or data.get("chat_id")
        
        # 1. Процесс: Постинг нового сообщения
        if event_type == "message_new" or "text" in message:
            text = message.get("text", "")
            print(f"📝 ПРОЦЕСС ПОСТИНГА: Новое сообщение в чате {chat_id}: '{text}'", flush=True)
            
            # Пример базовой логики реагирования
            if text.lower() == "привет":
                await send_message(chat_id, "Привет, бро! Я МаркX, и я работаю по феншуйным вебхукам!")
        
        # 2. Процесс: Изменение/Редактирование сообщения
        elif event_type == "message_edit" or data.get("action") == "edit":
            print(f"✏️ ПРОЦЕСС ИЗМЕНЕНИЯ: Сообщение было отредактировано юзером в чате {chat_id}", flush=True)
            # Тут будет логика отслеживания изменений текста или статусов
            
        return web.Response(text="OK", status=200)
        
    except Exception as e:
        print(f"❌ Ошибка при обработке процесса: {e}", flush=True)
        return web.Response(text="Error", status=500)

async def main():
    print(f"🔥 МАРК X ЗАПУСКАЕТСЯ НА RENDER (ПОРТ {PORT})... 🔥", flush=True)
    
    app = web.Application()
    # Принимаем POST-запросы на любые пути
    app.router.add_post("/", handle_webhook)
    app.router.add_post("/{tail:.*}", handle_webhook)
    app.router.add_get("/", lambda r: web.Response(text="Бот МаркX онлайн на Render!"))

    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"🟢 Сервер слушает интерфейс 0.0.0.0:{PORT} и готов к процессам", flush=True)
    
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Бот остановлен.")
        sys.exit(0)
