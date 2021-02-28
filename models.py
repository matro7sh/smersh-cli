from abc import ABC
from dataclasses import dataclass, fields
from typing import List, Optional, Union, get_type_hints, get_args, get_origin

from dataclasses_json import dataclass_json
from pydantic.typing import NoneType
from requests import HTTPError

from utils.json import wrap_id_dict, convert_dict_keys_case
from utils.case import camel_case


def lazy_model(_cls):

    def has_args(field):
        return hasattr(field, '__args__')

    def get_innermost_field(field):
        while has_args(field):
            field = get_args(field)[0]

        return field

    def is_model(field):
        return issubclass(get_innermost_field(field), Model)

    def is_optional(field):
        if (get_origin(field) == Union) and has_args(field):
            args = get_args(field)
            return (len(args) == 2) and (args[1] is NoneType)

        return False

    def from_dict_lazy(cls, kvs, *, infer_missing=False):
        lazy_keys = set()

        for field_name, field_type in get_type_hints(cls).items():
            if (field_name in kvs) and is_model(field_type):
                value = kvs[field_name]
                value_type = type(value)

                if ((value_type == list) and (len(value) > 0) and (type(value[0]) == str)) or (value_type == str):
                    lazy_keys.add(field_name)

        wrapped = wrap_id_dict(kvs, lazy_keys)
        return cls.from_dict_not_lazy(wrapped, infer_missing=infer_missing)

    def wrap(cls):
        for field in fields(cls):
            if (field.name != 'id') and not is_optional(field.type):
                raise RuntimeError('All fields must be declared optional for a lazy model')

        cls.from_dict_not_lazy = cls.from_dict
        cls.from_dict = classmethod(from_dict_lazy)

        return cls

    if _cls is None:
        return wrap

    return wrap(_cls)


@dataclass_json
@dataclass
class Model(ABC):

    API_ROOT = '/api'
    ENDPOINT_NAME = None

    id: str
    
    @classmethod
    def get(cls, api, id):
        return cls.from_dict(api.get(f'{Model.API_ROOT}/{cls.ENDPOINT_NAME}/{id}'))

    @classmethod
    def all(cls, api):
        results = []

        for e in api.get(f'{Model.API_ROOT}/{cls.ENDPOINT_NAME}'):
            results.append(cls.from_dict(e))

        return results

    def save(self, api, new=False):
        data = convert_dict_keys_case(self.to_dict(), camel_case)

        if new or (self.id is None):
            response = api.post(f'{Model.API_ROOT}/{self.ENDPOINT_NAME}', data)
            self.id = response['id'].split('/')[-1]

            return self
        else:
            try:
                api.patch(f'{Model.API_ROOT}/{self.ENDPOINT_NAME}/{self.id}', data)
                return True
            except HTTPError:
                return False

    def delete(self, api):
        try:
            api.delete(f'{Model.API_ROOT}/{self.ENDPOINT_NAME}/{self.id}')
            return True
        except HTTPError:
            return False

    def fetch(self, api):
        return self.get(api, self.id.split('/')[-1])

    def is_lazy(self):
        # TODO: It could be better to test with a regex to be sure it's a link but for now it will be good enough
        return self.id[0] == '/'

    @property
    def iri(self):
        if self.is_lazy():
            return self.id

        return f'{Model.API_ROOT}/{self.ENDPOINT_NAME}/{self.id}'


@lazy_model
@dataclass_json
@dataclass
class Mission(Model):

    ENDPOINT_NAME = 'missions'

    name: Optional[str] = None
    start_date: Optional[str] = None
    path_to_codi: Optional[str] = None
    end_date: Optional[str] = None
    users: Optional[List['User']] = None
    hosts: Optional[List['Host']] = None
    nmap: Optional[bool] = False
    nessus: Optional[bool] = False
    nmap_filer: Optional[bool] = False
    nessus_filer: Optional[bool] = False
    mission_type: Optional['MissionType'] = None
    credentials: Optional[str] = None
    clients: Optional[List['Client']] = None
    steps: Optional[List['Step']] = None


@lazy_model
@dataclass_json
@dataclass
class User(Model):

    ENDPOINT_NAME = 'users'

    username: Optional[str] = None
    roles: Optional[List[str]] = None
    enabled: Optional[bool] = False
    missions: Optional[List['Mission']] = None
    password: Optional[str] = None


@lazy_model
@dataclass_json
@dataclass
class Client(Model):

    ENDPOINT_NAME = 'clients'

    name: Optional[str] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    mail: Optional[str] = None
    missions: Optional[List['Mission']] = None


@lazy_model
@dataclass_json
@dataclass
class HostVuln(Model):

    ENDPOINT_NAME = 'host_vulns'

    host: Optional['Host'] = None
    vuln: Optional['Vuln'] = None
    impact: Optional['Impact'] = None
    current_state: Optional[str] = None


@lazy_model
@dataclass_json
@dataclass
class Host(Model):

    ENDPOINT_NAME = 'host'

    name: Optional[str] = None
    checked: Optional[bool] = False
    technology: Optional[str] = None
    host_vulns: Optional[List['HostVuln']] = None
    mission: Optional['Mission'] = None
    nmaps: Optional[List['Nmap']] = None


@lazy_model
@dataclass_json
@dataclass
class Impact(Model):

    ENDPOINT_NAME = 'impacts'

    name: Optional[str] = None
    vulns: Optional[List['Vuln']] = None


@lazy_model
@dataclass_json
@dataclass
class MissionType(Model):

    ENDPOINT_NAME = 'mission_types'

    name: Optional[str] = None


@lazy_model
@dataclass_json
@dataclass
class Nmap(Model):

    ENDPOINT_NAME = 'nmaps'

    date: Optional[str] = None
    status: Optional[bool] = False
    port: Optional[str] = None
    host: Optional[List['Host']] = None


@lazy_model
@dataclass_json
@dataclass
class NegativePoint(Model):

    ENDPOINT_NAME = 'negative_points'

    name: Optional[str] = None
    description: Optional[str] = None


@lazy_model
@dataclass_json
@dataclass
class PositivePoint(Model):

    ENDPOINT_NAME = 'positive_points'

    name: Optional[str] = None
    description: Optional[str] = None


@lazy_model
@dataclass_json
@dataclass
class Step(Model):

    ENDPOINT_NAME = 'steps'

    description: Optional[str] = None
    find_at: Optional[str] = None
    created_at: Optional[str] = None
    mission: Optional['Mission'] = None


@lazy_model
@dataclass_json
@dataclass
class VulnType(Model):

    ENDPOINT_NAME = 'vuln_types'

    name: Optional[str] = None
    vulns: Optional[List['Vuln']] = None


@lazy_model
@dataclass_json
@dataclass
class Vuln(Model):

    ENDPOINT_NAME = 'vulns'

    name: Optional[str] = None
    description: Optional[str] = None
    remediation: Optional[str] = None
    vuln_type: Optional['VulnType'] = None
    impact: Optional['Impact'] = None
    host_vulns: Optional[List['HostVuln']] = None
