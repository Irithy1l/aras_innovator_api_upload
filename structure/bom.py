from pathlib import Path

import extract.extract_from_directory as extract_from_directory


class BOM:

    def __init__(self, path: str, token):
        p = Path(path)

        # 根据路径提取根零部件以及其下属零部件
        self._root = extract_from_directory.extract(p, None, token=token)

        # 将根零部件展开，创建列表
        self._parts = extract_from_directory.create_list(self._root)

        # 将所有零部件以等级，从大到小排序
        # 等级越大，越处于目录结构的底部
        self._parts.sort(key=extract_from_directory.sort_by_level, reverse=True)

    def get_parts(self) -> list:
        return self._parts


