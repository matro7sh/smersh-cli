import argparse
from rich.console import Console
from rich.layout import Layout
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.text import Text

from api import SmershAPI
from models import User, Mission, Host


def parse_args():
    parser = argparse.ArgumentParser(description='A command-line client for the SMERSH collaborative pentest tool')

    parser.add_argument('url', type=str, help='The URL of the SMERSH backend server')

    return parser.parse_args()


def get_missions_table(missions):
    table = Table(title='Current missions', box=box.ASCII)

    table.add_column('ID', justify='center', style='cyan')
    table.add_column('Name', justify='center', style='magenta')
    table.add_column('Start date', justify='center', style='green')
    table.add_column('End date', justify='center', style='red')

    for mission in missions:
        end_date = mission.end_date

        if end_date is None:
            end_date = 'Undefined'

        table.add_row(str(mission.id), mission.name, mission.start_date, end_date)

    return table


def get_hosts_table(hosts):
    console.print(hosts);
    table = Table(title='All Hosts', box=box.ASCII)
    table.add_column('ID', justify='center', style='cyan')
    table.add_column('Name', justify='center', style='magenta')
    table.add_column('Technology', justify='center', style='yellow')
    for host in hosts:
        table.add_row(str(host.id), host.name, host.technology)
    return table


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

    hosts = {}
    missions = {}

    for mission in user.missions:
        mission_full = Mission.get(api, mission.id)
        missions[mission_full.id] = mission_full

    missions_table = get_missions_table(missions.values())
    console.print(missions_table)
    hosts_table = get_hosts_table(hosts)
    console.print(hosts_table)

    selected_mission_id = None

    while selected_mission_id not in missions:
        try:
            selected_mission_id = int(console.input('Please enter the ID of a mission to display: '))
        except ValueError:
            selected_mission_id = None

        if selected_mission_id not in missions:
            console.print(':cross_mark: This ID does not refer to an existing mission')

    selected_mission = missions[selected_mission_id]
    layout = Layout()

    layout.split(
        Layout(name='header', size=1),
        Layout(name='main')
    )

    layout['header'].update(Text(selected_mission.name, justify='center'))

    console.print(layout)

