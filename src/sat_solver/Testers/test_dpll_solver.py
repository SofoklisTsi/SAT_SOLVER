from sat_solver.Solver.dpll_solver import DPLLSolver
from sat_solver.DIMACS_Reader.clause_reader import ClauseReader
from sat_solver.DIMACS_Reader.clauses_model import ClausesModel

# TEST DPLL SOLVE WITH LOGGING ENABLED

# DIMACS file reading
filename = "../sat_solver/DATA/Clauses_Files/TESTS/twl_test.cnf"
clauses_model: ClausesModel = ClauseReader.read_file(filename)
print(f"Clauses: {clauses_model.clauses}")
print(f"Number of Variables: {clauses_model.num_vars}")
print(f"Number of Clauses: {clauses_model.num_clauses}")

# Initialize SATProblem with the clauses and DPLL solver with the clauses model instance.
solver = DPLLSolver(clauses_model=clauses_model, use_logger=True, heuristic='default', true_twl=False)

# Solve the problem.
is_satisfiable = solver.solve() 

# Print the satisfiability result and the steps in table format
print("Is satisfiable:", is_satisfiable)
solver.print_steps()
