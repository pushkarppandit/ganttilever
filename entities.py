# define entities to be used

from random import randint
import networkx as nx
import matplotlib.pyplot as plt


class Task:
    def __init__(self, name: str, effort: int) -> None:
        self.name = name
        self.effort = effort


class Project:
    def __init__(self, tasks: list, resources: int) -> None:
        self.tasks = []
        self.task_names = []
        self.graph = nx.DiGraph()
        for task in tasks:
            self.add_task(task)

        self.resources = resources

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)
        self.task_names.append(task.name)
        self.graph.add_node(task.name, effort=task.effort)

    def add_dependency(self, task1, task2: Task) -> None:
        if task1.name not in self.task_names:
            raise Exception(f"task {task1.name} not present in project")
        elif task2.name not in self.task_names:
            raise Exception(f"task {task2.name} not present in project")
        else:
            self.graph.add_edge(task1.name, task2.name)

    def visualize(self) -> None:
        nx.draw_networkx(self.graph)
        plt.show()
