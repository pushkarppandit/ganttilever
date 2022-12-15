from entities import *


t1 = Task("t1", 2)
t2 = Task("t2", 4)
t3 = Task("t3", 1)

p = Project([t1, t2, t3], 2)
p.add_dependency(t1, t2)
p.add_dependency(t3, t2)

p.visualize()
