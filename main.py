import asyncio
from config_data.config import load_config, Config
from handlers import user_handlers
from aiogram import Bot, Dispatcher


async def main() -> None:
    config: Config = load_config()
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher()

    dp.include_router(user_handlers.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


asyncio.run(main())
