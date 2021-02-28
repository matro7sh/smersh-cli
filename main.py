import argparse

import requests
from rich.console import Console
from rich.layout import Layout
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.text import Text
from cmd2 import Cmd, with_argparser

from api import SmershAPI
from models import User, Mission, Host


def get_show_parser():
    parser = argparse.ArgumentParser()

    return parser


class App(Cmd):

    def __init__(self, api):
        super().__init__()
        self.api = api
        self.user = User.get(api, api.authenticated_user_id)

        self.remove_useless_buitlins()

    def remove_useless_buitlins(self):
        """Remove all useless builtins command from cmd2"""

        delattr(self, 'do_edit')
        # delattr(self, 'do_ipy')
        # delattr(self, 'do_py')
        delattr(self, 'do_run_pyscript')
        delattr(self, 'do_run_script')
        delattr(self, 'do__relative_run_script')
        delattr(self, 'do_shell')

    @with_argparser(get_show_parser())
    def do_show(self):
        ...


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

    while not api.authenticated:
        username = console.input('Enter your username: ')
        password = console.input('Enter your password (will not be echoed): ', password=True)

        try:
            if api.authenticate(username, password):
                console.print(':heavy_check_mark: Successfully logged in')
            else:
                console.print(':cross_mark: Unable to log you in. Your credentials seem invalid')
        except requests.exceptions.ConnectionError:
            console.print("[red]Oh no. I can't connect to the specified URL. Please check there is no typo and that "
                          "the host accepts connections. Then try again.")
        except requests.exceptions.HTTPError as e:
            console.print(f'[red]HTTP error {e.response.status_code}: {e}')

    app = App(api)
    app.cmdloop()
