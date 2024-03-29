#!/usr/bin/env python3

import argparse
import logging
from collections import defaultdict

from . import runners
from .task import Task
from .list import list_tasks

logging.basicConfig(format='TaskGraph (%(asctime)s): %(message)s',
		    datefmt='%H:%M:%S',
		    level=logging.INFO)

def run_tasks(tasks, runners=[runners.Notebook(), runners.Python(), runners.Bash()], force=False):
    tasks = list_tasks(tasks)
    opened_tasks = set()
    done_tasks = set()
    tasks_objects = dict()

    def run_task(task):
        if task in done_tasks:
            return tasks_objects[task].success
        if task in opened_tasks:
            logging.error(f'Encountered circular dependency including task {task}')
            return False
        opened_tasks.add(task)

        if task not in tasks_objects:
            tasks_objects[task] = Task(task)

        obj = tasks_objects[task]

        if not obj.success or (force and task in tasks):
            for dep in obj.deps:
                if not run_task(dep):
                    done_tasks.add(task)
                    return False
            
            if not obj.run(runners, force=force):
                done_tasks.add(task)
                return False

        done_tasks.add(task)
        return True
    
    for task in tasks:
        if run_task(task):
            logging.info(f'Task {task} successfully completed')
        else: logging.error(f'Task {task} failed')

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Run specified task')
    parser.add_argument('tasks', nargs='+', help='The name of the tasks to run')
    parser.add_argument('--force', '-f', action='store_true', default=False, 
        help='Whether to run task even if it has been done before')
    args = parser.parse_args()
    run_tasks(**vars(args))
