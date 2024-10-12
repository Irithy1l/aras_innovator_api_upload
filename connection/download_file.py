
import requests

def get_part(user_id, token):
    url = 'http://SERVER_ADDRESS/InnovatorServer/Server/odata/Part?$expand=created_by_id'
    headers = {'Authorization': token}

    r = requests.get(url, headers=headers)
    print(r.text)
    part_list = r.json()['value']

    root_part = []

    for part in part_list:
        if (part['created_by_id']['id'] == user_id):
            root_part.append((part['item_number'], part['id'], part['name'], part['modified_on'], part['code']))

    print(root_part)
    return root_part

def get_file(user_id, token):
    base_url = 'http://SERVER_ADDRESS/InnovatorServer/Server/odata'
    headers = {'Authorization': token}

    url = base_url + f'/Document?$expand=created_by_id'

    r = requests.get(url, headers=headers)

    file_list = []

    document_list = r.json()['value']
    for document in document_list:
        if document['created_by_id']['id'] == user_id:
            file_list.append((document['name'], document['id'], document['created_on'], 'document'))

    print(file_list)
    print(r.text)





if __name__ == '__main__':
    import generate_token

    token = 'Bearer ' + generate_token.generate('liya@', '123456')

    get_part('35F9FBC8256F4EEE9DE21876A861E7B1', token)

