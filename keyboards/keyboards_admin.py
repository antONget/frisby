from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
import logging


# ГЛАВНОЕ МЕНЮ СУПЕРАДМИН
def keyboards_admin() -> ReplyKeyboardMarkup:
    logging.info("keyboards_super_admin")
    button_1 = KeyboardButton(text='Статистика')
    button_3 = KeyboardButton(text='Игрок')
    button_4 = KeyboardButton(text='Игра')
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1], [button_3], [button_4], ],
        resize_keyboard=True
    )
    return keyboard


def keyboards_super_admin() -> ReplyKeyboardMarkup:
    logging.info("keyboards_super_admin")
    button_1 = KeyboardButton(text='Статистика')
    button_3 = KeyboardButton(text='Игрок')
    button_4 = KeyboardButton(text='Игра')
    button_2 = KeyboardButton(text='Тренер')
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1], [button_3], [button_4], [button_2]],
        resize_keyboard=True
    )
    return keyboard


# ГЛАВНОЕ МЕНЮ МЕНЕДЖЕРА
def keyboards_player() -> ReplyKeyboardMarkup:
    logging.info("keyboards_manager")
    button_1 = KeyboardButton(text='Статистика')
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1], ],
        resize_keyboard=True
    )
    return keyboard
