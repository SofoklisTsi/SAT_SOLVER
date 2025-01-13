from sat_solver.DIMACS_Reader.clauses_model import ClausesModel
from sat_solver.Solvers.cdcl_solver import CDCLSolver, DPLLSolver
from sat_solver.DIMACS_Reader.clause_reader import ClauseReader

def create_dpll_results_files(cnf_filename: str, twl: bool = False, true_twl: bool = False) -> None:
    solver_type = "DPLL"
    heuristics = ["default", "dlcs", "dlis", "moms"]
    cnf_file_path = f"../sat_solver/DATA/{solver_type}_TESTS/TESTS/{cnf_filename}.cnf"
    results_directory_path = f"../sat_solver/DATA/{solver_type}_TESTS/Results/{cnf_filename}/"
    
    for heuristic in heuristics:
        results_filename = f"{cnf_filename}_{heuristic}.json"
        clauses_model: ClausesModel = ClauseReader.read_file(cnf_file_path)
        solver = DPLLSolver(clauses_model=clauses_model, use_logger=True, heuristic=heuristic, twl=twl, true_twl=true_twl)
        solver.solve()
        solver.step_logger.create_json_file(directory=results_directory_path, filename=results_filename)

def create_cdcl_results_files(cnf_filename: str, twl: bool = False, true_twl: bool = False) -> None:
    solver_type = "CDCL"
    heuristics = ["default", "dlcs", "dlis", "moms"]
    # cutting_methods = ["1UIP", "LUIP"]
    cutting_methods = ["1UIP"]
    cnf_file_path = f"../sat_solver/DATA/{solver_type}_TESTS/TESTS/{cnf_filename}.cnf"
    results_directory_path = f"../sat_solver/DATA/{solver_type}_TESTS/Results/{cnf_filename}/"
    graph_directory_path = f"{results_directory_path}Graphs/"
    
    for heuristic in heuristics:
        for cutting_method in cutting_methods:
            results_filename = f"{cnf_filename}_{heuristic}_{cutting_method}.json"
            graph_filename = f"{cnf_filename}_{heuristic}_{cutting_method}_graph.json"
            clauses_model: ClausesModel = ClauseReader.read_file(cnf_file_path)
            solver = CDCLSolver(clauses_model=clauses_model, use_logger=True, heuristic=heuristic, twl=twl, true_twl=true_twl, cutting_method=cutting_method)
            solver.solve()
            solver.step_logger.create_json_file(directory=results_directory_path, filename=results_filename)
            solver.graph_step_logger.create_json_file(directory=graph_directory_path, filename=graph_filename)


# run the functions
# create_dpll_results_files(cnf_filename="true_twl", true_twl=True)
create_cdcl_results_files(cnf_filename="twl2", twl=True)


        


