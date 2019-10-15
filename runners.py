import os
import importlib

class Bash:
    def match(self, cmd):
        return True

    def run(self, cmd):
        return os.system(cmd) == 0

class Python:
    def match(self, cmd):
        parts = cmd.split()
        return len(parts) > 0 and parts[0].endswith('.py')
    
    def run(self, cmd):
        return Bash().run('python ' + cmd)

class Notebook:
    def __init__(self):
        global nbconvert, nbformat
        nbconvert = importlib.import_module('nbconvert')
        nbformat = importlib.import_module('nbformat')

    def match(self, cmd):
        return cmd.endswith('.ipynb')

    def run(self, cmd):
        with open(cmd) as f:
            nb = nbformat.read(f, as_version=4)
        ep = nbconvert.preprocessors.ExecutePreprocessor()
        ok = True
        try:
            ep.preprocess(nb)
        except nbconvert.CellExecutionError:
            ok = False
        with open(cmd, 'w') as f:
            nbformat.write(nb, f)
        return ok
