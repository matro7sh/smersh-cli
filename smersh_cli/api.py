import base64
import json
import requests
from enum import IntFlag
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from .utils.json import clean_ldjson

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class APIRoles(IntFlag):

    ROLE_CLIENT_GET_LIST            = 1 << 0
    ROLE_CLIENT_POST                = 1 << 1
    ROLE_CLIENT_GET_ITEM            = 1 << 2
    ROLE_CLIENT_PUT                 = 1 << 3
    ROLE_CLIENT_PATCH               = 1 << 4
    ROLE_CLIENT_DELETE              = 1 << 5

    ROLE_HOST_GET_LIST              = 1 << 6
    ROLE_HOST_POST                  = 1 << 7
    ROLE_HOST_GET_ITEM              = 1 << 8
    ROLE_HOST_PUT                   = 1 << 9
    ROLE_HOST_PATCH                 = 1 << 10
    ROLE_HOST_DELETE                = 1 << 11

    ROLE_HOST_VULN_GET_LIST         = 1 << 12
    ROLE_HOST_VULN_POST             = 1 << 13
    ROLE_HOST_VULN_GET_ITEM         = 1 << 14
    ROLE_HOST_VULN_PUT              = 1 << 15
    ROLE_HOST_VULN_PATCH            = 1 << 16
    ROLE_HOST_VULN_DELETE           = 1 << 17

    ROLE_IMPACT_GET_LIST            = 1 << 18
    ROLE_IMPACT_POST                = 1 << 19
    ROLE_IMPACT_GET_ITEM            = 1 << 20
    ROLE_IMPACT_PUT                 = 1 << 21
    ROLE_IMPACT_PATCH               = 1 << 22
    ROLE_IMPACT_DELETE              = 1 << 23

    ROLE_MISSION_GET_LIST           = 1 << 24
    ROLE_MISSION_POST               = 1 << 25
    ROLE_MISSION_GET_ITEM           = 1 << 26
    ROLE_MISSION_PUT                = 1 << 27
    ROLE_MISSION_PATCH              = 1 << 28
    ROLE_MISSION_DELETE             = 1 << 29

    ROLE_MISSION_TYPE_GET_LIST      = 1 << 30
    ROLE_MISSION_TYPE_POST          = 1 << 31
    ROLE_MISSION_TYPE_GET_ITEM      = 1 << 32
    ROLE_MISSION_TYPE_PUT           = 1 << 33
    ROLE_MISSION_TYPE_PATCH         = 1 << 34
    ROLE_MISSION_TYPE_DELETE        = 1 << 35

    ROLE_NEGATIVE_POINT_GET_LIST    = 1 << 36
    ROLE_NEGATIVE_POINT_POST        = 1 << 37
    ROLE_NEGATIVE_POINT_GET_ITEM    = 1 << 38
    ROLE_NEGATIVE_POINT_PUT         = 1 << 39
    ROLE_NEGATIVE_POINT_PATCH       = 1 << 40
    ROLE_NEGATIVE_POINT_DELETE      = 1 << 41

    ROLE_POSITIVE_POINT_GET_LIST    = 1 << 42
    ROLE_POSITIVE_POINT_POST        = 1 << 43
    ROLE_POSITIVE_POINT_GET_ITEM    = 1 << 44
    ROLE_POSITIVE_POINT_PUT         = 1 << 45
    ROLE_POSITIVE_POINT_PATCH       = 1 << 46
    ROLE_POSITIVE_POINT_DELETE      = 1 << 47

    ROLE_STEP_GET_LIST              = 1 << 48
    ROLE_STEP_POST                  = 1 << 49
    ROLE_STEP_GET_ITEM              = 1 << 50
    ROLE_STEP_PUT                   = 1 << 51
    ROLE_STEP_PATCH                 = 1 << 52
    ROLE_STEP_DELETE                = 1 << 53

    ROLE_USER_GET_LIST              = 1 << 54
    ROLE_USER_POST                  = 1 << 55
    ROLE_USER_GET_ITEM              = 1 << 56
    ROLE_USER_PUT                   = 1 << 57
    ROLE_USER_PATCH                 = 1 << 58
    ROLE_USER_DELETE                = 1 << 59

    ROLE_VULN_GET_LIST              = 1 << 60
    ROLE_VULN_POST                  = 1 << 61
    ROLE_VULN_GET_ITEM              = 1 << 62
    ROLE_VULN_PUT                   = 1 << 63
    ROLE_VULN_PATCH                 = 1 << 64
    ROLE_VULN_DELETE                = 1 << 65

    ROLE_VULN_TYPE_GET_LIST         = 1 << 66
    ROLE_VULN_TYPE_POST             = 1 << 67
    ROLE_VULN_TYPE_GET_ITEM         = 1 << 68
    ROLE_VULN_TYPE_PUT              = 1 << 69
    ROLE_VULN_TYPE_PATCH            = 1 << 70
    ROLE_VULN_TYPE_DELETE           = 1 << 71

    ROLE_HOST_UPLOAD                = 1 << 72

    # This one is used but I'm not sure about its usefulness
    ROLE_USER                       = 1 << 73

    ROLE_CLIENT_MANAGE              = ROLE_CLIENT_GET_LIST | ROLE_CLIENT_POST | ROLE_CLIENT_PUT | ROLE_CLIENT_PATCH | \
                                      ROLE_CLIENT_DELETE | ROLE_CLIENT_GET_ITEM

    ROLE_HOST_MANAGE                = ROLE_HOST_GET_LIST | ROLE_HOST_POST | ROLE_HOST_PUT | ROLE_HOST_PATCH | \
                                      ROLE_HOST_DELETE | ROLE_HOST_GET_ITEM | ROLE_HOST_UPLOAD

    ROLE_HOST_VULN_MANAGE           = ROLE_HOST_VULN_GET_LIST | ROLE_HOST_VULN_POST | ROLE_HOST_VULN_PUT | \
                                      ROLE_HOST_VULN_PATCH | ROLE_HOST_VULN_DELETE | ROLE_HOST_VULN_GET_ITEM

    ROLE_IMPACT_MANAGE              = ROLE_IMPACT_GET_LIST | ROLE_IMPACT_POST | ROLE_IMPACT_PUT | ROLE_IMPACT_PATCH | \
                                      ROLE_IMPACT_DELETE | ROLE_IMPACT_GET_ITEM

    ROLE_MISSION_MANAGE             = ROLE_MISSION_GET_LIST | ROLE_MISSION_POST | ROLE_MISSION_PUT | ROLE_MISSION_PATCH | \
                                      ROLE_MISSION_DELETE | ROLE_MISSION_GET_ITEM

    ROLE_MISSION_TYPE_MANAGE        = ROLE_MISSION_TYPE_GET_LIST | ROLE_MISSION_TYPE_POST | ROLE_MISSION_TYPE_PUT | \
                                      ROLE_MISSION_TYPE_PATCH | ROLE_MISSION_TYPE_DELETE | ROLE_MISSION_TYPE_GET_ITEM

    ROLE_NEGATIVE_POINT_MANAGE      = ROLE_NEGATIVE_POINT_GET_LIST | ROLE_NEGATIVE_POINT_POST | ROLE_NEGATIVE_POINT_PUT | \
                                      ROLE_NEGATIVE_POINT_PATCH | ROLE_NEGATIVE_POINT_DELETE | \
                                      ROLE_NEGATIVE_POINT_GET_ITEM

    ROLE_POSITIVE_POINT_MANAGE      = ROLE_POSITIVE_POINT_GET_LIST | ROLE_POSITIVE_POINT_POST | ROLE_POSITIVE_POINT_PUT | \
                                      ROLE_POSITIVE_POINT_PATCH | ROLE_POSITIVE_POINT_DELETE | \
                                      ROLE_POSITIVE_POINT_GET_ITEM

    ROLE_STEP_MANAGE                = ROLE_STEP_GET_LIST | ROLE_STEP_POST | ROLE_STEP_PUT | ROLE_STEP_PATCH | \
                                      ROLE_STEP_DELETE | ROLE_STEP_GET_ITEM

    ROLE_USER_MANAGE                = ROLE_USER_GET_LIST | ROLE_USER_POST | ROLE_USER_PUT | ROLE_USER_PATCH | \
                                      ROLE_USER_DELETE | ROLE_USER_GET_ITEM

    ROLE_VULN_MANAGE                = ROLE_VULN_GET_LIST | ROLE_VULN_POST | ROLE_VULN_PUT | ROLE_VULN_PATCH | \
                                      ROLE_VULN_DELETE | ROLE_VULN_GET_ITEM

    ROLE_VULN_TYPE_MANAGE           = ROLE_VULN_TYPE_GET_LIST | ROLE_VULN_TYPE_POST | ROLE_VULN_TYPE_PUT | \
                                      ROLE_VULN_TYPE_PATCH | ROLE_VULN_TYPE_DELETE | ROLE_VULN_TYPE_GET_ITEM

    ROLE_CLIENT                     = ROLE_MISSION_GET_ITEM

    ROLE_MANAGER                    = ROLE_CLIENT | ROLE_CLIENT_MANAGE | ROLE_MISSION_MANAGE | ROLE_HOST_UPLOAD | \
                                      ROLE_USER_MANAGE

    ROLE_PENTESTER                  = ROLE_CLIENT | ROLE_MISSION_GET_ITEM | ROLE_MISSION_GET_LIST | ROLE_MISSION_PATCH | \
                                      ROLE_MISSION_PUT | ROLE_STEP_MANAGE | ROLE_USER_GET_ITEM | ROLE_USER_GET_LIST | \
                                      ROLE_USER_PATCH | ROLE_USER_PUT | ROLE_IMPACT_GET_LIST | ROLE_VULN_MANAGE | \
                                      ROLE_VULN_TYPE_MANAGE | ROLE_HOST_VULN_MANAGE | ROLE_HOST_UPLOAD

    ROLE_ADMIN                      = ROLE_PENTESTER | ROLE_MANAGER | ROLE_CLIENT | ROLE_CLIENT_MANAGE | \
                                      ROLE_HOST_MANAGE | ROLE_IMPACT_MANAGE | ROLE_MISSION_MANAGE | \
                                      ROLE_MISSION_TYPE_MANAGE | ROLE_NEGATIVE_POINT_MANAGE | \
                                      ROLE_POSITIVE_POINT_MANAGE | ROLE_VULN_MANAGE | ROLE_VULN_TYPE_MANAGE


