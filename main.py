import asyncio
import sys
import os
import aiohttp
from aiohttp import web
from config import MAX_BOT_TOKEN, MAX_API_URL

PORT = int(os.getenv("PORT", 10000))

# --- АВТОМАТИЧЕСКАЯ СВЯЗКА БОТА С RENDER ---
async def set_webhook_on_start():
    """Сообщает платформе MAX, куда нужно пересылать сообщения из чата"""
    webhook_url = "https://mark-x-bot.onrender.com/"
    
    # Пытаемся вызвать стандартный метод setWebhook
    url = f"{MAX_API_URL}/setWebhook"
    payload = {"url": webhook_url}
    headers = {
        "Authorization": f"Bearer {MAX_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print(f"📡 Попытка связать бота с новым адресом: {webhook_url}", flush=True)
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload, headers=headers) as resp:
                result = await resp.text()
                print(f"📡 Ответ платформы на привязку: {result} (Статус: {resp.status})", flush=True)
        except Exception as e:
            print(f"❌ Ошибка отправки запроса привязки: {e}", flush=True)

# --- ФУНКЦИЯ ОТПРАВКИ СООБЩЕНИЯ В ЧАТ ---
async def send_response_to_max(chat_id: int, text: str):
    url = f"{MAX_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    headers = {
        "Authorization": f"Bearer {MAX_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    async with aiohttp.ClientSession() as session:
        try:
            await session.post(url, json=payload, headers=headers)
            print(f"📤 Отправлен ответ в чат {chat_id}: '{text}'", flush=True)
        except Exception as e:
            print(f"❌ Не удалось отправить ответ: {e}", flush=True)

# --- ОБРАБОТЧИК ЖИВОГО ТРАФИКА ИЗ ЧАТА ---
async def handle_webhook(request):
    try:
        data = await request.json()
        print(f"📩 [УРА, ТРАФИК ПОШЁЛ!]: {data}", flush=True)
        
        message = data.get("message", {})
        chat_id = message.get("chat", {}).get("id") or data.get("chat_id")
        user_text = message.get("text", "").strip()
        
        if chat_id and user_text:
            if user_text.lower() == "подключить канал":
                await send_response_to_max(chat_id, "⏳ Команда принята! Перешли мне пост из канала.")
            else:
                await send_response_to_max(chat_id, f"Марк на связи! Ты написал: '{user_text}'")
                
        return web.Response(text="OK", status=200)
    except Exception as e:
        print(f"❌ Ошибка в обработчике: {e}", flush=True)
        return web.Response(text="Error", status=500)

async def main():
    print(f"🔥 МАРК X ЗАПУСКАЕТСЯ НА RENDER (ПОРТ {PORT})... 🔥", flush=True)
    
    app = web.Application()
    app.router.add_post("/", handle_webhook)
    app.router.add_post("/{tail:.*}", handle_webhook)
    app.router.add_get("/", lambda r: web.Response(text="Бот МаркX онлайн!"))

    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"🟢 Сервер слушает интерфейс 0.0.0.0:{PORT}", flush=True)
    
    # Даем серверу секунду опомниться и делаем привязку
    await asyncio.sleep(1)
    await set_webhook_on_start()
    
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Бот остановлен.")
        sys.exit(0)
