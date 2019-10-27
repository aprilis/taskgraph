import subprocess
import os
import importlib
import logging
import sys

try:
    import papermill as pm
    has_jupyter = True
except ImportError:
    has_jupyter = False

class Bash:
    def match(self, cmd):
        return True

    def run(self, cmd, env, path):
        new_env = dict(os.environ)
        new_env.update(env)
        result = subprocess.run(cmd, shell=True, env=new_env, cwd=path)
        return result.returncode == 0

class Python:
    def match(self, cmd):
        parts = cmd.split()
        return len(parts) > 0 and parts[0].endswith('.py')
    
    def run(self, cmd, env, path):
        return Bash().run('python ' + cmd, env, path)

class Notebook:
    def match(self, cmd):
        return cmd.endswith('.ipynb')

    def run(self, cmd, env, path):
        if not has_jupyter:
            logging.error('Papermill is not installed')
            return False
        notebook_path = os.path.join(path, cmd)
        ok = True
        parameters = env
        parameters['cli'] = True
        try:
            pm.execute_notebook(notebook_path,
                                notebook_path.replace('.ipynb', '_output.ipynb'),
                                cwd=path,
                                parameters=parameters,
                                timeout=None,
                                stdout_file=sys.stdout
                                stderr_file=sys.stderr
                                )
        except pm.exceptions.PapermillExecutionError as e:
            logging.error(str(e))
            ok = False
        return ok
