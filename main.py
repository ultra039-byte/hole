import asyncio

async def main():
    print("🚀 Бот запустился на GitHub-шаблоне!")
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
