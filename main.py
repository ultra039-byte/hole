import asyncio
import sys
import os
import aiohttp
from aiohttp import web
from config import MAX_BOT_TOKEN, MAX_API_URL

PORT = int(os.getenv("PORT", 10000))

# --- НАША БАЗА ДАННЫХ В ПАМЯТИ ---
CONNECTED_CHANNELS = set()
ADMIN_STATE = None

# --- БЛОК ПРОВЕРКИ ПРАВ И СБОР БАЗЫ ---

async def check_if_bot_is_admin(channel_id: str) -> bool:
    """Процесс: Проверка, является ли Марк админом в канале"""
    # Каноничный метод большинства API для проверки участников чата
    url = f"{MAX_API_URL}/getChatMember"
    params = {
        "chat_id": channel_id,
        "user_id": "bot_id_placeholder"  # В реальном запросе сюда передается ID самого бота
    }
    headers = {"Authorization": f"Bearer {MAX_BOT_TOKEN}"}
    
    print(f"🔍 [ПРОВЕРКА ПРАВ] Марк проверяет свои права в канале {channel_id}...", flush=True)
    
    # Симулируем запрос к API (так как мы пока не деплоим внешние хуки)
    # В реальном коде здесь будет: async with session.get(url, params=params) ...
    await asyncio.sleep(0.5) 
    
    # Для теста сделаем, что в @auto_news он админ, а в других — нет
    if channel_id == "@auto_news":
        print(f"🟢 [УСПЕХ] Права подтверждены! Марк является администратором в {channel_id}.", flush=True)
        return True
    else:
        print(f"❌ [ОТКАЗ] Марк НЕ админ в {channel_id} или у него нет прав на публикацию!", flush=True)
        return False


def click_connect_channel_button():
    """Админ нажал кнопку 'ПОДКЛЮЧИТЬ КАНАЛ'"""
    global ADMIN_STATE
    ADMIN_STATE = "WAITING_FOR_CHANNEL_POST"
    print("\n🔘 [КНОПКА НАЖАТА] Админ выбрал: 'ПОДКЛЮЧИТЬ КАНАЛ'", flush=True)
    print("⏳ [СТАТУС] Марк перешел в режим ожидания поста из канала...", flush=True)


async def handle_incoming_post(forwarded_from_chat: str):
    """Прием поста из канала, проверка прав и добавление в базу"""
    global ADMIN_STATE
    
    if ADMIN_STATE != "WAITING_FOR_CHANNEL_POST":
        print(f"⚠️ [ИГНОР] Пришел пост из {forwarded_from_chat}, но Марк не в режиме настройки.", flush=True)
        return
        
    # СТАДИЯ ПРОВЕРКИ: Прежде чем сохранить, проверяем админку
    is_admin = await check_if_bot_is_admin(forwarded_from_chat)
    
    if not is_admin:
        print(f"🚫 [ОШИБКА ПОДКЛЮЧЕНИЯ] Не удалось подключить {forwarded_from_chat}. Сначала добавьте бота в админы канала!", flush=True)
        ADMIN_STATE = None  # Сбрасываем режим ожидания
        show_connected_channels()
        return

    # Если проверка прошла — сохраняем
    if forwarded_from_chat not in CONNECTED_CHANNELS:
        CONNECTED_CHANNELS.add(forwarded_from_chat)
        print(f"🎉 [БАЗА ОБНОВЛЕНА] Канал {forwarded_from_chat} УСПЕШНО ПОДКЛЮЧЕН!", flush=True)
    else:
        print(f"⚠️ [БАЗА] Канал {forwarded_from_chat} уже есть в списке.", flush=True)
        
    ADMIN_STATE = None
    show_connected_channels()


def show_connected_channels():
    """Опция: Список подключенных каналов"""
    print("\n📋 [ОПЦИЯ: ПОДКЛЮЧЕННЫЕ КАНАЛЫ] Текущий список в базе:")
    if not CONNECTED_CHANNELS:
        print("   ❌ Нет подключенных каналов", flush=True)
    else:
        for i, channel in enumerate(CONNECTED_CHANNELS, 1):
            print(f"   {i}. {channel}", flush=True)
    print("----------------------------------------\n", flush=True)


# --- СЕРВЕРНАЯ ЧАСТЬ ---

async def handle_webhook(request):
    try:
        data = await request.json()
        action = data.get("action")
        
        if action == "click_connect":
            click_connect_channel_button()
            return web.json_response({"status": "waiting_for_post"})
        elif action == "send_post":
            channel_name = data.get("channel_name", "@unknown_channel")
            await handle_incoming_post(channel_name)
            return web.json_response({"channels": list(CONNECTED_CHANNELS)})
            
        return web.Response(text="МаркX на связи.", status=200)
    except Exception as e:
        print(f"❌ Ошибка: {e}", flush=True)
        return web.Response(text="Error", status=500)

async def main():
    print(f"🔥 МАРК X ЗАПУСКАЕТСЯ НА RENDER (ПОРТ {PORT})... 🔥", flush=True)
    print("📋 ЭТАП 1 + ВАЛИДАЦИЯ ПРАВ АДМИНИСТРАТОРА", flush=True)
    
    app = web.Application()
    app.router.add_post("/", handle_webhook)
    app.router.add_post("/{tail:.*}", handle_webhook)
    app.router.add_get("/", lambda r: web.Response(text="МаркX: База каналов с проверкой прав активна!"))

    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"🟢 Сервер слушает интерфейс 0.0.0.0:{PORT}", flush=True)
    
    # --- СИМУЛЯЦИЯ ДВУХ СИТУАЦИЙ ---
    await asyncio.sleep(1)
    
    # Ситуация А: Пробуем подключить канал, где Марк АДМИН
    click_connect_channel_button()
    await asyncio.sleep(1)
    await handle_incoming_post("@auto_news")
    
    # Ситуация Б: Пробуем подключить канал, где Марка ЗАБЫЛИ сделать админом
    await asyncio.sleep(1)
    click_connect_channel_button()
    await asyncio.sleep(1)
    await handle_incoming_post("@crypto_mafia")
    
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Бот остановлен.")
        sys.exit(0)
