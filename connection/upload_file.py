import requests
import json
import secrets
import os
import time

import connection.search as search
from exception.error import InsufficientPermissionsError
from exception.error import EmptyFileError
from exception.error import SkipExist

base_url = 'http://SERVER_ADDRESS/InnovatorServer'


def get_vault_id(username, token) -> str:
    """根据输入的用户名，获得上传文件的令牌"""

    headers = {'Authorization': token}

    user = search.search_item('User', 'login_name', username, token)
    user_id = user['id']

    url = base_url + f'/Server/odata/User(\'{user_id}\')?$select=default_vault'
    r = requests.get(url, headers=headers)
    return r.json()['default_vault@aras.id']


def begin_transaction(vault_id, token):
    """准备开始上传"""

    headers = {
        'Authorization': token,
        'VAULTID': vault_id
    }
    url = base_url + '/vault/odata/vault.BeginTransaction'
    r = requests.post(url, headers=headers)
    try:
        return r.json()['transactionId']
    except requests.exceptions.JSONDecodeError:
        print(r.text)


def get_upload_headers(token, escaped_name, start_range, end_range, file_size, transaction_id, vault_id):
    """上传时的头文件"""

    headers = {
        'VAULTID': vault_id,
        'Authorization': token,
        'Content-Disposition': 'attachment; filename*=utf-8\'\'' + escaped_name,
        'Content-Length': str(file_size),
        'Content-Range': 'bytes ' + str(start_range) + '-' + str(end_range) + '/' + str(file_size),
        'Content-Type': 'application/octet-stream',
        'transactionid': transaction_id
    }
    return headers


def escape_url(url):
    """将网址转换为合适的格式"""
    url = url.encode(encoding='utf-8')
    url = str(url)

    url = url.replace('\\', '~')

    url = url.replace('%', '%25')
    url = url.replace(' ', '%20')
    url = url.replace("'", '%27')
    url = url.replace('!', '%21')
    url = url.replace('"', '%22')
    url = url.replace('#', '%23')
    url = url.replace('$', '%24')
    url = url.replace('&', '%26')
    url = url.replace('(', '%28')
    url = url.replace(')', '%29')
    url = url.replace('*', '%2A')
    url = url.replace('+', '%2B')
    url = url.replace('?', '%3F')

    return url


def random_digit():
    """随机生成一位16进制的数字"""

    return secrets.choice('0123456789abcdef')


def generate_new_guid():
    """根据规则，生成一个随机的文件的ID"""

    template = 'xxxxxxxxxxxx4xxx8xxxxxxxxxxxxxxx'
    guid = ''.join(random_digit() if char == 'x' else char for char in template)
    return guid.upper()


def slice_file(filepath, start, end):
    """将大文件根据传入的开始与结尾进行切片"""

    with open(filepath, 'rb') as file:
        file.seek(start)
        chunk = file.read(end - start)
        file.close()
    return chunk


def upload_file_chunk(file, file_id, transaction_id, vault_id, token, chunk_size=10000000):
    """将文件进行切片上传"""

    escaped_name = escape_url(file.name.split('\\')[-1])



    result = []
    size = os.path.getsize(file.name)
    start = 0
    end = 0

    while end < size-1:
        end = start + chunk_size
        if size < end:
            end = size

        headers = get_upload_headers(token, escaped_name, start, end-1, size, transaction_id, vault_id)
        url_upload = base_url + '/vault/odata/vault.UploadFile?fileId=' + file_id
        chunck = slice_file(file.name, start, end)

        r = requests.post(url_upload, headers=headers, data=chunck)
        result.append(r)

        start += chunk_size

    # result 无实际用处，在文件上传报错时用以遍历查看请求的回复
    return result


def get_commit_headers(boundary, transaction_id, token):

    headers = {
        'Authorization': token,
        'OData-Version': '4.0',
        'transactionid': transaction_id,
        'Content-Type': 'multipart/mixed; boundary=' + boundary,
    }
    return headers


