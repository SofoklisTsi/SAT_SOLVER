"""
version_tester.py

This module defines the `VersionTester` class, which provides a suite of tests for validating 
the functionality of the SAT solver, including tests for specific features like pure literal 
elimination, unit propagation, Two Watched Literals (TWL), and decision logging. 

It also compares solver outputs to expected results provided in files to ensure correctness.

The `.results` files contain expected outputs for SAT solver tests in JSON format.
Each file can contain multiple heuristic-based expected results. Each heuristic's
entry lists the steps the solver is expected to take when using that heuristic.

Format Overview:
- Each heuristic is represented as a JSON object.
- The `heuristic` key specifies the name of the heuristic being tested.
- The `steps` key contains a list of decision logs, with each log representing a step.

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

Usage in `VersionTester`:
- The `VersionTester` class parses `.results` files during test execution to compare the solver's
  actual steps against the expected steps defined in these files.
"""

import sys
import os

# Add the parent directory of the project to the PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Solver.dpll_solver import SATProblem, DPLLSolver
from DIMACS_Reader.clause_reader import ClauseReader
import json

class VersionTester:
    """
    A testing utility class for validating the functionality of the SAT solver against expected results.

    Attributes:
        results_files_directory (str): Path to the directory containing expected results for PDF-based tests.
        clauses_files_directory (str): Path to the directory containing SAT problem files for PDF-based tests.
        func_results_files_directory (str): Path to the directory containing expected results for functional tests.
        func_clauses_files_directory (str): Path to the directory containing SAT problem files for functional tests.
        results_files (List[str]): List of paths to result files in the results directory.
        clauses_files (List[str]): List of paths to SAT problem files in the clauses directory.
        func_results_files (List[str]): List of paths to result files in the functional tests directory.
        func_clauses_files (List[str]): List of paths to SAT problem files in the functional tests directory.
        expected_results (Dict[str, Dict[str, List[Dict]]]): Parsed expected results from PDF-based tests, 
            keyed by filename and heuristic.
        clauses (Dict[str, List[List[int]]]): Parsed SAT clauses from PDF-based tests, keyed by filename.
        func_expected_results (Dict[str, Dict[str, List[Dict]]]): Parsed expected results from functional tests.
        func_clauses (Dict[str, List[List[int]]]): Parsed SAT clauses from functional tests.

    Methods:
        run_all_tests(): Runs all available tests in sequence: PLE, UPD, TWL, and PDFs.
        run_ple_test(): Tests the pure literal elimination feature of the solver.
        run_upd_test(): Tests the unit propagation feature of the solver.
        run_twl_test(): Tests the Two Watched Literals (TWL) optimization.
        run_pdfs_test(): Validates solver performance against expected decision logs for PDF-based tests.
    """
    def __init__(self):
        self.results_files_directory = "../DATA/Clauses_Files/Clauses_Files_Results/PDFS_Results"
        self.clauses_files_directory = "../DATA/Clauses_Files/PDFS"
        self.func_results_files_directory = "../DATA/Clauses_Files/Clauses_Files_Results/TESTS_Results"
        self.func_clauses_files_directory = "../DATA/Clauses_Files/TESTS"
        self.results_files = self._get_results_files(self.results_files_directory)
        self.clauses_files = self._get_clauses_files(self.clauses_files_directory)
        self.func_results_files = self._get_results_files(self.func_results_files_directory)
        self.func_clauses_files = self._get_clauses_files(self.func_clauses_files_directory)
        self.expected_results = self._load_all_expected_results(self.results_files)
        self.clauses = self._load_all_clauses(self.clauses_files)
        self.func_expected_results = self._load_all_expected_results(self.func_results_files)
        self.func_clauses = self._load_all_clauses(self.func_clauses_files)

    def _get_results_files(self, results_files_directory):
        """
        Scans a directory for result files with the `.results` extension.

        Args:
            results_files_directory (str): Path to the directory containing result files.

        Returns:
            List[str]: List of file paths to `.results` files.
        """
        results_files = []
        # for directory in self.results_directories:
        for root, _, files in os.walk(results_files_directory):
            results_files.extend([os.path.join(root, f) for f in files if f.endswith('.results')])
        return results_files
    
    def _get_clauses_files(self, clauses_files_directory):
        """
        Scans a directory for SAT problem files with the `.cnf` extension.

        Args:
            clauses_files_directory (str): Path to the directory containing clause files.

        Returns:
            List[str]: List of file paths to `.cnf` files.
        """
        clauses_files = []
        # for directory in self.results_directories:
        for root, _, files in os.walk(clauses_files_directory):
            clauses_files.extend([os.path.join(root, f) for f in files if f.endswith('.cnf')])
        return clauses_files

    def _load_all_expected_results(self, results_files):
        """
        Loads all expected results from `.results` files.

        Args:
            results_files (List[str]): List of file paths to `.results` files.

        Returns:
            Dict[str, Dict[str, List[Dict]]]: Parsed expected results, keyed by filename and heuristic.

        Raises:
            ValueError: If a `.results` file is not properly formatted.
        """
        expected_results = {}
        for filepath in results_files:
            # Extract the file name without extension to use as a top-level key
            file_name = os.path.splitext(os.path.basename(filepath))[0]
            expected_results[file_name] = {}

            with open(filepath, 'r') as file:
                # Read all content from the file
                file_content = file.read()
                
                # Add square brackets and commas to make it a valid JSON array
                fixed_content = f"[{file_content.replace('}\n{', '},\n{')}]"
                
                # Parse the content as a JSON array
                json_objects = json.loads(fixed_content)
                
                for entry in json_objects:
                    heuristic = entry["heuristic"]
                    if heuristic not in expected_results[file_name]:
                        expected_results[file_name][heuristic] = []
                    expected_results[file_name][heuristic].extend(entry["steps"])
        return expected_results

    def _load_all_clauses(self, clauses_files):
        """
        Loads all SAT problem clauses from `.cnf` files.

        Args:
            clauses_files (List[str]): List of file paths to `.cnf` files.

        Returns:
            Dict[str, List[List[int]]]: Parsed SAT clauses, keyed by filename.
        """
        clauses = {}  # Dictionary to map file names to problems
        for filepath in clauses_files:
            # Read clauses and create a SAT problem
            clauses_tmp, num_vars, num_clauses = ClauseReader.read_file(filepath)
            # Extract the file name without the .cnf extension
            file_name = os.path.splitext(os.path.basename(filepath))[0]
            clauses[file_name] = clauses_tmp
        return clauses

    def run_pdfs_test(self):
        """
        Validates solver performance against expected decision logs for PDF-based tests.

        For each `.cnf` file, the solver is run with all specified heuristics, and its 
        decision logs are compared to the expected logs from the corresponding `.results` file.

        Returns:
            bool: True if all tests pass, False otherwise.
        """
        success = True
        for file in self.expected_results:
            for heuristic in self.expected_results[file]:
                problem = SATProblem(self.clauses[file])
                solver = DPLLSolver(problem=problem, use_logger=True, heuristic=heuristic)
                is_satisfiable = solver.solve()
                print(f"    Running test for {file} with heuristic {heuristic}")
                print(f"    Is satisfiable: {is_satisfiable}")
                if solver.get_decision_steps() == self.expected_results[file][heuristic]:
                    print("    Test passed")
                else:   
                    success = False
                    print("Test failed")
                    print(f"Expected: {self.expected_results[file][heuristic]}")
                    print(f"Actual: {solver.get_decision_steps()}")
        print("ALL PDF TESTS PASSED" if success else "SOME PDF TESTS FAILED")
        return success

    def run_ple_test(self):
        """
        Tests the pure literal elimination (PLE) feature of the solver.

        Runs the solver on a specific test case and compares the decision log 
        to the expected result from the `.results` file.

        Returns:
            bool: True if the test passes, False otherwise.
        """        
        PLEProblem = SATProblem(self.func_clauses["ple_test"])
        PLESolver = DPLLSolver(PLEProblem, use_logger=True, use_pure_literal=True)
        is_satisfiable = PLESolver.solve()
        print(f"    Running the pure literal elimination test")
        print(f"    Is satisfiable: {is_satisfiable}")
        if PLESolver.get_decision_steps() == self.func_expected_results["ple_test"]['PLE']:
            print("    PLE test passed")
            return True
        else:
            print("PLE test failed")
            print(f"Expected: {self.func_expected_results['ple_test']['PLE']}")
            print(f"Actual: {PLESolver.get_decision_steps()}")
            return False

    def run_upd_test(self):
        """
        Tests the unit propagation (UPD) feature of the solver.

        Runs the solver on a specific test case for each heuristic and compares 
        the decision log to the expected result from the `.results` file.

        Returns:
            bool: True if all tests pass, False otherwise.
        """
        for heuristic in self.func_expected_results["upd_test"]:
            UPDProblem = SATProblem(self.func_clauses["upd_test"])
            UPDSolver = DPLLSolver(UPDProblem, use_logger=True, heuristic=heuristic)
            is_satisfiable = UPDSolver.solve()
            print(f"    Running the unit propagation test with heuristic {heuristic}")
            print(f"    Is satisfiable: {is_satisfiable}")
            if UPDSolver.get_decision_steps() == self.func_expected_results["upd_test"][heuristic]:
                print("    UPD test passed")
            else:
                print("UPD test failed")
                print(f"Expected: {self.func_expected_results['upd_test'][heuristic]}")
                print(f"Actual: {UPDSolver.get_decision_steps()}")
                return False
        return True

    def run_twl_test(self):
        """
        Tests the Two Watched Literals (TWL) optimization feature of the solver.

        Runs the solver on a specific test case for each heuristic and compares 
        the decision log to the expected result from the `.results` file.

        Returns:
            bool: True if all tests pass, False otherwise.
        """
        for heuristic in self.func_expected_results["twl_test"]:
            TWLProblem = SATProblem(self.func_clauses["twl_test"])
            TWLSolver = DPLLSolver(TWLProblem, use_logger=True, heuristic=heuristic, twl=True)
            is_satisfiable = TWLSolver.solve()
            print(f"    Running the two watched literals test with heuristic {heuristic}")
            print(f"    Is satisfiable: {is_satisfiable}")
            if TWLSolver.get_decision_steps() == self.func_expected_results["twl_test"][heuristic]:
                print("    TWL test passed")
            else:
                print("TWL test failed")
                print(f"Expected: {self.func_expected_results['twl_test'][heuristic]}")
                print(f"Actual: {TWLSolver.get_decision_steps()}")
                return False
        return True

    def run_all_tests(self):
        """
        Runs all available tests in sequence:
        1. Pure Literal Elimination (PLE) Test
        2. Unit Propagation (UPD) Test
        3. Two Watched Literals (TWL) Test
        4. PDF-Based Decision Log Test

        Returns:
            bool: True if all tests pass, False otherwise.
        """
        print("First test: pure literal elimination test")
        if self.run_ple_test(): 
            print("Second test: unit propagation test")
            if self.run_upd_test():
                print("Third test: TWL test")
                if self.run_twl_test():
                    print("Fourth test: pdfs test")
                    if self.run_pdfs_test():
                        print("ALL TESTS PASSED")
                        return True
# Usage:
tester = VersionTester()
tester.run_all_tests()
# tester.run_pdfs_test()
# tester.run_ple_test()
# tester.run_upd_test()