from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup, default_state

from filter.admin_filter import check_admin
from config_data.config import Config, load_config
from keyboards.keyboards_admin_game import keyboard_select_place, keyboards_create_command, keyboard_confirm_command, \
    keyboards_select_player, keyboard_confirm_game, keyboard_type_game, keyboard_event_game
from module.data_base import get_list_users, set_select, get_select, get_list_command, get_game, set_game, set_gameover,\
    add_game, create_table_games, get_info_coach

import logging
import json
from datetime import datetime

router = Router()
config: Config = load_config()


class Game(StatesGroup):
    name_command_1 = State()
    name_command_2 = State()


user_dict = {}


@router.message(F.text == 'Игра', lambda message: check_admin(message.chat.id))
async def process_game(message: Message, state: FSMContext) -> None:
    """
    Запуск игрового процесса
    :param message:
    :param state:
    :return:
    """
    logging.info(f'process_game: {message.chat.id}')
    await message.answer(text="Введите название вашей команды:")
    await state.set_state(Game.name_command_1)


@router.message(F.text, StateFilter(Game.name_command_1))
async def get_name_command_1(message: Message, state: FSMContext) -> None:
    """
    Получение название своей команды
    :param message: message.text содержит название команды
    :param state:
    :return:
    """
    logging.info(f'get_name_command_1: {message.chat.id}')
    await state.update_data(name_command_1=message.text)
    await message.answer(text="Введите название команды соперника:")
    await state.set_state(Game.name_command_2)


@router.message(F.text, StateFilter(Game.name_command_2))
async def get_name_command_2(message: Message, state: FSMContext) -> None:
    """
    Получение название команды соперника
    :param message: message.text содержит название команды соперника
    :param state:
    :return:
    """
    logging.info(f'get_name_command_2: {message.chat.id}')
    await state.update_data(name_command_2=message.text)
    user_dict[message.chat.id] = await state.get_data()
    name_command_1 = user_dict[message.chat.id]['name_command_1']
    name_command_2 = user_dict[message.chat.id]['name_command_2']
    await state.set_state(default_state)
    await message.answer(text=f'Укажите где проходит игра\n'
                              f'<b>{name_command_1} VS {name_command_2}</b>',
                         reply_markup=keyboard_select_place(),
                         parse_mode='html')


@router.callback_query(F.data.startswith('place'))
async def select_player(callback: CallbackQuery, state: FSMContext):
    """
    Получение места проведения игры, влияет на количество игроков в розыгрыше
    :param callback: callback.data.split('_')[1] содержит для ЗАЛА 5 и УЛИЦА 7 игроков
    :param state:
    :return:
    """
    logging.info(f'select_player: {callback.message.chat.id}')
    if callback.data.split('_')[1] == 'street':
        count_players = 7
    elif callback.data.split('_')[1] == 'room':
        count_players = 5
    await state.update_data(count_players=count_players)
    await state.update_data(place_game=callback.data.split('_')[1])
    list_user = get_list_users(id_coach=callback.message.chat.id)
    info_coach = get_info_coach(id_coach=callback.message.chat.id)
    list_user.append(info_coach)
    keyboard = keyboards_create_command(list_users=list_user,
                                        back=0,
                                        forward=2,
                                        count=6)
    user_dict[callback.message.chat.id] = await state.get_data()
    name_command_1 = user_dict[callback.message.chat.id]['name_command_1']
    name_command_2 = user_dict[callback.message.chat.id]['name_command_2']
    await callback.message.edit_text(text=f'Добавьте игроков в заявку на игру\n'
                                          f'<b>{name_command_1} VS {name_command_2}</b>',
                                     reply_markup=keyboard,
                                     parse_mode='html')


