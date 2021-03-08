import requests
import base64
import json

from .utils.json import clean_ldjson


class SmershAPI:

    DEFAULT_USER_AGENT = 'SmershPythonClient'

    def __init__(self, main_url, user_agent=DEFAULT_USER_AGENT):
        if main_url.endswith('/'):
            main_url = main_url[:-1]

        self.main_url = main_url
        self.user_agent = user_agent
        self.token = None

    def request(self, method, path, body=None, content_type='application/ld+json'):
        if path[0] != '/':
            path = '/' + path

        headers = {
            'Accept': 'application/ld+json',
            'Content-Type': content_type,
            'User-Agent': self.user_agent
        }

        if self.authenticated:
            headers['Authorization'] = f'Bearer {self.token}'

        if body is None:
            response = requests.request(method, self.main_url + path, headers=headers)
        else:
            response = requests.request(method, self.main_url + path, headers=headers, json=body)

        # This should never happen
        if response.status_code == 405:
            raise requests.HTTPError

        if response.status_code == 404:
            raise requests.HTTPError('Resource not found', response=response)

        if response.status_code == 400:
            raise requests.HTTPError('Error 400: {}'.format(response.json()['hydra:description']))

        if response.status_code >= 500:
            raise requests.HTTPError('Well, I guess the server died ¯\\_(ツ)_/¯', response=response)

        try:
            return clean_ldjson(response.json())
        except json.JSONDecodeError:
            return None

    def get(self, path, body=None):
        return self.request('GET', path, body)

    def post(self, path, body=None):
        return self.request('POST', path, body)

    def put(self, path, body=None):
        return self.request('PUT', path, body)

    def patch(self, path, body=None):
        return self.request('PATCH', path, body, content_type='application/merge-patch+json')

    def delete(self, path, body=None):
        return self.request('DELETE', path, body)

    def authenticate(self, username, password):
        data = {
            'username': username,
            'password': password
        }
        response = self.post('/authentication_token', data)

        if ('code' in response) and (response['code'] == 401):
            return False

        self.token = response['token']
        return True

    @property
    def authenticated(self):
        return self.token is not None

    @property
    def authenticated_user_id(self):
        if not self.authenticated:
            return None

        token_data = json.loads(base64.b64decode(self.token.split('.')[1]))
        user_path = token_data['user']

        return int(user_path.split('/')[-1])
