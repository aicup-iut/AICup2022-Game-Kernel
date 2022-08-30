from os import getpid, makedirs
from enum import Enum

DEBUG = 0


class Action(Enum):
    def __str__(self):
        return str(self.value)

    STAY = 0
    MOVE_DOWN = 1
    MOVE_UP = 2
    MOVE_RIGHT = 3
    MOVE_LEFT = 4
    UPGRADE_DEFENCE = 5
    UPGRADE_ATTACK = 6
    LINEAR_ATTACK_DOWN = 7
    LINEAR_ATTACK_UP = 8
    LINEAR_ATTACK_RIGHT = 9
    LINEAR_ATTACK_LEFT = 10
    RANGED_ATTACK = 11


class MapType(Enum):
    def __str__(self):
        return str(self.value)

    EMPTY = 0
    AGENT = 1
    GOLD = 2
    TREASURY = 3
    WALL = 4
    FOG = 5
    OUT_OF_SIGHT = 6
    OUT_OF_MAP = 7


class MapTile:
    def __init__(self):
        self.type: MapType
        self.data: int
        self.coordinates: tuple(int, int)


class Map:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.gold_count = 0
        self.sight_range = 0
        self.grid = []

    def set_grid_size(self):
        self.grid = [MapTile] * (self.sight_range ** 2)


class GameState:
    def __init__(self):
        self.rounds = int(input())
        self.def_upgrade_cost = int(input())
        self.atk_upgrade_cost = int(input())
        self.cool_down_rate = float(input())
        self.linear_attack_range = int(input())
        self.ranged_attack_radius = int(input())
        self.map = Map()
        self.map.width, self.map.height = tuple(
            [int(x) for x in input().split()])
        self.map.gold_count = int(input())
        self.map.sight_range = int(input())
        self.map.set_grid_size()
        self.debug_log = ''

    def set_info(self):
        self.location = tuple([int(x) for x in input().split()])
        for tile in self.map.grid:
            tile.type, tile.data, *tile.coordinates = tuple(
                [int(x) for x in input().split()])
        self.agent_id = int(input())
        self.current_round = int(input())
        self.attack_ratio = float(input())
        self.deflvl = int(input())
        self.atklvl = int(input())
        self.wallet = int(input())
        self.safe_wallet = int(input())
        self.wallets = [int(x) for x in input().split()]

    def debug(self):
        # Customize to your needs
        self.debug_log += f'round: {str(self.current_round)}\n'
        self.debug_log += f'location: {str(self.location)}\n'
        self.debug_log += f'agent ID: {str(self.agent_id)}\n'
        self.debug_log += f'attack ratio: {str(self.attack_ratio)}\n'
        self.debug_log += f'defence level: {str(self.deflvl)}\n'
        self.debug_log += f'attack level: {str(self.atklvl)}\n'
        self.debug_log += f'wallet: {str(self.wallet)}\n'
        self.debug_log += f'safe wallet: {str(self.safe_wallet)}\n'
        self.debug_log += f'list of wallets: {str(self.wallets)}\n'
        self.debug_log += f'{60 * "-"}\n'

    def debug_file(self):
        fileName = 'Clients/logs/'
        makedirs(fileName, exist_ok=True)
        fileName += f'p{getpid()}.log'
        with open(fileName, 'a') as f:
            f.write(self.debug_log)

    def get_action(self):
        # write your code here
        # return the action value
        return Action.STAY


if __name__ == '__main__':
    game_state = GameState()
    for _ in range(game_state.rounds):
        game_state.set_info()
        print(game_state.get_action())
        if DEBUG:
            game_state.debug()
    if DEBUG:
        game_state.debug_file()
