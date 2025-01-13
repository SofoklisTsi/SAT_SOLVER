"""
cdcl_version_tester.py

This module contains the test functions for the CDCL solver. The test functions
are parametrized to test the CDCL solver with different heuristics and cutting
methods. The test functions load the CNF problem and expected results from files
and compare the solver results with the expected results.
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
from typing import Dict
import json
from itertools import product
from sat_solver.Solvers.cdcl_solver import CDCLSolver
from sat_solver.DIMACS_Reader.clause_reader import ClauseReader
from sat_solver.DIMACS_Reader.clauses_model import ClausesModel

# Helper function to load `.cnf` files
def load_cnf(file_path: str) -> ClausesModel:
    """
    Load a CNF problem from a `.cnf` file.

    Args:
        file_path (str): Path to the `.cnf` file to load

    Returns:
        ClausesModel: The loaded CNF problem
    """
    clauses: ClausesModel = ClauseReader.read_file(file_path)
    return clauses
    
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
    
    # Preprocessing: Replace invalid single quotes with double quotes
    fixed_content = file_content.replace("'", '"').replace("None", "null")
    
    try:
        # Attempt to parse the JSON
        return json.loads(fixed_content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON in file {file_path}: {e}\nFixed Content:\n{fixed_content}")

# Parametrize using Cartesian product
filename = ["cdcl1", "cdcl2"]
heuristic = ["default", "dlcs", "dlis", "moms"]
cutting_method = ["1UIP"]
@pytest.mark.parametrize("filename, heuristic, cutting_method", product(filename, heuristic, cutting_method))
def test_cdcl_solver(filename: str, heuristic: str, cutting_method: str) -> None:
    """
    Test the CDCL solver with different heuristics and cutting methods.

    Args:
        filename (str): The filename of the problem to test
        heuristic (str): The heuristic to use
        cutting_method (str): The cutting method to use

    Asserts:
        - Solver's decision steps match expected results for the given heuristic
        - Solver's implication graph steps match expected results for the given
    """
    # Load the CNF problem
    cnf_file_path = f"../sat_solver/DATA/CDCL_TESTS/TESTS/{filename}.cnf"
    clauses_model: ClausesModel = load_cnf(cnf_file_path)
    
    # Load the expected results
    results_file_path = f"../sat_solver/DATA/CDCL_TESTS/RESULTS/{filename}/{filename}_{heuristic}_{cutting_method}.json"
    expected_results = load_results(results_file_path)
    graph_file_path = f"../sat_solver/DATA/CDCL_TESTS/RESULTS/{filename}/Graphs/{filename}_{heuristic}_{cutting_method}_graph.json"
    expected_graph_results = load_results(graph_file_path)
    
    # Create the solver instance
    solver = CDCLSolver(clauses_model=clauses_model, use_logger=True, heuristic=heuristic, cutting_method=cutting_method)
    is_satisfiable = solver.solve()

    # Compare solver's steps with expected steps
    actual_steps = solver.get_decision_steps()
    expected_steps = expected_results["steps"]

    assert len(actual_steps) == len(expected_steps), (
            f"Test failed for {filename} with heuristic {heuristic} and cutting method {cutting_method}. "
            "Mismatch in number of steps."
        )
    
    for actual, expected in zip(actual_steps, expected_steps):
        assert actual == expected, (
            f"Test failed for {filename} with heuristic {heuristic} and cutting method {cutting_method}. "
            f"Step mismatch: {actual} != {expected}"
        )

    # Compare solver implication graph with expected graph
    actual_graph_steps = solver.get_graph_steps()
    expected_graph_steps = expected_graph_results["steps"]

    assert len(actual_graph_steps) == len(expected_graph_steps), (
            f"Test failed for {filename} with heuristic {heuristic} and cutting method {cutting_method}. "
            "Mismatch in number of graph steps."
        )
    
    for actual, expected in zip(actual_graph_steps, expected_graph_steps):
        assert actual == expected, (
            f"Test failed for {filename} with heuristic {heuristic} and cutting method {cutting_method}. "
            f"Graph step mismatch: {actual} != {expected}"
        )

    logger.info(f"Test for {filename} with heuristic {heuristic} and cutting method {cutting_method} passed. Satisfiable: {is_satisfiable}")

filename = ["1", "2"]
# filename = ["1"]
heuristic = ["default", "dlcs", "dlis", "moms"]
cutting_method = ["1UIP"]
method = ["twl", "true_twl"]
# Map methods to their respective solver arguments
method_to_argument = {
    "twl": {"twl": True},
    "true_twl": {"true_twl": True},
}
@pytest.mark.parametrize("method, filename, heuristic, cutting_method", product(method, filename, heuristic, cutting_method)) 
def test_cdcl_solver_twl(method: str, filename: str, heuristic: str, cutting_method: str) -> None:
    """
    Tests the DPLL solver's Two Watched Literals (TWL) optimization.

    Args:
        heuristic (str): The heuristic to test. Supported heuristics are 'default', 'dlcs'.
        filename (str): The filename of the problem to test.

    Asserts:
        - Solver's decision steps for TWL match expected results.
    """
    # Load the CNF problem
    cnf_file_path = f"../sat_solver/DATA/CDCL_TESTS/TESTS/{method}{filename}.cnf"
    clauses_model: ClausesModel = load_cnf(cnf_file_path)
    
    # Load the expected results
    results_file_path = f"../sat_solver/DATA/CDCL_TESTS/RESULTS/{method}{filename}/{method}{filename}_{heuristic}_{cutting_method}.json"
    expected_results = load_results(results_file_path)
    graph_file_path = f"../sat_solver/DATA/CDCL_TESTS/RESULTS/{method}{filename}/Graphs/{method}{filename}_{heuristic}_{cutting_method}_graph.json"
    expected_graph_results = load_results(graph_file_path)
    
    # Create the solver instance
    solver = CDCLSolver(clauses_model=clauses_model, use_logger=True, heuristic=heuristic, **method_to_argument[method], cutting_method=cutting_method)
    is_satisfiable = solver.solve()

   # Compare solver's steps with expected steps
    actual_steps = solver.get_decision_steps()
    expected_steps = expected_results["steps"]

    assert len(actual_steps) == len(expected_steps), (
            f"Test failed for {method}{filename} with heuristic {heuristic} and cutting method {cutting_method}. "
            "Mismatch in number of steps."
        )
    
    for actual, expected in zip(actual_steps, expected_steps):
        assert actual == expected, (
            f"Test failed for {method}{filename} with heuristic {heuristic} and cutting method {cutting_method}. "
            f"Step mismatch: {actual} != {expected}"
        )

    # Compare solver implication graph with expected graph
    actual_graph_steps = solver.get_graph_steps()
    expected_graph_steps = expected_graph_results["steps"]

    assert len(actual_graph_steps) == len(expected_graph_steps), (
            f"Test failed for {method}{filename} with heuristic {heuristic} and cutting method {cutting_method}. "
            "Mismatch in number of graph steps."
        )
    
    for actual, expected in zip(actual_graph_steps, expected_graph_steps):
        assert actual == expected, (
            f"Test failed for {method}{filename} with heuristic {heuristic} and cutting method {cutting_method}. "
            f"Graph step mismatch: {actual} != {expected}"
        )

    logger.info(f"Test for {method}{filename} with heuristic {heuristic} and cutting method {cutting_method} passed. Satisfiable: {is_satisfiable}")