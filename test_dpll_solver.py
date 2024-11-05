from dpll_solver import SATProblem, DPLLSolver

# TEST DPLL SOLVE WITH LOGGING ENABLED

# Define the clauses for pure literal elimination check
clauses_ple_test = [
    [1, 3],      
    [-2, 3],     
    [2, 4],     
    [-4]         
]

# Define the clauses for unit propagation undo check while backtracking
clauses_upd_test = [
    [1, 2],
    [-1, 2],
    [-1, -2, 3, 4],
    [-1, -2, 3, -4],
    [-1, -2, -3, 4],
    [-1, -2, -3, -4]
]

# Define the clauses from the PDFs
clauses_pdf1 = [  # Correct Result
    [4, -3, 1],
    [2, 1, 3],
    [-4, -3],
    [3, -1],
    [-4, 2, 3],
    [4]
]

clauses_pdf4 = [  # Correct Result
    [1, 2, 3],
    [-1, -2, -3],
    [-1, 2, 3],
    [-2, 3],
    [2, -3]
]

clauses_pdf5 = [  # Correct Result SAME AS 6 AND 7
    [4, 3],
    [1, -3],
    [-1, -2, -3, -4],
    [3, 4, -2],
    [4, -3],
    [1, 3, 2, -4],
    [4, 1, -2],
    [-1, 4, 2, -3]
]

clauses_pdf8 = [  # Correct Result 
    [1, 2],
    [-2, -3]
]

clauses_pdf9 = [  # Correct Result 
    [1, 2],
    [-3, -4],
    [1, -2],
    [-1, 2],
    [3, 4],
    [-5, 4]
]

clauses_pdf10 = [  # Correct Result 
    [-1, 2],
    [-2, 1],
    [-1, 3],
    [2],
    [-3]
]

# Initialize SATProblem with the clauses
problem = SATProblem(clauses_upd_test)

# Initialize DPLLSolver with the problem and disable pure literal elimination
solver = DPLLSolver(problem)

# Solve the problem.
is_satisfiable = solver.solve()

# Print the satisfiability result and the steps in table format
print("Is satisfiable:", is_satisfiable)
solver.print_steps()
