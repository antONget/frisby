from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.filters import or_f
import logging
import asyncio
from module.data_base import add_token, get_list_users, get_user, delete_user, set_name_player
from secrets import token_urlsafe
from keyboards.keyboards_admin_player import keyboards_del_users, keyboard_delete_user, keyboard_edit_list_user, \
    keyboards_change_users, keyboard_change_user
from filter.admin_filter import check_super_admin, check_admin


router = Router()
user_dict = {}


class Player(StatesGroup):
    name_player = State()


# ИГРОК
@router.message(F.text == 'Игрок', or_f(lambda message: check_admin(message.chat.id),
                                        lambda message: check_super_admin(message.chat.id)))
async def process_player(message: Message) -> None:
    logging.info(f'process_player: {message.chat.id}')
    await message.answer(text="Добавить, редактировать имя или удалить игрока",
                         reply_markup=keyboard_edit_list_user())


# добавить менеджера
@router.callback_query(F.data == 'add_user')
async def process_add_user(callback: CallbackQuery) -> None:
    logging.info(f'process_add_user: {callback.message.chat.id}')
    token_new = str(token_urlsafe(8))
    add_token(token_new=token_new, id_coach=callback.message.chat.id)
    await callback.message.edit_text(text=f'Для добавления игрока в бот отправьте ему этот TOKEN'
                                          f' <code>{token_new}</code>.'
                                          f' По этому TOKEN может быть добавлен только один игрок,'
                                          f' не делитесь и не показывайте его никому, кроме тех лиц для кого он'
                                          f' предназначен',
                                     parse_mode='html')


# удалить пользователя
@router.callback_query(F.data == 'delete_user')
async def process_delete_user(callback: CallbackQuery) -> None:
    logging.info(f'process_description: {callback.message.chat.id}')
    list_user = get_list_users(id_coach=callback.message.chat.id)
    print(list_user)
    keyboard = keyboards_del_users(list_user, 0, 2, 6)
    await callback.message.edit_text(text='Выберите игрока, которого вы хотите удалить',
                                     reply_markup=keyboard)


# >>>>
@router.callback_query(F.data.startswith('forward'))
async def process_forward(callback: CallbackQuery) -> None:
    logging.info(f'process_forward: {callback.message.chat.id}')
    list_user = get_list_users(id_coach=callback.message.chat.id)
    forward = int(callback.data.split('_')[1]) + 1
    back = forward - 2
    keyboard = keyboards_del_users(list_user, back, forward, 6)
    try:
        await callback.message.edit_text(text='Выбeрите игрока, которого вы хотите удалить',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выберите игрока, которого вы хотите удалить',
                                         reply_markup=keyboard)


# <<<<
@router.callback_query(F.data.startswith('back'))
async def process_back(callback: CallbackQuery) -> None:
    logging.info(f'process_back: {callback.message.chat.id}')
    list_user = get_list_users(id_coach=callback.message.chat.id)
    back = int(callback.data.split('_')[1]) - 1
    forward = back + 2
    keyboard = keyboards_del_users(list_user, back, forward, 6)
    try:
        await callback.message.edit_text(text='Выберите игрока, которого вы хотите удалить',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выбeрите игрока, которого вы хотите удалить',
                                         reply_markup=keyboard)


