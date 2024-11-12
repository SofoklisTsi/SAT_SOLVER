from dpll_solver import SATProblem, DPLLSolver
from literal_count_branching_heuristics import dlcs, dlis, rdlis, rdlcs, default_heuristic
from clause_elimination_methods import pure_literal_elimination
from moms_branching_heuristics import moms, rmoms, _count_occurrences_in_smallest_clauses

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

# Define the test branching heuristics clauses
clauses_test_branching_heuristics = [
    [4, 3],
    [1, -3],
    [-1, -2, -3, -4],
    [3, -2, 4], # as it tries to change the twl, it will encounter 4 and map the clause to satisfied
    [4, -3],
    [1, 3, 2, -4],
    [4, 1, -2],
    # [], # enable to test empty clause
    [-4, -1, -2, -3], # keep to test two watched literals
    [-4, -1, -2, 3], # keep to test two watched literals
    [-4, -1, 2, 3], # keep to test two watched literals
    [-4, -1, 2, -3], # keep to test two watched literals
    [-1, 4, 2, -3]
]

# Initialize SATProblem with the clauses
problem = SATProblem(clauses_test_branching_heuristics)
_count_occurrences_in_smallest_clauses(problem)
# Initialize DPLLSolver with the problem without pure literal elimination
solver = DPLLSolver(problem, heuristic='dlcskjl', twl=True)
_count_occurrences_in_smallest_clauses(problem)


# Solve the problem.
is_satisfiable = solver.solve() # Enable this line to test the solver

# Print the satisfiability result and the steps in table format
print("Is satisfiable:", is_satisfiable)  # Enable this line to test the solver
solver.print_steps() # Enable this line to test the solver

# Print results for each heuristic
# print("\nTesting DLCS Heuristic:")  # Enable this line to test the heuristics
# print("-----------------------")  # Enable this line to test the heuristics
# chosen_literal_dlcs = dlcs(problem)  # Enable this line to test the heuristics
# print(f"DLCS selected literal: {chosen_literal_dlcs}\n")  # Enable this line to test the heuristics

# print("\nTesting DLIS Heuristic:")  # Enable this line to test the heuristics
# print("-----------------------")  # Enable this line to test the heuristics
# chosen_literal_dlis = dlis(problem)  # Enable this line to test the heuristics
# print(f"DLIS selected literal: {chosen_literal_dlis}\n")  # Enable this line to test the heuristics

# print("\nTesting RDLCS Heuristic:")  # Enable this line to test the heuristics
# print("------------------------")  # Enable this line to test the heuristics
# chosen_literal_rdlcs = rdlcs(problem)  # Enable this line to test the heuristics
# print(f"RDLCS selected literal: {chosen_literal_rdlcs}\n")  # Enable this line to test the heuristics

# print("\nTesting RDLIS Heuristic:")  # Enable this line to test the heuristics
# print("------------------------")  # Enable this line to test the heuristics
# chosen_literal_rdlis = rdlis(problem)  # Enable this line to test the heuristics
# print(f"RDLIS selected literal: {chosen_literal_rdlis}\n")  # Enable this line to test the heuristics

# Initialize DPLLSolver with the problem and enable the heuristics
# problem2 = SATProblem(clauses_test_branching_heuristics)
# problem3 = SATProblem(clauses_test_branching_heuristics)
# problem4 = SATProblem(clauses_test_branching_heuristics)
# problem5 = SATProblem(clauses_test_branching_heuristics)

# solver2 = DPLLSolver(problem2, heuristic='dlcs')
# solver3 = DPLLSolver(problem3, heuristic='dlis')
# solver4 = DPLLSolver(problem4, heuristic='rdlcs')
# solver5 = DPLLSolver(problem5, heuristic='rdlis')

# is_satisfiable = solver2.solve() # Enable this line to test the solver
# print("Is satisfiable:", is_satisfiable)  # Enable this line to test the solver
# solver2.print_steps() # Enable this line to test the solver

# is_satisfiable = solver3.solve() # Enable this line to test the solver
# print("Is satisfiable:", is_satisfiable)  # Enable this line to test the solver
# solver3.print_steps() # Enable this line to test the solver

# is_satisfiable = solver4.solve() # Enable this line to test the solver
# print("Is satisfiable:", is_satisfiable)  # Enable this line to test the solver
# solver4.print_steps() # Enable this line to test the solver

# is_satisfiable = solver5.solve() # Enable this line to test the solver
# print("Is satisfiable:", is_satisfiable)  # Enable this line to test the solver
# solver5.print_steps() # Enable this line to test the solver

