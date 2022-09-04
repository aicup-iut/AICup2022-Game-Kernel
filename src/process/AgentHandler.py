from sys import executable as pyExe
from subprocess import Popen, PIPE, STDOUT
from threading import Timer
from sys import platform


class AgentHandler:
    def __init__(self, executable_path, settings, map_size):
        try:
            self.process = Popen(self.exec_command(executable_path),
                                 stdin=PIPE, stdout=PIPE, stderr=STDOUT,
                                 text=True, shell=True, bufsize=1)
            self.settings = settings
            self.isFinished = False
            self.writer(self.settings['rounds'])
            self.writer(self.settings['def_upgrade_cost'])
            self.writer(self.settings['atk_upgrade_cost'])
            self.writer(self.settings['cool_down_rate'])
            self.writer(self.settings['linear_attack_range'])
            self.writer(self.settings['ranged_attack_radius'])
            self.writer(*map_size)
            self.writer(self.settings['gold_count'])
            self.writer(self.settings['agent_sight_range'])
        except Exception as e:
            raise e

    def exec_command(self, executable_path):
        if executable_path[-2:] == 'py':
            return f'{pyExe} {executable_path}'
        elif executable_path[-3:] == 'jar':
            return f'java -jar {executable_path}'
        elif executable_path[-3:] == 'exe' and 'linux' in platform:
            return f'mono {executable_path}'
        return executable_path

    def timeout_function(self):
        self.isFinished = True
        self.process.kill()

    def writer(self, *obj):
        txt = ' '.join(map(str, obj))
        self.process.stdin.write(txt + '\n')
        self.process.stdin.flush()

    def extract_obs(self, obs):
        self.writer(*obs[0])  # location
        for tile in obs[1]:  # game map
            self.writer(*tile)
        self.writer(obs[2])  # agent ID
        self.writer(obs[6] - obs[5] + 1)  # current round
        self.writer(obs[9])  # attack ratio
        self.writer(obs[10])  # defence level
        self.writer(obs[11])  # attack level
        self.writer(obs[12])  # wallet
        self.writer(obs[13])  # safe wallet
        self.writer(*obs[15])  # agents' wallet
        self.writer(obs[14])  # last action

    def action(self, obs):
        if self.isFinished:
            return 0
        timeout_timer = Timer(self.settings['timeout'], self.timeout_function)
        self.extract_obs(obs)
        try:
            timeout_timer.start()
            output = int(self.process.stdout.readline().strip())
            timeout_timer.cancel()
        except Exception as e:
            print(e)
            raise Exception('Timeout')
        finally:
            if self.isFinished:
                return 0
        output = output if 0 <= output <= 11 else 0
        return output

    def __del__(self):
        self.process.kill()
