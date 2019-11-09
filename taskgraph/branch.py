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
from . import util
from .duplicate import duplicate

util.config_logging()

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
        
        logging.info(f'Branching task {t} to {b}')
        duplicate(t, b, copy_mode, overwrite)
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
