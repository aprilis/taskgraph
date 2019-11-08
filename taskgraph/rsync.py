#!/usr/bin/env python3

import argparse
import logging
from collections import defaultdict
import subprocess
import os

from .task import Task
from .list import list_tasks

logging.basicConfig(format='TaskGraph (%(asctime)s): %(message)s',
		    datefmt='%H:%M:%S',
		    level=logging.INFO)

def ssh_file_exists(path):
    host, file = path.split(':', maxsplit=1)
    command = f'ssh -q {host} [[ -f {file} ]] && return 0 || return 1'
    return subprocess.run(command, shell=True).returncode == 0

def rsync(source, target):
    command = f'rsync -av --progress "{source}" "{target}"'
    logging.info('running %s', command)
    result = subprocess.run(command, shell=True)
    return result.returncode == 0

def rsync_tasks_to(path, tasks, **kwargs):
    tasks = list_tasks(tasks)
    opened_tasks = set()
    done_tasks = dict()
    tasks_objects = dict()

    def rsync_task(task):
        if task in done_tasks:
            return done_tasks[task]
        if task in opened_tasks:
            logging.error(f'Encountered circular dependency including task {task}')
            return False
        opened_tasks.add(task)

        if task not in tasks_objects:
            tasks_objects[task] = Task(task)

        obj = tasks_objects[task]

        if not obj.success:
            for dep in obj.deps:
                if not rsync_task(dep):
                    done_tasks[task] = False
                    return False
        elif not rsync(obj.path, os.path.join(path, Task.PATH)):
            done_tasks[task] = False
            return False

        done_tasks[task] = True
        return True
    
    for task in tasks:
        if rsync_task(task):
            logging.info(f'Task {task} successfully completed')
        else: logging.error(f'Task {task} failed')


def rsync_tasks_from(path, tasks, **kwargs):
    tasks = list_tasks(tasks)
    opened_tasks = set()
    done_tasks = dict()
    tasks_objects = dict()

    def rsync_task(task):
        if task in done_tasks:
            return done_tasks[task]
        if task in opened_tasks:
            logging.error(f'Encountered circular dependency including task {task}')
            return False
        opened_tasks.add(task)

        if task not in tasks_objects:
            tasks_objects[task] = Task(task)

        obj = tasks_objects[task]

        if not obj.success:
            remote_path = os.path.join(path, Task.PATH, task)
            if not (ssh_file_exists(os.path.join(remote_path, Task.SUCCESS_FILE)) \
                    and rsync(remote_path, Task.PATH)):
                #failed to synchronize, trying with deps
                for dep in obj.deps:
                    if not rsync_task(dep):
                        done_tasks[task] = False
                        return False

        done_tasks[task] = True
        return True
    
    for task in tasks:
        if rsync_task(task):
            logging.info(f'Task {task} successfully completed')
        else: logging.error(f'Task {task} failed')

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Transfers minimal subset of tasks required to compute selected tasks')

    parser.add_argument('direction', choices=['to', 'from'], help='Direction of the synchronization')
    parser.add_argument('path', help='host:path_to_repository')
    parser.add_argument('tasks', nargs='+', help='The name of the tasks to run')
    args = parser.parse_args()
    if args.direction == 'to':
        rsync_tasks_to(**vars(args))
    elif args.direction == 'from':
        rsync_tasks_from(**vars(args))
    else: raise ValueError('Invalid value for direction')
