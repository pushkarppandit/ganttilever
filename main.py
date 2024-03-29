from projectplanner.entities import *
from projectplanner.solvers import ORToolsScheduler
import pandas as pd
# from projectplanner import *



def create_project_from_files(task_csv_path: str, resource_csv_path: str, dependency_csv_path: str) -> Project:
    task_df = pd.read_csv(task_csv_path)
    resource_df = pd.read_csv(resource_csv_path)
    dependency_df = pd.read_csv(dependency_csv_path)
    return create_project_from_df(task_df=task_df, resource_df=resource_df, dependency_df=dependency_df)

def create_project_manually() -> Project:
    t1 = Task("task_1.1", 2, "dev", 0, "one")
    t2 = Task("task_1.2", 3, "dev", 0, "one")
    t3 = Task("task_1.3", 2, "QA", 0, "one")
    t4 = Task("task_1.4", 4, "dev", 0, "one")
    t5 = Task("task_1.5", 2, "QA", 0, "one")

    t6 = Task("task_2.1", 3, "dev", 0, "two")
    t7 = Task("task_2.2", 1, "dev", 0, "two")
    t8 = Task("task_2.3", 1, "QA", 0, "two")
    t9 = Task("task_2.4", 2, "dev", 0, "two")
    t10 = Task("task_2.5", 1, "QA", 0, "two")

    d1 = Resource("dev1", "dev")
    d2 = Resource("dev2", "dev")
    q1 = Resource("QA1", "QA")

    p = Project([t1, t2, t3, t4, t5, t6, t7, t8, t9, t10], [d1, d2, q1])
    p.add_dependency(t1, t3)
    p.add_dependency(t2, t3)
    p.add_dependency(t3, t4)
    p.add_dependency(t4, t5)

    p.add_dependency(t6, t8)
    p.add_dependency(t7, t8)
    p.add_dependency(t3, t9)
    p.add_dependency(t8, t9)
    p.add_dependency(t9, t10)
    return p
    



if __name__ == "__main__":
    # p = create_project_manually()
    p = create_project_from_files("sample_projects/project_1/tasks.csv","sample_projects/project_1/resources.csv","sample_projects/project_1/dependencies.csv")

    o = ORToolsScheduler()
    scheduled_tasks = o.solve(p)
    p.schedule_tasks(scheduled_tasks)
    p.visualise_gantt("2023-01-01", "resource")
    p.visualize_graph()