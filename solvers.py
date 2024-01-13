# Define solver implementations for job shop scheduling

import collections
from ortools.sat.python import cp_model
from entities import *
import abc


class Scheduler(metaclass=abc.ABCMeta):
    """
    Base class to define basic interface for solver of scheduling problem
    """
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'solve') and
                callable(subclass.solve) or
                NotImplemented)

    @abc.abstractmethod
    def solve(self, project: Project) -> dict:
        """solve the scheduling problem"""
        raise NotImplementedError


class ORToolsScheduler(Scheduler):
    """
    Concrete scheduler class using or tools constraint programming to solve scheduling problem
    """

    def solve(self, project: Project) -> dict:
        model = cp_model.CpModel()
        horizon = 0
        for t in project.tasks:
            horizon += t.duration

        # Global storage of variables.
        intervals_per_resources = collections.defaultdict(list)
        starts = {}  # indexed by (task.name).
        ends = {}  # indexed by (task.name).
        presences = {}  # indexed by (task.name, resource.name).

        for task in project.tasks:

             # Create main interval for the task.
            suffix_name = f"_{task.name}"
            start = model.NewIntVar(
                task.min_start, horizon, 'start' + suffix_name)
            end = model.NewIntVar(task.min_start, horizon, 'end' + suffix_name)
            interval = model.NewIntervalVar(start, task.duration, end,
                                            'interval' + suffix_name)

            # Store the start for the solution.
            starts[task.name] = start
            ends[task.name] = end

            if len(project.resources[task.type]) > 1:
                l_presences = []
                for r in project.resources[task.type]:
                    alt_suffix = f"_{task.name}_{r.name}"
                    l_presence = model.NewBoolVar('presence' + alt_suffix)
                    l_start = model.NewIntVar(
                        task.min_start, horizon, 'start' + alt_suffix)
                    l_end = model.NewIntVar(
                        task.min_start, horizon, 'end' + alt_suffix)
                    l_interval = model.NewOptionalIntervalVar(
                        l_start, task.duration, l_end, l_presence,
                        'interval' + alt_suffix)
                    l_presences.append(l_presence)

                    # Link the master variables with the local ones.
                    model.Add(start == l_start).OnlyEnforceIf(l_presence)
                    model.Add(end == l_end).OnlyEnforceIf(l_presence)

                    # Add the local interval to the right machine.
                    intervals_per_resources[r.name].append(l_interval)

                    # Store the presences for the solution.
                    presences[(task.name, r.name)] = l_presence

                # Select exactly one presence variable.
                model.AddExactlyOne(l_presences)
            else:
                r = project.resources[task.type][0]
                intervals_per_resources[r.name].append(interval)
                presences[(task.name, r.name)] = model.NewConstant(1)

        # precedence constraints because of dependencies
        for d in project.graph.edges:
            model.Add(starts[d[1]] >= ends[d[0]])

        # Create resources constraints.
        for _, res in project.resources.items():
            for r in res:
                intervals = intervals_per_resources[r.name]
                if len(intervals) > 1:
                    model.AddNoOverlap(intervals)

        # Makespan objective
        makespan = model.NewIntVar(0, horizon, 'makespan')
        model.AddMaxEquality(makespan, ends.values())
        model.Minimize(makespan)

        # Solve model.
        solver = cp_model.CpSolver()
        solution_printer = SolutionPrinter()
        status = solver.Solve(model, solution_printer)

        output = {}  # indexed on task.name, value is task with updated start and resource

        # Print final solution.
        for task in project.tasks:
            print(f"Task {task.name}:")
            start_value = solver.Value(starts[task.name])
            resource = -1
            for r in project.resources[task.type]:
                if solver.Value(presences[(task.name, r.name)]):
                    resource = r
            print(
                f"  task {task.name} starts at {start_value} on resource {resource.name}"
            )
            task.start = start_value
            task.resource = resource
            output[task.name] = task

        print('Solve status: %s' % solver.StatusName(status))
        print('Optimal objective value: %i' % solver.ObjectiveValue())
        print('Statistics')
        print('  - conflicts : %i' % solver.NumConflicts())
        print('  - branches  : %i' % solver.NumBranches())
        print('  - wall time : %f s' % solver.WallTime())

        return output


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__solution_count = 0

    def on_solution_callback(self):
        """Called at each new solution."""
        print('Solution %i, time = %f s, objective = %i' %
              (self.__solution_count, self.WallTime(), self.ObjectiveValue()))
        self.__solution_count += 1
