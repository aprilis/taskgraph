from graphviz import Digraph
from .task import Task
from .list import list_tasks

def visualize_tasks(tasks):
    tasks = list_tasks(tasks)

    dot = Digraph()
    visited = set()

    def visualize_task(task):
        if task in visited:
            return
        visited.add(task)
        obj = Task(task)
        dot.node(task, task)

        for dep in obj.deps:
            visualize_task(dep)
            dot.edge(dep, task)
    
    for t in tasks:
        visualize_task(t)
    return dot