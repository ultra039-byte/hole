import asyncio
import sys
import aiohttp
from config import MAX_BOT_TOKEN, MAX_API_URL

async def main():
    print("🔥 МАРК X ЗАПУЩЕН В РЕЖИМЕ LONG POLLING (ОПРОС СЕРВЕРА)... 🔥", flush=True)
    print(f"📡 Токен связи подгружен: {str(MAX_BOT_TOKEN)[:5]}***", flush=True)
    
    # ID последнего прочитанного сообщения, чтобы не обрабатывать старые по кругу
    offset = 0 
    
    # Создаем одну общую сессию для запросов
    async with aiohttp.ClientSession() as session:
        print("🟢 Начинаю слушать входящие сообщения от пользователей...", flush=True)
        
        while True:
            # Формируем стандартный запрос обновлений (getUpdates)
            # timeout=30 заставляет сервер Макса удерживать соединение, если новых сообщений пока нет
            url = f"{MAX_API_URL}/bot{MAX_BOT_TOKEN}/getUpdates?offset={offset}&timeout=30"
            
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Если сервер вернул список событий и он не пустой
                        if data.get("ok") and "result" in data:
                            updates = data["result"]
                            
                            for update in updates:
                                # Сдвигаем offset, чтобы подтвердить получение этого сообщения
                                offset = update["update_id"] + 1
                                
                                # Проверяем, есть ли текстовое сообщение
                                if "message" in update:
                                    msg = update["message"]
                                    text = msg.get("text", "")
                                    chat_id = msg.get("chat", {}).get("id")
                                    user = msg.get("from", {}).get("username", "Пользователь")
                                    
                                    print(f"📩 [{user}]: {text} (chat_id: {chat_id})", flush=True)
                                    
                                    # --- НАЧАЛО ТВОЕЙ ЛОГИКИ ОБРАБОТКИ ---
                                    if text.lower() == "/start":
                                        print(f"🤖 Бот зафиксировал команду старт от {user}!", flush=True)
                                    # --- КОНЕЦ ТВОЕЙ ЛОГИКИ ОБРАБОТКИ ---
                                    
                    elif response.status == 401:
                        print("❌ Ошибка: Неверный токен бота (401 Unauthorized). Проверь MAX_BOT_TOKEN!", flush=True)
                        await asyncio.sleep(10)
                    else:
                        print(f"⚠️ Сервер Макса вернул статус {response.status}", flush=True)
                        
            except Exception as e:
                print(f"❌ Ошибка сети или подключения к API: {e}", flush=True)
                # Ждем пару секунд перед повторной попыткой при сбое сети, чтобы не спамить вхолостую
                await asyncio.sleep(3)
                
            # Небольшая микропауза между циклами опроса
            await asyncio.sleep(0.5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Бот остановлен.")
        sys.exit(0)
