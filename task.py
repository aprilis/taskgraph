import os
import json
import logging
from string import Template

class Task:
    PATH = 'tasks'
    CONFIG_FILE = 'task.json'
    SUCCESS_FILE ='.taskgraph_success'

    def __init__(self, task_name):
        path = os.path.join(Task.PATH, task_name)
        if not os.path.isdir(path):
            raise FileNotFoundError(f'Task {task_name} does not exist')

        task_path = os.path.join(path, Task.CONFIG_FILE)
        with open(task_path) as f:
            task = json.load(f)
        
        self.name = task_name
        self.path = path
        self.success = os.path.exists(os.path.join(path, Task.SUCCESS_FILE))
        self.description = task['description'] if 'description' in task else ''
        self.depends = task['depends']
        
        mapping = { os.path.join(Task.PATH, dep): dep for dep in self.depends }
        mapping['self'] = path
        commands = task['commands']
        if type(commands) == str:
            commands = [commands]
        self.commands = [ Template(cmd).substitute(mapping) for cmd in commands ]

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
            if not runner.run(cmd):
                logging.error(f'Command {cmd} failed')
                return False

        #create empty file indicating success
        open(os.path.join(self.path, Task.SUCCESS_FILE)).close()

        self.success = True
        return True