import os
import json
import logging
from string import Template

class Task:
    PATH = 'tasks'
    CONFIG_FILE = 'task.json'
    SUCCESS_FILE ='.taskgraph_success'

    @staticmethod
    def get_path(task_name):
        return os.path.abspath(os.path.join(Task.PATH, task_name))

    @property
    def path(self):
        return Task.get_path(self.name)

    def __init__(self, task_name):
        self.name = task_name

        if not os.path.isdir(self.path):
            raise FileNotFoundError(f'Task {task_name} does not exist')

        task_path = os.path.join(self.path, Task.CONFIG_FILE)
        with open(task_path) as f:
            task = json.load(f)
        
        self.success = os.path.exists(os.path.join(self.path, Task.SUCCESS_FILE))
        self.description = task.get('description', '')
        self.depends = task.get('depends', [])
        
        self.mapping = { dep: Task.get_path(dep) for dep in self.depends }
        self.mapping['root'] = os.path.abspath('.')
        commands = task.get('commands', [])
        if type(commands) == str:
            commands = [commands]
        self.commands = [ Template(cmd).substitute(self.mapping) for cmd in commands ]
        #self.commands = commands

    def save_config(self):
        task_path = os.path.join(self.path, Task.CONFIG_FILE)
        result = {
            'description': self.description,
            'depends': self.depends,
            'commands': self.commands
        }
        with open(task_path, 'w') as f:
            json.dump(result, f, indent=4)

    def run(self, runners):
        if self.success:
            return True
        
        logging.info(f'Task {self.name} has started')
            
        for cmd in self.commands:
            for r in runners:
                if r.match(cmd):
                    runner = r
                    break
            else:
                logging.error(f'Runner for {cmd} not found')
                return False

            logging.info(f'Running "{cmd}"')
            if not runner.run(cmd, self.mapping, self.path):
                logging.error(f'Command {cmd} failed')
                return False

        #create empty file indicating success
        open(os.path.join(self.path, Task.SUCCESS_FILE), 'w').close()

        self.success = True
        return True
