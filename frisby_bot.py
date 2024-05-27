import asyncio
import logging

from aiogram import Bot, Dispatcher
from config_data.config import Config, load_config
from handlers import admin_main_handlers, admin_player_handlers, admin_game_handlers, admin_edit_admin_list
from handlers import auth_handler, player_handlers
from handlers import other_handlers
from module.data_base import create_table_users

# Инициализируем logger
logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def main():
    # create_table_users()
    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
        filename="py_log.log",
        filemode='w',
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Инициализируем бот и диспетчер
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher()

    # Регистрируем router в диспетчере
    dp.include_router(admin_main_handlers.router)
    dp.include_router(player_handlers.router)
    dp.include_router(admin_player_handlers.router)
    dp.include_router(admin_edit_admin_list.router)
    dp.include_router(admin_game_handlers.router)
    dp.include_router(auth_handler.router)
    dp.include_router(other_handlers.router)

    # Пропускаем накопившиеся update и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
