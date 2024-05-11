from aiogram.types import Message

import sqlite3
from config_data.config import Config, load_config
import logging


config: Config = load_config()
db = sqlite3.connect('database.db', check_same_thread=False, isolation_level='EXCLUSIVE')


# СОЗДАНИЕ ТАБЛИЦ
def create_table_users() -> None:
    """
    Создание таблицы верифицированных пользователей
    :return: None
    """
    logging.info("table_users")
    with db:
        sql = db.cursor()
        sql.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            token_auth TEXT,
            telegram_id INTEGER,
            username TEXT,
            is_admin INTEGER,
            in_command INTEGER,
            in_game INTEGER,
            coach INTEGER
        )""")
        db.commit()


def create_table_games() -> None:
    """
    Создание таблицы проведенных игр
    :return: None
    """
    logging.info("table_games")
    with db:
        sql = db.cursor()
        sql.execute("""CREATE TABLE IF NOT EXISTS games(
            id INTEGER PRIMARY KEY,
            time_game TEXT,
            name_game TEXT,
            place_game TEXT,
            goal INTEGER,
            goal_break INTEGER,
            nogoal INTEGER,
            turnover INTEGER,
            stat_command TEXT,
            coach INTEGER
        )""")
        db.commit()


# ПОЛЬЗОВАТЕЛЬ - верификация токена и добавление пользователя
def check_token(message: Message) -> bool:
    """
    Проверка токена на достоверность
    :param message:
    :return:
    """
    logging.info("check_token")
    with db:
        sql = db.cursor()
        # Выполнение запроса для получения token_auth
        sql.execute('SELECT token_auth, telegram_id  FROM users')
        list_token = [row for row in sql.fetchall()]
        # Извлечение результатов запроса и сохранение их в список
        print('check_token', list_token)
        for row in list_token:
            token = row[0]
            telegram_id = row[1]
            if token == message.text and telegram_id == 'telegram_id':
                if message.from_user.username:
                    sql.execute('UPDATE users SET telegram_id = ?, username = ? WHERE token_auth = ?',
                                (message.chat.id, message.from_user.username, message.text))
                    db.commit()
                    return True
                else:
                    sql.execute('UPDATE users SET telegram_id = ?, username = ? WHERE token_auth = ?',
                                (message.chat.id, 'anonimus', message.text))
                    db.commit()
                    return True

        db.commit()
        return False


def add_token(token_new: str, id_coach: int) -> None:
    """
    Добавление токена в таблицу пользователей с указанием кто его добавил
    :param token_new:
    :param id_coach:
    :return:
    """
    logging.info(f'add_token: {token_new}')
    with db:
        sql = db.cursor()
        sql.execute(f'INSERT INTO users (token_auth, telegram_id, username, is_admin, in_command, in_game, coach) '
                    f'VALUES ("{token_new}", "telegram_id", "username", 0, 0, 0, {id_coach})')
        db.commit()


def get_list_users(id_coach: int = None) -> list:
    """
    ПОЛЬЗОВАТЕЛЬ - список пользователей верифицированных в боте
    :return: list(telegram_id:int, username:str)
    """
    logging.info(f'get_list_users')
    with db:
        sql = db.cursor()
        sql.execute('SELECT telegram_id, username, in_command FROM users WHERE NOT username = ? AND coach = ?'
                    ' ORDER BY id', ('username', id_coach))
        list_username = [row for row in sql.fetchall()]
        return list_username


def get_user(telegram_id):
    """
    ПОЛЬЗОВАТЕЛЬ - имя пользователя по его id
    :param telegram_id:
    :return:
    """
    logging.info(f'get_user')
    with db:
        sql = db.cursor()
        return sql.execute('SELECT username FROM users WHERE telegram_id = ?', (telegram_id,)).fetchone()


def delete_user(telegram_id):
    """
    ПОЛЬЗОВАТЕЛЬ - удалить пользователя
    :param telegram_id:
    :return:
    """
    logging.info(f'delete_user')
    with db:
        sql = db.cursor()
        sql.execute('DELETE FROM users WHERE telegram_id = ?', (telegram_id,))
        db.commit()


def get_list_users_filter() -> list:
    """
    ПОЛЬЗОВАТЕЛЬ - список пользователей верифицированных в боте
    :return: list(telegram_id:int, username:str)
    """
    logging.info(f'get_list_users_filter')
    with db:
        sql = db.cursor()
        sql.execute('SELECT telegram_id, username, in_command FROM users WHERE NOT username = ?'
                    ' ORDER BY id', ('username',))
        list_username = [row for row in sql.fetchall()]
        return list_username


def add_super_admin(id_admin: int, user_name: str) -> None:
    """
    Добавление супер админа в таблицу пользователей
    :param id_admin:
    :param user_name:
    :return:
    """
    logging.info(f'add_super_admin')
    with db:
        sql = db.cursor()
        sql.execute('SELECT telegram_id FROM users')
        list_user = [row[0] for row in sql.fetchall()]

        if int(id_admin) not in list_user:
            sql.execute(f'INSERT INTO users (token_auth, telegram_id, username, is_admin, in_command, in_game, coach) '
                        f'VALUES ("SUPERADMIN", {id_admin}, "{user_name}", 1, 0, 0, {id_admin})')
            db.commit()


def get_list_command(id_coach: int = None) -> list:
    """
    ИГРА - список команды
    :return: list(telegram_id:int, username:str)
    """
    logging.info(f'get_list_users')
    with db:
        sql = db.cursor()
        sql.execute('SELECT telegram_id, username, in_game FROM users WHERE NOT username = ? AND coach = ?'
                    ' AND in_command = ? ORDER BY id', ('username', id_coach, 1))
        list_command = [row for row in sql.fetchall()]
        return list_command


def set_select(in_command: int, telegram_id: int):
    """
    Устанавливаем флаг добавления пользователя в команду
    :param telegram_id:
    :return:
    """
    logging.info(f'set_select')
    with db:
        sql = db.cursor()
        sql.execute('UPDATE users SET in_command = ? WHERE telegram_id = ?', (in_command, telegram_id))
        db.commit()


def get_select(telegram_id: int):
    """
    Получаем флаг пользователя в команде
    :param telegram_id:
    :return:
    """
    logging.info(f'set_select')
    with db:
        sql = db.cursor()
        in_command = sql.execute('SELECT in_command FROM users WHERE telegram_id = ?', (telegram_id,)).fetchone()
        return in_command[0]


def set_game(in_game: int, telegram_id: int):
    """
    Устанавливаем флаг добавления пользователя в розыгрыш
    :param telegram_id:
    :return:
    """
    logging.info(f'set_select')
    with db:
        sql = db.cursor()
        sql.execute('UPDATE users SET in_game = ? WHERE telegram_id = ?', (in_game, telegram_id))
        db.commit()


def get_game(telegram_id: int):
    """
    Получаем флаг пользователя в розыгрыше
    :param telegram_id:
    :return:
    """
    logging.info(f'set_select')
    with db:
        sql = db.cursor()
        in_command = sql.execute('SELECT in_game FROM users WHERE telegram_id = ?', (telegram_id,)).fetchone()
        return in_command[0]


def set_gameover(telegram_id: int):
    """
    Устанавливаем флаг добавления пользователя в розыгрыш
    :param telegram_id:
    :return:
    """
    logging.info(f'set_select')
    with db:
        sql = db.cursor()
        # telegram_id, username, in_command
        list_command = get_list_users(id_coach=telegram_id)
        for player in list_command:
            sql.execute('UPDATE users SET in_game = ? WHERE telegram_id = ?', (0, player[0]))
            sql.execute('UPDATE users SET in_command = ? WHERE telegram_id = ?', (0, player[0]))
        db.commit()


def get_list_admins() -> list:
    logging.info(f'get_list_admins')
    with db:
        sql = db.cursor()
        sql.execute('SELECT telegram_id, username FROM users WHERE is_admin = ? AND NOT username = ?', (1, 'username'))
        list_admins = [row for row in sql.fetchall()]
        return list_admins


def add_game(name_game: str, time_game: str, place_game: str, goal: int, goal_break: int, nogoal: int, turnover: int, stat_command: str, id_coach: int) -> None:
    logging.info(f'add_game')
    with db:
        sql = db.cursor()
        print(type(stat_command))
        sql.execute(f'INSERT INTO games (name_game, time_game, place_game, goal, goal_break, nogoal, turnover, stat_command, coach)'
                    f'VALUES ("{name_game}", "{time_game}", "{place_game}", {goal}, {goal_break}, {nogoal}, {turnover},'
                    f' "{stat_command}", {id_coach})')
        db.commit()


def get_id_coach(id_player: int) -> int:
    """
    СТАТИСТИКА - получить id тренера
    :return: list(telegram_id:int, username:str)
    """
    logging.info(f'get_list_users_filter')
    with db:
        sql = db.cursor()
        coach = sql.execute('SELECT coach FROM users WHERE telegram_id = ?', (id_player,)).fetchone()

        return coach[0]


def get_list_game(id_coach) -> list:
    """
    СТАТИСТИКА - список всех игр
    :return: list(telegram_id:int, username:str)
    """
    logging.info(f'get_list_users_filter')
    with db:
        sql = db.cursor()
        sql.execute('SELECT * FROM games WHERE coach = ?'
                    ' ORDER BY id', (id_coach,))
        list_username = [row for row in sql.fetchall()]
        return list_username



