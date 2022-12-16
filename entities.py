# define entities to be used

import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict


class Task:
    def __init__(self, name: str, duration: int, type: str, min_start) -> None:
        self.name = name
        self.duration = duration
        self.type = type
        self.min_start = min_start
        self.start: int = None
        self.resource: str = None


class Resource:
    def __init__(self, name: str, type: str) -> None:
        self.name = name
        self.type = type


class Project:
    def __init__(self, tasks: list, resources: list) -> None:
        self.tasks = []
        self.task_names = []
        self.graph = nx.DiGraph()
        for task in tasks:
            self.add_task(task)

        self.resources = defaultdict(list)
        self._organize_resources(resources)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)
        self.task_names.append(task.name)
        self.graph.add_node(task.name, duration=task.duration)

    def add_dependency(self, task1, task2: Task) -> None:
        if task1.name not in self.task_names:
            raise Exception(f"task {task1.name} not present in project")
        elif task2.name not in self.task_names:
            raise Exception(f"task {task2.name} not present in project")
        else:
            self.graph.add_edge(task1.name, task2.name)

    def _organize_resources(self, resources: list) -> None:
        for r in resources:
            self.resources[r.type].append(r)

    def visualize(self) -> None:
        nx.draw_networkx(self.graph)
        plt.show()
