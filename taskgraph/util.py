import subprocess
import os
import sys
import logging

def shell(command, cwd='.'):
    result = subprocess.run(command, shell=True, cwd=os.path.abspath(cwd), text=True,
        stdout=subprocess.PIPE, stderr=sys.stderr)
    if result.returncode != 0:
        raise RuntimeError(f'Command {command} exited with non-zero exit code: {result.returncode}')
    return result.stdout

def config_logging():
    logging.basicConfig(format='TaskGraph (%(asctime)s): %(message)s',
		    datefmt='%H:%M:%S',
		    level=logging.INFO)
    return logging.getLogger()