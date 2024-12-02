import sys
import os

# Add the parent directory of the project to the PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from sat_solver.Solver.dpll_solver import SATProblem, DPLLSolver
from sat_solver.DIMACS_Reader.clause_reader import ClauseReader
import cProfile

def profile_solver(clauses):
    """
    Profile the SAT solver execution with cProfile.
    """
    problem = SATProblem(clauses)
    solver = DPLLSolver(problem,use_logger=False,heuristic='dlcs',twl=False,true_twl=True)
    profiler = cProfile.Profile()
    profiler.enable()
    isat = solver.solve()
    profiler.disable()
    profiler.dump_stats("profile_output.prof")
    print(f"Is SAT: {isat}")

if __name__ == "__main__":
    # filename = "../sat_solver/DATA/SATLIB/uf20-91/uf20-01.cnf" # runs
    # filename = "../sat_solver/DATA/SATLIB/uf75-325/uf75-01.cnf" # runs
    # filename = "../sat_solver/DATA/SATLIB/uf100-430/uf100-01.cnf" # runs
    filename = "../sat_solver/DATA/SATLIB/uf125-538/uf125-01.cnf" # runs
    # filename = "../sat_solver/DATA/SATLIB/uf150-645/uf150-01.cnf" # runs
    # filename = "../sat_solver/DATA/SATLIB/uf250-1065/uf250-01.cnf" # does not run!!!
    clauses, num_vars, num_clauses = ClauseReader.read_file(filename)
    profile_solver(clauses)
