import time
from pathlib import Path


class User:
    def __init__(self, username, password, auto_login, login_date):
        self.username = username
        self.password = password
        self.auto_login = auto_login
        self.login_date = float(login_date)

    def __str__(self):
        return f'{self.username} {self.password} {self.auto_login} {self.login_date}'

    def set_auto_login(self, value):
        self.auto_login = value

    def refresh_login_date(self):
        self.login_date = time.time()


class UserList:
    def __init__(self, filepath):
        self.user_list = {}

        self.filepath = Path(filepath)
        file = open(self.filepath, 'r')

        for line in file.readlines():
            username, pwd, auto, date = line.split()
            self.user_list[username] = User(username, pwd, auto, date)

        file.close()

    def write_user_list(self):
        file = open(self.filepath, 'w')
        output = []

        for username, user in self.user_list.items():
            output.append(str(user) + '\n')
        print(output)
        file.writelines(output)
        file.close()

    def add_user(self, user):
        self.user_list[user.username] = user




