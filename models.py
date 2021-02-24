from dataclasses import dataclass
from dataclasses_json import LetterCase, dataclass_json
from typing import List, Optional


class Model:

    @staticmethod
    def get(api, id):
        raise NotImplementedError

    @staticmethod
    def getAll(api):
        raise NotImplementedError


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Mission(Model):

    id: int
    name: str
    start_date: Optional[str] = None  # TODO: Automatic parsing of date
    path_to_codi: Optional[str] = None
    contact: Optional[str] = None
    end_date: Optional[str] = None  # TODO: Automatic parsing of date
    users: Optional[List[str]] = None
    hosts: Optional[List[str]] = None
    nmap: Optional[bool] = False
    nessus: Optional[bool] = False
    nmap_filer: Optional[bool] = False
    nessus_filer: Optional[bool] = False
    mission_type: Optional[str] = None
    credentials: Optional[str] = None
    clients: Optional[List[str]] = None
    steps: Optional[List[str]] = None

    @staticmethod
    def get(api, id):
        return Mission.from_dict(api.get(f'/api/missions/{id}'))


@dataclass_json
@dataclass
class User(Model):

    id: int
    username: str
    roles: List[str]
    enabled: bool
    missions: List[Mission]

    @staticmethod
    def get(api, id):
        return User.from_dict(api.get(f'/api/users/{id}'))


@dataclass_json
@dataclass
class Host(Model):

    id: int
    name: str
    technology: str

    @staticmethod
    def getAll(api):
        hosts = []
        response = api.get('/api/hosts')

        for host in response:
            hosts.append(Host.from_dict(host))

        return hosts



@dataclass_json
@dataclass
class Impact(Model):

    id: int
    name: str

    @staticmethod
    def get(api, id):
        return Impact.from_dict(api.get(f'/api/impacts/{id}'))


@dataclass_json
@dataclass
class MissionType(Model):

    id: int
    name: str

    @staticmethod
    def get(api, id):
        return MissionType.from_dict(api.get(f'/api/mission_types/{id}'))