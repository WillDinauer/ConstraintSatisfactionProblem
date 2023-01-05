# Written by William Dinauer
# CS74 Fall 2022

class MapProblem:

    def __init__(self, graph, domain_values):
        self.graph = graph
        self.domain_values = domain_values

    def initialize_domains(self):
        # Every domain starts with the same domain values
        domains = {}
        for var in self.graph.keys():
            domains[var] = set(self.domain_values)
        return domains

    # Returns True or False depending on if we are constrained or not
    def constrained(self, var, val, adj, domains):
        # As long as there is a valid value for the adjacent variables, we are good to go
        for adj_val in domains[adj]:
            if adj_val != val:
                return True
        return False

    # Updates the domains such that illegal values are removed from the domain
    def update_domains(self, var, asgnmnt, domains):
        # If an adjacent variable has a color that matches the assignment of our variable, remove
        # that color from their domain
        for adj in self.graph[var]:
            remove = []
            for color in domains[adj]:
                if color == asgnmnt[var]:
                    remove.append(color)
                    break
            for color in remove:
                domains[adj].remove(color)
        return domains

    # Returns the overlap with the adjacent variable
    def numeric_overlap(self, var, adj, asgnmnt, domains):
        # if assigning var to its value constrains the adjacent variable, return -1
        if asgnmnt[var] in domains[adj]:
            return -1
        return 0

