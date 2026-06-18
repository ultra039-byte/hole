import asyncio
import sys
import os
import aiohttp
from aiohttp import web
from config import MAX_BOT_TOKEN, MAX_API_URL

PORT = int(os.getenv("PORT", 10000))

# --- ФУНКЦИЯ ОТПРАВКИ СООБЩЕНИЯ В ЧАТ МАКСА ---
async def send_response_to_max(chat_id: int, text: str):
    """Отправляет реальное текстовое сообщение обратно пользователю в чат"""
    # Используем официальный метод sendMessage базового API
    url = f"{MAX_API_URL}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    
    headers = {
        "Authorization": f"Bearer {MAX_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print(f"📤 Отправляем ответ в чат {chat_id}: '{text}'", flush=True)
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload, headers=headers) as resp:
                result = await resp.text()
                print(f"📤 Статус отправки: {resp.status}. Ответ API: {result}", flush=True)
        except Exception as e:
            print(f"❌ Не удалось отправить сообщение в MAX: {e}", flush=True)

# --- ОБРАБОТЧИК ВХОДЯЩИХ СОБЫТИЙ ---
async def handle_webhook(request):
    try:
        data = await request.json()
        print(f"📩 [ЖИВОЙ ХУК ИЗ MAX]: {data}", flush=True)
        
        # Вытаскиваем текст и ID чата из входящего вебхука
        message = data.get("message", {})
        chat_id = message.get("chat", {}).get("id") or data.get("chat_id")
        user_text = message.get("text", "").strip()
        
        if chat_id and user_text:
            print(f"👤 Юзер написал: '{user_text}' в чате {chat_id}", flush=True)
            
            # Реагируем на команду
            if user_text.lower() == "подключить канал":
                reply = "⏳ Марк принял команду! Теперь перешли мне любой пост из канала, который нужно подключить."
                await send_response_to_max(chat_id, reply)
            else:
                reply = f"Привет! Я услышал тебя. Ты написал: '{user_text}'. Давай настроим работу каналов!"
                await send_response_to_max(chat_id, reply)
                
        return web.Response(text="OK", status=200)
    except Exception as e:
        print(f"❌ Ошибка в обработчике: {e}", flush=True)
        return web.Response(text="Error", status=500)

async def main():
    print(f"🔥 МАРК X ЗАПУСКАЕТСЯ НА RENDER (ПОРТ {PORT})... 🔥", flush=True)
    
    app = web.Application()
    app.router.add_post("/", handle_webhook)
    app.router.add_post("/{tail:.*}", handle_webhook)
    app.router.add_get("/", lambda r: web.Response(text="Бот МаркX онлайн на Render и готов слать сообщения!"))

    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"🟢 Сервер слушает интерфейс 0.0.0.0:{PORT}", flush=True)
    
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Бот остановлен.")
        sys.exit(0)
