import subprocess
import os
import importlib
import logging

try:
    import nbconvert
    import nbformat
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
            logging.error('Jupyter nbconvert is not installed')
            return False
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
        except nbconvert.preprocessors.CellExecutionError as e:
            logging.error(str(e))
            ok = False
        with open(cmd, 'w') as f:
            nbformat.write(nb, f)
        return ok
