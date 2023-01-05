# Written by William Dinauer
# CS74 Fall 2022

from ConstraintSatisfactionProblem.ConstraintSatisfactionProblem import ConstraintSatisfactionProblem
from ConstraintSatisfactionProblem.MapProblem import MapProblem

# Creating Graph for USA Map
with open('USA_Map.txt', 'r') as f:

    num = {}
    count = 0

    graph = {}

    for line in f:
        state = line[0]
        state += line[1]
        num[state] = count
        graph[count] = set()
        count += 1

    f.seek(0)

    for line in f:
        pos = 3
        state = line[0]
        state += line[1]
        n = num[state]

        while pos < len(line):
            adj = line[pos]
            adj += line[pos+1]
            n_adj = num[adj]
            graph[n].add(n_adj)
            pos += 3

# Testing USA Map
map_values = [0, 1, 2, 3]
map_problem = MapProblem(graph, map_values)

csp = ConstraintSatisfactionProblem(map_problem, "Degree", True, True)

assignment = csp.backtracking_search()
print(assignment)
