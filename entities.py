# define entities to be used

import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import plotly.express as px
import pandas as pd


class Resource:
    def __init__(self, name: str, type: str) -> None:
        self.name = name
        self.type = type


class Task:
    def __init__(self, name: str, duration: int, type: str, min_start: int, initiative: str = None) -> None:
        self.name = name
        self.duration = duration
        self.type = type
        self.min_start = min_start
        self.start: int = None
        self.resource: Resource = None
        if initiative is None:
            self.initiative = name
        else:
            self.initiative = initiative


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

    def visualize_graph(self) -> None:
        nx.draw_networkx(self.graph)
        plt.show()

    def schedule_tasks(self, scheduled_tasks: dict) -> None:
        for tn in self.tasks:
            tn.start = scheduled_tasks[tn.name].start
            tn.resource = scheduled_tasks[tn.name].resource

    def visualise_gantt(self, start_date: str, by: str = "initiative_resource") -> None:
        tasks_df = self._scheduled_tasks_to_df(start_date)
        # print(tasks_df)
        if by == "initiative_resource":
            fig = px.timeline(tasks_df, x_start="start", x_end="finish",
                              y="y", color="resource_type", text="task")
        elif by == "resource":
            fig = px.timeline(tasks_df, x_start="start", x_end="finish",
                              y="resource", color="initiative", text="task")
        else:
            raise Exception(
                "by cannot take values other than 'initiative_resource' or 'resource'")

        fig.update_yaxes(categoryorder='category ascending',
                         autorange='reversed')
        fig.show()

    def _scheduled_tasks_to_df(self, start_date: str) -> pd.DataFrame:
        rows = []
        for t in self.tasks:
            start_dt = pd.Timestamp(start_date) + pd.Timedelta(days=7*t.start)
            end_dt = pd.Timestamp(start_date) + \
                pd.Timedelta(days=7*(t.start + t.duration))
            rows.append(dict(task=t.name, start=start_dt, finish=end_dt,
                             resource=t.resource.name, resource_type=t.resource.type, initiative=t.initiative, y=f"{t.initiative} - {t.resource.name}"))
        df = pd.DataFrame(rows).sort_values(by="y").reset_index(drop=True)
        return df
