from aiogram import Router, F
from aiogram.types import Message, CallbackQuery


from config_data.config import Config, load_config
from filter.user_filter import check_user
from module.data_base import get_list_game, get_id_coach, get_user
from keyboards.keyboards_player import keyboards_list_game, keyboard_place

import logging
import json


router = Router()
user_dict = {}
config: Config = load_config()



@router.message(F.text == 'Статистика', lambda message: check_user(message.chat.id))
async def process_statistic(message: Message) -> None:
    """
    Получение статитстики по игре
    :param message:
    :return:
    """
    logging.info(f'process_statistic: {message.chat.id}')
    await message.answer(text="Выберите место проведения игра для получения статистики",
                         reply_markup=keyboard_place())


@router.callback_query(F.data.startswith('statplace_'))
async def process_statistic(callback: CallbackQuery) -> None:
    """
    Получение статитстики по игре
    :param message:
    :return:
    """
    logging.info(f'process_statistic: {callback.message.chat.id}')
    place_game = callback.data.split('_')[1]
    print(place_game)
    id_coach = get_id_coach(id_player=callback.message.chat.id)
    list_game = []
    for game in get_list_game(id_coach=id_coach):
        print(game)
        if game[3] == place_game:
            list_game.append(game)
    keyboard = keyboards_list_game(list_game=list_game,
                                   back=0, forward=2, count=6)
    await callback.message.answer(text="Выберите игру по которой желаете получить статистику",
                                  reply_markup=keyboard)


# >>>>
@router.callback_query(F.data.startswith('gamesforward'))
async def process_forward_game(callback: CallbackQuery) -> None:
    """
    Пагинация по списку игр игрока
    :param callback: int(callback.data.split('_')[1]) номер блока для вывода игр
    :return:
    """
    logging.info(f'process_forward_game: {callback.message.chat.id}')
    place_game = callback.data.split('_')[1]
    id_coach = get_id_coach(id_player=callback.kmessage.chat.id)
    list_game = [game for game in get_list_game(id_coach=id_coach) if game[4] == place_game]

    forward = int(callback.data.split('_')[1]) + 1
    back = forward - 2
    keyboard = keyboards_list_game(list_game=list_game,
                                   back=back, forward=forward, count=6)
    try:
        await callback.message.edit_text(text="Выберите игру по которой желаете получить статистику",
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text="Выбeрите игру по которой желаете получить статистику",
                                         reply_markup=keyboard)


# <<<<
@router.callback_query(F.data.startswith('gamesback'))
async def process_back_game(callback: CallbackQuery) -> None:
    """
    Пагинация по списку игр игрока
    :param callback: int(callback.data.split('_')[1]) номер блока для вывода игр
    :return:
    """
    logging.info(f'process_back_game: {callback.message.chat.id}')
    place_game = callback.data.split('_')[1]
    id_coach = get_id_coach(id_player=callback.kmessage.chat.id)
    list_game = [game for game in get_list_game(id_coach=id_coach) if game[4] == place_game]
    back = int(callback.data.split('_')[1]) - 1
    forward = back + 2
    keyboard = keyboards_list_game(list_game=list_game,
                                   back=back, forward=forward, count=6)
    try:
        await callback.message.edit_text(text="Выберите игру по которой желаете получить статистику",
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text="Выбeрите игру по которой желаете получить статистику",
                                         reply_markup=keyboard)


@router.callback_query(F.data.startswith('gameselect_'))
async def process_select_player_game(callback: CallbackQuery) -> None:
    """
    Статистика игрока и команды по выбранной игре
    :param callback:
    :param state:
    :return:
    """
    id_game = int(callback.data.split('_')[1])
    id_coach = get_id_coach(callback.message.chat.id)
    list_game = get_list_game(id_coach)
    name_player = get_user(callback.message.chat.id)[0]
    # id INT, time_game TEXT, name_game TEXT, place_game TEXT, goal INT, goal_break INT, nogoal INT, turnover INT, stat_command TEXT, coach INT
    select_game = [game for game in list_game if game[0] == id_game][0]
    print(select_game[7])
    # stat_player = json.loads(select_game[7])
    stat_player = eval(select_game[8])
    await callback.message.answer(text=f'<b>Статистика команды:</b>\n'
                                       f'<u>Игра: {select_game[2]} - {select_game[3]}</u>\n'
                                       f'Cчет: <i>{select_game[4] + select_game[5]} - {select_game[6]}</i>\n'
                                       f'Очки занесенные из атаки: {select_game[4]}\n'
                                       f'Количество "Break": {select_game[5]}\n'
                                       f'Количество "Turnover": {select_game[7]}\n\n'
                                       f'Статистика игрока: @{name_player}\n'
                                       f'Атака: {stat_player[callback.message.chat.id][0]}\n'
                                       f'Защита: {stat_player[callback.message.chat.id][1]}',
                                  parse_mode='html')
