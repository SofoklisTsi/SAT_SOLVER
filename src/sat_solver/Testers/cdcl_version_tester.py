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
    
def load_results(file_path: str) -> Dict:
    """
    Load results from a JSON file with preprocessing to handle common formatting issues.

    Args:
        file_path (str): Path to the JSON file to load

    Returns:
        Dict: The loaded JSON data

    Raises:
        ValueError: If there is an error decoding the JSON
    """
    with open(file_path, 'r') as f:
        file_content = f.read()
    
    # Preprocessing: Replace invalid single quotes with double quotes
    fixed_content = file_content.replace("'", '"').replace("None", "null")
    
    try:
        # Attempt to parse the JSON
        return json.loads(fixed_content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON in file {file_path}: {e}\nFixed Content:\n{fixed_content}")

# Parametrize using Cartesian product
heuristic = ["default", "dlcs", "dlis", "moms"]
cutting_method = ["1UIP"]
@pytest.mark.parametrize("heuristic, cutting_method", product(heuristic, cutting_method))
def test_cdcl_solver(heuristic: str, cutting_method: str) -> None:
    """
    Test the CDCL solver with different heuristics and cutting methods.

    Args:
        heuristic (str): The heuristic to use
        cutting_method (str): The cutting method to use
    """
    cnf_file = "../sat_solver/DATA/CDCL_Clauses_Files/TESTS/cdcl_test.cnf"
    result_file = f"../sat_solver/DATA/CDCL_Clauses_Files/Clauses_Files_Results/CDCL_Results/cdcl_{heuristic}_{cutting_method}.results"
    graph_result_file = f"../sat_solver/DATA/CDCL_Clauses_Files/Clauses_Files_Results/CDCL_Results/Graphs/cdcl_{heuristic}_{cutting_method}.gresults"

    # Load the CNF problem and expected results
    clauses_model: ClausesModel = load_cnf(cnf_file)
    expected_results = load_results(result_file)
    expected_graph_results = load_results(graph_result_file)

    # Instantiate the CDCLSolver
    solver = CDCLSolver(clauses_model=clauses_model, use_logger=True, heuristic=heuristic, cutting_method=cutting_method)

    # Solve the CNF problem
    is_satisfiable = solver.solve()

    # Compare solver steps with expected steps
    actual_steps = solver.get_decision_steps()
    expected_steps = expected_results["steps"]

    assert len(actual_steps) == len(expected_steps), (
            f"cdcl test failed for heuristic {heuristic} and cut {cutting_method}. "
            "Mismatch in number of steps."
        )
    
    for actual, expected in zip(actual_steps, expected_steps):
        assert actual == expected, (
            f"cdcl test failed for heuristic {heuristic} and cut {cutting_method}. "
            f"Step mismatch: {actual} != {expected}"
        )

    # Compare solver implication graph with expected graph
    actual_graph_steps = solver.get_graph_steps()
    expected_graph_steps = expected_graph_results["steps"]

    assert len(actual_graph_steps) == len(expected_graph_steps), (
            f"cdcl test failed for heuristic {heuristic} and cut {cutting_method}. "
            "Mismatch in number of graph steps."
        )
    
    for actual, expected in zip(actual_graph_steps, expected_graph_steps):
        assert actual == expected, (
            f"cdcl test failed for heuristic {heuristic} and cut {cutting_method}. "
            f"Graph step mismatch: {actual} != {expected}"
        )
    logger.info(f"CDCL Test for heuristic {heuristic} and cut {cutting_method} passed. Satisfiable: {is_satisfiable}")  