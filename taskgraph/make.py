#!/usr/bin/env python3
import os
import argparse
import json

from .task import Task

gitignore = """
*
!*.py
!*.ipynb
!*.sh
!task.json
!.gitignore
*_output.ipynb
"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Create task with given name')
    parser.add_argument('task', help='The name of the task to create')
    args = parser.parse_args()

    path = Task.get_path(args.task)
    os.makedirs(path)

    obj = {
        'description': '',
        'depends': [],
        'commands': []
    }

    with open(os.path.join(path, Task.CONFIG_FILE), 'w') as f:
        json.dump(obj, f, indent=4)

    with open(os.path.join(path, '.gitignore'), 'w') as f:
        f.write(gitignore)