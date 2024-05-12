from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging


def keyboard_select_place() -> None:
    logging.info("keyboard_select_place")
    button_1 = InlineKeyboardButton(text='Улица',
                                    callback_data='place_street')
    button_2 = InlineKeyboardButton(text='Зал',
                                    callback_data='place_room')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1, button_2]],
    )
    return keyboard


def keyboards_create_command(list_users: list, back: int, forward: int, count: int):
    logging.info("keyboards_create_command")
    # проверка чтобы не ушли в минус
    if back < 0:
        back = 0
        forward = 2
    # считаем сколько всего блоков по заданному количество элементов в блоке
    count_users = len(list_users)
    whole = count_users // count
    remains = count_users % count
    max_forward = whole + 1
    # если есть остаток, то увеличиваем количество блоков на один, чтобы показать остаток
    if remains:
        max_forward = whole + 2
    if forward > max_forward:
        forward = max_forward
        back = forward - 2
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    # print(list_users, count_users, back, forward, max_forward)
    for row in list_users[back*count:(forward-1)*count]:
        # row - [telegram_id, username, select]
        if row[2] == 0:
            select = ' ❌'
        else:
            select = ' ✅'
        text = row[1] + select
        button = f'selectplayer_{row[0]}'
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    button_back = InlineKeyboardButton(text='<<',
                                       callback_data=f'playerback_{str(back)}')
    button_count = InlineKeyboardButton(text=f'Команда',
                                        callback_data='create_command')
    button_next = InlineKeyboardButton(text='>>',
                                       callback_data=f'playerforward_{str(forward)}')
    kb_builder.row(*buttons, width=1)
    kb_builder.row(button_back, button_count, button_next)
    return kb_builder.as_markup()


def keyboard_confirm_command() -> None:
    """
    ИГРА -> подтверждение создания команды
    :return:
    """
    logging.info("keyboard_confirm_command")
    button_1 = InlineKeyboardButton(text='Создать команду',
                                    callback_data='confirm_command')
    button_2 = InlineKeyboardButton(text='Изменить состав',
                                    callback_data='change_command')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1], [button_2]],
    )
    return keyboard


def keyboards_select_player(list_users: list, back: int, forward: int, count: int):
    logging.info("keyboards_select_player")
    # проверка чтобы не ушли в минус
    if back < 0:
        back = 0
        forward = 2
    # считаем сколько всего блоков по заданному количество элементов в блоке
    count_users = len(list_users)
    whole = count_users // count
    remains = count_users % count
    max_forward = whole + 1
    # если есть остаток, то увеличиваем количество блоков на один, чтобы показать остаток
    if remains:
        max_forward = whole + 2
    if forward > max_forward:
        forward = max_forward
        back = forward - 2
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    # print(list_users, count_users, back, forward, max_forward)
    for row in list_users[back*count:(forward-1)*count]:
        # row - [telegram_id, username, select]
        if row[2] == 0:
            select = ' ❌'
        else:
            select = ' ✅'
        text = row[1] + select
        button = f'gameplayer_{row[0]}'
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    button_back = InlineKeyboardButton(text='<<',
                                       callback_data=f'gameback_{str(back)}')
    button_count = InlineKeyboardButton(text=f'Розыгрыш',
                                        callback_data='create_game')
    button_next = InlineKeyboardButton(text='>>',
                                       callback_data=f'gameforward_{str(forward)}')
    button_game_over = InlineKeyboardButton(text='Завершить игру',
                                            callback_data=f'game_over')
    kb_builder.row(*buttons, width=1)
    kb_builder.row(button_back, button_count, button_next)
    kb_builder.row(button_game_over)
    return kb_builder.as_markup()


def keyboard_confirm_game() -> None:
    """
    ИГРА -> подтверждение создания команды
    :return:
    """
    logging.info("keyboard_confirm_game")
    button_1 = InlineKeyboardButton(text='Создать розыгрыш',
                                    callback_data='confirm_game')
    button_2 = InlineKeyboardButton(text='Изменить состав',
                                    callback_data='change_game')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1], [button_2]],
    )
    return keyboard


def keyboard_type_game() -> None:
    """
    ИГРА -> Атака или Защита
    :return:
    """
    logging.info("keyboard_type_game")
    button_1 = InlineKeyboardButton(text='Атака',
                                    callback_data='position_attack')
    button_2 = InlineKeyboardButton(text='Защита',
                                    callback_data='position_protection')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1], [button_2]],
    )
    return keyboard


def keyboard_event_game() -> None:
    """
    ИГРА -> Атака или Защита
    :return:
    """
    logging.info("keyboard_type_game")
    button_1 = InlineKeyboardButton(text='ГОЛ',
                                    callback_data='goal')
    button_6 = InlineKeyboardButton(text='ПРОПУСК',
                                    callback_data='nogoal')
    button_2 = InlineKeyboardButton(text='Turnover',
                                    callback_data='turnover')
    button_3 = InlineKeyboardButton(text='BREAK',
                                    callback_data='break')
    button_5 = InlineKeyboardButton(text='Замена в розыгрыше',
                                    callback_data='change_game')
    button_4 = InlineKeyboardButton(text='Завершить игру',
                                    callback_data='game_over')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1, button_6], [button_2], [button_5], [button_4]],
    )
    return keyboard