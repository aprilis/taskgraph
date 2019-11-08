import argparse
import nbformat
import logging
import glob
import os

from .list import list_tasks
from .task import Task

logging.basicConfig(format='TaskGraph (%(asctime)s): %(message)s',
		    datefmt='%H:%M:%S',
		    level=logging.INFO)

def fix_notebook(path, params):
    notebook = nbformat.read(path, as_version=4)
    for i, c in enumerate(notebook.cells):
        if 'metadata' in c and 'tags' in c['metadata'] and 'parameters' in c['metadata']['tags']:
            break
    else:
        i = 0
        notebook.cells.insert(0, None)
    
    source = ['#parameters (generated automatically)']
    for k, v in params.items():
        source.append(f'{k} = {repr(v)}')

    notebook.cells[i] = nbformat.v4.new_code_cell(
        metadata={'tags': ['parameters']},
        source='\n'.join(source))

    nbformat.write(notebook, path)

def fix_notebooks(tasks):
    tasks = list_tasks(tasks)
    for t in tasks:
        path = Task.get_path(t)
        params = { k: os.path.relpath(v, path) for k, v in Task(t).mapping.items() }
        params['cli'] = False
        notebooks = glob.glob(os.path.join(path, '**.ipynb'), recursive=True)
        for n in notebooks:
            logging.info(f'Fixing notebook {n}')
            fix_notebook(n, params)

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Fix jupyter notebooks by injecting a cell with parameters')
    parser.add_argument('tasks', nargs='+', help='Tasks to look for notebooks')
    args = parser.parse_args()
    fix_notebooks(**vars(args))