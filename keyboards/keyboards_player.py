from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging


def keyboards_list_game(list_game: list, back: int, forward: int, count: int):
    logging.info("keyboards_list_game")
    # проверка чтобы не ушли в минус
    if back < 0:
        back = 0
        forward = 2
    # считаем сколько всего блоков по заданному количество элементов в блоке
    count_users = len(list_game)
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
    for row in list_game[back*count:(forward-1)*count]:
        # row - [id, time_game, name_game, , goal, goal_break, nogoal, turnover, stat_command, coach]
        text = f'{row[2]} {row[1]}'
        button = f'gameselect_{row[0]}'
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    button_back = InlineKeyboardButton(text='<<',
                                       callback_data=f'gamesback_{str(back)}')
    button_next = InlineKeyboardButton(text='>>',
                                       callback_data=f'gamesforward_{str(forward)}')
    kb_builder.row(*buttons, width=1)
    kb_builder.row(button_back, button_next)
    return kb_builder.as_markup()


def keyboard_place() -> None:
    """
    ИГРА -> Атака или Защита
    :return:
    """
    logging.info("keyboard_type_game")
    button_1 = InlineKeyboardButton(text='Улица',
                                    callback_data='statplace_street')
    button_2 = InlineKeyboardButton(text='Зал',
                                    callback_data='statplace_room')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1], [button_2]],
    )
    return keyboard