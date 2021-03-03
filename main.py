import argparse
import sys

import requests
from cmd2 import Cmd, Cmd2ArgumentParser, with_argparser, with_argument_list
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from api import SmershAPI
from models import User, Mission, Client, Vuln, PositivePoint, NegativePoint, Model

TABLE_BOX_TYPE = box.ROUNDED
COMMAND_PROMPT = '\x1b[1;31mSMERSH {}>>\x1b[0m '


def has_ipython():
    try:
        import IPython
        return True
    except:
        return False


def get_show_parser():
    parser = Cmd2ArgumentParser()

    parser.add_argument(
        'model',
        nargs='?',
        choices=['mission', 'user', 'client', 'vuln', 'positive_point', 'negative_point'],
        default=None,
        help='The object type to query information about.'
    )

    parser.add_argument(
        'ids',
        nargs='*',
        type=int,
        help='A list of identifiers (separated by spaces) of specific objects to print information about. If this '
             'list is empty, the program will print every object.'
    )

    parser.add_argument(
        '-r',
        '--raw',
        action='store_true',
        help='Whether to print the data in raw (without formatting) or in a table. Default is to print in a table.'
    )

    return parser


def get_use_parser():
    parser = Cmd2ArgumentParser()

    parser.add_argument(
        'model',
        choices=['mission', 'user', 'client', 'vuln', 'positive_point', 'negative_point'],
        help='The object type to query information about.'
    )

    parser.add_argument(
        'id',
        nargs='?',
        type=int,
        default=None,
        help=''
    )

    return parser


def get_assign_parser(model):
    def object_id_checker(o):
        i = int(o)

        if i < 0:
            raise argparse.ArgumentTypeError('The object ID must be positive')

        return o

    def bool_checker(v):
        if isinstance(v, bool):
            return v
        if v.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')

    def add_str_subparser(_subparsers, field_name):
        str_subparser = _subparsers.add_parser(field_name)
        str_subparser.add_argument('value', type=str)

    def add_list_subparser(_subparsers, field_name, item_type=None, choices=None):
        assert(not ((item_type is None) and (choices is None)))

        list_subparser = _subparsers.add_parser(field_name)
        list_subparser.add_argument('action', choices=['add', 'remove'])

        if choices is None:
            list_subparser.add_argument('value', nargs='+', type=item_type)
        else:
            list_subparser.add_argument('value', nargs='+', choices=choices)

    def add_bool_subparser(_subparsers, field_name):
        bool_subparser = _subparsers.add_parser(field_name)
        bool_subparser.add_argument('value', type=bool_checker)

    def add_object_subparser(_subparsers, field_name):
        object_subparser = _subparsers.add_parser(field_name)
        object_subparser.add_argument('value', type=object_id_checker)

    parser = Cmd2ArgumentParser()
    subparsers = parser.add_subparsers(dest='field')

    if isinstance(model, Mission):
        add_str_subparser(subparsers, 'name')
        add_str_subparser(subparsers, 'start_date')  # TODO: Add a date subparser
        add_str_subparser(subparsers, 'path_to_codi')
        add_str_subparser(subparsers, 'end_date')  # TODO: Add a date subparser
        add_list_subparser(subparsers, 'users', item_type=object_id_checker)
        add_bool_subparser(subparsers, 'nmap')
        add_bool_subparser(subparsers, 'nessus')
        add_bool_subparser(subparsers, 'nmap_filer')
        add_bool_subparser(subparsers, 'nessus_filer')
        add_object_subparser(subparsers, 'mission_type')
        add_str_subparser(subparsers, 'credentials')
        add_list_subparser(subparsers, 'clients', item_type=object_id_checker)
        add_list_subparser(subparsers, 'steps', item_type=object_id_checker)

    elif isinstance(model, User):
        add_str_subparser(subparsers, 'username')
        add_str_subparser(subparsers, 'password')
        add_list_subparser(subparsers, 'roles', choices=['ROLE_USER', 'ROLE_ADMIN'])
        add_bool_subparser(subparsers, 'enabled')
        add_list_subparser(subparsers, 'missions', item_type=object_id_checker)

    elif isinstance(model, Client):
        add_str_subparser(subparsers, 'name')
        add_str_subparser(subparsers, 'phone')
        add_str_subparser(subparsers, 'first_name')
        add_str_subparser(subparsers, 'last_name')
        add_str_subparser(subparsers, 'mail')
        add_list_subparser(subparsers, 'missions', item_type=object_id_checker)

    elif isinstance(model, Vuln):
        add_str_subparser(subparsers, 'name')
        add_str_subparser(subparsers, 'description')
        add_str_subparser(subparsers, 'remediation')
        add_object_subparser(subparsers, 'vuln_type')
        add_object_subparser(subparsers, 'impact')
        add_list_subparser(subparsers, 'host_vulns', item_type=object_id_checker)

    elif isinstance(model, PositivePoint) or isinstance(model, NegativePoint):
        add_str_subparser(subparsers, 'name')
        add_str_subparser(subparsers, 'description')

    return parser


