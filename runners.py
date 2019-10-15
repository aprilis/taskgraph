import os

class Bash:
    def match(self, cmd):
        return True

    def run(self, cmd):
        return os.system(cmd) == 0

class Python:
    def match(self, cmd):
        return cmd.split()[0].endswith('.py')
    
    def run(self, cmd):
        return Bash().run('python ' + cmd)