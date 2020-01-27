import vk_api as vkapi
import requests
from bs4 import BeautifulSoup
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor, VkKeyboardButton
import json
output_rows = []
writeyourgroup = {}
writeyourdate = {}
usergroup = {}
# token : 4753258aa36e727b82691af62ec3425da7e41b82afc62cac1d0fbbf401cdaad837c069ec9ed4f5beb59c4
# клавиатура
keyboard = VkKeyboard(one_time=False, inline=False)

keyboard.add_button('Изменения моей группы', color=VkKeyboardColor.PRIMARY)
keyboard.add_button('Изменения по датам', color=VkKeyboardColor.DEFAULT)
keyboard.add_line()  # Переход на вторую строку
keyboard.add_button('В какой я группе?', color=VkKeyboardColor.POSITIVE)
keyboard.add_button('Изменить группу', color=VkKeyboardColor.NEGATIVE)


# парсим
r = requests.get('http://www.tthk.ee/tunniplaani-muudatused/')
html_content = r.text
soup = BeautifulSoup(html_content, 'html.parser')
table = soup.findChildren('table')
def updatefile(usergroup):
    file = open('ids.txt', 'w', encoding='utf-8')
    file.write(json.dumps(usergroup))
    file.close()
    return usergroup
def openfromfile(usergroup):
    file = open('ids.txt', 'r', encoding='utf-8')
    usergroup = eval(file.read())
    file.close()
    return usergroup
def write_msg(user_id, random_id, message):
    vk.method('messages.send', {'user_id': user_id, 'random_id': random_id, 'message': message})
def send_keyboard(peer_id, random_id, message):
    vk.method('messages.send', {'peer_id': peer_id, 'random_id': random_id, 'keyboard': keyboard.get_keyboard(), 'message': message})

token = "4753258aa36e727b82691af62ec3425da7e41b82afc62cac1d0fbbf401cdaad837c069ec9ed4f5beb59c4"
vk = vkapi.VkApi(token=token)


DayOfWeek = {'E': 'Понедельник',
            'T': 'Вторник',
            'K': 'Среда',
            'N': 'Четверг',
            'R': 'Пятница',
            'L': 'Суббота',
            'P': "Воскресенье"}


usergroup = openfromfile(usergroup)


def parsepage(table):
    print(len(table))
    muudatused = []
    for i in range(len(table)):
        my_table = table[i]
        rows = my_table.find_all('tr')
        for row in rows:
            muudatus = []
            cells = row.find_all('td')
            for cell in cells:
                if cell.text not in ["\xa0", "Kuupäev", "Rühm", "Tund", "Õpetaja", "Ruum"]:
                    data = cell.text
                    muudatus.append(data)
            # здесь есть полноценный список muudatus
            if muudatus != []:
                muudatused.append(muudatus)
        else:
            continue
    return muudatused

def getmuudatused(setgroup, usergroup, user):
    forshow = []
    muudatused = parsepage(table)
    for i in muudatused:
        if setgroup in i[2]:
            try:
                print(i[4])
            except IndexError:
                forshow.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]}")
                continue
            try:
                print(i[5])
            except IndexError:
                forshow.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]} Преподаватель: {i[4]}")
                continue
            if i[4] == " ":
                forshow.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]}")
            elif i[5] == " ":
                forshow.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]} Преподаватель: {i[4]}")
            elif i[4].lower() == "jääb ära":
                forshow.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]} не состоится")
            elif i[4].lower() == "söögivahetund":
                forshow.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]} обеденный перерыв")
            elif i[5].lower() == "iseseisev töö kodus":
                forshow.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]} самостоятельная работа дома")
            else:
                forshow.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]} Преподаватель: {i[4]} Кабинет: {i[5]}")
    if len(forshow) > 0:
        write_msg(event.user_id, event.random_id, f"Для группы {setgroup} на данный момент следующие изменения в расписании:")
        for w in forshow:
            write_msg(event.user_id, event.random_id, w)
    elif len(forshow) == 0:
        write_msg(user, event.random_id,"Для вашей группы изменений в расписании нет. Подробнее: www.tthk.ee/tunniplaani-muudatused.")

