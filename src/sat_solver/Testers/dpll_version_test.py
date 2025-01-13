"""
dpll_version_tester.py

This module defines the `DPLL Version Tester` testing suite for the DPLL SAT Solver. It validates the solver 
against various functionality tests using pytest, ensuring correctness and compliance with 
business requirements.

Tests included:
1. **General Tests**:
   - Compares the solver's decision logs against expected results in the corresponding results folder.
3. **Unit Propagation (UP) Test**:
   - Validates the correctness of unit propagation under different heuristics.
4. **Two Watched Literals (TWL) Test and True Two Watched Literals (TrueTWL) Test**:
   - Ensures that the solver implements the Two Watched Literals optimization correctly.

### Structure

1. **Parameterized Tests**:
    - Uses `pytest.mark.parametrize` to dynamically run tests for each heuristic or feature.
"""

# Set up a logger
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

import pytest
from typing import Callable, Dict, Tuple
from sat_solver.Solvers.dpll_solver import DPLLSolver
from sat_solver.DIMACS_Reader.clause_reader import ClauseReader
from sat_solver.DIMACS_Reader.clauses_model import ClausesModel
import json
from itertools import product

# Helper function to load `.cnf` files
def load_cnf(file_path: str) -> ClausesModel:
    """
    Load a CNF problem from a `.cnf` file.

    Args:
        file_path (str): Path to the `.cnf` file to load

    Returns:
        ClausesModel: The loaded CNF problem
    """
    clauses_model: ClausesModel = ClauseReader.read_file(file_path)
    return clauses_model

# Helper function to load `.results` or `.gresults` files
def load_results(file_path: str) -> Dict:
    """
    Load results from a JSON file with preprocessing to handle common formatting issues.

    Args:
        file_path (str): Path to the JSON file to load

    Returns:
        Dict: The loaded JSON data
    """
    with open(file_path, 'r') as f:
        return json.load(f)

filename = ["dpll1", "dpll2", "dpll3", "dpll4", "dpll5", "dpll6"]
heuristic = ["default", "dlcs", "dlis", "moms"]
@pytest.mark.parametrize("filename, heuristic", product(filename, heuristic))
def test_dpll_solver(filename: str, heuristic: str) -> None:
    """
    Tests the DPLL solver against a set of problems.

    Args:
        heuristic (str): The heuristic to test. Supported heuristics are 'default', 'dlcs', 'dlis', 'moms'.
        filename (str): The filename of the problem to test.

    Asserts:
        - Solver's decision steps match expected results for the given heuristic.
    """
    # Load the CNF problem
    cnf_file_path = f"../sat_solver/DATA/DPLL_TESTS/TESTS/{filename}.cnf"
    clauses_model: ClausesModel = load_cnf(cnf_file_path)
    
    # Load the expected results
    results_file_path = f"../sat_solver/DATA/DPLL_TESTS/RESULTS/{filename}/{filename}_{heuristic}.json"
    expected_results = load_results(results_file_path)
    
    # Create the solver instance
    solver = DPLLSolver(clauses_model=clauses_model, use_logger=True, heuristic=heuristic)
    is_satisfiable = solver.solve()

    # Compare solver's steps with expected steps
    actual_steps = solver.get_decision_steps()
    expected_steps = expected_results["steps"]

    assert len(actual_steps) == len(expected_steps), (
            f"Test failed for {filename} with heuristic {heuristic}. "
            "Mismatch in number of steps."
        )
    
    for actual, expected in zip(actual_steps, expected_steps):
        assert actual == expected, (
            f"Test failed for {filename} with heuristic {heuristic}. "
            f"Step mismatch: {actual} != {expected}"
        )

    logger.info(f"Test for {filename} with heuristic {heuristic} passed. Satisfiable: {is_satisfiable}")

filename = ["bcp"]
heuristic = ["default", "dlcs", "dlis", "moms"]
@pytest.mark.parametrize("filename, heuristic", product(filename, heuristic))
def test_dpll_solver_bpc(filename: str, heuristic: str) -> None:
    """
    Tests the DPLL solver's unit propagation functionality.

    Args:
        heuristic (str): The heuristic to test. Supported heuristics are 'default', 'dlcs', 'dlis', 'moms'.
        filename (str): The filename of the problem to test.

    Asserts:
        - Solver's decision steps match expected results for the given heuristic.
    """
    # Load the CNF problem
    cnf_file_path = f"../sat_solver/DATA/DPLL_TESTS/TESTS/{filename}.cnf"
    clauses_model: ClausesModel = load_cnf(cnf_file_path)
    
    # Load the expected results
    results_file_path = f"../sat_solver/DATA/DPLL_TESTS/RESULTS/{filename}/{filename}_{heuristic}.json"
    expected_results = load_results(results_file_path)
    
    # Create the solver instance
    solver = DPLLSolver(clauses_model=clauses_model, use_logger=True, heuristic=heuristic)
    is_satisfiable = solver.solve()

    # Compare solver's steps with expected steps
    actual_steps = solver.get_decision_steps()
    expected_steps = expected_results["steps"]

    assert len(actual_steps) == len(expected_steps), (
            f"Test failed for {filename} with heuristic {heuristic}. "
            "Mismatch in number of steps."
        )
    
    for actual, expected in zip(actual_steps, expected_steps):
        assert actual == expected, (
            f"Test failed for {filename} with heuristic {heuristic}. "
            f"Step mismatch: {actual} != {expected}"
        )

    logger.info(f"Test for {filename} with heuristic {heuristic} passed. Satisfiable: {is_satisfiable}")

filename = ["twl", "true_twl"]
heuristic = ["default", "dlcs", "dlis", "moms"]
# Map filenames to their respective solver arguments
filename_to_argument = {
    "twl": {"twl": True},
    "true_twl": {"true_twl": True},
}
@pytest.mark.parametrize("filename, heuristic", product(filename, heuristic)) 
def test_dpll_solver_twl(filename: str, heuristic: str) -> None:
    """
    Tests the DPLL solver's Two Watched Literals (TWL) optimization.

    Args:
        heuristic (str): The heuristic to test. Supported heuristics are 'default', 'dlcs'.
        filename (str): The filename of the problem to test.

    Asserts:
        - Solver's decision steps for TWL match expected results.
    """
    # Load the CNF problem
    cnf_file_path = f"../sat_solver/DATA/DPLL_TESTS/TESTS/{filename}.cnf"
    clauses_model: ClausesModel = load_cnf(cnf_file_path)
    
    # Load the expected results
    results_file_path = f"../sat_solver/DATA/DPLL_TESTS/RESULTS/{filename}/{filename}_{heuristic}.json"
    expected_results = load_results(results_file_path)
    
    # Create the solver instance
    solver = DPLLSolver(clauses_model=clauses_model, use_logger=True, heuristic=heuristic, **filename_to_argument[filename])
    is_satisfiable = solver.solve()

    # Compare solver's steps with expected steps
    actual_steps = solver.get_decision_steps()
    expected_steps = expected_results["steps"]

    assert len(actual_steps) == len(expected_steps), (
            f"Test failed for {filename} with heuristic {heuristic}. "
            "Mismatch in number of steps."
        )
    
    for actual, expected in zip(actual_steps, expected_steps):
        assert actual == expected, (
            f"Test failed for {filename} with heuristic {heuristic}. "
            f"Step mismatch: {actual} != {expected}"
        )

    logger.info(f"Test for {filename} with heuristic {heuristic} passed. Satisfiable: {is_satisfiable}")