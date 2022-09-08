from os import makedirs
from enum import Enum
from secrets import choice

DEBUG = 0


class Action(Enum):
    def __str__(self) -> str:
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
    def __str__(self) -> str:
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
    def __init__(self) -> None:
        self.type: MapType
        self.data: int
        self.coordinates: tuple(int, int)

    def __str__(self) -> str:
        res = self.type.name
        if self.type in [MapType.OUT_OF_SIGHT, MapType.OUT_OF_MAP]:
            return res.center(16)
        elif self.type in [MapType.AGENT, MapType.GOLD]:
            res += f':{self.data}'
        res += f' ({self.coordinates[0]},{self.coordinates[1]})'
        return res.center(16)


class Map:
    def __init__(self) -> None:
        self.width: int
        self.height: int
        self.gold_count: int
        self.sight_range: int
        self.grid: list

    def __str__(self) -> str:
        res = f'sight range -> {self.sight_range}\n'
        for i in range(self.sight_range):
            res += '\t'
            for j in range(self.sight_range):
                res += str(self.grid[i * self.sight_range + j])
                res += '*' if j < 4 else '\n'
        return res[:-1]

    def set_grid_size(self) -> None:
        self.grid = [MapTile() for _ in range(self.sight_range ** 2)]


class GameState:
    def __init__(self) -> None:
        self.rounds = int(input())
        self.def_upgrade_cost = int(input())
        self.atk_upgrade_cost = int(input())
        self.cool_down_rate = float(input())
        self.linear_attack_range = int(input())
        self.ranged_attack_radius = int(input())
        self.map = Map()
        self.map.width, self.map.height = map(int, input().split())
        self.map.gold_count = int(input())
        self.map.sight_range = int(input())  # equivalent to (2r+1)
        self.map.set_grid_size()
        self.debug_log = ''

    def set_info(self) -> None:
        self.location = tuple(map(int, input().split()))  # (row, column)
        for tile in self.map.grid:
            tile.type, tile.data, *tile.coordinates = map(int, input().split())
            tile.type = MapType(tile.type)
        self.agent_id = int(input())  # player1: 0,1 --- player2: 2,3
        self.current_round = int(input())  # 1 indexed
        self.attack_ratio = float(input())
        self.deflvl = int(input())
        self.atklvl = int(input())
        self.wallet = int(input())
        self.safe_wallet = int(input())
        self.wallets = [*map(int, input().split())]  # current wallet
        self.last_action = int(input())  # -1 if unsuccessful

    def debug(self) -> None:
        # Customize to your needs
        self.debug_log += f'round: {str(self.current_round)}\n'
        self.debug_log += f'location: {str(self.location)}\n'
        self.debug_log += f'Map: {str(self.map)}\n'
        self.debug_log += f'attack ratio: {str(self.attack_ratio)}\n'
        self.debug_log += f'defence level: {str(self.deflvl)}\n'
        self.debug_log += f'attack level: {str(self.atklvl)}\n'
        self.debug_log += f'wallet: {str(self.wallet)}\n'
        self.debug_log += f'safe wallet: {str(self.safe_wallet)}\n'
        self.debug_log += f'list of wallets: {str(self.wallets)}\n'
        self.debug_log += f'last action: {str(self.last_action)}\n'
        self.debug_log += f'{60 * "-"}\n'

    def debug_file(self) -> None:
        fileName = 'Clients/logs/'
        makedirs(fileName, exist_ok=True)
        fileName += f'AGENT{self.agent_id}.log'
        with open(fileName, 'a') as f:
            f.write(self.debug_log)

    def get_action(self) -> Action:
        return Action(actions.pop(0))

actions = [9, 1, 8, 5, 5, 7, 3, 0, 0, 2, 8, 9, 5, 1, 7, 0, 10, 9, 10, 5, 1, 2, 10, 11, 11, 10, 1, 1, 11, 6, 5, 0, 9, 1, 0, 1, 3, 3, 11, 9, 0, 11, 7, 0, 0, 10, 5, 1, 7, 5, 5, 0, 7, 2, 1, 10, 11, 1, 3, 8, 5, 8, 9, 2, 7, 7, 2, 5, 8, 8, 10, 7, 1, 0, 6, 11, 2, 4, 8, 2, 10, 8, 6, 7, 8, 6, 2, 10, 11, 4, 0, 5, 4, 0, 3, 2, 3, 9, 6, 7, 11, 3, 7, 4, 11, 6, 11, 3, 4, 9, 4, 8, 3, 3, 3, 1, 6, 0, 2, 7, 7, 6, 7, 3, 2, 8, 3, 2, 0, 4, 10, 4, 7, 11, 4, 7, 3, 1, 11, 10, 9, 8, 0, 9, 7, 4, 9, 8, 2, 11, 0, 5, 2, 6, 10, 4, 10, 0, 11, 7, 0, 4, 7, 4, 5, 2, 8, 2, 7, 0, 6, 6, 4, 2, 7, 0, 7, 8, 9, 11, 2, 0, 6, 2, 8, 8, 0, 4, 5, 1, 8, 7, 1, 4, 0, 3, 6, 7, 8, 2]

if __name__ == '__main__':
    game_state = GameState()
    for _ in range(game_state.rounds):
        game_state.set_info()
        print(game_state.get_action())
        if DEBUG:
            game_state.debug()
    if DEBUG:
        game_state.debug_file()