def getmuudatusedall(user, date):
    forshowall = []
    muudatused = parsepage(table)
    for i in muudatused:
        try:
            i[4]
        except IndexError:
            if i[1] == date:
                forshowall.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]}")
            continue
        try:
            i[5]
        except IndexError:
            if i[1] == date:
                forshowall.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]} Преподаватель: {i[4]}")
            continue
            # other
        if i[4] == " ":
            if i[1] == date:
                forshowall.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]}")
        elif i[5] == " ":
            if i[1] == date:
                forshowall.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]} Преподаватель: {i[4]}")
        elif i[4].lower() == "jääb ära":
            if i[1] == date:
                forshowall.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]} не состоится")
        elif i[4].lower() == "söögivahetund":
            if i[1] == date:
                forshowall.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]} обеденный перерыв")
        elif i[5].lower() == "iseseisev töö kodus":
            if i[1] == date:
                forshowall.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]} самостоятельная работа дома")
        else:
            if i[1] == date:
                forshowall.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]} Преподаватель: {i[4]} Кабинет: {i[5]}")
            else:
                print("There is just nothing.")
    if len(forshowall) > 0:
        write_msg(user, event.random_id, f"В учебном заведении на {date} следующие изменения в расписании:")
        kogutunniplaan = ""
        for w in forshowall:
            kogutunniplaan += f"{w}\n"
        write_msg(user, event.random_id, kogutunniplaan)
    elif len(forshowall) == 0:
        write_msg(user, event.random_id,"В данный момент изменений в расписании нет на дату, которую вы ввели. Подробнее: www.tthk.ee/tunniplaani-muudatused.")


longpoll = VkLongPoll(vk)
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            if event.text.lower() == "начать":
                usergroup = openfromfile(usergroup)
                send_keyboard(event.peer_id, event.random_id, "Выберите вариант из клаиватуры ниже.")
                if str(event.user_id) not in usergroup.keys():
                    write_msg(event.user_id, event.random_id, "У вас не указан код группы.")
            elif event.text.lower() == "указать группу" or event.text.lower() == "изменить группу":
                write_msg(event.user_id, event.random_id, "В какой группе вы находитесь?\nУкажите код вашей группы: ")
                writeyourgroup[event.user_id] = 1
            elif event.text[-3:].lower() in ['v19', 'v18', 'v17', 'e19', 'e18', 'e17'] and writeyourgroup[event.user_id] == 1:
                group = event.text
                usergroup[str(event.user_id)] = group
                write_msg(event.user_id, event.random_id, f"Вы указали, что Ваша группа: {usergroup[str(event.user_id)]}.")
                writeyourgroup[event.user_id] = 0
                usergroup = updatefile(usergroup)
            elif event.text.lower() == "в какой я группе?":
                if str(event.user_id) not in usergroup.keys():
                    write_msg(event.user_id, event.random_id, "У вас не указан код группы.")
                    pass
                write_msg(event.user_id, event.random_id, f"Вы указали, что Ваша группа: {usergroup[str(event.user_id)]}.")
            elif event.text.lower() == "изменения моей группы":
                setgroup = usergroup[str(event.user_id)]
                lastmuudatused = getmuudatused(setgroup, usergroup, event.user_id)
            elif event.text.lower() == "изменения по датам":
                write_msg(event.user_id, event.random_id, f"Укажите дату которую желаете найти в формате ДД.ММ.ГГГГ:")
                writeyourdate[str(event.user_id)] = 1
            elif event.text[-5:].lower() in ['.2020', '.2021', '.2022', '.2023', '.2024', '.2025', '.2026'] and writeyourdate[str(event.user_id)] == 1:
                newmuudatused = getmuudatusedall(event.user_id, event.text)
            else:
                write_msg(event.user_id, event.random_id, f"Данной команды не существует.")
