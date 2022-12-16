from entities import *
from solvers import ORToolsScheduler


t1 = Task("t1", 2, "dev", 0)
t2 = Task("t2", 4, "dev", 0)
t3 = Task("t3", 3, "QA", 0)
t4 = Task("t4", 3, "dev", 0)
t5 = Task("t5", 1, "QA", 0)

r1 = Resource("dev1", "dev")
r2 = Resource("dev2", "dev")
r3 = Resource("QA1", "QA")

p = Project([t1, t2, t3, t4, t5], [r1, r2, r3])
p.add_dependency(t1, t2)
p.add_dependency(t3, t2)
p.add_dependency(t4, t5)

# p.visualize()

o = ORToolsScheduler()
o.solve(p)
