from argparse import ArgumentParser
from sys import platform
from time import time
from process.GameHandler import GameHandler


if __name__ == '__main__':
    parser = ArgumentParser(description='args')
    parser.add_argument('-p1', default='Clients/main.py', type=str,
                        help='First player path')
    parser.add_argument('-p2', default='Clients/main.py', type=str,
                        help='Second player path')
    parser.add_argument('-n1', default='Team 1', type=str,
                        help='First player name')
    parser.add_argument('-n2', default='Team 2', type=str,
                        help='Second player name')
    parser.add_argument('--setting', default='src/settings.json', type=str,
                        help='Setting JSON file path')
    parser.add_argument('--log', default=f'/logs/{int(time() * 1000)}', type=str,
                        help='Path to store logs')
    parser.add_argument('--map', default='maps/map1.json', type=str,
                        help='Map for running the game')
    parser.add_argument('--cg', action='store_true',
                        help='Enable cgroups (only available in linux)')

    args = parser.parse_args()

    # Disable cgroup for windows and mac
    args.cg = args.cg and not 'win' in platform.lower()

    game = GameHandler(args)
    game.run()
