#!/usr/bin/env python3

import argparse
import logging
from collections import defaultdict
import subprocess
import os
import shutil
from functools import reduce
import operator
import sys

from .task import Task
from .list import list_tasks

logging.basicConfig(format='TaskGraph (%(asctime)s): %(message)s',
		    datefmt='%H:%M:%S',
		    level=logging.INFO)

def shell(command, cwd='.'):
    result = subprocess.run(command, shell=True, cwd=os.path.abspath(cwd), text=True,
        stdout=subprocess.PIPE, stderr=sys.stderr)
    if result.returncode != 0:
        raise RuntimeError(f'Command {command} exited with non-zero exit code: {result.returncode}')
    return result.stdout

def branch(src, dst, mode, overwrite):
    if mode == 'all':
        shutil.copytree(src, dst, dirs_exist_ok=overwrite)
    elif mode in ('git-tracked', 'git-commited'):
        os.makedirs(dst, exist_ok=overwrite)
        if mode == 'git-tracked':
            command = 'git ls-files'
        else:
            command = 'git ls-tree -r HEAD --name-only'
        files = shell(command, cwd=src).split()
        for f in files:
            f_src = os.path.join(src, f)
            f_dst = os.path.join(dst, f)
            os.makedirs(os.path.dirname(f_dst), exist_ok=True)
            shutil.copy2(f_src, f_dst)
    else: raise ValueError('Invalid mode')

def visit_all(graph, start):
    visited = set()

    def dfs(v):
        if v in visited: return
        visited.add(v)
        for u in graph[v]:
            dfs(u)

    dfs(start)
    return visited

def branch_tasks(branched_task, targets, suffix, copy_mode, overwrite):
    targets = list_tasks(targets)
    tasks = {}
    for t in list_tasks():
        try:
            task = Task(t)
            tasks[task.name] = task
        except:
            pass
        
    graph = { t.name: t.deps for t in tasks.values() }
    rev_graph = defaultdict(list)
    for t in tasks.values():
        for d in t.deps:
            rev_graph[d].append(t.name)
    
    branched = visit_all(rev_graph, branched_task)
    if targets != []:
        targets_deps = reduce(operator.or_, (visit_all(graph, t) for t in targets))
        branched = branched & targets_deps
    for t in branched:
        b = t + suffix
        src = Task.get_path(t)
        dst = Task.get_path(b)
        
        logging.info(f'Branching task {t} to {b}')
        branch(src, dst, copy_mode, overwrite)
        task = Task(b)
        for d in list(task.deps):
            if d in branched:
                task.trainslate_dep(d, d + suffix)
        task.save_config()

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Branches a task and its dependants')

    parser.add_argument('branched_task', help='Name of the task to start branching from')
    parser.add_argument('targets', nargs='*', 
        help='The names (or patterns) of target tasks to be branched. Script will branch all tasks that depend on branched_task and that at least one of targets depends on (including themselves). If none specified all dependants of branched_task will be copied')
    parser.add_argument('--suffix', help='Suffix to be added to all branched tasks', required=True)
    parser.add_argument('--copy_mode', '-c', choices=['all', 'git-tracked', 'git-commited'],
        default='git-tracked',
        help='''How to copy tasks: 
        all - copies all files,
        git-tracked (default) - copies all files according to .gitignore rules,
        git-commited - copies all files in HEAD''')
    parser.add_argument('--overwrite', '-o', action='store_true', 
        help='Allow script to overwrite existing tasks')
    args = parser.parse_args()
    branch_tasks(**vars(args))
