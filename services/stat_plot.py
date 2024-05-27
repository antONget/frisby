from matplotlib import pyplot as plt
from module.data_base import get_user
import os


def plot_stat_player(stat_command: dict, id_player: int, command_1: str, command_2: str):
	position = ['Атака', 'Защита']
	data = [stat_command[id_player][0], stat_command[id_player][1]]
	user_name = get_user(telegram_id=id_player)[0]
	fig = plt.figure(figsize=(10, 10))
	plt.title(label=f"Статистика {user_name}\n в игре {command_1} VS {command_2}", fontsize=30)
	plt.pie(data, labels=position, textprops={'fontsize': 25}, autopct='%1.0f%%')

	if not os.path.exists("./data"):
		os.makedirs("./data")
	fig.savefig(f'data/stat_{id_player}.png')


# def plot_stat_command(stat_command: dict, id_player: int, command_1: str, command_2: str):
# 	position = ['Атака', 'Защита']
# 	attack = 0
# 	protect = 0
# 	for player
# 	data = [stat_command[id_player][0], stat_command[id_player][1]]
# 	user_name = get_user(telegram_id=id_player)[0]
# 	fig = plt.figure(figsize=(10, 10))
# 	plt.title(label=f"Статистика {user_name}\n в игре {command_1} VS {command_2}", fontsize=30)
# 	plt.pie(data, labels=position, textprops={'fontsize': 25}, autopct='%1.0f%%')
#
# 	if not os.path.exists("./data"):
# 		os.makedirs("./data")
# 	fig.savefig(f'data/stat_{id_player}.png')
