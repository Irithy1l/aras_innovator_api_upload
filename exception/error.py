class GetFailedError(Exception):
    def __init__(self, item_type=''):
        self.item_type = item_type
        if item_type != '':
            self.item_type += ' '

    def __str__(self):
        return f'GET {self.item_type}Failed'


class SearchFailedError(Exception):

    def __init__(self, attribute, value):
        self.para = attribute
        self.value = value

    def __str__(self):
        return f'{self.para} = {self.value} 的搜索失败'


class UnauthorizedError(Exception):
    def __str__(self):
        return '未验证登陆'


class EmptyFileError(Exception):

    def __init__(self, path):
        self.path = str(path)

    def __str__(self):
        return '此文件为空：' + self.path


class InsufficientPermissionsError(Exception):
    def __init__(self, item_type, name):
        self.item_type = item_type
        self.name = name

    def __str__(self):
        return f'无该{self.item_type}的更改权限: {self.name}'


class UploadFinish(Exception):
    def __init__(self, act, type, name):
        self.act = act
        self.type = type
        self.name = name

    def __str__(self):
        return f'完成{self.act}{self.type}: {self.name}'


class SkipExist(Exception):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f'跳过{self.name}'
