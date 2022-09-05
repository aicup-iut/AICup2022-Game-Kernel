import gym
from gym import error, spaces, utils, logger
from gym.utils import seeding
import numpy as np
from random import randint, sample, shuffle, randrange
import json
import os

# map
EMPTY = 0
AGENT = 1
GOLD = 2
TREASURY = 3
WALL = 4
FOG = 5
OUT_OF_SIGHT = 6
OUT_OF_MAP = 7

# actions
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

win_dict = {
    0: 'safe wallet', 1: 'wallet', 2: 'attack', 3: 'less upgrade cost', 4: 'random'
}
act_dict = {
    STAY: (0, 0),
    MOVE_DOWN: (1, 0),
    MOVE_UP: (-1, 0),
    MOVE_RIGHT: (0, 1),
    MOVE_LEFT: (0, -1)
}


class agent:
    def __init__(self, x, y, wallet, id, safe_wallet=0):
        self.x = x
        self.y = y
        self.action = -1
        self.wallet = wallet
        self.id = id
        self.safe_wallet = safe_wallet
        self.alpha = 0  # cool down
        self.atk_lvl = 1
        self.def_lvl = 1
        self.upgrade_cost = 0
        self.robbed_gold = 0


class AICUP2022ENV(gym.Env):
    x_size = None
    y_size = None
    # agents_cnt=None

    def __init__(self,
                 input_map,
                 def_upgrade_cost=2,
                 atk_upgrade_cost=2,
                 cool_down_rate=1/2,
                 linear_attack_range=4,
                 ranged_attack_radius=2,
                 agents_cnt=4,
                 rounds=1000,
                 gold_count=10,
                 agent_sight_range=5
                 ):
        # TODO
        # treasury multiple players
        # configure spaces
        self.teams = [{
            'wallet': 0
        },
            {
            'wallet': 0
        }]
        self.input_map = input_map
        self.x_size = input_map['height']
        self.y_size = input_map['width']
        self.agents_cnt = agents_cnt
        self.rounds = rounds
        self.max_rounds = rounds
        self.gold_count = gold_count
        self.main_board = np.zeros((self.x_size, self.y_size), dtype=int)
        self.data_board = np.zeros((self.x_size, self.y_size), dtype=int)
        self.fog_map = np.zeros((self.x_size, self.y_size), dtype=int)
        self.attack_board = np.zeros((self.x_size, self.y_size), dtype=int)
        self.agentd_dest = [[-1, [-1, -1]] for _ in range(agents_cnt)]
        self.agents_list = [agent(0, 0, 0, id=_) for _ in range(agents_cnt)]
        self.treasury_coord = self.initialize_treasury(5, 5)
        self.linear_attack_range = linear_attack_range
        self.ranged_attack_radius = ranged_attack_radius
        self.cool_down_rate = cool_down_rate
        self.def_upgrade_cost = def_upgrade_cost
        self.atk_upgrade_cost = atk_upgrade_cost
        self.winner = -1
        self.win_reason = -1
        self.agent_sight_range = agent_sight_range
        # self.agent_coords=np.zeros((agents_cnt,2),dtype=int)
        # TODO: properly configure these spaces
        self.action_space = [spaces.Discrete(5) for _ in range(agents_cnt)]
        self.observation_space = spaces.Box(
            0, 1, (self.x_size, self.y_size), np.int16)
        self.reset()

    def step(self, action):
        done = False
        # if rounds is zero at start of step
        # ignore actions
        if self.rounds <= 0:
            done = True
            self.winner = self.decide_winner()
            # if self.teams[0]['wallet']>self.teams[1]['wallet']:
            #     self.winner=0
            # elif self.teams[1]['wallet']>self.teams[0]['wallet']:
            #     self.winner=1
            # elif self.teams[1]['wallet']==self.teams[0]['wallet']:
            #     self.winner=randint(0,1)
            observation = self.generate_observation()
            info = self.generate_info()
            return (observation, None, done, info)

        moved = [False for i in range(self.agents_cnt)]
        self.attack_board = np.zeros((self.x_size, self.y_size), dtype=int)
        agents_order = self.agents_random_order(action)
        move_queue = []
        for agent in agents_order:
            # action converted to coordinations differences dx dy

            self.agents_list[agent].action = -1
            self.agents_list[agent].alpha -= 1
            self.run_action(action[agent], self.agents_list[agent])
            if self.agents_list[agent].action == -1 and action[agent] <= MOVE_LEFT:
                move_queue.append([action[agent], self.agents_list[agent]])
            self.agents_list[agent].alpha = max(
                0, self.agents_list[agent].alpha)
            self.update_board()
        # repeating actions for unsuccessful moves
        count = 12
        while len(move_queue) > 0 and count > 0:
            self.run_action(move_queue[0][0], move_queue[0][1])
            if move_queue[0][1].action == -1:
                move_queue.append([move_queue[0][0], move_queue[0][1]])
            move_queue.pop(0)
            count -= 1
        # return -(action number in obs and info) for unsuccessful actions:
        for index, agent in enumerate(self.agents_list):
            if agent.action == -1:
                agent.action = -1*action[index]
        self.update_board()
        self.add_gold()
        self.rounds -= 1
        if self.rounds == 0:
            done = True
            self.winner = self.decide_winner()
            # if self.teams[0]['wallet']>self.teams[1]['wallet']:
            #     self.winner=0
            # elif self.teams[1]['wallet']>self.teams[0]['wallet']:
            #     self.winner=1
            # elif self.teams[1]['wallet']==self.teams[0]['wallet']:
            #     self.winner=randint(0,1)
            observation = self.generate_observation()
            info = self.generate_info()
            return (observation, None, done, info)

        observation = self.generate_observation()
        info = self.generate_info()
        return (observation, None, done, info)

    def reset(self):
        # TODO :adjust this due to agent class
        # commented section random positioning of agents
        # X=sample(range(self.x_size),4)
        # Y=sample(range(self.y_size),4)
        # #problem with sample funciton
        # for index,agent in enumerate(self.agents_list):
        #     agent.x,agent.y=X[index],Y[index]
        self.load_map()
        self.add_gold()
        self.update_board()
        observation = self.generate_observation()

        return (observation, None, None, None)

    def render(self, mode='human'):
        raise NotImplementedError

    def close(self):
        pass

    def check_coords_empty(self, x, y):
        valid_obstacle = [EMPTY, GOLD, TREASURY]
        agents = [(i.x, i.y) for i in self.agents_list]

        if self.main_board[x][y] not in valid_obstacle:
            return False
        if (x, y) in agents:
            return False
        return True

    def check_coord_valid(self, x, y):
        # TODO
        # check walls
        # valid_obstacle=[EMPTY,GOLD, TREASURY]
        if x < 0 or x >= self.x_size:
            return False
        if y < 0 or y >= self.y_size:
            return False
        # if self.main_board[x][y] not in valid_obstacle:
        #     return False
        return True

    def update_board(self):
        # update the board with agents' coordinations
        # TODO
        gold_map = np.copy(self.main_board)
        for i in range(self.x_size):
            for j in range(self.y_size):
                self.main_board[i][j] = 0

        for index, agent in enumerate(self.agents_list):
            x, y = agent.x, agent.y
            if (x, y) in self.treasury_coord:
                self.teams[index//2]['wallet'] += agent.wallet
                agent.wallet = 0

            if gold_map[x][y] == GOLD:
                agent.wallet += self.data_board[x][y]
                gold_map[x][y] = AGENT
            self.main_board[x][y] = AGENT
            self.data_board[x][y] = index
        # update every agent's safe wallet with team wallet

        for index, agent in enumerate(self.agents_list):
            agent.safe_wallet = self.teams[index//2]['wallet']

        for i in range(self.x_size):
            for j in range(self.y_size):
                if gold_map[i][j] == GOLD:
                    self.main_board[i][j] = GOLD
                if gold_map[i][j] == WALL:
                    self.main_board[i][j] = WALL
        for coord in self.treasury_coord:
            self.main_board[coord[0]][coord[1]] = TREASURY
        for i in range(self.x_size):
            for j in range(self.y_size):
                if self.main_board[i][j] == 0:
                    self.data_board[i][j] = 0

        return self

    def manhattan_sight(self, x, y, distance=5, fog=False):
        # return a numpy array with distance*distance dimension
        # which is a copy of the mentioned frame
        # with (x,y) in center of it from game board
        r = (distance-1)//2
        temp_observation = np.zeros(
            (distance, distance, 4), dtype=int) + OUT_OF_SIGHT
        for i in range(distance):
            for j in range(abs(i-r), distance-abs(i-r)):
                temp_x, temp_y = self.coord_transform(x, y, i-r, j-r)
                if self.check_coord_valid(temp_x, temp_y):
                    # [type,data,(x,y)]
                    # type: -2 for out of sight
                    #      -1 for out of  map
                    #       0-5 for EMPTY,AGENT,GOLD,TREASURY,WALL,FOG
                    # data==-2 use for invalid coords
                    temp_observation[i][j] = np.array(
                        [self.main_board[temp_x][temp_y], self.data_board[temp_x][temp_y], temp_x, temp_y], dtype=int)
                    if self.fog_map[temp_x][temp_y] == True and fog:
                        temp_observation[i][j] = [FOG, 0, temp_x, temp_y]
                else:
                    temp_observation[i][j] = [OUT_OF_MAP,
                                              OUT_OF_SIGHT, OUT_OF_MAP, OUT_OF_MAP]
        return temp_observation

    def coord_transform(self, x, y, dx, dy):
        # return new coordination after moving in the board by from
        # (x,y) to (x+dx,y+dy)
        new_x = x + dx
        new_y = y + dy
        # top and bottom edges are connected
        # if new_y >=self.y_size or new_y<0:
        #     new_y = (new_y % self.y_size)
        # # left and right edges likewise
        # if new_x >= self.x_size or new_x < 0:
        #     new_x =  (new_x %self.x_size)
        return (new_x, new_y)

    def add_wall(self, wall_list):
        for i in range(self.x_size):
            for j in range(self.y_size):
                if wall_list[i][j]:
                    self.main_board[i][j] = WALL
        # self.main_board[np.where(wall_list==True)]=WALL

    def add_gold(self):
        current_gold = 0
        for i in self.main_board:
            for j in i:
                if j == GOLD:
                    current_gold += 1
        count = self.gold_count-current_gold
        empty_coords = self.empty_coords_list(count)
        count -= 1
        while count >= 0:
            X, Y = empty_coords[count]
            self.main_board[X][Y] = 2
            self.data_board[X][Y] = 1
            count -= 1
        return self

    def empty_coords_list(self, count):
        # to be tested
        # error for not valid count
        # error for count greater than available coords
        coords = []
        for _ in range(count):
            x = randint(0, self.x_size-1)
            y = randint(0, self.y_size-1)
            while self.main_board[x][y] != 0 or ((x, y) in coords):
                x = randint(0, self.x_size-1)
                y = randint(0, self.y_size-1)
            coords.append((x, y))
        return coords

    def generate_observation(self):
        observation = []
        for agent in self.agents_list:
            action = agent.action
            if agent.action < 0:
                action = -1

            x, y = agent.x, agent.y
            manhattan = self.manhattan_sight(
                x, y, self.agent_sight_range, fog=True)
            manhattan = manhattan.reshape(
                np.shape(manhattan)[0]*np.shape(manhattan)[1], np.shape(manhattan)[2])
            # manhattan=manhattan[np.where(manhattan[:,:,1]!=-2)]
            agent_observation = [
                (x, y), manhattan.tolist(), agent.id, self.x_size, self.y_size, self.rounds, self.max_rounds, agent.alpha, self.cool_down_rate, min(
                    self.cool_down_rate**agent.alpha, 1), agent.def_lvl, agent.atk_lvl, agent.wallet, agent.safe_wallet, action, [i.wallet for i in self.agents_list]
            ]
            observation.append(agent_observation)
        return observation

    def generate_info(self):
        info = []
        coin_map = np.zeros(np.shape(self.data_board), dtype=int)
        coin_map[np.where(self.main_board == GOLD)
                 ] = self.data_board[np.where(self.main_board == GOLD)]
        for agent in self.agents_list:
            info.append(
                {
                    'winner': self.winner, 'win_reason': self.win_reason, 'attack efficiency': self.cool_down_rate**agent.alpha, 'rounds': self.rounds, 'def_lvl': agent.def_lvl, 'atk_lvl': agent.atk_lvl, 'wallet': agent.wallet, 'safe wallet': agent.safe_wallet, 'x': agent.x, 'y': agent.y, 'board': coin_map, 'data': self.data_board, 'map': self.main_board, 'action': agent.action, 'attack': self.attack_board

                }
            )
        return info

    def load_map(self):
        conf_dic = self.input_map
        self.x_size = conf_dic["height"]
        self.y_size = conf_dic["width"]
        self.fog_map = conf_dic["fog_map"]
        for i in range(self.agents_cnt):
            self.agents_list[i].x = conf_dic[f"player{i+1}_coordinate"][0]
            self.agents_list[i].y = conf_dic[f"player{i+1}_coordinate"][1]
        self.treasury_coord = self.initialize_treasury(
            conf_dic["treasury_coordinate"][0], conf_dic["treasury_coordinate"][1])
        walls = conf_dic["walls"]
        self.add_wall(walls)

    def run_action(self, action, agent):

        if action == STAY:
            agent.action = 0
        # call the corresponding function for each action
        if action <= MOVE_LEFT:
            self.move(action, agent)
        elif action == UPGRADE_DEFENCE:
            self.upgrade_defence(agent)
            return
        elif action == UPGRADE_ATTACK:
            self.upgrade_attack(agent)
            return
        elif action <= LINEAR_ATTACK_LEFT:
            self.linear_attack(agent, action)
        elif action == RANGED_ATTACK:
            self.ranged_attack(agent)

    def move(self, action, agent):
        dx, dy = act_dict[action]
        # getting agent's coordinations
        x, y = agent.x, agent.y
        new_x, new_y = self.coord_transform(x, y, dx, dy)
        # check the validation of action

        if self.check_coord_valid(new_x, new_y) and self.check_coords_empty(new_x, new_y):
            x = new_x
            y = new_y
            agent.action = action
        # updating agent's coordinations
        agent.x, agent.y = x, y
        return self

    def linear_attack(self, agent, action):
        X, Y = agent.x, agent.y

        if(action == LINEAR_ATTACK_DOWN):
            (dx, dy) = act_dict[MOVE_DOWN]
            for i in range(1, self.linear_attack_range+1):
                x, y = self.coord_transform(X, Y, dx*i, dy*i)
                if (not self.check_coord_valid(x, y)) or self.main_board[x][y] == WALL:
                    break
                # update attack list:
                self.attack_board[x][y] = 1
                if self.main_board[x][y] == AGENT and self.data_board[x][y]//2 != self.data_board[X][Y]//2:
                    def_agent = self.agents_list[self.data_board[x][y]]
                    self.hit_agent(agent, def_agent)
        elif(action == LINEAR_ATTACK_UP):
            (dx, dy) = act_dict[MOVE_UP]
            for i in range(1, self.linear_attack_range+1):
                x, y = self.coord_transform(X, Y, dx*i, dy*i)
                if (not self.check_coord_valid(x, y)) or self.main_board[x][y] == WALL:
                    break
                # update attack list:
                self.attack_board[x][y] = 1
                if self.main_board[x][y] == AGENT and self.data_board[x][y]//2 != self.data_board[X][Y]//2:
                    def_agent = self.agents_list[self.data_board[x][y]]
                    self.hit_agent(agent, def_agent)
        elif(action == LINEAR_ATTACK_RIGHT):
            (dx, dy) = act_dict[MOVE_RIGHT]
            for i in range(1, self.linear_attack_range+1):
                x, y = self.coord_transform(X, Y, dx*i, dy*i)
                if (not self.check_coord_valid(x, y)) or self.main_board[x][y] == WALL:
                    break
                # update attack list:
                self.attack_board[x][y] = 1
                if self.main_board[x][y] == AGENT and self.data_board[x][y]//2 != self.data_board[X][Y]//2:
                    def_agent = self.agents_list[self.data_board[x][y]]
                    self.hit_agent(agent, def_agent)
        elif(action == LINEAR_ATTACK_LEFT):
            (dx, dy) = act_dict[MOVE_LEFT]
            for i in range(1, self.linear_attack_range+1):
                x, y = self.coord_transform(X, Y, dx*i, dy*i)
                if (not self.check_coord_valid(x, y)) or self.main_board[x][y] == WALL:
                    break
                # update attack list:
                self.attack_board[x][y] = 1
                if self.main_board[x][y] == AGENT and self.data_board[x][y]//2 != self.data_board[X][Y]//2:
                    def_agent = self.agents_list[self.data_board[x][y]]
                    self.hit_agent(agent, def_agent)
        agent.action = action
        agent.alpha = agent.alpha+2

    def ranged_attack(self, attacker: agent):
        r = self.ranged_attack_radius
        R = int(r*2 + 1)
        attacker_index = self.data_board[attacker.x][attacker.y]
        attack_range = self.manhattan_sight(attacker.x, attacker.y, R)
        attack_x = attack_range[:, :, 2][np.where(
            attack_range[:, :, 1] != OUT_OF_SIGHT)]
        attack_y = attack_range[:, :, 3][np.where(
            attack_range[:, :, 1] != OUT_OF_SIGHT)]
        self.attack_board[attack_x, attack_y] = 1
        # update attack list:
        agents_in_range = attack_range[np.where(
            attack_range[:, :, 0] == AGENT)]
        for agent in agents_in_range:
            agent_index = agent[1]
            defender = self.agents_list[agent_index]
            if attacker_index//2 != agent_index//2:
                self.hit_agent(attacker, defender)
        attacker.action = RANGED_ATTACK
        attacker.alpha = attacker.alpha+2

    def hit_agent(self, attacker: agent, defender: agent):
        attck_effc = min(self.cool_down_rate**attacker.alpha, 1)
        attack_rate = attck_effc*attacker.atk_lvl / \
            (attacker.atk_lvl+defender.def_lvl)
        gold_amount = int(defender.wallet*attack_rate)
        defender.wallet -= gold_amount
        attacker.robbed_gold += gold_amount
        gold = self.perimeter_gold_distribution(
            gold_amount, defender.x, defender.y)
        for i in range(3):
            for j in range(3):
                x, y = self.coord_transform(defender.x, defender.y, i-1, j-1)
                if not self.check_coord_valid(x, y):
                    continue
                if gold[i][j] > 0:
                    if self.main_board[i][j] == GOLD or self.main_board[i][j] == EMPTY:
                        self.main_board[i][j] = GOLD
                        self.data_board[i][j] += gold[i][j]
                    elif self.main_board[i][j] == AGENT:
                        index = self.data_board[i][j]
                        self.agents_list[index].wallet += gold[i][j]

    def perimeter_gold_distribution(self, gold_amount, x, y):
        around_agent = np.zeros((3, 3), dtype=int)
        count = 0
        while count < gold_amount:
            coord = randint(0, 8)
            dx = coord//3 - 1
            dy = coord % 3 - 1
            temp_x, temp_y = self.coord_transform(x, y, dx, dy)
            if self.check_coord_valid(temp_x, temp_y):
                if (dx != 0 or dy != 0) and self.main_board[temp_x][temp_y] != WALL and self.main_board[temp_x][temp_y] != TREASURY:
                    around_agent[dx+1][dy+1] += 1
                    count += 1
        return around_agent

    def upgrade_defence(self, agent: agent):
        if (agent.wallet >= self.def_upgrade_cost):
            agent.def_lvl += 1
            agent.wallet -= self.def_upgrade_cost
            agent.upgrade_cost += self.def_upgrade_cost
            agent.action = UPGRADE_DEFENCE
        return self

    def upgrade_attack(self, agent: agent):
        if (agent.wallet >= self.atk_upgrade_cost):
            agent.atk_lvl += 1
            agent.wallet -= self.atk_upgrade_cost
            agent.upgrade_cost += self.atk_upgrade_cost
            agent.action = UPGRADE_ATTACK
        return self

    def agents_random_order(self, action):
        agents_order = list(range(self.agents_cnt))
        #agents_order=[(self.agents_list[i].wallet,i) for i in range(self.agent_cnt)]
        shuffle(agents_order)
        # giving higher priority to agents with less gold
        priority_list = [3, 3, 3, 3, 3, 1, 1, 2, 2, 2, 2, 2]
        def s_key(index): return self.agents_list[index].wallet+priority_list[action[index]] if(
            action[index] < UPGRADE_DEFENCE) else priority_list[action[index]]
        agents_order.sort(key=s_key)
        #agents_order=[agent[1] for agent in agents_order ]
        return agents_order

    def decide_winner(self):
        self.win_reason = 0
        if self.teams[0]['wallet'] > self.teams[1]['wallet']:
            self.winner = 0
            return self.winner
        if self.teams[1]['wallet'] > self.teams[0]['wallet']:
            self.winner = 1
            return self.winner
        # team0 safe wallet == team1 safe wallet winner is team with more coins in wallet:
        self.win_reason = 1
        team0_wallet = self.agents_list[0].wallet+self.agents_list[1].wallet
        team1_wallet = self.agents_list[2].wallet+self.agents_list[3].wallet
        if team0_wallet > team1_wallet:
            self.winner = 0
            return self.winner
        if team0_wallet < team1_wallet:
            self.winner = 1
            return self.winner
        # team0  wallet == team1  wallet winner is team with that robbed  in attacks:
        self.win_reason = 2
        team0_robb = self.agents_list[0].robbed_gold + \
            self.agents_list[1].robbed_gold
        team1_robb = self.agents_list[2].robbed_gold + \
            self.agents_list[3].robbed_gold
        if team0_robb > team1_robb:
            self.winner = 0
            return self.winner
        if team0_robb < team1_robb:
            self.winner = 1
            return self.winner
        # team with less upgrade cost is winner
        self.win_reason = 3
        team0_cost = self.agents_list[0].upgrade_cost + \
            self.agents_list[1].upgrade_cost
        team1_cost = self.agents_list[2].upgrade_cost + \
            self.agents_list[3].upgrade_cost
        if team0_cost < team1_cost:
            self.winner = 0
            return self.winner
        if team0_cost > team1_cost:
            self.winner = 1
            return self.winner
        # random winner:
        self.win_reason = 4
        self.winner = randint(0, 1)
        return self.winner

    def initialize_treasury(self, x, y):
        coords = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                coords.append((x+i, y+j))
        return coords
