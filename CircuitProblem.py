# Written by William Dinauer
# CS74 Fall 2022

class CircuitProblem:

    def __init__(self, m, n, variables):
        self.m = m
        self.n = n
        self.variables = variables

        self.num_variables = len(variables)

        # build a dictionary to track how wide (x) and tall (y) each component is
        self.x = {}
        self.y = {}
        for var in range(self.num_variables):
            self.y[var] = len(variables[var])
            self.x[var] = len(variables[var][0])

        # initialize domain values and map grid numbers to x and y positions
        self.domain_values = []
        self.pos_to_xy = {}
        for r in range(m):
            for c in range(n):
                self.domain_values.append([r*n+c, 0])
                self.domain_values.append([r*n+c, 1])
                self.pos_to_xy[r*n+c] = [c, r]

        # create a graph (adjacency list representation) such that every variable is connected to every other
        self.graph = {}
        for var in range(self.num_variables):
            self.graph[var] = []
            for adj in range(self.num_variables):
                if adj != var:
                    self.graph[var].append(adj)

    # Create the initial domain for each variable, returned as a dictionary mapping variables to their domain
    def initialize_domains(self):
        domains = {}
        for var in range(self.num_variables):
            domains[var] = []
            # Try every domain position and rotation
            for pair in self.domain_values:
                val = pair[0]
                rotation = pair[1]
                x, y = self.pos_to_xy[val]
                # If valid, add this pair to the domain for the variable
                if rotation == 0 and x+self.x[var]-1 < self.n and y+self.y[var]-1 < self.m:
                    domains[var].append(pair)
                elif rotation == 1 and x+self.y[var]-1 < self.n and y+self.x[var]-1 < self.m:
                    domains[var].append(pair)
        return domains

    # Updates the domains based on the constraints
    def update_domains(self, var, asgnmnt, domains):
        pair = asgnmnt[var]
        start = pair[0]
        rotation = pair[1]
        # Start x and y is the bottom left corner of our component
        start_x, start_y = self.pos_to_xy[start]
        # set var_x and var_y based on the rotation (how long/tall our component is)
        var_x = self.x[var]
        var_y = self.y[var]
        if rotation == 1:
            temp = var_x
            var_x = var_y
            var_y = temp

        # Create a list of covered positions for our component's assignment
        covered = []
        for r in range(start_y, start_y+var_y):
            for c in range(start_x, start_x+var_x):
                covered.append(r*self.n+c)

        # See how adjacent components are affected
        for adj in domains:
            if adj not in asgnmnt:
                remove = []
                adj_x = self.x[adj]
                adj_y = self.y[adj]
                for pair in domains[adj]:
                    pos = pair[0]
                    adj_rot = pair[1]
                    asx, asy = self.pos_to_xy[pos]
                    # x and y dimensions are based on the rotation of the component
                    x_dif = adj_x
                    y_dif = adj_y
                    if adj_rot == 1:
                        x_dif = adj_y
                        y_dif = adj_x
                    removed = False
                    # Remove domains values that overlap
                    for r in range(asy, asy + y_dif):
                        for c in range(asx, asx + x_dif):
                            if r * self.n + c in covered:
                                remove.append(pair)
                                removed = True
                                break
                        if removed:
                            break
                # Removing pairs here - cannot modify what we are looping over inside the loop itself
                for pair in remove:
                    domains[adj].remove(pair)
        return domains

    # Return the reduction in the size of the domain of adj based on the theoretical assignment of var
    def numeric_overlap(self, var, adj, asgnmnt, domains):
        # Process of finding what squares are covered is repeated here as with update_domains
        result = 0
        covered = []
        pair = asgnmnt[var]
        pos = pair[0]
        rotation = pair[1]
        start_x, start_y = self.pos_to_xy[pos]
        # X and Y dimensions based on component's rotation
        if rotation == 0:
            var_x = self.x[var]
            var_y = self.y[var]
        else:
            var_x = self.y[var]
            var_y = self.x[var]
        # Creating list of covered
        for r in range(start_y, start_y+var_y):
            for c in range(start_x, start_x+var_x):
                covered.append(r * self.n + c)

        adj_x = self.x[adj]
        adj_y = self.y[adj]
        for pair in domains[adj]:
            pos = pair[0]
            rotation = pair[1]
            # starting x and y for position
            asx, asy = self.pos_to_xy[pos]
            if rotation == 0:
                x_dif = adj_x
                y_dif = adj_y
            else:
                x_dif = adj_y
                y_dif = adj_x
            # The more restricted our domain, the lower the result value
            overlap = False
            for r in range(asy, asy+y_dif):
                for c in range(asx, asx+x_dif):
                    if r * self.n + c in covered:
                        result -= 1
                        overlap = True
                        break
                if overlap:
                    break
        return result

    # Return True if there is some valid location for adj based on the assignment of var. Return False otherwise
    def constrained(self, var, val, adj, domains):
        # Create 'covered', the list of all spaces covered by component var
        covered = []
        pos = val[0]
        rotation = val[1]
        start_x, start_y = self.pos_to_xy[pos]
        if rotation == 0:
            var_x = self.x[var]
            var_y = self.y[var]
        else:
            var_x = self.y[var]
            var_y = self.x[var]
        for r in range(start_y, start_y+var_y):
            for c in range(start_x, start_x+var_x):
                covered.append(r*self.n+c)

        adj_x = self.x[adj]
        adj_y = self.y[adj]
        # for every possible domain value, check if var and adj intersect
        for pair in domains[adj]:
            # adj start x (asx) and adj start y (asy)
            pos = pair[0]
            rotation = pair[1]
            asx, asy = self.pos_to_xy[pos]
            if rotation == 0:
                x_dif = adj_x
                y_dif = adj_y
            else:
                x_dif = adj_y
                y_dif = adj_x
            intersection = False
            for r in range(asy, asy+y_dif):
                for c in range(asx, asx+x_dif):
                    if r*self.n+c in covered:
                        # if there is some intersection, break to try the next domain value
                        intersection = True
                        break
                if intersection:
                    break
            if not intersection:
                return True
        # Every possible value for adj results in an intersection, return False
        return False

    # Prints the resulting assignment as a grid to see where the components are located
    def print_grid_format(self, asgnmnt):
        grid = []
        # Start by making a grid of all '.'
        for r in range(self.m):
            row = []
            for c in range(self.n):
                row.append('.')
            grid.append(row)

        # For every assigned var, update its associated character in the grid
        for var in asgnmnt:
            pair = asgnmnt[var]
            val = pair[0]
            rotation = pair[1]
            # Component bottom left corner x and y
            start_x, start_y = self.pos_to_xy[val]
            # Component dimensions
            if rotation == 0:
                var_x = self.x[var]
                var_y = self.y[var]
            else:
                var_x = self.y[var]
                var_y = self.x[var]
            # The character to be placed in the grid
            character = self.variables[var][0][0]
            # Loop over all slots for this component, placing the associated character in the grid
            for r in range(start_y, start_y + var_y):
                for c in range(start_x, start_x + var_x):
                    grid[r][c] = character
        # Print the grid row by row
        for r in range(self.m):
            print(grid[r])


# Unit Testing
if __name__ == "__main__":
    arr = [['aaa', 'aaa'], ['bbbbb', 'bbbbb'], ['cc', 'cc', 'cc'], ['eeeeeee']]

    csp = CircuitProblem(3, 10, arr)
    domains = csp.initialize_domains()
    assignment = {}
    print(arr[0][0][0])

    print(domains)
    assignment[0] = [0, 0]
    csp.update_domains(0, assignment, domains)
    print(domains)
    assignment[1] = [3, 0]
    csp.update_domains(1, assignment, domains)
    print(domains)
    assignment[2] = [8, 0]
    csp.update_domains(2, assignment, domains)
    print(domains)