import os
import fnmatch
import sys
import argparse

from .task import Task

def _is_task_dir(dir_path):
    return os.path.exists(os.path.join(dir_path, Task.CONFIG_FILE))

filter_tasks = fnmatch.filter

def list_tasks(patterns=[]):
    tasks_path = Task.PATH
    results = []

    def _scan_for_tasks(path):
        with os.scandir(os.path.join(tasks_path, path)) as it:
            for entry in it:
                if entry.is_dir():
                    relative_path = os.path.join(path, entry.name)
                    if _is_task_dir(entry.path):
                        results.append(relative_path)
                    else:
                        _scan_for_tasks(relative_path)

    _scan_for_tasks('')
    if type(patterns) == str:
        patterns = [patterns]
    results = sum((filter_tasks(results, p) for p in patterns), [])
    results = list(set(results))
    return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser('List all tasks in lexicographic order')
    parser.add_argument('patterns', nargs='*', help='Patterns to filter results (eg. task_group/*, *_task_suffix)')
    args = parser.parse_args()
    if args.patterns == []:
        args.patterns = '*'
    tasks = list_tasks(**vars(args))
    print('\n'.join(sorted(tasks)))