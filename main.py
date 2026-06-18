import asyncio
import sys
from config import MAX_BOT_TOKEN

async def main():
    # Этот текст обязан мгновенно появиться в логах
    print("🔥 МАРК X ОФИЦИАЛЬНО ЖИВ И В СТРОЮ! 🔥", flush=True)
    print(f"📡 Токен мессенджера успешно подгружен: {str(MAX_BOT_TOKEN)[:5]}***", flush=True)
    
    counter = 0
    while True:
        counter += 5
        print(f"🟢 Робот активен. Время в сети: {counter} сек.", flush=True)
        await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Бот остановлен.")
        sys.exit(0)
