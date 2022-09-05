from os import getcwd, makedirs
from json import load, dump
from process.AgentHandler import AgentHandler
from random import randrange
from environment.env import AICUP2022ENV


class GameHandler:
    def __init__(self, args):
        self.obs: list
        self.action: list
        self.agents = []
        self.final_info = {'initial_game_data': {}, 'steps': []}
        with open(args.setting) as json_settings:
            self.settings = load(json_settings)
        self.log_path = f'{getcwd()}/{args.log}'
        makedirs(self.log_path, exist_ok=True)
        with open(args.map) as input_map:
            self.map = load(input_map)
        self.environment = AICUP2022ENV(input_map=self.map,
                                        rounds=self.settings['rounds'],
                                        agents_cnt=4,
                                        def_upgrade_cost=self.settings['def_upgrade_cost'],
                                        atk_upgrade_cost=self.settings['atk_upgrade_cost'],
                                        cool_down_rate=self.settings['cool_down_rate'],
                                        linear_attack_range=self.settings['linear_attack_range'],
                                        ranged_attack_radius=self.settings['ranged_attack_radius'],
                                        gold_count=self.settings['gold_count'],
                                        agent_sight_range=self.settings['agent_sight_range'])
        self.players = [{'path': args.p1, 'name': args.n1},
                        {'path': args.p2, 'name': args.n2}]
        self.winner = [-1, '']
        self.is_alive = 4 * [True]
        self.end_engine = False
        self.current_step = 0
        self.cg_enable = args.cg
        if self.cg_enable:
            from cgroups import Cgroup
            self.crp = Cgroup('RunningProcess')
            self.crp.set_cpu_limit(self.settings['running_cpu_limit'])
            self.crp.set_memory_limit(self.settings['memory_limit'])
            self.csp = []
            for i in range(4):
                self.csp.append(Cgroup(f'SleepingProcess{i}'))
                self.csp[i].set_cpu_limit(self.settings['sleeping_cpu_limit'])
                self.csp[i].set_memory_limit(self.settings['memory_limit'])

    def run(self):
        self.create_agents()
        self.obs, _, _, _ = self.environment.reset()
        for _ in range(self.settings['rounds']):
            if self.end_engine:
                break
            self.step()
        self.final_update_info()
        self.log_jsonify()

    def create_agents(self):
        try:
            for i in range(4):
                self.agents.append(AgentHandler(
                    self.players[i//2]['path'], self.settings,
                    (self.map['width'], self.map['height'])))
                if(self.cg_enable):
                    self.csp[i].add(self.agents[i].process.pid)
        except Exception as e:
            print(f'Agent of player {i//2 + 1} cannot be created!')
            print('Error: ' + str(e))

    def step(self):
        self.current_step += 1
        actions = []
        for i in range(4):
            try:
                if self.cg_enable:
                    self.csp[i].remove(self.agents[i].process.pid)
                    self.crp.add(self.agents[i].process.pid)
                actions.append(self.agents[i].action(
                    self.obs[i]) if self.is_alive[i] else 0)
            except Exception as e:
                print(f'Agent {i} destroyed!')
                print('Error: ' + str(e))
                self.is_alive[i] = False
                actions.append(0)
            finally:
                if self.cg_enable:
                    self.crp.remove(self.agents[i].process.pid)
                    self.csp[i].add(self.agents[i].process.pid)
        self.obs, _, _, self.info = self.environment.step(actions)
        self.update_info()
        self.check_finish()

    def check_finish(self):
        if self.info[0]['winner'] in [0, 1]:
            self.end_engine = True
            self.winner[0] = self.info[0]['winner'] + 1

            if self.info[0]['win_reason'] == 0:
                self.winner[1] = 'More coins in safe wallet'
            elif self.info[0]['win_reason'] == 1:
                self.winner[1] = 'More coins in wallet'
            elif self.info[0]['win_reason'] == 2:
                self.winner[1] = 'More coins in attck'
            elif self.info[0]['win_reason'] == 3:
                self.winner[1] = 'Less upgrade cost'
            elif self.info[0]['win_reason'] == 4:
                self.winner[1] = 'Random'
        elif not (self.is_alive[0] or self.is_alive[1]):
            print('Agents of player 1 destroyed!')
            self.end_engine = True
            self.winner = [2, 'Timeout']

        if not (self.is_alive[2] or self.is_alive[3]):
            print('Agents of player 2 destroyed!')
            self.end_engine = True
            self.winner = [1, 'Timeout']
            if(self.end_engine):
                self.winner[0] = randrange(2)
                self.winner[1] += '/random'

    def update_info(self):
        self.final_info['steps'].append({'players_data': [], 'map_data': {}})
        for i in range(len(self.agents)):
            player_info = {}
            player_info['id'] = i + 1
            player_info['x_position'] = int(self.info[i]['x'])
            player_info['y_position'] = int(self.info[i]['y'])
            if self.info[i]['action'] == 1:  # move down
                player_info['x_position'] -= 1
            elif self.info[i]['action'] == 2:  # move up
                player_info['x_position'] += 1
            elif self.info[i]['action'] == 3:  # move right
                player_info['y_position'] -= 1
            elif self.info[i]['action'] == 4:  # move left
                player_info['y_position'] += 1
            player_info['x_position_after'] = int(self.info[i]['x'])
            player_info['y_position_after'] = int(self.info[i]['y'])
            player_info['coins'] = int(self.info[i]['wallet'])
            player_info['vault'] = int(self.info[i]['safe wallet'])
            player_info['action'] = int(self.info[i]['action'])
            player_info['attack_level'] = int(self.info[i]['atk_lvl'])
            player_info['defense_level'] = int(self.info[i]['def_lvl'])
            player_info['efficiency'] = float(
                self.info[i]['attack efficiency'])
            self.final_info['steps'][self.current_step -
                                     1]['players_data'].append(player_info)
        self.final_info['steps'][self.current_step -
                                 1]['map_data']['coins'] = self.info[0]['board'].tolist()
        self.final_info['steps'][self.current_step -
                                 1]['map_data']['attack'] = self.info[0]['attack'].tolist()

    def final_update_info(self):
        igd = self.final_info['initial_game_data']
        igd['last_step'] = self.current_step
        igd['winner'] = self.players[self.winner[0] - 1]['name']
        igd['winnerId'] = self.winner[0]
        igd['win_reason'] = self.winner[1]
        igd['map_width'] = self.map['width']
        igd['map_height'] = self.map['height']
        igd['map_data'] = {}
        igd['map_data']['obstacle'] = self.map['walls']
        igd['map_data']['fog'] = self.map['fog_map']
        igd['map_data']['vault'] = self.map['treasury_map']
        igd['is_vision_limited'] = 'true'
        for i in range(len(self.players)):
            igd[f'team_{i+1}_name'] = self.players[i]['name']
        for i in range(len(self.agents)):
            igd[f'player_{i+1}_init_x'] = self.map[f'player{i+1}_coordinate'][0]
            igd[f'player_{i+1}_init_y'] = self.map[f'player{i+1}_coordinate'][1]

    def log_jsonify(self):
        with open(f'{self.log_path}/game.json', 'w', encoding='utf8') as json_file:
            dump(self.final_info, json_file, ensure_ascii=False, indent='\t')
