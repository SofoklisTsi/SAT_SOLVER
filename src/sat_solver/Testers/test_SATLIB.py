from sat_solver.Solver.dpll_solver import DPLLSolver
from sat_solver.DIMACS_Reader.clause_reader import ClauseReader
from sat_solver.DIMACS_Reader.clauses_model import ClausesModel
import cProfile

def profile_solver(clauses_model: ClausesModel) -> None:
    """
    Profile the SAT solver execution with cProfile.
    """
    solver = DPLLSolver(clauses_model=clauses_model, use_logger=False, heuristic='dlcs', twl=False)
    profiler = cProfile.Profile()
    profiler.enable()
    isat = solver.solve()
    profiler.disable()
    profiler.dump_stats("testers/profile_output.prof")
    print(f"Is SAT: {isat}")

if __name__ == "__main__":
    # filename = "../sat_solver/DATA/SATLIB/uf20-91/uf20-01.cnf" # runs
    # filename = "../sat_solver/DATA/SATLIB/uf75-325/uf75-01.cnf" # runs
    filename = "../sat_solver/DATA/SATLIB/uf100-430/uf100-01.cnf" # runs
    # filename = "../sat_solver/DATA/SATLIB/uf125-538/uf125-01.cnf" # runs
    # filename = "../sat_solver/DATA/SATLIB/uf150-645/uf150-01.cnf" # runs
    # filename = "../sat_solver/DATA/SATLIB/uf175-753/uf175-01.cnf" # runs
    # filename = "../sat_solver/DATA/SATLIB/uf200-860/uf200-01.cnf" # runs
    # filename = "../sat_solver/DATA/SATLIB/uf225-960/uf225-01.cnf" # does not run!!!
    # filename = "../sat_solver/DATA/SATLIB/uf250-1065/uf250-01.cnf" # does not run!!!
    clauses_model: ClausesModel = ClauseReader.read_file(filename)
    profile_solver(clauses_model)
