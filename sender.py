import datetime
import os

import vk_api

from bot import SQL, Changes, Bot
import datetime
import os

import vk_api

from bot import SQL, Changes, Bot


class Sender:
    def __init__(self, api_token):
        self.mysql_l = os.environ['MYSQL_LOGIN']
        self.mysql_p = os.environ["MYSQL_PASS"]  # Getting login and password from service there bot is deployed
        self.sql = SQL()
        self.c = Changes()
        self.vk = vk_api.VkApi(token=api_token)
        self.bot = Bot(vk=self.vk)

    def start(self):
        print("Sender waiting.")
        t = datetime.datetime.now()
        t = t.hour, t.month, t.day
        wd = t.weekday()
        if t == (5, 0, 0) and wd not in [5, 6]:
            print("Sender was started.")
            list = self.getSenderList()
            for i in list:
                changes = self.makeSend(list[0], list[1])
                if changes is not None:
                    self.bot.sendMsg(vkid=list[0], msg=changes)

    def getSenderList(self):
        conn = self.sql.getConnection()
        with conn.cursor() as cursor:  # Getting user's group at school from database
            cursor.execute("SELECT `vkid`, `thkruhm` FROM `users` WHERE `sendStatus` = 1")
            row = cursor.fetchall()
            cursor.close()
        conn.close()
        return row['vkid', 'thkruhm']

    def makeSend(self, vkid, group):
        changes = self.c.parseChanges()
        for line in changes:
            if line[2].lower() in group:
                changeList = self.makeChanges(line, True)  # Takes converted lines of changes from makeChanges func
        if len(changeList) > 0:
            userfname = (self.vk.method('users.get', {'user_ids': vkid, 'fields': 'first_name'})[0])["first_name"]
            refChanges = f"Доброе утро, {userfname}!\n" \
                         f"Для группы 🦆 {group} на данный момент следующие изменения в расписании:\n"  # Head of the message
            for i in changeList:
                refChanges += f"{i}\n"
            return refChanges
        return None


access_token = os.environ["ACCESS_TOKEN"]
sender = Sender(access_token)
sender.start()
