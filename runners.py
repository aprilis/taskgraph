import subprocess
import os
import importlib

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
    def __init__(self):
        global nbconvert, nbformat
        nbconvert = importlib.import_module('nbconvert')
        nbformat = importlib.import_module('nbformat')

    def match(self, cmd):
        return cmd.endswith('.ipynb')

    def run(self, cmd, env, path):
        with open(os.path.join(path, cmd)) as f:
            nb = nbformat.read(f, as_version=4)
        ep = nbconvert.preprocessors.ExecutePreprocessor()
        ok = True
        try:
            ep.preprocess(nb, {
                'metadata': {
                    'path': path,
                    'kernelspec': { 'env': env }
                }})
        except nbconvert.CellExecutionError:
            ok = False
        with open(cmd, 'w') as f:
            nbformat.write(nb, f)
        return ok
