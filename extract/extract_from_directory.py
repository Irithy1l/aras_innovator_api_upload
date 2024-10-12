from pathlib import Path
from structure.part import Part


def extract(path: Path, parent=None, token=''):
    """从文件夹中提取零部件信息，并以迭代的形式来对目录结构进行读取"""

    dot = path.name.find('.')
    code = path.name[:dot]
    name = path.name[dot+1:]

    p = str(path)
    level = 0
    while p.find('\\') != -1:
        level += 1
        p = p[p.find('\\')+1:]

    part = Part(code, name, parent, level, token=token)

    for d in path.iterdir():
        if d.is_file():
            if d.name.endswith('.DRWDOT'):
                part.add_cad(d)
            else:
                part.add_document(d)
        elif d.is_dir():
            part.add_subpart(extract(d, parent=part, token=token))

    return part


def create_list(part):
    """将根零部件展开，返回一个包括了根零部件及其下属零部件的列表"""

    part_list = [part]
    for p in part.get_subpart():
        subpart_list = create_list(p)
        for subpart in subpart_list:
            part_list.append(subpart)

    return part_list



def sort_by_level(part):
    """将零部件以第几级文件来排列的方法"""

    return part.get_level()
