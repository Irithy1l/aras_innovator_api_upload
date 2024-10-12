import requests

from exception.error import SearchFailedError
from exception.error import UnauthorizedError


def search_item(item_type, attribute, value, token):
    """根据一个对象所属的对象类，属性名称与属性数值，来搜索是否存在，若是，则返回该搜索结果"""

    headers = {'Authorization': token}
    url = 'http://SERVER_ADDRESS/InnovatorServer/server/odata/' + item_type
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        for part in data['value']:
            try:
                if part[attribute] == value:
                    return part
            except KeyError as e:
                print(e.__str__())
        return None
    else:
        raise SearchFailedError(attribute, value)


def exist_part(name, code, token):
    """根据一个零部件的物料名称，图号/型号来查找零部件是否存在，若是，则返回该搜索结果"""

    headers = {'Authorization': token}
    url = 'http://SERVER_ADDRESS/InnovatorServer/server/odata/Part'
    response = requests.get(url, headers=headers)
    # print(response.text)
    if response.status_code == 200:
        data = response.json()
        for part in data['value']:
            if part['name'] == name and part['code'] == code:
                return part
        return None
    elif response.status_code == 401:
        raise UnauthorizedError()
    else:
        raise SearchFailedError('name', name)


if __name__ == '__main__':
    import connection.generate_token as generate_token
    import time
    token = 'Bearer ' + generate_token.generate('admin', 'innovator')
    start = time.time()
    r = exist_part('链条', 'AOB02-H6060YF-1323', token)
    end = time.time()

    print(r, end - start)

