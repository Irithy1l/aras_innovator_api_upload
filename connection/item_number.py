import connection.search as search


def generate_item_number(name, code, token):
    result_part = search.exist_part(name, code, token)
    if result_part:
        return result_part['item_number']
    else:
        return ''


if __name__ == '__main__':
    import generate_token
    import time
    start = time.time()
    print(generate_item_number('name', 'code',
                               generate_token.generate('admin', 'innovator')))
    end = time.time()
    print(end - start)

