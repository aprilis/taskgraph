import argparse
import logging
import os

from .task import Task
from .fix_notebooks import fix_notebook

logging.basicConfig(format='TaskGraph (%(asctime)s): %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO)

empty_notebook = """
{
    "cells": [],
    "metadata": {},
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        }
    }
}
"""

def make_notebook(task_name, notebook_name, command=False):
    t = Task(task_name)
    notebook_path = os.path.join(t.path, notebook_name)

    with open(notebook_path, 'w') as f:
        f.write(empty_notebook)

    params = { k: os.path.relpath(v, t.path) for k, v in t.mapping.items() }
    params['cli'] = False

    fix_notebook(notebook_path, params)

    if command:
        t.commands.append(notebook_name)
        t.save_config()

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Create a jupyter notebook with a cell with parameters')
    parser.add_argument('task_name', type=str, help='The task name')
    parser.add_argument('notebook_name', type=str, 
        help='The notebook name (or path relative to the task path)')
    parser.add_argument('--command', '-c', default=False, action='store_true',
        help='Add new notebook to command list')
    args = parser.parse_args()
    make_notebook(**vars(args))