def commit_transaction(file, file_id, transaction_id, vault_id, token):
    """打包已上传文件切片，并作为整体上传"""

    boundary = 'batch_' + file_id
    commit_header = get_commit_headers(boundary, transaction_id, token)
    url_commit = base_url + '/vault/odata/vault.CommitTransaction'

    eol = '\r\n'

    size = os.path.getsize(file.name)

    original_name = file.name.split('\\')[-1]
    # name = escape_url(original_name)
    name = original_name

    commit_body = '--'
    commit_body += boundary
    commit_body += eol
    commit_body += 'Content-Type: application/http'
    commit_body += eol
    commit_body += eol
    commit_body += 'POST ' + base_url + '/Server/odata/File HTTP/1.1'
    commit_body += eol
    commit_body += 'Content-Type: application/json'
    commit_body += eol
    commit_body += eol
    commit_body += '{"id":"' + file_id + '",'
    commit_body += '"filename":"' + name + '",'
    commit_body += '"file_size":' + str(size) + ','
    commit_body += '"Located":[{"file_version":1,"related_id":"'+vault_id+'"}]}'
    commit_body += eol
    commit_body += "--" + boundary + "--"

    r = requests.post(url_commit, headers=commit_header, data=commit_body)
    # print('hello')
    return r, original_name


def upload_file(path: str, username, token) -> list[str]:
    """将上面的步骤打包进行完成"""

    vault_id = get_vault_id(username, token)
    transaction_id = begin_transaction(vault_id, token)
    file = open(path)
    file_id = generate_new_guid()
    upload_file_chunk(file, file_id, transaction_id, vault_id, token)
    r, original_name = commit_transaction(file, file_id, transaction_id, vault_id, token)
    return [r, file_id, original_name]


def unescape_url(url):
    """将被转换过的网址转换回来"""

    url = url.replace('~', '\\')
    url = url.replace('%20', ' ')
    url = url.replace('%21', '!')
    url = url.replace('%22', '"')
    url = url.replace('%23', '#')
    url = url.replace('%24', '$')
    url = url.replace('%25', '%')
    url = url.replace('%26', '&')
    url = url.replace('%27', "'")
    url = url.replace('%28', '(')
    url = url.replace('%29', ')')
    url = url.replace('%2A', '*')
    url = url.replace('%2B', '+')
    url = url.replace('%3F', '?')

    return url


def create_linked_document(file_id, original_name, overwrite, token):
    """根据文件类型，以及是否存在，是否覆盖，来让上传后的文件绑定到一个文档或工程图之下"""

    headers = {'Authorization': token}
    if original_name.endswith('.DRWDOT'):
        item_type = 'CAD'
    else:
        item_type = 'Document'

    item = search.search_item(item_type, 'name', original_name, token)
    if item:
        if overwrite:
            id = item['id']
            url_patch = base_url + f'/server/odata/{item_type}(\'{id}\')'
            body_patch = {
                'native_file@odata.bind': f'File(\'{file_id}\')'
            }
            p = requests.patch(url_patch, headers=headers, data=json.dumps(body_patch))
        else:
            raise SkipExist(original_name)

    else:
        url_post = base_url + '/server/odata/' + item_type
        body_post = {
            'name': original_name,
            'native_file@odata.bind': f'File(\'{file_id}\')'
        }
        p = requests.post(url_post, headers=headers, data=json.dumps(body_post))
    if p.status_code == 200 or p.status_code == 201:
        p = p.json()
        return p
    elif p.status_code == 500 and p.json()['error']['code'] == 'SOAP-ENV:Server.InsufficientPermissionsException':
        raise_item_type = '工程图' if item_type == 'CAD' else '文档'
        raise InsufficientPermissionsError(raise_item_type, original_name)


def upload(path, username, overwrite, token) -> str:
    """集合上面的步骤，并添加判断，返回文档或工程图的ID"""

    if os.path.getsize(path) == 0:
        raise EmptyFileError(path)
    response, file_id, original_name = upload_file(path, username, token)
    try:
        document_id = create_linked_document(file_id, original_name, overwrite, token)
    except InsufficientPermissionsError as e:
        raise InsufficientPermissionsError(e.item_type, e.name)
    except SkipExist as e:
        raise SkipExist(e.name)
    else:
        pass

    return document_id


if __name__ == '__main__':
    import connection.generate_token as generate_token
    token = 'Bearer ' + generate_token.generate('123', '123')

    start = time.time()
    print(upload('C:\\Users\\Administrator\\Desktop\\20240730存档.rar','123', True, token))
    end = time.time()

    print('time', end - start)
