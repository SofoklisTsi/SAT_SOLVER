"""
dpll_version_tester.py

This module defines the `DPLL VersionTester` testing suite for the SAT Solver. It validates the solver 
against various functionality tests using pytest, ensuring correctness and compliance with 
business requirements.

Tests included:
1. **PDF Problem Tests**:
   - Compares the solver's decision logs against expected results in `.results` files for 
     problems provided in the `PDFS` directory.
2. **Pure Literal Elimination (PLE) Test**:
   - Tests the solver's ability to eliminate pure literals effectively.
3. **Unit Propagation (UPD) Test**:
   - Validates the correctness of unit propagation under different heuristics.
4. **Two Watched Literals (TWL) Test and True Two Watched Literals (TrueTWL) Test**:
   - Ensures that the solver implements the Two Watched Literals optimization correctly.

### .results Files

- `.results` files specify the expected behavior of the solver during each step, in JSON format.
- These files are used as reference outputs for the tests. They contain a list of logs
  for each heuristic, which are compared to the solver's actual behavior.

Example Structure:
{
    "heuristic": "<heuristic_name>",
    "steps": [
        {
            "Decision Level": <int>,                 # Current decision depth level
            "Partial Assignment": "<{variables}>",   # Assigned variables at this step
            "Decision Literal": <int|null>,         # Literal chosen for decision, or null if implied
            "Implied Literal": <int|null>,          # Literal propagated by unit propagation, or null if none
            "Satisfied Clauses": [<int>, ...],      # List of satisfied clause indices
            "Contradicted Clauses": [<int>, ...],   # List of contradicted clause indices
            "Unit Clauses": [<int>, ...],           # List of clause indices containing unit clauses
            "Pending Clauses": [<int>, ...],        # List of clause indices containing unresolved clauses
            "Explanation": "<string>"              # Explanation of the action taken
        },
        ...
    ]
}

Multiple heuristic entries can exist in a `.results` file, separated by newline characters.

Example:
{
    "heuristic": "default",
    "steps": [
        {
            "Decision Level": 1,
            "Partial Assignment": "{1}",
            "Decision Literal": 1,
            "Implied Literal": null,
            "Satisfied Clauses": [0],
            "Contradicted Clauses": [],
            "Unit Clauses": [1],
            "Pending Clauses": [2, 3, 4, 5],
            "Explanation": "INC_DL default"
        },
        ...
    ]
}
{
    "heuristic": "dlcs",
    "steps": [
        {
            "Decision Level": 1,
            "Partial Assignment": "{-1}",
            "Decision Literal": -1,
            "Implied Literal": null,
            "Satisfied Clauses": [1, 2, 3, 4, 5],
            "Contradicted Clauses": [],
            "Unit Clauses": [0],
            "Pending Clauses": [],
            "Explanation": "INC_DL dlcs"
        },
        ...
    ]
}

### Structure

1. **Fixtures**:
    - `load_test_data`: Loads `.results` and `.cnf` files for testing.
    - `load_pdfs_test_data`: Loads problems and results from the `PDFS` directory.
    - `load_func_test_data`: Loads functional tests like PLE and UPD from `TESTS` directory.
2. **Parameterized Tests**:
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
import os
import json
from itertools import product

@pytest.fixture
def load_test_data() -> Callable:
    """
    Fixture to load test clauses and results from the directory.

    Returns:
        A callable function `_load_test_data(results_dir, clauses_dir)` that takes two arguments:
        - results_dir (str): Path to the `.results` files directory.
        - clauses_dir (str): Path to the `.cnf` files directory.

    Output:
        tuple: (expected_results, clauses)
        - expected_results (Dict): Parsed JSON objects of `.results` files.
        - clauses (Dict): Parsed clauses from `.cnf` files.
    """
    def _load_test_data(results_dir: str, clauses_dir: str) -> Tuple[Dict[str, Dict[str, list]], Dict[str, ClausesModel]]:
        results_files = []
        clauses_files = []
        for root, _, files in os.walk(results_dir):
            results_files.extend([os.path.join(root, f) for f in files if f.endswith('.results')])
        for root, _, files in os.walk(clauses_dir):
            clauses_files.extend([os.path.join(root, f) for f in files if f.endswith('.cnf')])
        
        # create a dictionary of expected results
        expected_results: Dict[str, Dict[str, list]] = {}
        for filepath in results_files:
            file_name = os.path.splitext(os.path.basename(filepath))[0]
            expected_results[file_name] = {}
            with open(filepath, 'r') as file:
                content = file.read().replace('}\n{', '},\n{')
                fixed_content = f"[{content}]"
                json_objects = json.loads(fixed_content)
                for entry in json_objects:
                    heuristic = entry["heuristic"]
                    if heuristic not in expected_results[file_name]:
                        expected_results[file_name][heuristic] = []
                    expected_results[file_name][heuristic].extend(entry["steps"])
        # create a dictionary of ClausesModel objects
        clauses: Dict[str, ClausesModel] = {}
        for filepath in clauses_files:
            clauses_tmp: ClausesModel = ClauseReader.read_file(filepath)
            file_name = os.path.splitext(os.path.basename(filepath))[0]
            clauses[file_name] = clauses_tmp
        
        return expected_results, clauses

    return _load_test_data

@pytest.fixture
def load_pdfs_test_data(load_test_data: Callable) -> Tuple[Dict[str, Dict[str, list]], Dict[str, ClausesModel]]:
    """
    Loads PDF problems for testing.

    Returns:
        tuple: (expected_results, clauses)
        - expected_results (Dict): Expected results from PDF `.results` files.
        - clauses (Dict): Parsed PDF problem clauses.
    """
    return load_test_data(
        "../sat_solver/DATA/DPLL_Clauses_Files/Clauses_Files_Results/PDFS_Results",
        "../sat_solver/DATA/DPLL_Clauses_Files/PDFS"
    )

@pytest.fixture
def load_func_test_data(load_test_data: Callable) -> Tuple[Dict[str, Dict[str, list]], Dict[str, ClausesModel]]:
    """
    Loads functional test problems for PLE, UPD, and TWL.

    Returns:
        tuple: (expected_results, clauses)
        - expected_results (Dict): Expected results from TEST `.results` files.
        - clauses (Dict): Parsed functional test clauses.
    """
    return load_test_data(
        "../sat_solver/DATA/DPLL_Clauses_Files/Clauses_Files_Results/TESTS_Results",
        "../sat_solver/DATA/DPLL_Clauses_Files/TESTS"
    )

@pytest.mark.parametrize("heuristic", ["default", "dlcs", "dlis", "moms"])
def test_pdf_problems(heuristic: str, load_pdfs_test_data: Tuple[Dict[str, Dict[str, list]], Dict[str, ClausesModel]]) -> None:
    """
    Tests the solver's correctness on problems provided in the PDFS directory.

    Args:
        heuristic (str): The heuristic to test. Supported heuristics are 'default', 'dlcs', 'dlis', 'moms'.
        load_pdfs_test_data (fixture): Loaded PDF problem clauses and expected results.

    Asserts:
        - Solver's decision steps match expected results for the given heuristic.
    """
    expected_results, clauses = load_pdfs_test_data
    for file in expected_results:
        if heuristic in expected_results[file]:
            solver = DPLLSolver(clauses_model=clauses[file], use_logger=True, heuristic=heuristic)
            is_satisfiable = solver.solve()
            assert solver.get_decision_steps() == expected_results[file][heuristic], (
                f"Test failed for {file} with heuristic {heuristic}. "
                f"Expected: {expected_results[file][heuristic]}, Actual: {solver.get_decision_steps()}"
            )
            logger.info(f"PDF Problem {file}, Heuristic {heuristic} passed. Satisfiable: {is_satisfiable}")

@pytest.mark.parametrize("heuristic", ["default", "dlcs", "dlis", "moms"])
def test_upd(heuristic: str, load_func_test_data: Tuple[Dict[str, Dict[str, list]], Dict[str, ClausesModel]]) -> None:
    """
    Tests the solver's implementation of unit propagation (UPD) under different heuristics.

    Args:
        heuristic (str): The heuristic to test. Supported heuristics are 'default', 'dlcs', 'dlis', 'moms'.
        load_func_test_data (fixture): Loaded functional test clauses and expected results.

    Asserts:
        - Solver's decision steps for UPD match expected results.
    """
    expected_results, clauses = load_func_test_data
    if heuristic in expected_results["upd_test"]:
        solver = DPLLSolver(clauses_model=clauses["upd_test"], use_logger=True, heuristic=heuristic)
        is_satisfiable = solver.solve()
        assert solver.get_decision_steps() == expected_results["upd_test"][heuristic], (
            f"Unit propagation test failed for heuristic {heuristic}. "
            f"Expected: {expected_results['upd_test'][heuristic]}, Actual: {solver.get_decision_steps()}"
        )
        logger.info(f"Unit Propagation Test for heuristic {heuristic} passed. Satisfiable: {is_satisfiable}")

# Parametrize using Cartesian product
heuristic = ["default", "dlcs"]
method = ["twl_test", "true_twl_test"]
argument = ["twl", "true_twl"]
# Map methods to their respective solver arguments
method_to_argument = {
    "twl_test": {"twl": True},
    "true_twl_test": {"true_twl": True},
}
@pytest.mark.parametrize("heuristic, method", product(heuristic, method))
def test_twl(heuristic: str, method: str, load_func_test_data: Tuple[Dict[str, Dict[str, list]], Dict[str, ClausesModel]]) -> None:
    """
    Tests the solver's Two Watched Literals (TWL) optimization.

    Args:
        heuristic (str): The heuristic to test. Supported heuristics are 'default', 'dlcs'.
        method (str): The TWL test to perform ('twl_test' or 'true_twl_test').
        load_func_test_data (fixture): Loaded functional test clauses and expected results.

    Asserts:
        - Solver's decision steps for TWL match expected results.
    """
    expected_results, clauses = load_func_test_data
    if heuristic in expected_results[method]:
        # Dynamically unpack the correct arguments based on the method
        solver = DPLLSolver(clauses_model=clauses["twl_test"], use_logger=True, heuristic=heuristic, **method_to_argument[method])
        is_satisfiable = solver.solve()
        assert solver.get_decision_steps() == expected_results[method][heuristic], (
            f"{argument} test failed for heuristic {heuristic}. "
            f"Expected: {expected_results[method][heuristic]}, Actual: {solver.get_decision_steps()}"
        )
        logger.info(f"{argument} Test for heuristic {heuristic} passed. Satisfiable: {is_satisfiable}")    