#!/usr/bin/env python3

import argparse
import logging
from collections import defaultdict
import subprocess
import os
from string import Template
import shlex

from .task import Task
from .list import list_tasks
from .util import shell

SEND_COMMAND = 'tar -c {} | lz4 -v'
RECEIVE_COMMAND = 'lz4 -d | tar -x'
REMOTE_COMMAND = 'ssh -q {} {}'
FILE_EXISTS_COMMAND = '[[ -f {} ]] && return 0 || return 1'

logging.basicConfig(format='TaskGraph (%(asctime)s): %(message)s',
		    datefmt='%H:%M:%S',
		    level=logging.INFO)

def ssh_path_split(path):
    return path.split(':', maxsplit=1)

def make_command(pattern, *args):
    return pattern.format(*map(shlex.quote, args))

def make_remote(command, host_path):
    host, path = ssh_path_split(host_path)
    command = make_command('cd {}; ', path) + command
    return make_command(REMOTE_COMMAND, host, command)

def remote_file_exists(file, host_path):
    command = make_command(FILE_EXISTS_COMMAND, file)
    command = make_remote(command, host_path)
    return shell(command, mode='exit_success')

def sync(task_path, host_path, direction):
    send_command = make_command(SEND_COMMAND, task_path)
    receive_command = RECEIVE_COMMAND
    if direction == 'to':
        receive_command = make_remote(receive_command, host_path)
    else:
        send_command = make_remote(send_command, host_path)
    command = send_command  + ' | ' + receive_command
    logging.info('running %s', command)
    return shell(command, mode='exit_success')

def sync_tasks_to(path, tasks, **kwargs):
    tasks = list_tasks(tasks)
    opened_tasks = set()
    done_tasks = dict()
    tasks_objects = dict()

    def sync_task(task):
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
                if not sync_task(dep):
                    done_tasks[task] = False
                    return False
        elif not sync(obj.repo_path, path, 'to'):
            done_tasks[task] = False
            return False

        done_tasks[task] = True
        return True
    
    for task in tasks:
        if sync_task(task):
            logging.info(f'Task {task} successfully completed')
        else: logging.error(f'Task {task} failed')


def sync_tasks_from(path, tasks, **kwargs):
    tasks = list_tasks(tasks)
    opened_tasks = set()
    done_tasks = dict()
    tasks_objects = dict()

    def sync_task(task):
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
            task_path = obj.repo_path
            if not (remote_file_exists(os.path.join(task_path, Task.SUCCESS_FILE), path) \
                    and sync(task_path, path, 'from')):
                #failed to synchronize, trying with deps
                for dep in obj.deps:
                    if not sync_task(dep):
                        done_tasks[task] = False
                        return False

        done_tasks[task] = True
        return True
    
    for task in tasks:
        if sync_task(task):
            logging.info(f'Task {task} successfully completed')
        else: logging.error(f'Task {task} failed')

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Transfers minimal subset of tasks required to compute selected tasks')

    parser.add_argument('direction', choices=['to', 'from'], help='Direction of the synchronization')
    parser.add_argument('path', help='host:path_to_repository')
    parser.add_argument('tasks', nargs='+', help='The name of the tasks to run')
    args = parser.parse_args()
    if args.direction == 'to':
        sync_tasks_to(**vars(args))
    elif args.direction == 'from':
        sync_tasks_from(**vars(args))
    else: raise ValueError('Invalid value for direction')
