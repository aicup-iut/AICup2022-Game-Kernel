from argparse import ArgumentParser
from sys import platform
from time import time
from pathlib import Path
from process.GameHandler import GameHandler


if __name__ == '__main__':
    parser = ArgumentParser(description='args')
    parser.add_argument('-p1', default=Path(r'Clients/Python/main.py'), type=Path,
                        help='First player path')
    parser.add_argument('-p2', default=Path(r'Clients/Python/main.py'), type=Path,
                        help='Second player path')
    parser.add_argument('-n1', default='Team 1', type=str,
                        help='First player name')
    parser.add_argument('-n2', default='Team 2', type=str,
                        help='Second player name')
    parser.add_argument('--setting', default=Path(r'src/settings.json'), type=Path,
                        help='Setting JSON file path')
    parser.add_argument('--log', default=Path(r'logs/{}'.format(int(time() * 1000))), type=Path,
                        help='Path to store logs')
    parser.add_argument('--map', default=Path(r'maps/map1.json'), type=Path,
                        help='Map for running the game')
    parser.add_argument('--cg', action='store_true',
                        help='Enable cgroups (only available in linux)')
    parser.add_argument('-v', '--visualizer', default=None, type=Path,
                        help='Path to visualizer')

    args = parser.parse_args()

    # Disable cgroup for windows and mac
    args.cg = args.cg and not 'win' in platform.lower()

    game = GameHandler(args)
    game.run()
