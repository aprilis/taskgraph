import shutil
import os
import argparse

from .util import shell
from .task import Task

def duplicate(source, destination, copy_mode, overwrite):
    src = Task.get_path(source)
    dst = Task.get_path(destination)

    if copy_mode == 'all':
        if overwrite and os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
    elif copy_mode in ('git-tracked', 'git-commited'):
        os.makedirs(dst, exist_ok=overwrite)
        if copy_mode == 'git-tracked':
            command = 'git ls-files'
        else:
            command = 'git ls-tree -r HEAD --name-only'
        files = shell(command, cwd=src, mode='stdout').split()
        for f in files:
            f_src = os.path.join(src, f)
            f_dst = os.path.join(dst, f)
            os.makedirs(os.path.dirname(f_dst), exist_ok=True)
            shutil.copy2(f_src, f_dst)
    else: raise ValueError('Invalid copy mode')

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Duplicates specified task')

    parser.add_argument('source', help='Name of the task to duplicate')
    parser.add_argument('destination',  help='Name of the copy')
    parser.add_argument('--copy_mode', '-c', choices=['all', 'git-tracked', 'git-commited'],
        default='git-tracked',
        help='''How to copy tasks: 
        all - copies all files,
        git-tracked (default) - copies all files according to .gitignore rules,
        git-commited - copies all files in HEAD''')
    parser.add_argument('--overwrite', '-o', action='store_true', 
        help='Allow script to overwrite existing tasks')
    args = parser.parse_args()
    duplicate(**vars(args))
