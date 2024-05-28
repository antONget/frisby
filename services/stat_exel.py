import pandas as pd
from module.data_base import get_user


def list_sales_to_exel(stat_command: dict, command_1: str, command_2: str):
    dict_stat = {"№ п/п": [], "Имя игрока": [], "Атака": [], "Защита": []}
    i = 0
    attack = 0
    protect = 0
    for id_player, stat_player in stat_command.items():
        i += 1
        dict_stat["№ п/п"].append(i)
        user_name = get_user(telegram_id=id_player)
        dict_stat["Имя игрока"].append(user_name)
        dict_stat["Атака"].append(stat_player[0])
        dict_stat["Защита"].append(stat_player[1])
        attack += stat_player[0]
        protect += stat_player[1]
    # dict_stat["№ п/п"].append('-')
    # dict_stat["Имя игрока"].append('Итого')
    # dict_stat["Атака"].append(attack)
    # dict_stat["Защита"].append(protect)
    df_stat = pd.DataFrame(dict_stat)
    with pd.ExcelWriter(path='./sales.xlsx', engine='xlsxwriter') as writer:
        df_stat.to_excel(writer, sheet_name=f'Статистика', index=False)