# >>>>
@router.callback_query(F.data.startswith('playerforward'))
async def process_forward(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Действие на пагинацию, если в блоке недостаточно места для всех игроков
    :param callback: callback.data.split('_')[1] номер блока для вывода списка игроков
    :param state:
    :return:
    """
    logging.info(f'process_forward: {callback.message.chat.id}')
    list_user = get_list_users(id_coach=callback.message.chat.id)
    info_coach = get_info_coach(id_coach=callback.message.chat.id)
    list_user.append(info_coach)
    forward = int(callback.data.split('_')[1]) + 1
    back = forward - 2
    keyboard = keyboards_create_command(list_user, back, forward, 6)
    user_dict[callback.message.chat.id] = await state.get_data()
    name_command_1 = user_dict[callback.message.chat.id]['name_command_1']
    name_command_2 = user_dict[callback.message.chat.id]['name_command_2']
    try:
        await callback.message.edit_text(text=f'Выбeрите игрока, которого вы хотите добавить в заявку на игру'
                                              f'<b>{name_command_1} VS {name_command_2}</b>',
                                         reply_markup=keyboard,
                                         parse_mode='html')
    except:
        await callback.message.edit_text(text=f'Выберите игрока, которого вы хотите добавить в заявку на игру'
                                              f'<b>{name_command_1} VS {name_command_2}</b>',
                                         reply_markup=keyboard,
                                         parse_mode='html')


# <<<<
@router.callback_query(F.data.startswith('playerback'))
async def process_back(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Действие на пагинацию, если в блоке недостаточно места для всех игроков
    :param callback: callback.data.split('_')[1] номер блока для вывода списка игроков
    :param state:
    :return:
    """
    logging.info(f'process_back: {callback.message.chat.id}')
    list_user = get_list_users(id_coach=callback.message.chat.id)
    info_coach = get_info_coach(id_coach=callback.message.chat.id)
    list_user.append(info_coach)
    back = int(callback.data.split('_')[1]) - 1
    forward = back + 2
    keyboard = keyboards_create_command(list_user, back, forward, 6)
    user_dict[callback.message.chat.id] = await state.get_data()
    name_command_1 = user_dict[callback.message.chat.id]['name_command_1']
    name_command_2 = user_dict[callback.message.chat.id]['name_command_2']
    try:
        await callback.message.edit_text(text=f'Выберите игрока, которого вы хотите добавить в заявку на игру'
                                              f'<b>{name_command_1} VS {name_command_2}</b>',
                                         reply_markup=keyboard,
                                         parse_mode='html')
    except:
        await callback.message.edit_text(text=f'Выбeрите игрока, которого вы хотите добавить в заявку на игру'
                                              f'<b>{name_command_1} VS {name_command_2}</b>',
                                         reply_markup=keyboard,
                                         parse_mode='html')


# добавление игрока в команду
@router.callback_query(F.data.startswith('selectplayer_'))
async def process_select_player(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Перевод игрока команды в заявку на игру (при повторном нажатии вывод из заявки),
    на клавиатуре при нажатии появляются эмодзи ❌ и ✅ для выведенного из заявки и добавленного игрока в нее
    соответственно
    :param callback: callback.data.split('_')[1] содержит id телеграм выбранного игрока для добавления в заявку на игру
    :param state:
    :return:
    """
    logging.info(f'process_select_player: {callback.message.chat.id}')
    telegram_id = int(callback.data.split('_')[1])
    if get_select(telegram_id=telegram_id):
        set_select(in_command=0, telegram_id=telegram_id)
    else:
        set_select(in_command=1, telegram_id=telegram_id)
    list_user = get_list_users(id_coach=callback.message.chat.id)
    info_coach = get_info_coach(id_coach=callback.message.chat.id)
    list_user.append(info_coach)
    user_dict[callback.message.chat.id] = await state.get_data()
    name_command_1 = user_dict[callback.message.chat.id]['name_command_1']
    name_command_2 = user_dict[callback.message.chat.id]['name_command_2']
    keyboard = keyboards_create_command(list_users=list_user,
                                        back=0,
                                        forward=2,
                                        count=6)
    await callback.message.edit_reply_markup(text=f'Добавьте игроков в заявку на игру'
                                                  f'<b>{name_command_1} VS {name_command_2}</b>',
                                             reply_markup=keyboard)


@router.callback_query(F.data == 'create_command')
async def process_create_command(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Согласование состава команды на игру (заявки на игру)
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_create_command: {callback.message.chat.id}')
    list_command = get_list_command(id_coach=callback.message.chat.id)
    info_coach = get_info_coach(id_coach=callback.message.chat.id)
    if info_coach[2]:
        list_command.append(info_coach)
    user_dict[callback.message.chat.id] = await state.get_data()
    name_command_1 = user_dict[callback.message.chat.id]['name_command_1']
    text = f'<b>Состав команды {name_command_1}:</b>\n'
    for i, player in enumerate(list_command):
        text += f'{i+1}. {player[1]}\n'
    await callback.message.edit_text(text=text,
                                     reply_markup=keyboard_confirm_command(),
                                     parse_mode='html')


@router.callback_query(F.data == 'change_command')
async def process_change_command(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Изменение состава команды (заявки на игру)
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_change_command: {callback.message.chat.id}')
    list_user = get_list_users(id_coach=callback.message.chat.id)
    info_coach = get_info_coach(id_coach=callback.message.chat.id)
    list_user.append(info_coach)
    user_dict[callback.message.chat.id] = await state.get_data()
    name_command_1 = user_dict[callback.message.chat.id]['name_command_1']
    name_command_2 = user_dict[callback.message.chat.id]['name_command_2']
    keyboard = keyboards_create_command(list_users=list_user,
                                        back=0,
                                        forward=2,
                                        count=6)
    await callback.message.edit_reply_markup(text=f'Добавьте игроков в заявку на игру'
                                                  f'<b>{name_command_1} VS {name_command_2}</b>',
                                             reply_markup=keyboard)


@router.callback_query(F.data == 'confirm_command')
async def process_confirm_command(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Подтверждение создания состава команды (заявки на игру)
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_confirm_command: {callback.message.chat.id}')
    # указываем что это первый розыгрыш
    await state.update_data(firstgame=1)
    list_command = get_list_command(id_coach=callback.message.chat.id)
    info_coach = get_info_coach(id_coach=callback.message.chat.id)
    if info_coach[2]:
        list_command.append([info_coach[0], info_coach[1], info_coach[3]])
    user_dict[callback.message.chat.id] = await state.get_data()
    name_command_1 = user_dict[callback.message.chat.id]['name_command_1']
    await callback.message.edit_text(text=f'Команда {name_command_1} создана')
    keyboard = keyboards_select_player(list_users=list_command,
                                       back=0,
                                       forward=2,
                                       count=6)
    await callback.message.edit_text(text='Добавьте игроков в розыгрыш',
                                     reply_markup=keyboard)


# >>>>
@router.callback_query(F.data.startswith('gameforward'))
async def process_forward_game(callback: CallbackQuery) -> None:
    """
    Пагинация по списку угроков в завке на игру для добавления в розыгрыш
    :param callback: int(callback.data.split('_')[1]) номер блока для вывода игроков
    :return:
    """
    logging.info(f'process_forward_game: {callback.message.chat.id}')
    list_command = get_list_command(id_coach=callback.message.chat.id)
    info_coach = get_info_coach(id_coach=callback.message.chat.id)
    if info_coach[2]:
        list_command.append([info_coach[0], info_coach[1], info_coach[3]])
    forward = int(callback.data.split('_')[1]) + 1
    back = forward - 2
    keyboard = keyboards_select_player(list_command, back, forward, 6)
    try:
        await callback.message.edit_text(text='Выбeрите игрока, которого вы хотите добавить в розыгрыш',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выберите игрока, которого вы хотите добавить в розыгрыш',
                                         reply_markup=keyboard)


# <<<<
@router.callback_query(F.data.startswith('gameback'))
async def process_back_game(callback: CallbackQuery) -> None:
    """
    Пагинация по списку угроков в завке на игру для добавления в розыгрыш
    :param callback: int(callback.data.split('_')[1]) номер блока для вывода игроков
    :return:
    """
    logging.info(f'process_back_game: {callback.message.chat.id}')
    list_command = get_list_command(id_coach=callback.message.chat.id)
    info_coach = get_info_coach(id_coach=callback.message.chat.id)
    if info_coach[2]:
        list_command.append([info_coach[0], info_coach[1], info_coach[3]])
    back = int(callback.data.split('_')[1]) - 1
    forward = back + 2
    keyboard = keyboards_select_player(list_command, back, forward, 6)
    try:
        await callback.message.edit_text(text='Выберите игрока, которого вы хотите добавить в розыгрыш',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выбeрите игрока, которого вы хотите добавить в розыгрыш',
                                         reply_markup=keyboard)


# добавление игрока в розыгрыш
@router.callback_query(F.data.startswith('gameplayer_'))
async def process_select_player_game(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Добавление игрока команды в розыгрыш (при повторном нажатии удаление из розыгрыша),
    на клавиатуре при нажатии появляются эмодзи ❌ и ✅ для удаленного из розыгрыша и добавленного игрока в него
    соответственно
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_select_player_game: {callback.message.chat.id}')
    telegram_id = int(callback.data.split('_')[1])
    print(telegram_id)
    if get_game(telegram_id=telegram_id):
        set_game(in_game=0,
                 telegram_id=telegram_id)
    else:
        set_game(in_game=1,
                 telegram_id=telegram_id)
    list_command = get_list_command(id_coach=callback.message.chat.id)
    info_coach = get_info_coach(id_coach=callback.message.chat.id)
    if info_coach[2]:
        list_command.append([info_coach[0], info_coach[1], info_coach[3]])
    keyboard = keyboards_select_player(list_users=list_command,
                                       back=0,
                                       forward=2,
                                       count=6)
    await callback.message.edit_reply_markup(text='Добавьте игроков в розыгрыш',
                                             reply_markup=keyboard)


@router.callback_query(F.data == 'create_game')
async def process_create_game(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Согласование состава розыгрыша
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_create_game: {callback.message.chat.id}')
    list_command = get_list_command(id_coach=callback.message.chat.id)
    info_coach = get_info_coach(id_coach=callback.message.chat.id)
    if info_coach[2]:
        list_command.append([info_coach[0], info_coach[1], info_coach[3]])
    # list_command_ = []
    list_command_ = [player for player in list_command if player[2]]
    user_dict[callback.message.chat.id] = await state.get_data()
    count_players = user_dict[callback.message.chat.id]['count_players']
    print(count_players, len(list_command_))
    if len(list_command_) < count_players:
        await callback.answer(text=f'В розыгрыше недостаточно игроков, добавьте еще {count_players - len(list_command_)}'
                                   f' игрока(ов)',
                              show_alert=True)
        # return
    elif len(list_command_) > count_players:
        await callback.answer(text=f'В розыгрыш добавлено много игроков, уберите {len(list_command_) - count_players}'
                                   f' игрока(ов)',
                              show_alert=True)
        # return
    # else:
    if len(list_command_) < count_players:
        text = f'<b>Состав розыгрыша:</b>\n'
        i = 0
        for player in list_command_:
            if player[2]:
                i += 1
                text += f'{i}. {player[1]}\n'

        await callback.message.edit_text(text=text,
                                         reply_markup=keyboard_confirm_game(),
                                         parse_mode='html')


@router.callback_query(F.data == 'change_game')
async def process_change_game(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Измененение состава розыгрыша
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_change_game: {callback.message.chat.id}')
    list_command = get_list_command(id_coach=callback.message.chat.id)
    info_coach = get_info_coach(id_coach=callback.message.chat.id)
    if info_coach[2]:
        list_command.append([info_coach[0], info_coach[1], info_coach[3]])
    # если игра уже идет, и производится замена игроков в розыгрыше, то нужно удалить последнюю позицию розыгрыша
    if 'stat' in user_dict[callback.message.chat.id].keys():
        user_dict[callback.message.chat.id] = await state.get_data()
        position = user_dict[callback.message.chat.id]['position']
        for player in list_command:
            # telegram_id, username, in_game
            if player[2]:
                if position == 'attack':
                    user_dict[callback.message.chat.id]['stat'][player[0]][0] -= 1
                else:
                    user_dict[callback.message.chat.id]['stat'][player[0]][1] -= 1
    keyboard = keyboards_select_player(list_users=list_command,
                                       back=0,
                                       forward=2,
                                       count=6)
    await callback.message.edit_text(text='Добавьте игрока в розыгрыш',
                                     reply_markup=keyboard)


@router.callback_query(F.data == 'confirm_game')
async def process_confirm_game(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Начало игры (первый розыгрыш)
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_create_command: {callback.message.chat.id}')
    user_dict[callback.message.chat.id] = await state.get_data()
    # проверка, что розыгрыш первый
    if user_dict[callback.message.chat.id]['firstgame']:
        await state.update_data(firstgame=0)
        await state.update_data(turnover=0)
        await state.update_data(goal=0)
        await state.update_data(goal_break=0)
        await state.update_data(nogoal=0)
        await state.update_data(stat={})
        await callback.message.edit_text(text='С какой позиции начинается первый розыгрыш?',
                                         reply_markup=keyboard_type_game())
    # если розыгрыш не первый, то позиция (Атака или Защита) назначается автоматически
    else:
        await process_get_position_game_continue(callback=callback,
                                                 state=state)


@router.callback_query(F.data.startswith('position'))
async def process_get_position_game(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Получаем позицию команды, с которой начинается игра
    :param callback: callback.data.split('_')[1] позиция (attack или protection)
    :param state:
    :return:
    """
    logging.info(f'process_get_position_game: {callback.message.chat.id}')
    await state.update_data(position=callback.data.split('_')[1])
    await process_get_position_game_continue(callback=callback,
                                             state=state)


async def process_get_position_game_continue(callback: CallbackQuery, state: FSMContext, turn: bool = True) -> None:
    """
    Ведение статистики событий игры
    :param callback:
    :param state:
    :param turn:
    :return:
    """
    logging.info(f'process_get_position_game_continue: {callback.message.chat.id}')
    user_dict[callback.message.chat.id] = await state.get_data()
    # получаем позицию
    type_position = user_dict[callback.message.chat.id]['position']
    if type_position == 'attack':
        position = 'АТАКА'
    else:
        position = 'ЗАЩИТА'
    # список игроков в команде для формирования списка розыгрыша
    list_command = get_list_command(id_coach=callback.message.chat.id)
    text = f'<i>Состав розыгрыша:</i>\n'
    i = 0
    for player in list_command:
        if player[2]:
            i += 1
            text += f'{i}. {player[1]}\n'
    # формируем статистику для игроков, если нажата любая из кнопок кроме turnover
    if turn:
        # получаем текущую статистику
        stat = user_dict[callback.message.chat.id]['stat']
        print(stat)
        # проходим по списку команды
        for player in list_command:
            # если игорок в текущем розыгрыше
            # telegram_id, username, in_game
            if player[2]:
                # если в словаре статистики уже есть этот игрок
                if player[0] in stat.keys():
                    if type_position == 'attack':
                        # увеличиваем количество розыгрышей в атаке для игрока
                        stat[player[0]][0] += 1
                    else:
                        # увеличиваем количество розыгрышей в защите для игрока
                        stat[player[0]][1] += 1
                # если нет в статистике этого игрока
                else:
                    if type_position == 'attack':
                        # создаем ключ игрока в словаре и указываем количество розыгрышей для игрока
                        stat[player[0]] = [1, 0]
                    else:
                        # создаем ключ игрока в словаре и указываем количество розыгрышей для игрока
                        stat[player[0]] = [0, 1]
        print(stat)
    # получаем текущие стат данные
    turnover = user_dict[callback.message.chat.id]['turnover']
    goal = user_dict[callback.message.chat.id]['goal']
    nogoal = user_dict[callback.message.chat.id]['nogoal']
    break_goal = user_dict[callback.message.chat.id]['goal_break']
    await callback.message.edit_text(text=f'<b>{position}</b>\n'
                                          f'{text}'
                                          f'Cчет: {goal+break_goal}-{nogoal}\n'
                                          f'Turnover: {turnover}\n'
                                          f'Выберите событие:',
                                     reply_markup=keyboard_event_game(),
                                     parse_mode='html')


@router.callback_query(F.data.startswith('turnover'))
async def process_set_event_turnover(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Нажата кнопка turnover, счет производится только из позиции атака
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_set_event_turnover: {callback.message.chat.id}')
    user_dict[callback.message.chat.id] = await state.get_data()
    position = user_dict[callback.message.chat.id]['position']
    turnover = user_dict[callback.message.chat.id]['turnover']
    if position == 'attack':
        await state.update_data(turnover=turnover + 1)
        await callback.answer(text='Произошла потеря, переход в ЗАЩИТУ')
        await state.update_data(position='protection')
    else:
        await callback.answer(text='Произошел перехват, переход в АТАКУ')
        # await state.update_data(position='attack')
    await process_get_position_game_continue(callback=callback, state=state, turn=False)


@router.callback_query(F.data.startswith('goal'))
async def process_set_event_goal(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Нажата кнопка ГОЛ, идет подсчет голов забитых из атаки и защиты
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_set_event_goal: {callback.message.chat.id}')
    user_dict[callback.message.chat.id] = await state.get_data()
    position = user_dict[callback.message.chat.id]['position']
    if position == 'attack':
        goal = user_dict[callback.message.chat.id]['goal']
        await state.update_data(goal=goal + 1)
    else:
        goal_break = user_dict[callback.message.chat.id]['goal_break']
        await state.update_data(goal_break=goal_break + 1)
    await callback.answer(text='Команда забила ГОЛ!!! Переход в защиту')
    await state.update_data(position='protection')
    await process_get_position_game_continue(callback=callback, state=state)


@router.callback_query(F.data.startswith('nogoal'))
async def process_set_event_goal(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Нажата кнопка ПРОПУСК
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_set_event_goal: {callback.message.chat.id}')
    goal = user_dict[callback.message.chat.id]['nogoal']
    await state.update_data(nogoal=goal + 1)
    await callback.answer(text='Команда соперника забила ГОЛ((( Переход в атаку')
    await state.update_data(position='attack')
    await process_get_position_game_continue(callback=callback, state=state)


# @router.callback_query(F.data.startswith('break'))
# async def process_set_event_break(callback: CallbackQuery, state: FSMContext) -> None:
#     logging.info(f'process_set_event_break: {callback.message.chat.id}')
#     break_goal = user_dict[callback.message.chat.id]['goal_break']
#     await state.update_data(goal_break=break_goal + 1)
#     await callback.answer(text='Команда забила гол начиная с защиты!!!. Переход в защиту')
#     await state.update_data(position='protection')
#     await process_get_position_game_continue(callback=callback, state=state)


@router.callback_query(F.data.startswith('game_over'))
async def process_set_event_game_over(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    logging.info(f'process_set_event_game_over: {callback.message.chat.id}')
    user_dict[callback.message.chat.id] = await state.get_data()
    if 'position' not in user_dict[callback.message.chat.id]:
        await bot.delete_message(chat_id=callback.message.chat.id,
                                 message_id=callback.message.message_id)
        await callback.answer(text='Игра завершена. Статистика не собрана', show_alert=True)
        return
    list_command = get_list_command(id_coach=callback.message.chat.id)
    user_dict[callback.message.chat.id] = await state.get_data()
    position = user_dict[callback.message.chat.id]['position']
    # если игра уже идет, и производится замена игроков в розыгрыше, то нужно удалить последнюю позицию розыгрыша
    if 'stat' in user_dict[callback.message.chat.id].keys():
        for player in list_command:
            # telegram_id, username, in_game
            if player[2]:
                if position == 'attack':
                    user_dict[callback.message.chat.id]['stat'][player[0]][0] -= 1
                else:
                    user_dict[callback.message.chat.id]['stat'][player[0]][1] -= 1
    turnover = user_dict[callback.message.chat.id]['turnover']
    goal = user_dict[callback.message.chat.id]['goal']
    nogoal = user_dict[callback.message.chat.id]['nogoal']
    break_goal = user_dict[callback.message.chat.id]['goal_break']
    name_command_1 = user_dict[callback.message.chat.id]['name_command_1']
    name_command_2 = user_dict[callback.message.chat.id]['name_command_2']
    place_game = user_dict[callback.message.chat.id]['place_game']
    stat = user_dict[callback.message.chat.id]['stat']
    # stat_result = json.dumps(stat)
    await callback.message.answer(text=f'Игра завершена:\n'
                                       f'Cчет: {goal+break_goal}-{nogoal}\n'
                                       f'Turnover: {turnover}')
    await state.update_data(firstgame=0)
    await state.update_data(turnover=0)
    await state.update_data(goal=0)
    await state.update_data(goal_break=0)

    set_gameover(telegram_id=callback.message.chat.id)
    create_table_games()
    # получаем текущую дату
    current_date = datetime.now()
    # преобразуем ее в строку
    time_game = current_date.strftime('%d/%m/%Y')
    add_game(name_game=f'{name_command_1} VS {name_command_2}',
             place_game=place_game,
             time_game=time_game,
             goal=goal,
             goal_break=break_goal,
             nogoal=nogoal,
             turnover=turnover,
             stat_command=str(stat),
             id_coach=callback.message.chat.id)
    await callback.answer(text='Игра завершена. Статистика занесена в базу данных', show_alert=True)