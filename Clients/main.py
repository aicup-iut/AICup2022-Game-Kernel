from os import makedirs
from enum import Enum

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


class Map:
    def __init__(self) -> None:
        self.width: int
        self.height: int
        self.gold_count: int
        self.sight_range: int
        self.grid: list

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
