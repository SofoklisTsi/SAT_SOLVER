from sat_solver.Solvers.dpll_solver import DPLLSolver
from sat_solver.Solvers.cdcl_solver import CDCLSolver
from sat_solver.DIMACS_Reader.clause_reader import ClauseReader
from sat_solver.DIMACS_Reader.clauses_model import ClausesModel
import cProfile

def profile_solver(filename: str, heuristic: str, cutting_method: str, twl: bool, true_twl: bool, solver_type: str) -> None:
    """
    Profile the SAT solver execution with cProfile.
    """
    # Read the clauses from the file.
    clauses_model: ClausesModel = ClauseReader.read_file(filename)
    # Map the solver type to the solver function.
    solver_function = DPLLSolver if solver_type == "dpll" else CDCLSolver
    # Initialize SATProblem with the clauses and DPLL solver with the clauses model instance.
    if solver_type == "dpll":
        solver = solver_function(clauses_model=clauses_model, use_logger=False, heuristic=heuristic, twl=twl, true_twl=true_twl)
    else:
        solver = solver_function(clauses_model=clauses_model, use_logger=False, heuristic=heuristic, twl=twl, true_twl=true_twl, cutting_method=cutting_method)
    # Solve the problem and get the satisfiability result.
    profiler = cProfile.Profile()
    profiler.enable()
    is_satisfiable = solver.solve() 
    profiler.disable()
    profiler.dump_stats("Usage_Examples/profile_output.prof")
    print("Is satisfiable:", is_satisfiable)

if __name__ == "__main__":
    # Set the filename, solver type, heuristic and cutting method. THOSE ARE THE ONLY VARIABLES THAT NEED TO BE CHANGED.

    filename = "../sat_solver/DATA/SATLIB/uf20-91/uf20-01.cnf" # runs
    # filename = "../sat_solver/DATA/SATLIB/uf75-325/uf75-01.cnf" # runs
    # filename = "../sat_solver/DATA/SATLIB/uf100-430/uf100-01.cnf" # runs
    # filename = "../sat_solver/DATA/SATLIB/uf125-538/uf125-01.cnf" # runs
    # filename = "../sat_solver/DATA/SATLIB/uf150-645/uf150-01.cnf" # runs
    # filename = "../sat_solver/DATA/SATLIB/uf175-753/uf175-01.cnf" # runs
    # filename = "../sat_solver/DATA/SATLIB/uf200-860/uf200-01.cnf" # runs
    # filename = "../sat_solver/DATA/SATLIB/uf225-960/uf225-01.cnf" # does not run!!!
    # filename = "../sat_solver/DATA/SATLIB/uf250-1065/uf250-01.cnf" # does not run!!!

    solver_type = "dpll" # or "cdcl"
    heuristic = "default" # or "dlcs" or "dlis" or "moms"
    cutting_method = "1UIP"
    twl = False
    true_twl = False

    profile_solver(filename, heuristic, cutting_method, twl, true_twl, solver_type)
