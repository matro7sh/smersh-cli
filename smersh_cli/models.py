import copy
from abc import ABC
from dataclasses import dataclass, fields, field
from typing import List, Optional, Union, get_type_hints

from dataclasses_json import dataclass_json
from pydantic.typing import NoneType
from requests import HTTPError

from .api import APIRoles
from .utils.json import wrap_id_dict, convert_dict_keys_case, clean_none_keys
from .utils.case import camel_case


# HACK: This is a ugly fix for old Python versions
import sys

if sys.version_info < (3, 8):
    def get_args(field):
        return field.__args__

    def get_origin(field):
        return field.__origin__
else:
    from typing import get_args, get_origin


def default_field(obj):
    return field(default_factory=lambda: copy.copy(obj))


def has_args(field):
    return hasattr(field, '__args__')


def get_innermost_field(field):
    while has_args(field):
        field = get_args(field)[0]

    return field


def is_list(field):
    while has_args(field):
        field = get_args(field)[0]

        if hasattr(field, '__origin__') and (get_origin(field) == list):
            return True

    return False


def is_model(field):
    return issubclass(get_innermost_field(field), Model)


def is_optional(field):
    if (get_origin(field) == Union) and has_args(field):
        args = get_args(field)
        return (len(args) == 2) and (args[1] is NoneType)

    return False


def lazy_model(_cls):

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
        data = convert_dict_keys_case(self._export(), camel_case)

        if new or (self.id is None):
            response = api.post(f'{Model.API_ROOT}/{self.ENDPOINT_NAME}', data)
            self.id = response['id'].split('/')[-1]
        else:
            api.patch(self.iri, clean_none_keys(data))

        return self

    def delete(self, api):
        try:
            api.delete(self.iri)
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

    def _export(self):
        data = {}

        for field_name, field_type in get_type_hints(self.__class__).items():
            field_value = getattr(self, field_name)

            data[field_name] = self._export_field(field_type, field_value)

        return data

    def _export_field(self, field_type, field_value):
        if is_list(field_type):
            l = []
            item_type = get_innermost_field(field_type)

            for e in field_value:
                l.append(self._export_field(item_type, e))

            return l
        elif is_model(field_type):
            if issubclass(field_value.__class__, Model):
                return field_value.iri
            else:
                # Here we handle the case were user has specified an ID of the model
                # So we create an instance of this model, assign this id to it and then get the iri
                # That's dirty but it works
                return get_innermost_field(field_type)(id=field_value).iri

        return field_value


@lazy_model
@dataclass_json
@dataclass
class Mission(Model):

    ENDPOINT_NAME = 'missions'

    name: Optional[str] = None
    start_date: Optional[str] = None
    path_to_codi: Optional[str] = None
    end_date: Optional[str] = None
    users: Optional[List['User']] = default_field([])
    hosts: Optional[List['Host']] = default_field([])
    nmap: Optional[bool] = False
    nessus: Optional[bool] = False
    nmap_filer: Optional[bool] = False
    nessus_filer: Optional[bool] = False
    # mission_type: Optional['MissionType'] = None
    credentials: Optional[str] = None
    clients: Optional[List['Client']] = default_field([])
    steps: Optional[List['Step']] = default_field([])


@lazy_model
@dataclass_json
@dataclass
class User(Model):

    ENDPOINT_NAME = 'users'

    username: Optional[str] = None
    roles: Optional[List[str]] = default_field([])
    enabled: Optional[bool] = False
    missions: Optional[List['Mission']] = default_field([])
    password: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    trigram: Optional[str] = None
    mail: Optional[str] = None


    @property
    def roles_flags(self):
        flags = 0

        for role in self.roles:
            flags |= APIRoles[role]

        return flags


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
    missions: Optional[List['Mission']] = default_field([])


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

    ENDPOINT_NAME = 'hosts'

    name: Optional[str] = None
    checked: Optional[bool] = False
    technology: Optional[str] = None
    host_vulns: Optional[List['HostVuln']] = default_field([])
    mission: Optional['Mission'] = None
    nmaps: Optional[List['Nmap']] = default_field([])


@lazy_model
@dataclass_json
@dataclass
class Impact(Model):

    ENDPOINT_NAME = 'impacts'

    name: Optional[str] = None
    vulns: Optional[List['Vuln']] = default_field([])


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
    host: Optional[List['Host']] = default_field([])


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
    vulns: Optional[List['Vuln']] = default_field([])


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
    # host_vulns: Optional[List['HostVuln']] = default_field([])
