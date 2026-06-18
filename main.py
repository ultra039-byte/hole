import asyncio
import sys
import os
from aiohttp import web

PORT = int(os.getenv("PORT", 10000))

# Временная база данных в памяти для отслеживания наших постов
# Структура: { post_id: {"text": "текст", "status": "draft/published", "updated": False} }
POSTS_DB = {}
post_id_counter = 1

# --- БЛОК ПРОЦЕССОВ ПОСТИНГА И ИЗМЕНЕНИЯ ---

def create_post(text: str) -> int:
    """Процесс создания нового поста (Постинг)"""
    global post_id_counter
    p_id = post_id_counter
    POSTS_DB[p_id] = {
        "text": text,
        "status": "draft",
        "updated": False
    }
    post_id_counter += 1
    print(f"📝 [ПРОЦЕСС ПОСТИНГА] Создан черновик поста #{p_id}: '{text}'", flush=True)
    return p_id

def publish_post(p_id: int):
    """Процесс публикации поста"""
    if p_id in POSTS_DB:
        POSTS_DB[p_id]["status"] = "published"
        print(f"🚀 [ПРОЦЕСС ПОСТИНГА] Пост #{p_id} успешно опубликован!", flush=True)
    else:
        print(f"❌ Ошибка публикации: Пост #{p_id} не найден", flush=True)

def edit_post(p_id: int, new_text: str):
    """Процесс изменения/редактирования существующего поста"""
    if p_id in POSTS_DB:
        old_text = POSTS_DB[p_id]["text"]
        POSTS_DB[p_id]["text"] = new_text
        POSTS_DB[p_id]["updated"] = True
        print(f"✏️ [ПРОЦЕСС ИЗМЕНЕНИЯ] Пост #{p_id} изменен!", flush=True)
        print(f"   Было: '{old_text}'\n   Стало: '{new_text}'", flush=True)
    else:
        print(f"❌ Ошибка изменения: Пост #{p_id} не найден", flush=True)

# --- СЕРВЕРНАЯ ЧАСТЬ ---

async def handle_webhook(request):
    """Приём внешних событий и триггеров"""
    try:
        data = await request.json()
        action = data.get("action")
        
        # Симулируем процессы через входящие запросы для тестов
        if action == "create":
            text = data.get("text", "Новый пост")
            p_id = create_post(text)
            return web.json_response({"status": "created", "post_id": p_id})
            
        elif action == "publish":
            p_id = int(data.get("post_id", 0))
            publish_post(p_id)
            return web.json_response({"status": "published", "post_id": p_id})
            
        elif action == "edit":
            p_id = int(data.get("post_id", 0))
            new_text = data.get("text", "Измененный текст")
            edit_post(p_id, new_text)
            return web.json_response({"status": "edited", "post_id": p_id})

        return web.Response(text="МаркX принял запрос, но действие неизвестно", status=200)
    except Exception as e:
        print(f"❌ Ошибка обработки запроса: {e}", flush=True)
        return web.Response(text="Error", status=500)

async def main():
    print(f"🔥 МАРК X ЗАПУСКАЕТСЯ НА RENDER (ПОРТ {PORT})... 🔥", flush=True)
    print("🤖 ЛОГИКА ПОСТИНГА И ИЗМЕНЕНИЙ ПОДКЛЮЧЕНА СТРОГО В КОДЕ.", flush=True)
    
    app = web.Application()
    app.router.add_post("/", handle_webhook)
    app.router.add_post("/{tail:.*}", handle_webhook)
    app.router.add_get("/", lambda r: web.Response(text="Бот МаркX онлайн и обрабатывает логику постинга!"))

    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"🟢 Сервер слушает интерфейс 0.0.0.0:{PORT}", flush=True)
    
    # Демонстрация работы процессов прямо в консоли при старте для проверки
    await asyncio.sleep(2)
    print("\n--- ТЕСТОВАЯ СИМУЛЯЦИЯ ПРОЦЕССОВ ВНУТРИ БОТА ---", flush=True)
    my_post = create_post("Привет, это мой первый автоматический пост!")
    publish_post(my_post)
    edit_post(my_post, "Привет, это мой первый автоматический пост! (Отредактировано)")
    print("------------------------------------------------\n", flush=True)
    
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Бот остановлен.")
        sys.exit(0)
