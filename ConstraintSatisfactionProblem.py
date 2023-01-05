# Written by William Dinauer
# CS74 Fall 2022

import random
import time
import copy

from MapProblem import MapProblem
from CircuitProblem import CircuitProblem


class ConstraintSatisfactionProblem:
    def __init__(self, csp, heuristic=None, lcv=False, inference=False):
        self.heuristic = heuristic
        self.lcv = lcv
        self.inference = inference
        self.csp = csp
        self.graph = csp.graph

    # Initialize the domains and begin the backtracking search
    def backtracking_search(self):
        domains = self.csp.initialize_domains()
        return self.recursive_backtracking({}, domains)

    # Follows the pseudocode from the book/slides
    def recursive_backtracking(self, asgnmnt, domains):
        # if our assignment is complete, return it
        if len(asgnmnt) == len(self.graph):
            return asgnmnt
        # Select an unassigned variable
        var = self.select_unassigned_variable(asgnmnt, domains)
        # Try every domain value for the chosen variable
        for value in self.order_domain_values(var, asgnmnt, domains):
            asgnmnt[var] = value
            # Update the domain given the new assignment
            new_domain = self.csp.update_domains(var, asgnmnt, copy.deepcopy(domains))
            # Check for consistency
            if self.consistent(asgnmnt, new_domain):
                result = self.recursive_backtracking(asgnmnt, new_domain)
                if result is not False:
                    return result
            # Failed for this assignment - backtrack
            asgnmnt.pop(var)
        return False

    # Check if the assignment is consistent based on the domains (and potentially Arc-3)
    def consistent(self, asgnmnt, domains):
        # Arc-3 algorithm
        if self.inference:
            # Initialize the queue
            queue = []
            for start in self.graph.keys():
                for end in self.graph[start]:
                    queue.append([start, end])

            # Perform Arc-3 until the queue is empty
            while len(queue) > 0:
                x, y = queue.pop(0)
                if self.remove_inconsistent_values(x, y, domains):
                    for adj in self.graph[x]:
                        queue.append([adj, x])

            # If any variables have an empty domain, return False
            for var in domains:
                if len(domains[var]) == 0:
                    return False
            return True

        # Arc-3 not enforced:
        # Check if any variables have an empty domain
        for var in domains:
            if len(domains[var]) == 0:
                return False
        # For every assigned variable, check that adjacent variables still have a valid value
        for var in asgnmnt.keys():
            val = asgnmnt[var]
            for adj in self.graph[var]:
                if not self.csp.constrained(var, val, adj, domains):
                    return False
            return True

    # Helper function for Arc-3, based on pseudocode from book and slides
    def remove_inconsistent_values(self, x, y, domains):
        removed = False
        marked = []
        for val in domains[x]:
            satisfied = self.csp.constrained(x, val, y, domains)
            if not satisfied:
                marked.append(val)
                removed = True
        for val in marked:
            domains[x].remove(val)
        return removed

    # Order the domain values based on LCV
    def order_domain_values(self, var, asgnmnt, domains):
        # Least Constraining Value Heuristic
        if self.lcv:
            # Initialize dict mapping values to level of constraint
            val_to_cst = {}

            # Current constraint with no value selected for var
            current_constraint = 0
            for adj in self.graph[var]:
                if adj not in asgnmnt:
                    current_constraint += len(domains[adj])

            # Initialize mapping in case domain values are not a single integer
            num_to_domain_val = {}
            num = 0
            # Try every legal value and store the difference in the constraint
            for val in domains[var]:
                new_constraint = 0
                asgnmnt[var] = val
                num_to_domain_val[num] = val
                for adj in self.graph[var]:
                    if adj not in asgnmnt:
                        # Add the length of the domain for adjacent variables
                        new_constraint += len(domains[adj])
                        # Subtract any overlap
                        new_constraint += self.csp.numeric_overlap(var, adj, asgnmnt, domains)
                asgnmnt.pop(var)
                val_to_cst[num] = current_constraint-new_constraint
                num += 1

            # Sort the dictionary by item value
            sort = sorted(val_to_cst.items(), key=lambda x: x[1])
            # We return a list of the values
            ret = []
            for pair in sort:
                ret.append(num_to_domain_val[pair[0]])
            return ret
        return domains[var]

    def select_unassigned_variable(self, asgnmnt, domains):
        variables = list(self.graph.keys())
        random.seed(time.time())
        random.shuffle(variables)

        # Minimum Remaining Value Heuristic
        if self.heuristic == "MRV":
            min_val = len(self.csp.domain_values) + 1
            chosen_var = None
            # Loop over every unassigned variable
            for var in variables:
                if var not in asgnmnt.keys():
                    # Get the number of legal values for the variable
                    num_values = len(domains[var])
                    # If we have a minimum, select it as the variable to be chosen
                    if num_values < min_val:
                        min_val = num_values
                        chosen_var = var
            return chosen_var

        # Degree Heuristic
        elif self.heuristic == "Degree":
            # First, use MRV to find all the minimum variables
            min_val = len(self.csp.domain_values) + 1
            min_variables = []
            # Loop over every unassigned variable
            for var in variables:
                if var not in asgnmnt.keys():
                    # Get the number of legal values for the variable
                    num_values = len(domains[var])
                    # If we have a minimum, select it as the variable to be chosen
                    if num_values < min_val:
                        min_val = num_values
                        min_variables = [var]
                    elif num_values == min_val:
                        min_variables.append(var)

            # Then, compare based on their degree
            max_degree = -1
            chosen_var = None
            # Loop over every minimum variable
            for var in min_variables:
                # Get its degree
                degree = self.degree(var, asgnmnt)
                # If greater than the maximum degree, it's currently selected
                if degree > max_degree:
                    max_degree = degree
                    chosen_var = var
            return chosen_var

        # No heuristic - simply random choice
        else:
            for var in variables:
                if var not in asgnmnt.keys():
                    return var
            return None

    # Simple degree function
    def degree(self, var, asgnmnt):
        deg = 0
        for adj in self.graph[var]:
            if adj not in asgnmnt:
                deg += 1
        return deg

# Tests are run here
if __name__ == "__main__":
    # Setup for Map Problem
    map_graph = {0: {1, 2, 3, 4, 5},
             1: {0, 2},
             2: {0, 1, 3},
             3: {0, 2, 4},
             4: {0, 3, 5},
             5: {0, 4},
             6: {}}
    map_values = [0, 1, 2]
    map_problem = MapProblem(map_graph, map_values)

    # Setup for Circuit Problem
    circuit_variables = [['aaa', 'aaa'], ['bbbbb', 'bbbbb'], ['cc', 'cc', 'cc'], ['eeeeeee']]
    circuit_problem = CircuitProblem(3, 10, circuit_variables)

    # Setting our CSP. Only one should be uncommented
    # ----------------------------------------------------------------
    # csp = ConstraintSatisfactionProblem(map_problem, "Degree", True, True)
    csp = ConstraintSatisfactionProblem(circuit_problem, "Degree", True, True)

    # This is always uncommented - run the backtracking search
    # ----------------------------------------------------------------
    assignment = csp.backtracking_search()
    print(assignment)

    # For the circuit problem, print it as a grid
    # ----------------------------------------------------------------
    circuit_problem.print_grid_format(assignment)
