# define entities to be used

import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import plotly.express as px
import pandas as pd


class Resource:
    """
    Class to model a resource.
    name: resource name
    type: type of resource. A task of this type will be fulfilled by this resource.
    """

    def __init__(self, name: str, type: str) -> None:
        self.name = name
        self.type = type


class Task:
    """
    Class to model a task
    name: task name
    duration_days: effort duration in days. Assumed to be constant and independent of specific resource
    type: type of task. A resource of this type can fulfil this task.
    min_start_days: The earliest time that this task can start, in days from start of project
    initiative: (Optional) The larger initiative the task is part of. If absent, the task name is taken to be the initiative name
    """

    def __init__(self, name: str, duration_days: int, type: str, min_start_days: int, initiative: str = None) -> None:
        self.name = name
        self.duration = duration_days
        self.type = type
        self.min_start = min_start_days
        self.start: int = None
        self.resource: Resource = None
        if initiative is None:
            self.initiative = name
        else:
            self.initiative = initiative


class Project:
    """
    Class to model a project. Consists of a number of tasks with their specifications and constraints, along with a 
    team of resources of different types. All resources of a particular type are assumed to be equally competent and
    will take the same amount of time to fulfil a particular task. Hence duration has been modelled as part of task 
    instead of per resource
    tasks: A list of task objects
    resources: A list of resource objects
    """

    def __init__(self, tasks: list, resources: list) -> None:
        self.tasks = []
        self.task_names = []
        self.graph = nx.DiGraph()
        for task in tasks:
            self.add_task(task)

        self.resources = defaultdict(list)
        self._organize_resources(resources)

    def add_task(self, task: Task) -> None:
        """
        method to add a task to a project
        """
        self.tasks.append(task)
        self.task_names.append(task.name)
        self.graph.add_node(task.name, duration=task.duration)

    def add_dependency(self, task1, task2: Task) -> None:
        """
        Method to add a dependency between tasks to a project. 
        The interpretation is that task2 is dependent on task1
        """
        if task1.name not in self.task_names:
            raise Exception(f"task {task1.name} not present in project")
        elif task2.name not in self.task_names:
            raise Exception(f"task {task2.name} not present in project")
        else:
            self.graph.add_edge(task1.name, task2.name)

    def _organize_resources(self, resources: list) -> None:
        """
        Create a dict[resource type] -> list of resources of that type from list of resources
        """
        for r in resources:
            self.resources[r.type].append(r)

    def visualize_graph(self) -> None:
        """
        Visualise tasks dependency as a graph
        """
        nx.draw_networkx(self.graph)
        plt.show()

    def schedule_tasks(self, scheduled_tasks: dict) -> None:
        """
        Given a list of tasks with schedule fields populated, update the tasks in the project based on that. 
        Assumed that the tasks in scheduled tasks are the same as those in the project
        """
        for tn in self.tasks:
            tn.start = scheduled_tasks[tn.name].start
            tn.resource = scheduled_tasks[tn.name].resource

    def visualise_gantt(self, start_date: str, by: str = "initiative_resource") -> None:
        """
        Visualise scheduled tasks as a gantt chart
        start_date: Since the entire calculation till now has been done in days starting from 0, start_date is the starting date corresopnding to 0. 
                    The gantt chart is plotted with this date as starting point
        by: How the rows of the gantt 
        """
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
        """
        Utility function to create a df from scheduled tasks to make plotting gantt easier
        """
        rows = []
        for t in self.tasks:
            start_dt = pd.Timestamp(start_date) + pd.Timedelta(days=7*t.start)
            end_dt = pd.Timestamp(start_date) + \
                pd.Timedelta(days=7*(t.start + t.duration))
            rows.append(dict(task=t.name, start=start_dt, finish=end_dt,
                             resource=t.resource.name, resource_type=t.resource.type, initiative=t.initiative, y=f"{t.initiative} - {t.resource.name}"))
        df = pd.DataFrame(rows).sort_values(by="y").reset_index(drop=True)
        return df


def create_project_from_df(task_df: pd.DataFrame, resource_df: pd.DataFrame, dependency_df: pd.DataFrame) -> Project:
    """
    Create a Project object from a task df, resource df and dependency df
    task_df: pandas DataFrame with task data. Expected to have columns - name: str, duration: int, type: str, min_start: int, initiative: str
    resource_df: pandas DataFrame with resource data. Expected to have columns -  name: str, type: str
    dependency_df: pandas DataFrame with dependency data. Expected to have columns - task1: str, tast2: str

    Returns a Project object
    """
    task_dict = {}
    for _, row in task_df.iterrows():
        task_dict[row.name] = Task(name=row.name, duration_days=row.duration,
                                   type=row.type, min_start_days=row.min_start, initiative=row.initiative)

    resource_list = []
    for _, row in resource_df.iterrows():
        resource_df.append(Resource(name=row.name, type=row.type))

    project = Project(tasks=list(task_dict.values()), resources=resource_list)
    for _, row in dependency_df.iterrows():
        project.add_dependency(task1=task_dict(
            row.task1), task2=task_dict(row.task2))

    return project
