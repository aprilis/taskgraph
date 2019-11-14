import subprocess
import os
import sys
import logging

def shell(command, cwd='.', mode='exit_success'):
    result = subprocess.run(command, shell=True, cwd=os.path.abspath(cwd), text=True,
        stdout=subprocess.PIPE, stderr=sys.stderr)
    if mode == 'stdout':
        if result.returncode != 0:
            raise RuntimeError(f'Command {command} exited with non-zero exit code: {result.returncode}')
        return result.stdout
    elif mode == 'exit_success':
        return result.returncode == 0
    elif mode == 'exit_code':
        return result.returncode
    else:
        raise ValueError(f'Invalid mode: {mode}')

def config_logging():
    logging.basicConfig(format='TaskGraph (%(asctime)s): %(message)s',
		    datefmt='%H:%M:%S',
		    level=logging.INFO)
    return logging.getLogger()