import json
import requests

from connection.item_number import generate_item_number
import connection.search as search
import connection.upload_file as upload_file

from exception.error import InsufficientPermissionsError
from exception.error import EmptyFileError
from exception.error import UploadFinish
from exception.error import SkipExist


class Part:
    def __init__(self, code: str, name: str, parent, level, classification='', token=''):
        """
        设置
        :param code: 图号/型号
        :param name: 物料名称
        :param parent: 父零部件
        :param level: 属于第几级零部件
        :param classification: 所属分类
        :param token: 令牌，用以上传零部件
        """
        self._code = code
        self._name = name
        self._parent = parent
        self._level = level

        if classification != '':
            self._classification = classification
        else:
            if self._parent is None:
                self._classification = '成品'
            elif self._parent.get_classification() == '成品':
                self._classification = '加工件/Assembly'
            else:
                self._classification = '加工件/Part'

        self._item_number = generate_item_number(self._name, self._code, token)

        self._data = {
            'name': self._name,
            'classification': self._classification,
            'code': self._code,
            'Part Document': [],
            'Part CAD': [],
            'Part BOM': []
        }

        self._subpart = []
        self._document = []
        self._cad = []

    def get_name(self) -> str:
        return self._name

    def get_level(self):
        return self._level

    def get_document(self):
        return self._document

    def get_cad(self):
        return self._cad

    def get_subpart(self):
        return self._subpart

    def get_classification(self):
        return self._classification

    def get_id(self, token):
        part = search.exist_part(self.get_name(), self.get_code(), token)
        if part:
            return part['id']
        else:
            return None

    def get_code(self):
        return self._code

    def add_subpart(self, p):
        self._subpart.append(p)

    def add_document(self, d):
        self._document.append(d)

    def add_cad(self, cad):
        self._cad.append(cad)

    def add_relation(self, item_type, id):
        """在该零部件的关系类下添加子零部件/子工程图/子文档"""

        relation = {
            'related_id@odata.bind': f'{item_type}(\'{id}\')'
        }
        self._data['Part '+item_type].append(relation)

    def upload_cad(self, cad, username, overwrite, token):
        """
        以输入用户名的账户，上传工程图
        :param cad: 工程图
        :param username: 用户名
        :param overwrite: 若已存在同名文件，是否要覆盖
        :param token: 令牌
        """

        try:
            file = upload_file.upload(cad, username, overwrite, token)
            id = file['id']
            item_number = file['item_number']
            # print('id', id)
        except EmptyFileError as e:
            raise EmptyFileError(e.path)
        except InsufficientPermissionsError as e:
            raise InsufficientPermissionsError(e.item_type, e.name)
        except SkipExist as e:
            raise SkipExist(e.name)
        else:
            if self.find_part_relation('CAD', item_number, token):
                raise UploadFinish('更新', '工程图', cad.name)
            else:
                self.add_relation('CAD', id)
                raise UploadFinish('上传', '工程图', cad.name)

    def upload_document(self, document, username, overwrite, token):
        """
        以输入用户名的账户，上传文档
        :param document: 文档
        :param username: 用户名
        :param overwrite: 若已存在同名文件，是否要覆盖
        :param token: 令牌
        """

        try:
            file = upload_file.upload(document, username, overwrite, token)
            id = file['id']
            item_number = file['item_number']
            # print('document id', id)
        except EmptyFileError as e:
            raise EmptyFileError(e.path)
        except InsufficientPermissionsError as e:
            raise InsufficientPermissionsError(e.item_type, e.name)
        except SkipExist as e:
            raise SkipExist(e.name)
        else:
            if self.find_part_relation('Document', item_number, token):
                raise UploadFinish('更新', '文档', document.name)
            else:
                self.add_relation('Document', id)
                raise UploadFinish('上传', '文档', document.name)

    def add_subpart_relation(self, token):
        """将子零部件加入关系类中"""

        for p in self._subpart:
            part = search.exist_part(p.get_name(), p.get_code(), token)
            if part:
                id = part['id']
                item_number = part['item_number']
                if self.find_part_relation('BOM', item_number, token):
                    pass
                else:
                    self.add_relation('BOM', id)
            else:
                pass

    def upload_part(self, token):
        """上传零部件"""

        # 准备上传的网址和头文件
        base_url = 'http://SERVER_ADDRESS/InnovatorServer/server/odata/Part'
        headers = {'Authorization': token}

        # 搜索该零部件是否存在
        part = search.exist_part(self.get_name(), self.get_code(), token)

        # 若存在，则更改该零部件的属性和关系类
        if part:
            part_id = part['id']
            url_patch = base_url + f'(\'{part_id}\')'
            r = requests.patch(url_patch, headers=headers, data=json.dumps(self._data))
            if r.status_code == 200:
                raise UploadFinish('更新', '零部件', self.get_name())
            elif r.status_code == 500 and r.json()['error']['code'] == 'SOAP-ENV:Server.InsufficientPermissionsException':
                raise InsufficientPermissionsError('零部件', self.get_name())

        # 若不存在，则创建新零部件
        else:
            url_post = base_url
            r = requests.post(url_post, headers=headers, data=json.dumps(self._data))
            print(url_post)
            print(self._data)
            print(r.text)
            raise UploadFinish('上传', '零部件', self.get_name())

    def find_part_relation(self, type, item_number, token):
        """
        搜索该零部件是否存在输入的关系类
        :param type: 子关系类所连接的对象类
        :param item_number: 物料编码
        :param token: 令牌
        :return: 是否存在该物料编码的子对象
        """

        # 准备获取关系类的头文件
        url_part_relation = f'http://SERVER_ADDRESS/InnovatorServer/server/odata/Part(\'{self.get_id(token)}\')/Part {type}'
        headers = {'Authorization': token}

        # 请求获取子对象列表
        part_relation = requests.get(url_part_relation, headers=headers)

        if part_relation.status_code == 200:
            part_relation = part_relation.json()

            # 遍历子对象列表
            for pb in part_relation['value']:
                # 获取该子关系类的ID
                id = pb['id']

                # 通过关系类的ID来获取其链接的子对象物料编码
                url_get = url_part_relation + f'(\'{id}\')?$select=related_id'
                get = requests.get(url_get, headers=headers)

                # 对比是否是目标物料编码
                if get.status_code == 200:
                    bom_item_number = get.json()['related_id@aras.keyed_name']
                    if bom_item_number == item_number:
                        return True

            return False

        else:
            return




