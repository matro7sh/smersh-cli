import argparse
import sys

import requests
from rich.console import Console
from rich.layout import Layout
from rich.pretty import Pretty
from rich.table import Table
from rich.panel import Panel
from rich import box, pretty
from rich.text import Text
from cmd2 import Cmd, Cmd2ArgumentParser, with_argparser

from api import SmershAPI
from models import User, Mission, Host, Client, Vuln, Impact, MissionType, PositivePoint, NegativePoint


TABLE_BOX_TYPE = box.ROUNDED


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
        choices=['mission', 'user', 'client', 'vuln', 'positive_point', 'negative_point'],
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


class App(Cmd):

    def __init__(self, api):
        super().__init__(
            use_ipython=has_ipython(),
            allow_cli_args=False)

        self.api = api
        self.user = User.get(api, api.authenticated_user_id)

        self.prompt = '\x1b[1;31mSMERSH >>\x1b[0m '
        self.continuation_prompt = '\x1b[1;31m>>\x1b[0m '
        self.self_in_py = True

    @with_argparser(get_show_parser())
    def do_show(self, namespace):
        """Print information about one or more object"""

        model = self.get_model_from_name(namespace.model)
        ids = namespace.ids

        if namespace.raw:
            print_function = self.print_object
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

    def get_model_from_name(self, model_name):
        return {
            'mission': Mission,
            'user': User,
            'client': Client,
            'vuln': Vuln,
            'positive_point': PositivePoint,
            'negative_point': NegativePoint
        }[model_name]

    def get_print_function_from_model_name(self, model_name):
        return {
            'mission': self.print_missions_table,
            'user': self.print_users_table,
            'client': self.print_clients_table,
            'vuln': self.print_vulns_table,
            'positive_point': self.print_points_table,
            'negative_point': self.print_points_table
        }[model_name]

    @staticmethod
    def print_object(object):
        if type(object) == list:
            console.print([e.to_dict() for e in object])
        else:
            console.print(object.to_dict())

    @staticmethod
    def print_missions_table(missions):
        table = Table(box=TABLE_BOX_TYPE)

        table.add_column('ID', justify='center', style='cyan')
        table.add_column('Name', justify='center', style='magenta')
        table.add_column('Start date', justify='center', style='green')
        table.add_column('End date', justify='center', style='red')

        for mission in missions:
            table.add_row(mission.id, mission.name, mission.start_date, mission.end_date)

        console.print(table)

    @staticmethod
    def print_users_table(users):
        table = Table(box=TABLE_BOX_TYPE)

        table.add_column('ID', justify='center')
        table.add_column('Name', justify='center')
        table.add_column('Enabled', justify='center')
        table.add_column('Assigned missions', justify='center')

        for user in users:
            enabled = '[green]Yes' if user.enabled else '[red]No'

            if len(user.missions) == 0:
                missions = 'None'
            else:
                missions = ', '.join([mission.id for mission in user.missions])

            table.add_row(user.id, user.username, enabled, missions)

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