class App(Cmd):

    def __init__(self, api):
        super().__init__(
            use_ipython=has_ipython(),
            allow_cli_args=False)

        self.api = api

        self.continuation_prompt = '\x1b[1;31m>>\x1b[0m '
        self.self_in_py = True
        self.context = None

        self.update_prompt()

    @with_argparser(get_show_parser())
    def do_show(self, namespace):
        """Print information about one or more object"""

        if namespace.model is None:
            if self.context is None:
                console.print('[red]There is no context')
            else:
                if namespace.raw:
                    console.print(self.context)
                else:
                    model_name = self.context.__class__.__name__.lower()
                    print_function = self.get_print_function_from_model_name(model_name)

                    print_function([self.context])

            return

        model = self.get_model_from_name(namespace.model)
        ids = namespace.ids

        if namespace.raw:
            print_function = console.print
        else:
            print_function = self.get_print_function_from_model_name(namespace.model)

        if len(ids) == 0:
            print_function(model.all(self.api))
        else:
            objects = []

            for id in ids:
                try:
                    objects.append(model.get(self.api, id))
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 404:
                        console.print(f'[yellow]Unable to find an object with id: {id}')
                    else:
                        console.print(f'[red]An HTTP error occurred: {e}')

            if len(objects) > 0:
                print_function(objects)
            else:
                console.print('Your request returned no object :(')

    @with_argparser(get_use_parser())
    def do_use(self, namespace):
        model = self.get_model_from_name(namespace.model)
        id = namespace.id

        if id is None:
            self.context = model(id=None)
        else:
            try:
                self.context = model.get(self.api, id)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    console.print(f'[yellow]Unable to find an object with id: {id}')
                else:
                    console.print(f'[red]An HTTP error occurred: {e}')

        self.update_prompt()

    @with_argument_list
    def do_assign(self, args):
        if self.context is None:
            console.print('[red]You must enter into a context before setting a field')
            return

        try:
            args = get_assign_parser(self.context).parse_known_args(args)[0]

            if 'action' in args:
                l = getattr(self.context, args.field)

                if args.action == 'add':
                    for e in args.value:
                        if e in l:
                            console.print(f'[yellow]The item "{e}" was already added into the field named "{args.field}"')
                        else:
                            l.append(e)
                else:
                    for e in l:
                        _id = e

                        if issubclass(e.__class__, Model):
                            _id = e.id

                        if _id in args.value:
                            l.remove(e)

                setattr(self.context, args.field, l)
            else:
                setattr(self.context, args.field, args.value)
        except SystemExit:
            # Just ignore the SystemExit exception. The error message is printed by argparse
            pass

    def do_exit(self, _):
        if self.context is None:
            console.print('[red]You have no context to exit')
        else:
            self.context = None
            self.update_prompt()

    def do_save(self, _):
        if self.context is None:
            console.print('[red]You need to be in a context to save something')
        else:
            try:
                self.context = self.context.save(self.api)
                self.update_prompt()

                console.print('[green]The object was saved successfully')

            except requests.exceptions.HTTPError as e:
                console.print(f'[red]Unable to save the object. {e}')

    def do_delete(self, _):
        if self.context is None:
            console.print('[red]You must be in a context to delete something')
        elif self.context.id is None:
            console.print('[red]You can\'t delete a NEW object')
        else:
            if self.context.delete(self.api):
                console.print('[green]The object was deleted successfully')

                self.context = None
                self.update_prompt()
            else:
                console.print('[red]An error occurred. Unable to delete the object')

    def update_prompt(self):
        if self.context is None:
            self.prompt = COMMAND_PROMPT.format('')
        else:
            model_name = self.context.__class__.__name__
            id = '\x1b[1;39mNEW\x1b[0m' if (self.context.id is None) else self.context.id

            self.prompt = COMMAND_PROMPT.format(f'-\x1b[0m {model_name}[{id}]\x1b[1;31m ')

    def get_model_from_name(self, model_name):
        return {
            'mission': Mission,
            'user': User,
            'client': Client,
            'vuln': Vuln,
            'positivepoint': PositivePoint,
            'negativepoint': NegativePoint
        }[model_name.replace('_', '')]

    def get_print_function_from_model_name(self, model_name):
        return {
            'mission': self.print_missions_table,
            'user': self.print_users_table,
            'client': self.print_clients_table,
            'vuln': self.print_vulns_table,
            'positivepoint': self.print_points_table,
            'negativepoint': self.print_points_table
        }[model_name.replace('_', '')]

    @staticmethod
    def get_printable_user_role(user_role):
        return {
            'ROLE_USER': 'User',
            'ROLE_ADMIN': 'Administrator'
        }[user_role]

    @staticmethod
    def get_printable_flag(flag, yes_text='Yes', no_text='No'):
        return f'[green]{yes_text}' if flag else f'[red]{no_text}'

    @staticmethod
    def print_missions_table(missions):
        table = Table(box=TABLE_BOX_TYPE)

        table.add_column('ID', justify='center', style='cyan')
        table.add_column('Name', justify='center', style='magenta')
        table.add_column('Start date', justify='center', style='green')
        table.add_column('End date', justify='center', style='red')
        table.add_column('Nmap', justify='center')
        table.add_column('Nessus', justify='center')

        for mission in missions:
            nmap = App.get_printable_flag(mission.nmap, 'Done', 'To do')
            nessus = App.get_printable_flag(mission.nessus, 'Done', 'To do')

            table.add_row(mission.id, mission.name, mission.start_date, mission.end_date, nmap, nessus)

        console.print(table)

    @staticmethod
    def print_users_table(users):
        table = Table(box=TABLE_BOX_TYPE)

        table.add_column('ID', justify='center')
        table.add_column('Name', justify='center')
        table.add_column('Enabled', justify='center')
        table.add_column('Roles', justify='center')
        table.add_column('Assigned missions', justify='center')

        for user in users:
            enabled = '[green]Yes' if user.enabled else '[red]No'
            roles = ', '.join([App.get_printable_user_role(role) for role in user.roles])

            if len(user.missions) == 0:
                missions = 'None'
            else:
                missions = ', '.join([mission.id for mission in user.missions])

            table.add_row(user.id, user.username, enabled, roles, missions)

        console.print(table)

    @staticmethod
    def print_clients_table(clients):
        table = Table(box=TABLE_BOX_TYPE)

        table.add_column('ID', justify='center')
        table.add_column('Name', justify='center')
        table.add_column('Contact name', justify='center')
        table.add_column('Phone number', justify='center')
        table.add_column('Email address', justify='center')

        for client in clients:
            contact_name = f'{client.first_name} {client.last_name}'

            table.add_row(client.id, client.name, contact_name, client.phone, client.mail)

        console.print(table)

    @staticmethod
    def print_vulns_table(vulns):
        table = Table(box=TABLE_BOX_TYPE, show_lines=True)

        table.add_column('ID', justify='center')
        table.add_column('Name', justify='center')
        table.add_column('Description', justify='center')
        table.add_column('Remediation', justify='center')

        for vuln in vulns:
            table.add_row(vuln.id, vuln.name, vuln.description, vuln.remediation)

        console.print(table)

    @staticmethod
    def print_points_table(points):
        table = Table(box=TABLE_BOX_TYPE, show_lines=True)

        table.add_column('ID', justify='center')
        table.add_column('Name', justify='center')
        table.add_column('Description', justify='center')

        for point in points:
            table.add_row(point.id, point.name, point.description)

        console.print(table)


