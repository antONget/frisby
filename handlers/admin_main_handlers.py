from aiogram import Router
from aiogram.filters import CommandStart, or_f
from aiogram.types import Message

from filter.admin_filter import check_super_admin, check_admin
from filter.user_filter import check_user
from module.data_base import create_table_users, add_super_admin
from keyboards.keyboards_admin import keyboards_super_admin, keyboards_admin, keyboards_player

import logging

router = Router()


@router.message(CommandStart(), lambda message: check_super_admin(message.chat.id))
async def s(message: Message) -> None:
    logging.info("process_start_command")
    """
    Запуск бота супер-администратором
    :param message: 
    :return: 
    """
    create_table_users()
    add_super_admin(id_admin=message.chat.id, user_name=message.from_user.username)
    await message.answer(text=f"Привет, {message.from_user.first_name} 👋\n"
                              f"Вы администратор проекта, вы можете добавить игроков, смотреть статистику.",
                         reply_markup=keyboards_super_admin())


@router.message(CommandStart(), lambda message: check_admin(message.chat.id))
async def process_start_command_admin(message: Message) -> None:
    logging.info("process_start_command")
    """
    Запуск бота администратором
    :param message: 
    :return: 
    """
    create_table_users()
    add_super_admin(id_admin=message.chat.id, user_name=message.from_user.username)
    await message.answer(text=f"Привет, {message.from_user.first_name} 👋\n"
                              f"Вы администратор проекта, вы можете добавить игроков, смотреть статистику.",
                         reply_markup=keyboards_admin())


@router.message(CommandStart(), lambda message: check_user(message.chat.id))
async def process_start_command_manager(message: Message) -> None:
    logging.info("process_start_command_manager")
    """
    Запуск бота игроком
    :param message: 
    :return: 
    """
    create_table_users()
    await message.answer(text=f"Привет, {message.from_user.first_name} 👋\n"
                              f"Здесь можно посмотреть статистику",
                         reply_markup=keyboards_player())


