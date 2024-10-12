import requests
import hashlib


def generate(username, password):
    innovator_username = username
    # innovator_password = "607920B64FE136F9AB2389E371852AF2"  # MD5 hash of Innovator user password
    innovator_password = hashlib.md5(password.encode()).hexdigest()
    innovator_database = "InnovatorSolutions"
    oauth_server_client_id = "IOMApp"
    innovator_server_discovery_url = 'http://SERVER_ADDRESS/InnovatorServer/Server/OAuthServerDiscovery.aspx'

    # Get OAuth server url
    oauth_server_url = get_oauth_server_url(innovator_server_discovery_url)
    if not oauth_server_url:
        return None

    # Get token endpoint
    oauth_server_configuration_url = f"{oauth_server_url}/.well-known/openid-configuration"
    token_url = get_token_endpoint(oauth_server_configuration_url)
    if not token_url:
        return None

    # Get access token
    body = {
        "grant_type": "password",
        "scope": "Innovator",
        "client_id": oauth_server_client_id,
        "username": innovator_username,
        "password": innovator_password,
        "database": innovator_database,
    }
    token_data = get_json(token_url, body=body)

    if not token_data:
        return None

    # Request parts using OData
    access_token = token_data.get('access_token')
    return access_token


def get_json(url, body=None):
    headers = {
        "Accept": "application/json",
    }
    response = None
    if body:
        response = requests.post(url, headers=headers, data=body)
    else:
        response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"{url}: {response.status_code} ({response.reason})")
        return None


def get_oauth_server_url(url):
    discovery = get_json(url)
    if discovery and 'locations' in discovery:
        return discovery['locations'][0]['uri']
    return None


def get_token_endpoint(url):
    configuration = get_json(url)
    return configuration.get('token_endpoint')


if __name__ == "__main__":
    # print(generate())
    pass