def parse_args():
    parser = argparse.ArgumentParser(description='A command-line client for the SMERSH collaborative pentest tool')

    parser.add_argument('url', type=str, help='The URL of the SMERSH backend server')

    return parser.parse_args()


def print_hello():
    # TODO: Replace this by a beautiful ASCII art picture ?
    console.print(Panel(Text('Welcome to the SMERSH Python client', justify='center')))


if __name__ == '__main__':
    args = parse_args()
    console = Console()
    api = SmershAPI(args.url)

    print_hello()

    try:
        while not api.authenticated:
            username = console.input('Enter your username: ')
            password = console.input('Enter your password (will not be echoed): ', password=True)

            try:
                if api.authenticate(username, password):
                    console.print('[green]:heavy_check_mark: Successfully logged in')
                else:
                    console.print('[red]:cross_mark: Unable to log you in. Your credentials seem invalid')
            except requests.exceptions.ConnectionError:
                console.print("[red]Oh no. I can't connect to the specified URL. Please check there is no typo and "
                              "that the host accepts connections. Then try again.")
            except requests.exceptions.HTTPError as e:
                console.print(f'[red]HTTP error {e.response.status_code}: {e}')
    except EOFError:
        # The \n is important because we need to not print inside the input caption
        console.print('\nBye')
        sys.exit(0)

    app = App(api)
    sys.exit(app.cmdloop())
