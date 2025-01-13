from sat_solver.Solvers.dpll_solver import DPLLSolver
from sat_solver.Solvers.cdcl_solver import CDCLSolver
from sat_solver.DIMACS_Reader.clause_reader import ClauseReader
from sat_solver.DIMACS_Reader.clauses_model import ClausesModel

# Set the filename, solver type, heuristic and cutting method. THOSE ARE THE ONLY VARIABLES THAT NEED TO BE CHANGED.
filename = "../sat_solver/DATA/DPLL_TESTS/TESTS/twl.cnf"
solver_type = "cdcl" # or "cdcl"
heuristic = "default" # or "dlcs" or "dlis" or "moms"
cutting_method = "1UIP"
twl = False
true_twl = False

# Map the solver type to the solver function and the results functions to be called.
solver_function = DPLLSolver if solver_type == "dpll" else CDCLSolver
results_functions = {
    "dpll": ["print_steps"],
    "cdcl": ["print_steps", "print_implication_graph"]
}

# Read the clauses from the file and print the clauses, number of variables and number of clauses.
clauses_model: ClausesModel = ClauseReader.read_file(filename)
print(f"Clauses: {clauses_model.clauses}")
print(f"Number of Variables: {clauses_model.num_vars}")
print(f"Number of Clauses: {clauses_model.num_clauses}")

# Initialize SATProblem with the clauses and DPLL solver with the clauses model instance.
if solver_type == "dpll":
    solver = solver_function(clauses_model=clauses_model, use_logger=True, heuristic=heuristic, twl=twl, true_twl=true_twl)
else:
    solver = solver_function(clauses_model=clauses_model, use_logger=True, heuristic=heuristic, twl=twl, true_twl=true_twl, cutting_method=cutting_method)

# Solve the problem and get the satisfiability result.
is_satisfiable = solver.solve() 

# Print the satisfiability result and the steps in table format
print("Is satisfiable:", is_satisfiable)
for function in results_functions[solver_type]:
    getattr(solver, function)()