# Project Planning

Given a list of tasks, interdependencies between them, effort estimates and resources to complete them, create a project plan. Internally formulates this as a scheduling problem to solve the optimisation.

## Solvers

### Constraint programming solver
Model this as a constraint programming problem and solved using google or tools library.

__Objective__: To minimise the total time taken to fulfil all tasks. Currently we are weighing all tasks equally. 

__Decision variables__:
1. Start time of tasks
2. Resource assigned for each task

__Constraints__: 
1. All task dependencies modelled as precendence constraints i.e. end time of task1 <= start time of task2
2. For a resource, no overlap constraint i.e. a resource can only work on one task at a time
2. For all resources which can do a particular task, only one no overlap constraint is enforced per task, dependent on if that resource is assigned for that task

## Planned features

1. UI to add data
2. Additional constraints
    1. Limited availability of certain resources at certain times
3. Additional objectives
    1. Fulfilling higher weighted tasks first
    2. Most task weight fulfilled by a certain time
4. Standalone application / web application
