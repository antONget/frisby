from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import or_f
import logging
import asyncio
from module.data_base import add_token, get_list_users, get_user, delete_user
from secrets import token_urlsafe
from keyboards.keyboards_admin_player import keyboards_del_users, keyboard_delete_user, keyboard_edit_list_user
from filter.admin_filter import check_super_admin, check_admin


router = Router()
user_dict = {}


# ИГРОК
@router.message(F.text == 'Игрок', or_f(lambda message: check_admin(message.chat.id),
                                        lambda message: check_super_admin(message.chat.id)))
async def process_player(message: Message) -> None:
    logging.info(f'process_player: {message.chat.id}')
    await message.answer(text="Добавить или удалить игрока",
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
async def process_description(callback: CallbackQuery) -> None:
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
    list_user = get_list_users()
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
    list_user = get_list_users()
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
async def process_descriptiondel_user(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_descriptiondel_user: {callback.message.chat.id}')
    user_dict[callback.message.chat.id] = await state.get_data()
    delete_user(user_dict[callback.message.chat.id]["del_telegram_id"])
    await callback.message.answer(text=f'Игрок успешно удален')
    await asyncio.sleep(3)
    await process_player(callback.message)