# подтверждение удаления пользователя из базы
@router.callback_query(F.data.startswith('deleteuser'))
async def process_deleteuser(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_deleteuser: {callback.message.chat.id}')
    telegram_id = int(callback.data.split('_')[1])
    user_info = get_user(telegram_id)
    await state.update_data(del_telegram_id=telegram_id)
    await callback.message.edit_text(text=f'Удалить игрока {user_info[0]}',
                                     reply_markup=keyboard_delete_user())


# отмена удаления пользователя
@router.callback_query(F.data == 'notdel_user')
async def process_notdel_user(callback: CallbackQuery) -> None:
    logging.info(f'process_notdel_user: {callback.message.chat.id}')
    await process_player(callback.message)


# удаление после подтверждения
@router.callback_query(F.data == 'del_user')
async def process_del_user(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_descriptiondel_user: {callback.message.chat.id}')
    user_dict[callback.message.chat.id] = await state.get_data()
    delete_user(user_dict[callback.message.chat.id]["del_telegram_id"])
    await callback.message.answer(text=f'Игрок успешно удален')
    await asyncio.sleep(3)
    await process_player(callback.message)


# удалить пользователя
@router.callback_query(F.data == 'change_user')
async def process_change_user(callback: CallbackQuery) -> None:
    logging.info(f'process_change_user: {callback.message.chat.id}')
    list_user = get_list_users(id_coach=callback.message.chat.id)
    print(list_user)
    keyboard = keyboards_change_users(list_user, 0, 2, 6)
    await callback.message.edit_text(text='Выберите игрока, имя которого вы хотите отредактировать',
                                     reply_markup=keyboard)


# >>>>
@router.callback_query(F.data.startswith('changeforward'))
async def process_forward_changeuser(callback: CallbackQuery) -> None:
    logging.info(f'process_forward_changeuser: {callback.message.chat.id}')
    list_user = get_list_users(id_coach=callback.message.chat.id)
    forward = int(callback.data.split('_')[1]) + 1
    back = forward - 2
    keyboard = keyboards_change_users(list_user, back, forward, 6)
    try:
        await callback.message.edit_text(text='Выбeрите игрока, имя которого вы хотите отредактировать',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выберите игрока, имя которого вы хотите отредактировать',
                                         reply_markup=keyboard)


# <<<<
@router.callback_query(F.data.startswith('changeback'))
async def process_back_changeuser(callback: CallbackQuery) -> None:
    logging.info(f'process_back_changeuser: {callback.message.chat.id}')
    list_user = get_list_users(id_coach=callback.message.chat.id)
    back = int(callback.data.split('_')[1]) - 1
    forward = back + 2
    keyboard = keyboards_change_users(list_user, back, forward, 6)
    try:
        await callback.message.edit_text(text='Выберите игрока, имя которого вы хотите отредактировать',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выбeрите игрока, имя которого вы хотите отредактировать',
                                         reply_markup=keyboard)


# подтверждение редактирования пользователя из базы
@router.callback_query(F.data.startswith('changeuser'))
async def process_changeuser(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_changeuser: {callback.message.chat.id}')
    telegram_id = int(callback.data.split('_')[1])
    user_info = get_user(telegram_id)
    await state.update_data(change_telegram_id=telegram_id)
    await callback.message.edit_text(text=f'Редактировать имя игрока {user_info[0]}',
                                     reply_markup=keyboard_change_user())


# отмена редактирования пользователя
@router.callback_query(F.data == 'notchange_user')
async def process_notchange_user(callback: CallbackQuery) -> None:
    logging.info(f'process_notchange_user: {callback.message.chat.id}')
    await process_player(callback.message)


# ввод нового имени
@router.callback_query(F.data == 'change_name_user')
async def process_change_name_user(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_change_name_user: {callback.message.chat.id}')
    user_dict[callback.message.chat.id] = await state.get_data()
    id_user = user_dict[callback.message.chat.id]["change_telegram_id"]
    user_name = get_user(telegram_id=id_user)[0]
    await callback.message.answer(text=f'Пришлите новое имя для пользователя {user_name}')
    await state.set_state(Player.name_player)


@router.message(F.text, StateFilter(Player.name_player))
async def get_name_player(message: Message, state: FSMContext) -> None:
    logging.info(f'get_name_player: {message.chat.id}')
    name_player = message.text
    user_dict[message.chat.id] = await state.get_data()
    id_user = user_dict[message.chat.id]["change_telegram_id"]
    set_name_player(name_player=name_player, telegram_id=id_user)
    await message.answer(text=f'Имя обновлено')
    await state.set_state(default_state)