class SmershAPI:

    DEFAULT_USER_AGENT = 'SmershPythonClient'

    def __init__(self, main_url, user_agent=DEFAULT_USER_AGENT, certificate=None):
        if main_url.endswith('/'):
            main_url = main_url[:-1]

        self.main_url = main_url
        self.user_agent = user_agent
        self.certificate = certificate
        self.token = None

    def request(self, method, path, body=None, content_type='application/ld+json', files=None):
        if path[0] != '/':
            path = '/' + path

        headers = {
            'Accept': 'application/ld+json',
            'User-Agent': self.user_agent
        }

        if files is None:
            headers['Content-Type'] = content_type

        if self.authenticated:
            headers['Authorization'] = f'Bearer {self.token}'

        if body is None:
            response = requests.request(method, self.main_url + path, verify=self.certificate, headers=headers,
                                        files=files)
        elif files is None:
            response = requests.request(method, self.main_url + path, verify=self.certificate, headers=headers,
                                        json=body)
        else:
            response = requests.request(method, self.main_url + path, verify=self.certificate, headers=headers,
                                        data=body, files=files)

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

    def upload_hosts(self, file_path, mission):
        with open(file_path, 'rb') as inf:
            hosts_data = inf.read()
            data = {'missionName': mission.name}

            return self.request('POST', '/api/upload/host', body=data, files=dict(filename=hosts_data))

    @property
    def authenticated(self):
        return self.token is not None

    @property
    def authenticated_user_id(self):
        if not self.authenticated:
            return None

        # HACK: Ugly fix because of a badly encoded token
        token_data_b64 = self.token.split('.')[1]
        missing_padding_count = (4 - (len(token_data_b64) % 4))

        if missing_padding_count == 3:
            token_data_b64 += 'A=='
        else:
            token_data_b64 += '=' * missing_padding_count

        token_data = json.loads(base64.b64decode(token_data_b64))
        user_path = token_data['user']

        return int(user_path.split('/')[-1])
