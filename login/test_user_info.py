import unittest
from user_info import *


class MyTestCase(unittest.TestCase):

    def test_user_init_str(self):
        a = User('123', '123', '1', '1724745213.159656')
        self.assertEqual(str(a), '123 123 1 1724745213.159656')

    def test_user_list_init(self):
        file = open('username_pwd.txt', 'w')
        file.writelines(['123 123 1 1724745213.159656'])
        file.close()

        user_list = UserList('username_pwd.txt')
        for username, user in user_list.user_list.items():
            self.assertEqual(user.username, '123')
            self.assertEqual(user.password, '123')
            self.assertEqual(user.auto_login, '1')
            self.assertEqual(user.login_date, '1724745213.159656')

    def test_write_user_info(self):
        user_list = UserList('username_pwd.txt')
        user_list.add_user(User('admin', 'innovator', '1', '1724747592.162849'))
        user_list.write_user_list()

        file = open('username_pwd.txt', 'r')
        lines = file.readlines()
        self.assertEqual(lines, ['123 123 1 1724745213.159656\n', 'admin innovator 1 1724747592.162849\n'])
        file.close()




if __name__ == '__main__':
    unittest.main()
