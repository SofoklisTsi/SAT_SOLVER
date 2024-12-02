import sys
import os

# Add the parent directory of the project to the PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from sat_solver.Solver.dpll_solver import SATProblem, DPLLSolver
from sat_solver.DIMACS_Reader.clause_reader import ClauseReader

# TEST DPLL SOLVE WITH LOGGING ENABLED

# DIMACS file reading
filename = "../sat_solver/DATA/Clauses_Files/TESTS/twl_test.cnf"
# filename = "../DATA/Clauses_Files/TESTS/ple_test.cnf"
clauses, num_vars, num_clauses = ClauseReader.read_file(filename)
print(f"Clauses: {clauses}")
print(f"Number of Variables: {num_vars}")
print(f"Number of Clauses: {num_clauses}")

# Initialize SATProblem with the clauses and DPLL solver with the problem
problem = SATProblem(clauses)
solver = DPLLSolver(problem, use_logger=True, heuristic='default', true_twl=True)

# Solve the problem.
is_satisfiable = solver.solve() # Enable this line to test the solver

# Print the satisfiability result and the steps in table format
print("Is satisfiable:", is_satisfiable)  # Enable this line to test the solver
solver.print_steps() # Enable this line to test the solver
